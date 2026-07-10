from app.services import agent_reason_service as module
from app.services.agent_reason_service import enrich_decision_reasons


def test_reason_generation_batches_llm_calls(monkeypatch):
    calls = {"count": 0}

    class FakeLLMClient:
        def anthropic_enabled(self):
            return True

        def complete_json(self, prompt):
            calls["count"] += 1
            return [
                {"persona_index": index, "reason": f"Reason {index}"}
                for index in range((calls["count"] - 1) * 10, calls["count"] * 10)
            ]

    monkeypatch.setattr(module, "LLMClient", FakeLLMClient)
    monkeypatch.setattr(module, "get_settings", lambda: type("Settings", (), {"ai_provider": "anthropic"})())
    personas = [{"name": f"Persona {index}"} for index in range(25)]
    decisions = [
        {
            "persona_index": index,
            "action": "liked",
            "engagement_score": 0.7,
            "reason": "fallback",
        }
        for index in range(25)
    ]

    enriched = enrich_decision_reasons(
        decisions,
        personas,
        "Transcript",
        {"hook_score": 0.8},
        "founders",
        batch_size=10,
    )

    assert calls["count"] == 3
    assert enriched[0]["reason"] == "Reason 0"
    assert enriched[10]["reason"] == "Reason 10"
