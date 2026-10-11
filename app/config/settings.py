"""Application configuration from environment variables."""

from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_env_path)


class Settings:
    """Central configuration loaded from environment."""

    # Telegram
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    AUTHOR_STICKER_ID: str | None = os.getenv("AUTHOR_STICKER_ID", None)

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://aquamaster:secret@localhost:5432/aquamaster_db",
    )

    # Admin
    _admin_ids: list[int] | None = None
    _super_admin_ids: list[int] | None = None

    @property
    def ADMIN_IDS(self) -> list[int]:
        if self._admin_ids is not None:
            return self._admin_ids
        raw = os.getenv("ADMIN_IDS", "")
        cleaned = raw.replace(";", ",").replace(" ", ",")
        return [int(x.strip()) for x in cleaned.split(",") if x.strip().isdigit()]

    @ADMIN_IDS.setter
    def ADMIN_IDS(self, val: list[int]) -> None:
        self._admin_ids = val

    @property
    def SUPER_ADMIN_IDS(self) -> list[int]:
        if self._super_admin_ids is not None:
            return self._super_admin_ids
        raw = os.getenv("SUPER_ADMIN_IDS", "")
        cleaned = raw.replace(";", ",").replace(" ", ",")
        return [int(x.strip()) for x in cleaned.split(",") if x.strip().isdigit()]

    @SUPER_ADMIN_IDS.setter
    def SUPER_ADMIN_IDS(self, val: list[int]) -> None:
        self._super_admin_ids = val

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))

    # AI (ZenMux Primary)
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_API_URL: str = os.getenv("AI_API_URL", "https://zenmux.ai/api/v1")
    AI_MODEL: str = os.getenv("AI_MODEL", "dots-studio/dots3-note-prev")

    # AI (Google Gemini Fallback)
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_API_MODEL: str = os.getenv("GOOGLE_API_MODEL", "gemini-3.8-flash")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/bot.log")

    # Media
    MEDIA_PATH: str = os.getenv("MEDIA_PATH", "media/")
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))

    # Pagination
    PAGE_SIZE: int = 8


settings = Settings()
