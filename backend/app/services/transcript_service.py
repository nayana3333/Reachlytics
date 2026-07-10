import logging

from openai import OpenAI
from sqlalchemy.orm import Session

from app.ai.llm_client import LLMClient
from app.models.transcript import Transcript
from app.models.video import Video
from app.core.config import get_settings

logger = logging.getLogger(__name__)


def _fallback_text(video: Video) -> str:
    text = (
        f"Demo video '{video.title}' introduces a product, explains the core problem, "
        "shows the workflow, and asks viewers to try it. The hook is practical and "
        "focused on saving time for a specific audience."
    )
    return text


def create_transcript(db: Session, video: Video) -> Transcript:
    settings = get_settings()
    text = ""
    language = "en"
    confidence = 0.0
    ai_source = "fallback"

    llm_client = LLMClient()

    if settings.ai_provider == "gemini" and llm_client.gemini_enabled():
        try:
            text = llm_client.transcribe_audio_gemini(video.file_path)
            confidence = 0.9 if text else 0.0
            if text:
                ai_source = "real_gemini"
        except Exception:
            logger.exception("Gemini transcription failed for video %s", video.id)

    if not text and settings.ai_provider == "anthropic" and settings.openai_api_key:
        try:
            client = OpenAI(api_key=settings.openai_api_key)
            with open(video.file_path, "rb") as video_file:
                result = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=video_file,
                    response_format="json",
                )
            text = getattr(result, "text", "") or ""
            confidence = 0.9 if text else 0.0
            if text:
                ai_source = "real_anthropic"
        except Exception:
            logger.exception("Whisper transcription failed for video %s", video.id)

    if not text:
        if settings.ai_provider == "gemini" and llm_client.gemini_enabled():
            complete_json = llm_client.complete_json_gemini
            source = "real_gemini"
        elif settings.ai_provider == "openrouter" and llm_client.openrouter_enabled():
            complete_json = llm_client.complete_json_openrouter
            source = "real_openrouter"
        elif settings.ai_provider == "anthropic" and llm_client.anthropic_enabled():
            complete_json = llm_client.complete_json
            source = "real_anthropic"
        else:
            complete_json = None
            source = "fallback"

        if complete_json:
            try:
                logger.warning(
                    "Falling back to filename-based LLM description for video %s; this is not a real transcript.",
                    video.id,
                )
                response = complete_json(
                    "Create a cautious fallback description for a video when audio transcription failed. "
                    "Return strict JSON: {\"text\": string}. "
                    f"Filename: {video.filename}. Title: {video.title}. "
                    f"Duration seconds: {video.duration_seconds}."
                )
                text = str(response.get("text") or "")
                confidence = 0.35
                if text:
                    ai_source = source
            except Exception:
                logger.exception("LLM transcript fallback failed for video %s", video.id)

    if not text:
        logger.warning(
            "Using deterministic transcript fallback for video %s; no real audio transcript is available.",
            video.id,
        )
        text = _fallback_text(video)
        confidence = 0.2

    transcript = Transcript(video_id=video.id, text=text, language=language, confidence=confidence, ai_source=ai_source)
    db.add(transcript)
    db.commit()
    db.refresh(transcript)
    return transcript


def create_mock_transcript(db: Session, video: Video) -> Transcript:
    return create_transcript(db, video)
