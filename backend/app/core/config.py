from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Reachlytics API"
    environment: str = "development"
    database_url: str = "sqlite:///./reachlytics.db"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret_key: str = "dev-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    upload_dir: str = "uploads"
    max_upload_mb: int = 100
    allowed_video_extensions: str = ".mp4,.mov,.webm,.mkv"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash-lite"
    openrouter_api_key: str | None = None
    openrouter_model: str = "openrouter/free"
    ai_provider: str = "mock"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
