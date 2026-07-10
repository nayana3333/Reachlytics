import logging
import random
from typing import Any

from app.ai.llm_client import LLMClient
from app.ai.prompts import PERSONA_GENERATION_PROMPT
from app.core.config import get_settings

logger = logging.getLogger(__name__)

FALLBACK_NAMES = [
    "Priya Nair",
    "Arjun Mehta",
    "Sneha Rao",
    "Kabir Singh",
    "Ananya Iyer",
    "Rohan Das",
    "Maya Kapoor",
    "Neel Shah",
    "Tara Joshi",
    "Ishaan Verma",
]

FALLBACK_INTERESTS = [
    "startups",
    "productivity",
    "marketing",
    "AI tools",
    "design",
    "creator economy",
    "analytics",
    "small business",
    "coding",
    "finance",
]


def _fallback_personas(count: int, target_audience: str) -> list[dict]:
    random.seed(f"{count}:{target_audience}")
    personas = []
    for index in range(count):
        in_target = index < int(count * 0.7)
        interests = random.sample(FALLBACK_INTERESTS, 4)
        if in_target and "startups" not in interests:
            interests[0] = "startups"
        personas.append(
            {
                "name": f"{random.choice(FALLBACK_NAMES)} {index + 1}",
                "age": random.randint(19, 45 if in_target else 58),
                "location": random.choice(["Bengaluru, India", "Mumbai, India", "Delhi, India", "Austin, USA", "London, UK"]),
                "profession": random.choice(
                    ["Founder", "Product Manager", "Designer", "Student", "Growth Marketer", "Software Engineer"]
                ),
                "interests": interests,
                "pain_points": random.sample(
                    ["low reach", "manual workflows", "unclear messaging", "limited budget", "slow content testing"], 2
                ),
                "content_preferences": random.sample(
                    ["short demos", "case studies", "before-after proof", "tutorials", "founder stories"], 2
                ),
                "engagement_tendency": round(random.uniform(0.35, 0.9 if in_target else 0.72), 2),
                "share_probability": round(random.uniform(0.18, 0.78 if in_target else 0.55), 2),
                "skepticism_level": round(random.uniform(0.1, 0.65 if in_target else 0.85), 2),
                "in_target": in_target,
            }
        )
    random.shuffle(personas)
    return personas


def _as_float(value: Any, default: float) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return default


def _normalize_persona(raw: dict, fallback: dict, in_target: bool) -> dict:
    return {
        "name": str(raw.get("name") or fallback["name"]),
        "age": int(raw.get("age") or fallback["age"]),
        "location": str(raw.get("location") or raw.get("city") or fallback["location"]),
        "profession": str(raw.get("profession") or raw.get("job") or fallback["profession"]),
        "interests": list(raw.get("interests") or fallback["interests"])[:6],
        "pain_points": list(raw.get("pain_points") or raw.get("painPoints") or fallback["pain_points"])[:5],
        "content_preferences": list(
            raw.get("content_preferences")
            or raw.get("contentPreferences")
            or fallback["content_preferences"]
        )[:5],
        "engagement_tendency": _as_float(raw.get("engagement_tendency"), fallback["engagement_tendency"]),
        "share_probability": _as_float(raw.get("share_probability"), fallback["share_probability"]),
        "skepticism_level": _as_float(raw.get("skepticism_level"), fallback["skepticism_level"]),
        "in_target": in_target,
    }


def generate_personas_with_source(count: int, target_audience: str, batch_size: int = 15) -> tuple[list[dict], str]:
    settings = get_settings()
    llm_client = LLMClient()
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
        return _fallback_personas(count, target_audience), "fallback"

    personas: list[dict] = []
    fallback_personas = _fallback_personas(count, target_audience)
    try:
        while len(personas) < count:
            remaining = count - len(personas)
            current_batch_size = min(batch_size, remaining)
            prompt = PERSONA_GENERATION_PROMPT.format(
                count=current_batch_size,
                target_audience=target_audience,
            )
            raw_batch = complete_json(prompt)
            if not isinstance(raw_batch, list):
                raise ValueError("Persona generation response must be a JSON array")
            for raw in raw_batch[:current_batch_size]:
                index = len(personas)
                in_target = index < int(count * 0.7)
                personas.append(
                    _normalize_persona(
                        raw if isinstance(raw, dict) else {},
                        fallback_personas[index],
                        in_target,
                    )
                )
        return personas[:count], source
    except Exception:
        logger.exception("LLM persona generation failed; using deterministic fallback")
        return fallback_personas, "fallback"


def generate_personas(count: int, target_audience: str, batch_size: int = 15) -> list[dict]:
    personas, _source = generate_personas_with_source(count, target_audience, batch_size)
    return personas
