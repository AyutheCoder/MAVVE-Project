"""
Application configuration loaded from environment variables.
Uses pydantic-settings for type-safe config management.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """MAVVE application settings."""

    # ── App ──────────────────────────────────────────────
    APP_NAME: str = "MAVVE"
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = True

    # ── Database ─────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://mavve:mavve_secret@localhost:5432/mavve_db"
    DATABASE_ECHO: bool = False

    # ── Redis ────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── LLM ──────────────────────────────────────────────
    LLM_PROVIDER: str = "openrouter"  # "gemini" | "openai" | "openrouter"
    GOOGLE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    LLM_MODEL_NAME: str = "google/gemini-2.0-flash-001"
    LLM_TEMPERATURE: float = 0.3

    # ── WhatsApp Business API ────────────────────────────
    WHATSAPP_API_TOKEN: Optional[str] = None
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None
    WHATSAPP_VERIFY_TOKEN: str = "mavve_verify_token_2026"
    WHATSAPP_API_URL: str = "https://graph.facebook.com/v21.0"

    # ── Bhashini ─────────────────────────────────────────
    BHASHINI_API_KEY: Optional[str] = None
    BHASHINI_USER_ID: Optional[str] = None
    BHASHINI_PIPELINE_URL: str = "https://dhruva-api.bhashini.gov.in"
    BHASHINI_MOCK_MODE: bool = True

    # ── Payment Gateway ──────────────────────────────────
    RAZORPAY_KEY_ID: Optional[str] = None
    RAZORPAY_KEY_SECRET: Optional[str] = None

    # ── MAVVE Agent Config ───────────────────────────────
    RTO_RISK_THRESHOLD: float = 0.65
    MAX_DISCOUNT_PERCENT: float = 15.0
    MAX_CONVERSATION_ROUNDS: int = 5
    SESSION_TIMEOUT_HOURS: int = 24
    ADDRESS_CONFIDENCE_THRESHOLD: float = 0.85

    # ── CORS ─────────────────────────────────────────────
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
