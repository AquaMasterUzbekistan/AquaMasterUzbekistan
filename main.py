"""Main application entry point for AquaMasterUzbekistan Telegram Bot."""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault

from app.config.settings import settings
from app.database.base import Base
from app.database.engine import engine
from app.handlers import all_routers
from app.middleware import (
    ErrorHandlerMiddleware,
    RateLimitMiddleware,
    AuthMiddleware,
    LoggingMiddleware,
)
import app.models  # noqa: F401 — ensure all models are imported for metadata registration


def setup_logging() -> logging.Logger:
    """Configure console and rotating/file logging."""
    log_file_path = Path(settings.LOG_FILE)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    handlers: list[logging.Handler] = [console_handler]

    try:
        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        handlers.append(file_handler)
    except Exception as e:
        print(f"Warning: Could not open log file {log_file_path}: {e}", file=sys.stderr)

    logging.basicConfig(level=log_level, handlers=handlers, force=True)
    return logging.getLogger("aquamaster")


logger = setup_logging()


async def set_bot_commands(bot: Bot) -> None:
    """Register standard commands in Telegram UI command menu."""
    commands = [
        BotCommand(command="start", description="🏠 Asosiy menyuni ochish"),
        BotCommand(command="search", description="🔍 Baliq turini qidirish"),
        BotCommand(command="images", description="🔎 Baliq suratlarini qidirish"),
        BotCommand(command="calc", description="🧮 Akvarium kalkulyatorlari"),
        BotCommand(command="my_aquarium", description="🏠 Mening akvariumlarim"),
        BotCommand(command="help", description="ℹ️ Yordam va qo'llanma"),
        BotCommand(command="admin", description="🔧 Boshqaruv paneli (adminlar uchun)"),
        BotCommand(command="admin_stats", description="📊 Statistika (adminlar uchun)"),
    ]
    try:
        await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
        logger.info("Bot commands successfully registered with Telegram")
    except Exception as e:
        logger.warning(f"Failed to register bot commands: {e}")


async def init_database() -> None:
    """Create tables if they don't exist already."""
    logger.info("Checking database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        try:
            from sqlalchemy import text
            await conn.execute(text("ALTER TABLE users ADD COLUMN last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
            logger.info("Added missing column last_active_at to users table")
        except Exception:
            # Column already exists
            pass
    logger.info("Database schema initialized successfully")

    # Check if database is empty on fresh deployment, seed automatically if needed
    try:
        from app.database.session import async_session
        from sqlalchemy import select, func
        from app.models.species import Species
        async with async_session() as session:
            count = (await session.execute(select(func.count()).select_from(Species))).scalar_one()
            if count == 0:
                logger.info("Database is empty. Running automatic initial data ingestion...")
                from scripts.run_full_ingestion import main as run_ingestion
                await run_ingestion()
                logger.info("Automatic initial data ingestion completed successfully!")
    except Exception as e:
        logger.warning("Auto-seed check note: %s", e)


async def on_startup(bot: Bot) -> None:
    """Bot startup hook."""
    logger.info("Starting AquaMasterUzbekistan Fish Atlas Bot...")
    await init_database()
    await set_bot_commands(bot)
    bot_info = await bot.get_me()
    logger.info(f"Bot connected: @{bot_info.username} (ID: {bot_info.id})")


async def on_shutdown(bot: Bot) -> None:
    """Bot shutdown hook."""
    logger.info("Shutting down bot...")
    await bot.session.close()
    await engine.dispose()
    logger.info("Bot stopped and resources cleanly disposed.")


def create_dispatcher() -> Dispatcher:
    """Create and configure aiogram Dispatcher."""
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Register Middlewares
    # Outer/inner middleware execution order:
    # ErrorHandler -> RateLimit -> Logging -> Auth -> Handler
    dp.message.middleware(ErrorHandlerMiddleware())
    dp.callback_query.middleware(ErrorHandlerMiddleware())

    dp.message.middleware(RateLimitMiddleware())
    dp.callback_query.middleware(RateLimitMiddleware())

    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())

    # Register all routers
    for router in all_routers:
        dp.include_router(router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    return dp


async def main() -> None:
    """Application main runner."""
    if not settings.BOT_TOKEN or settings.BOT_TOKEN == "your_telegram_bot_token_here":
        logger.error(
            "BOT_TOKEN is not configured! Please set BOT_TOKEN in your .env file or environment."
        )
        print("\n[!] ERROR: BOT_TOKEN is missing or using placeholder.", file=sys.stderr)
        print("Please configure BOT_TOKEN in your .env file before running.\n", file=sys.stderr)
        sys.exit(1)

    from aiogram.client.session.aiohttp import AiohttpSession

    # Optimized session for reliable Telegram connection without semaphore freezes
    custom_session = AiohttpSession(timeout=30.0)

    bot = Bot(
        token=settings.BOT_TOKEN,
        session=custom_session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = create_dispatcher()

    logger.info("Starting polling...")
    try:
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
            polling_timeout=15,
        )
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot execution terminated.")
