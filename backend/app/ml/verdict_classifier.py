from functools import lru_cache
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

PRE_SIM_FEATURES = [
    "hook_score",
    "clarity_score",
    "emotional_appeal_score",
    "shareability_score",
    "audience_fit_score",
    "population_size",
    "in_target_percentage",
]

MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "verdict_classifier.joblib"


@lru_cache
def load_pre_sim_model() -> Any | None:
    if not MODEL_PATH.exists():
        logger.info("ML verdict model not found at %s; skipping ML prediction.", MODEL_PATH)
        return None
    try:
        import joblib

        return joblib.load(MODEL_PATH)
    except Exception:
        logger.exception("Failed to load ML verdict model from %s", MODEL_PATH)
        return None


def warm_verdict_model() -> None:
    load_pre_sim_model()


def predict_pre_sim_verdict(features: dict[str, float | int]) -> str | None:
    model = load_pre_sim_model()
    if model is None:
        return None
    row = [[features[name] for name in PRE_SIM_FEATURES]]
    try:
        return str(model.predict(row)[0])
    except Exception:
        logger.exception("ML verdict prediction failed")
        return None
