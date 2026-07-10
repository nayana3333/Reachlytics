import logging

from sqlalchemy.orm import Session

from app.ai.llm_client import LLMClient
from app.ai.prompts import CONTENT_ANALYSIS_PROMPT, MULTIMODAL_CONTENT_ANALYSIS_PROMPT
from app.core.config import get_settings
from app.models.content_analysis import ContentAnalysis
from app.services.frame_extraction_service import extract_frames

logger = logging.getLogger(__name__)


def _bounded_score(value, default: float) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return default


def _fallback_scores(transcript: str, target_audience: str) -> dict:
    words = transcript.lower().split()
    hook_terms = {"save", "fast", "simple", "demo", "new", "easy", "growth"}
    hook_score = min(1.0, 0.45 + 0.05 * len(hook_terms.intersection(words)))
    clarity_score = 0.76 if len(words) < 120 else 0.66
    emotional_appeal_score = 0.58
    shareability_score = min(0.92, (hook_score + emotional_appeal_score) / 2 + 0.12)
    audience_fit_score = 0.74 if len(target_audience) > 20 else 0.62
    return {
        "hook_score": hook_score,
        "clarity_score": clarity_score,
        "emotional_appeal_score": emotional_appeal_score,
        "shareability_score": shareability_score,
        "audience_fit_score": audience_fit_score,
        "product_category": "productivity / software",
        "summary": "The demo is clear and niche-focused, with solid in-audience appeal.",
        "visual_description": "Visual analysis was not available; this estimate is based on transcript text only.",
        "strengths": ["Specific audience promise", "Clear product walkthrough", "Practical hook"],
        "weaknesses": ["Needs a sharper emotional payoff", "Could show stronger proof or outcome"],
    }


def _normalized_analysis(raw: dict, fallback: dict) -> dict:
    return {
        "hook_score": _bounded_score(raw.get("hook_score"), fallback["hook_score"]),
        "clarity_score": _bounded_score(raw.get("clarity_score"), fallback["clarity_score"]),
        "emotional_appeal_score": _bounded_score(
            raw.get("emotional_appeal_score"), fallback["emotional_appeal_score"]
        ),
        "shareability_score": _bounded_score(raw.get("shareability_score"), fallback["shareability_score"]),
        "audience_fit_score": _bounded_score(raw.get("audience_fit_score"), fallback["audience_fit_score"]),
        "product_category": str(raw.get("product_category") or fallback["product_category"]),
        "summary": str(raw.get("summary") or fallback["summary"]),
        "visual_description": str(raw.get("visual_description") or fallback["visual_description"]),
        "strengths": list(raw.get("strengths") or fallback["strengths"]),
        "weaknesses": list(raw.get("weaknesses") or fallback["weaknesses"]),
    }


def analyze_content(
    db: Session, video_id: str, transcript: str, target_audience: str, video_path: str | None = None
) -> ContentAnalysis:
    data = _fallback_scores(transcript, target_audience)
    ai_source = "fallback"
    settings = get_settings()
    llm_client = LLMClient()
    provider = settings.ai_provider
    if provider == "gemini" and llm_client.gemini_enabled():
        text_call = llm_client.complete_json_gemini
        image_call = llm_client.complete_json_with_images_gemini
        text_source = "real_gemini_text"
        image_source = "real_gemini_mm"
    elif provider == "openrouter" and llm_client.openrouter_enabled():
        text_call = llm_client.complete_json_openrouter
        image_call = llm_client.complete_json_with_images_openrouter
        text_source = "real_openrouter_text"
        image_source = "real_openrouter_mm"
    elif provider == "anthropic" and llm_client.anthropic_enabled():
        text_call = llm_client.complete_json
        image_call = llm_client.complete_json_with_images
        text_source = "real_anthropic_text"
        image_source = "real_anthropic_mm"
    else:
        text_call = None
        image_call = None
        text_source = "fallback"
        image_source = "fallback"

    if text_call:
        try:
            frame_paths = extract_frames(video_path, num_frames=4) if video_path else []
            if frame_paths:
                raw = image_call(
                    MULTIMODAL_CONTENT_ANALYSIS_PROMPT.format(
                        transcript=transcript,
                        target_audience=target_audience,
                    ),
                    frame_paths,
                )
                ai_source = image_source
            else:
                raw = text_call(
                    CONTENT_ANALYSIS_PROMPT.format(
                        transcript=transcript,
                        target_audience=target_audience,
                    )
                )
                ai_source = text_source
            if not isinstance(raw, dict):
                raise ValueError("Content analysis response must be a JSON object")
            data = _normalized_analysis(raw, data)
        except Exception:
            logger.exception("LLM content analysis failed; using deterministic fallback")

    analysis = ContentAnalysis(
        video_id=video_id,
        hook_score=data["hook_score"],
        clarity_score=data["clarity_score"],
        emotional_appeal_score=data["emotional_appeal_score"],
        shareability_score=data["shareability_score"],
        audience_fit_score=data["audience_fit_score"],
        product_category=data["product_category"],
        summary=data["summary"],
        visual_description=data["visual_description"],
        strengths=data["strengths"],
        weaknesses=data["weaknesses"],
        ai_source=ai_source,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis
