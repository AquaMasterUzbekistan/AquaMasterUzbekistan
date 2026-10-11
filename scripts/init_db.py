"""Standalone script to create and initialize database tables."""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.base import Base
from app.database.engine import engine
from app.config.settings import settings
import app.models  # noqa: F401

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("init_db")


async def init_db() -> None:
    logger.info("Initializing database using DATABASE_URL=%s", settings.DATABASE_URL)
    try:
        async with engine.begin() as conn:
            logger.info("Creating all tables from declarative models...")
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables successfully created!")
    except Exception as e:
        logger.error("❌ Failed to initialize database: %s", e, exc_info=True)
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())
