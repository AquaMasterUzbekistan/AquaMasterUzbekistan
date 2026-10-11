import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from app.config.settings import settings

async def main():
    session = AiohttpSession(timeout=30.0)
    bot = Bot(token=settings.BOT_TOKEN, session=session)
    try:
        me = await bot.get_me()
        print(f"Success with AiohttpSession: @{me.username}")
        updates = await bot.get_updates(limit=1, timeout=1)
        print(f"Updates fetched: {len(updates)}")
    except Exception as e:
        print(f"AiohttpSession error: {type(e).__name__}: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
