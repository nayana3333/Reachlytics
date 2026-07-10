from types import SimpleNamespace
from unittest.mock import mock_open

from app.services import ai_analysis_service
from app.services import persona_service
from app.services import transcript_service


class FakeDB:
    def add(self, obj):
        self.obj = obj

    def commit(self):
        pass

    def refresh(self, obj):
        pass


def _settings(provider: str):
    return SimpleNamespace(
        ai_provider=provider,
        gemini_api_key="gemini-key" if provider == "gemini" else None,
        openrouter_api_key="openrouter-key" if provider == "openrouter" else None,
        openrouter_model="openrouter/free",
        anthropic_api_key="anthropic-key" if provider == "anthropic" else None,
        openai_api_key="openai-key" if provider == "anthropic" else None,
    )


def _persona_response(name: str):
    return [
        {
            "name": name,
            "age": 27,
            "location": "Bengaluru, India",
            "profession": "Creator",
            "interests": ["gaming", "audio"],
            "pain_points": ["bad sound"],
            "content_preferences": ["short demos"],
            "engagement_tendency": 0.8,
            "share_probability": 0.5,
            "skepticism_level": 0.2,
        }
    ]


def _analysis_response(summary: str):
    return {
        "hook_score": 0.7,
        "clarity_score": 0.8,
        "emotional_appeal_score": 0.6,
        "shareability_score": 0.55,
        "audience_fit_score": 0.9,
        "product_category": "gaming audio",
        "summary": summary,
        "visual_description": "A headset is shown during a gaming demo.",
        "strengths": ["clear product"],
        "weaknesses": ["limited proof"],
    }


def test_gemini_persona_generation_parses_real_response(monkeypatch):
    class FakeLLMClient:
        def gemini_enabled(self):
            return True

        def complete_json_gemini(self, prompt):
            return _persona_response("Gemini Persona")

    monkeypatch.setattr(persona_service, "get_settings", lambda: _settings("gemini"))
    monkeypatch.setattr(persona_service, "LLMClient", FakeLLMClient)

    personas, source = persona_service.generate_personas_with_source(1, "gamers")

    assert source == "real_gemini"
    assert personas[0]["name"] == "Gemini Persona"


def test_anthropic_persona_generation_falls_back_on_exception(monkeypatch):
    class FakeLLMClient:
        def anthropic_enabled(self):
            return True

        def complete_json(self, prompt):
            raise RuntimeError("provider down")

    monkeypatch.setattr(persona_service, "get_settings", lambda: _settings("anthropic"))
    monkeypatch.setattr(persona_service, "LLMClient", FakeLLMClient)

    personas, source = persona_service.generate_personas_with_source(2, "gamers")

    assert source == "fallback"
    assert len(personas) == 2
    assert personas[0]["name"] != "Gemini Persona"


def test_openrouter_persona_generation_parses_real_response(monkeypatch):
    class FakeLLMClient:
        def openrouter_enabled(self):
            return True

        def complete_json_openrouter(self, prompt):
            return _persona_response("OpenRouter Persona")

    monkeypatch.setattr(persona_service, "get_settings", lambda: _settings("openrouter"))
    monkeypatch.setattr(persona_service, "LLMClient", FakeLLMClient)

    personas, source = persona_service.generate_personas_with_source(1, "gamers")

    assert source == "real_openrouter"
    assert personas[0]["name"] == "OpenRouter Persona"


def test_anthropic_content_analysis_parses_real_response(monkeypatch):
    class FakeLLMClient:
        def anthropic_enabled(self):
            return True

        def complete_json(self, prompt):
            return _analysis_response("Anthropic text analysis")

        def complete_json_with_images(self, prompt, image_paths):
            return _analysis_response("Anthropic visual analysis")

    monkeypatch.setattr(ai_analysis_service, "get_settings", lambda: _settings("anthropic"))
    monkeypatch.setattr(ai_analysis_service, "LLMClient", FakeLLMClient)
    monkeypatch.setattr(ai_analysis_service, "extract_frames", lambda video_path, num_frames: [])

    analysis = ai_analysis_service.analyze_content(
        FakeDB(), "video-id", "Headset narration", "gamers", video_path="demo.mp4"
    )

    assert analysis.ai_source == "real_anthropic_text"
    assert analysis.summary == "Anthropic text analysis"


def test_gemini_content_analysis_uses_multimodal_source(monkeypatch):
    class FakeLLMClient:
        def gemini_enabled(self):
            return True

        def complete_json_gemini(self, prompt):
            return _analysis_response("Gemini text analysis")

        def complete_json_with_images_gemini(self, prompt, image_paths):
            assert image_paths == ["frame.jpg"]
            return _analysis_response("Gemini visual analysis")

    monkeypatch.setattr(ai_analysis_service, "get_settings", lambda: _settings("gemini"))
    monkeypatch.setattr(ai_analysis_service, "LLMClient", FakeLLMClient)
    monkeypatch.setattr(ai_analysis_service, "extract_frames", lambda video_path, num_frames: ["frame.jpg"])

    analysis = ai_analysis_service.analyze_content(
        FakeDB(), "video-id", "Headset narration", "gamers", video_path="demo.mp4"
    )

    assert analysis.ai_source == "real_gemini_mm"
    assert analysis.summary == "Gemini visual analysis"
    assert "headset" in analysis.visual_description.lower()


