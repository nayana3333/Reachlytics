import os

# Tests must never depend on the developer's local .env (e.g. a real
# AI_PROVIDER + API key configured for a live demo) — force a hermetic,
# fallback-only environment before any test module imports app.main.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["AI_PROVIDER"] = "mock"
os.environ["ANTHROPIC_API_KEY"] = ""
os.environ["OPENAI_API_KEY"] = ""
os.environ["GEMINI_API_KEY"] = ""
os.environ["OPENROUTER_API_KEY"] = ""
