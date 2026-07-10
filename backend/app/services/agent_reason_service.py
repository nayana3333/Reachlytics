import json
import logging

from app.ai.llm_client import LLMClient
from app.core.config import get_settings

logger = logging.getLogger(__name__)


def _chunks(items: list[dict], size: int):
    for index in range(0, len(items), size):
        yield items[index : index + size]


def enrich_decision_reasons_with_source(
    decisions: list[dict],
    personas: list[dict],
    transcript: str,
    content_analysis: dict,
    target_audience: str,
    batch_size: int = 12,
) -> tuple[list[dict], str]:
    settings = get_settings()
    llm_client = LLMClient()
    if settings.ai_provider == "gemini" and llm_client.gemini_enabled():
        complete_json = llm_client.complete_json_gemini
        source_label = "real_gemini"
    elif settings.ai_provider == "openrouter" and llm_client.openrouter_enabled():
        complete_json = llm_client.complete_json_openrouter
        source_label = "real_openrouter"
    elif settings.ai_provider == "anthropic" and llm_client.anthropic_enabled():
        complete_json = llm_client.complete_json
        source_label = "real_anthropic"
    else:
        return decisions, "fallback"

    enriched = [{**decision} for decision in decisions]
    decision_by_index = {decision["persona_index"]: decision for decision in enriched}
    enriched_count = 0

    for batch in _chunks(enriched, batch_size):
        payload = [
            {
                "persona_index": decision["persona_index"],
                "action": decision["action"],
                "engagement_score": decision["engagement_score"],
                "persona": personas[decision["persona_index"]],
            }
            for decision in batch
        ]
        try:
            raw = complete_json(
                (
                    "You are simulating multiple social media personas reacting to a product demo. "
                    "The scoring engine has already decided each action. Generate individualized "
                    "2-3 sentence reasons for why each persona took that action.\n\n"
                    "Return strict JSON only as an array of objects:\n"
                    '[{"persona_index": integer, "reason": string}]\n\n'
                    f"Transcript:\n{transcript[:4000]}\n\n"
                    f"Content analysis:\n{json.dumps(content_analysis)}\n\n"
                    f"Target audience:\n{target_audience}\n\n"
                    f"Decisions and personas:\n{json.dumps(payload)}"
                )
            )
            if not isinstance(raw, list):
                raise ValueError("Batch reason response must be a JSON array")
            for item in raw:
                if not isinstance(item, dict):
                    continue
                persona_index = item.get("persona_index")
                reason = item.get("reason")
                if persona_index in decision_by_index and reason:
                    previous_reason = decision_by_index[persona_index].get("reason")
                    decision_by_index[persona_index]["reason"] = str(reason)
                    if str(reason) != previous_reason:
                        enriched_count += 1
        except Exception:
            logger.exception("LLM batch reason generation failed for %s decisions", len(batch))
            break

    source = source_label if decisions and enriched_count >= len(decisions) / 2 else "fallback"
    return enriched, source


def enrich_decision_reasons(
    decisions: list[dict],
    personas: list[dict],
    transcript: str,
    content_analysis: dict,
    target_audience: str,
    batch_size: int = 12,
) -> list[dict]:
    enriched, _source = enrich_decision_reasons_with_source(
        decisions, personas, transcript, content_analysis, target_audience, batch_size
    )
    return enriched
