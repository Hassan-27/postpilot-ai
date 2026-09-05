from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):

    # ── App ───────────────────────────────────────────────
    APP_NAME: str = "PostPilot AI"
    DEBUG: bool = False
    SECRET_KEY: str                          # required — no default means crash if missing
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ── Database ──────────────────────────────────────────
    DATABASE_URL: str                        # required

    # ── Redis ─────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Celery ────────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # ── LinkedIn OAuth ────────────────────────────────────
    LINKEDIN_CLIENT_ID: str
    LINKEDIN_CLIENT_SECRET: str
    LINKEDIN_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/linkedin/callback"

    # ── Gemini ────────────────────────────────────────────
    GEMINI_API_KEY: str
    
    # ── Discord ────────────────────────────────────────────
    DISCORD_WEBHOOK_URL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",                      # ignore unexpected env vars (safe for Docker)
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()