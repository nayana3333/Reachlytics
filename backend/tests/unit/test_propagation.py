from app.services.persona_service import generate_personas
from app.simulation.propagation import run_propagation


def test_propagation_outputs_core_artifacts():
    analysis = {
        "hook_score": 0.72,
        "clarity_score": 0.76,
        "emotional_appeal_score": 0.58,
        "shareability_score": 0.7,
        "audience_fit_score": 0.74,
    }
    personas = generate_personas(50, "solo founders and small teams running tech businesses")

    result = run_propagation(personas, analysis, "solo founders and small teams", 3)

    assert len(result["personas"]) == 50
    assert result["metrics"]["predicted_reach"] > 0
    assert result["metrics"]["verdict"]
    assert result["rounds"]