def test_openrouter_content_analysis_uses_multimodal_source(monkeypatch):
    class FakeLLMClient:
        def openrouter_enabled(self):
            return True

        def complete_json_openrouter(self, prompt):
            return _analysis_response("OpenRouter text analysis")

        def complete_json_with_images_openrouter(self, prompt, image_paths):
            assert image_paths == ["frame.jpg"]
            return _analysis_response("OpenRouter visual analysis")

    monkeypatch.setattr(ai_analysis_service, "get_settings", lambda: _settings("openrouter"))
    monkeypatch.setattr(ai_analysis_service, "LLMClient", FakeLLMClient)
    monkeypatch.setattr(ai_analysis_service, "extract_frames", lambda video_path, num_frames: ["frame.jpg"])

    analysis = ai_analysis_service.analyze_content(
        FakeDB(), "video-id", "Headset narration", "gamers", video_path="demo.mp4"
    )

    assert analysis.ai_source == "real_openrouter_mm"
    assert analysis.summary == "OpenRouter visual analysis"


def test_gemini_content_analysis_falls_back_on_exception(monkeypatch):
    class FakeLLMClient:
        def gemini_enabled(self):
            return True

        def complete_json_gemini(self, prompt):
            raise RuntimeError("provider down")

        def complete_json_with_images_gemini(self, prompt, image_paths):
            raise RuntimeError("provider down")

    monkeypatch.setattr(ai_analysis_service, "get_settings", lambda: _settings("gemini"))
    monkeypatch.setattr(ai_analysis_service, "LLMClient", FakeLLMClient)
    monkeypatch.setattr(ai_analysis_service, "extract_frames", lambda video_path, num_frames: [])

    analysis = ai_analysis_service.analyze_content(
        FakeDB(), "video-id", "Headset narration", "gamers", video_path="demo.mp4"
    )

    assert analysis.ai_source == "fallback"
    assert analysis.summary == "The demo is clear and niche-focused, with solid in-audience appeal."


def test_anthropic_content_analysis_falls_back_on_exception(monkeypatch):
    class FakeLLMClient:
        def anthropic_enabled(self):
            return True

        def complete_json(self, prompt):
            raise RuntimeError("provider down")

        def complete_json_with_images(self, prompt, image_paths):
            raise RuntimeError("provider down")

    monkeypatch.setattr(ai_analysis_service, "get_settings", lambda: _settings("anthropic"))
    monkeypatch.setattr(ai_analysis_service, "LLMClient", FakeLLMClient)
    monkeypatch.setattr(ai_analysis_service, "extract_frames", lambda video_path, num_frames: [])

    analysis = ai_analysis_service.analyze_content(
        FakeDB(), "video-id", "Headset narration", "gamers", video_path="demo.mp4"
    )

    assert analysis.ai_source == "fallback"
    assert analysis.product_category == "productivity / software"


def test_gemini_transcription_uses_gemini_branch(monkeypatch):
    class FakeLLMClient:
        def gemini_enabled(self):
            return True

        def transcribe_audio_gemini(self, video_path):
            return "A creator demos a wireless gaming headset."

    video = SimpleNamespace(
        id="video-id",
        file_path="demo.mp4",
        filename="demo.mp4",
        title="Headset demo",
        duration_seconds=12,
    )
    monkeypatch.setattr(transcript_service, "get_settings", lambda: _settings("gemini"))
    monkeypatch.setattr(transcript_service, "LLMClient", FakeLLMClient)

    transcript = transcript_service.create_transcript(FakeDB(), video)

    assert transcript.ai_source == "real_gemini"
    assert "headset" in transcript.text


def test_anthropic_transcription_uses_mocked_whisper(monkeypatch):
    class FakeTranscriptions:
        def create(self, **kwargs):
            return SimpleNamespace(text="Whisper transcript for a headset demo.")

    class FakeOpenAI:
        def __init__(self, api_key):
            self.audio = SimpleNamespace(transcriptions=FakeTranscriptions())

    video = SimpleNamespace(
        id="video-id",
        file_path="demo.mp4",
        filename="demo.mp4",
        title="Headset demo",
        duration_seconds=12,
    )
    monkeypatch.setattr(transcript_service, "get_settings", lambda: _settings("anthropic"))
    monkeypatch.setattr(transcript_service, "OpenAI", FakeOpenAI)
    monkeypatch.setattr("builtins.open", mock_open(read_data=b"fake video"))

    transcript = transcript_service.create_transcript(FakeDB(), video)

    assert transcript.ai_source == "real_anthropic"
    assert "Whisper transcript" in transcript.text


def test_openrouter_transcription_uses_llm_description_fallback(monkeypatch):
    class FakeLLMClient:
        def openrouter_enabled(self):
            return True

        def complete_json_openrouter(self, prompt):
            return {"text": "OpenRouter cautious description for a gaming headset video."}

    video = SimpleNamespace(
        id="video-id",
        file_path="demo.mp4",
        filename="demo.mp4",
        title="Headset demo",
        duration_seconds=12,
    )
    monkeypatch.setattr(transcript_service, "get_settings", lambda: _settings("openrouter"))
    monkeypatch.setattr(transcript_service, "LLMClient", FakeLLMClient)

    transcript = transcript_service.create_transcript(FakeDB(), video)

    assert transcript.ai_source == "real_openrouter"
    assert "OpenRouter cautious description" in transcript.text


def test_transcription_falls_back_when_provider_fails(monkeypatch):
    class FakeLLMClient:
        def transcribe_audio_gemini(self, video_path):
            raise RuntimeError("provider down")

        def gemini_enabled(self):
            return False

    video = SimpleNamespace(
        id="video-id",
        file_path="demo.mp4",
        filename="demo.mp4",
        title="Headset demo",
        duration_seconds=12,
    )
    monkeypatch.setattr(transcript_service, "get_settings", lambda: _settings("gemini"))
    monkeypatch.setattr(transcript_service, "LLMClient", FakeLLMClient)

    transcript = transcript_service.create_transcript(FakeDB(), video)

    assert transcript.ai_source == "fallback"
    assert "Headset demo" in transcript.text
