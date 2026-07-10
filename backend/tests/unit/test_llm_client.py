from app.ai import llm_client as module
from app.ai.llm_client import LLMClient


class RetryableError(Exception):
    pass


class TextBlock:
    type = "text"
    text = '{"ok": true}'


class Response:
    content = [TextBlock()]


def test_complete_json_retries_transient_failure(monkeypatch):
    calls = {"count": 0}

    class Messages:
        def create(self, **kwargs):
            calls["count"] += 1
            if calls["count"] == 1:
                raise RetryableError("temporary network problem")
            return Response()

    class FakeAnthropic:
        def __init__(self, api_key):
            self.messages = Messages()

    monkeypatch.setattr(module, "APIConnectionError", RetryableError)
    monkeypatch.setattr(module, "Anthropic", FakeAnthropic)
    monkeypatch.setattr(module.time, "sleep", lambda seconds: None)
    monkeypatch.setattr(
        module,
        "get_settings",
        lambda: type("Settings", (), {"anthropic_api_key": "test-key"})(),
    )

    result = LLMClient().complete_json("Return JSON")

    assert result == {"ok": True}
    assert calls["count"] == 2
