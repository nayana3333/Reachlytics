from app.services import persona_service as module
from app.services.persona_service import generate_personas


def test_llm_persona_generation_uses_single_fallback_precompute(monkeypatch):
    calls = {"fallback": 0}
    original_fallback = module._fallback_personas

    class FakeLLMClient:
        def anthropic_enabled(self):
            return True

        def complete_json(self, prompt):
            return [
                {
                    "name": "Generated Persona",
                    "age": 30,
                    "location": "Bengaluru, India",
                    "profession": "Founder",
                    "interests": ["startups"],
                    "pain_points": ["low reach"],
                    "content_preferences": ["short demos"],
                    "engagement_tendency": 0.7,
                    "share_probability": 0.4,
                    "skepticism_level": 0.2,
                }
                for _ in range(10)
            ]

    def counted_fallback(count, target_audience):
        calls["fallback"] += 1
        return original_fallback(count, target_audience)

    monkeypatch.setattr(module, "LLMClient", FakeLLMClient)
    monkeypatch.setattr(module, "_fallback_personas", counted_fallback)
    monkeypatch.setattr(module, "get_settings", lambda: type("Settings", (), {"ai_provider": "anthropic"})())

    personas = generate_personas(25, "startup founders", batch_size=10)

    assert len(personas) == 25
    assert calls["fallback"] == 1
