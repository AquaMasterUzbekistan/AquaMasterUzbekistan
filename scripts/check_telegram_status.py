import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aiogram import Bot
from app.config.settings import settings

async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    me = await bot.get_me()
    print(f"Bot info: @{me.username} ({me.first_name}) [ID: {me.id}]")
    wh = await bot.get_webhook_info()
    print(f"Webhook URL: '{wh.url}' | Pending updates: {wh.pending_update_count}")
    res = await bot.delete_webhook(drop_pending_updates=True)
    print(f"Webhook deleted and pending updates dropped: {res}")
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
