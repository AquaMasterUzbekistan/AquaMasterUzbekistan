import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aiogram import Bot
from app.config.settings import settings

async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    try:
        wh = await bot.get_webhook_info()
        print(f"Webhook URL: '{wh.url}'")
        print(f"Has custom certificate: {wh.has_custom_certificate}")
        print(f"Pending update count: {wh.pending_update_count}")
        print(f"Last error message: {wh.last_error_message}")
        print(f"Last error date: {wh.last_error_date}")
        print(f"Last sync error date: {wh.last_synchronization_error_date}")
        print(f"Max connections: {wh.max_connections}")
        print(f"IP address: {wh.ip_address}")
    except Exception as e:
        print(f"Error checking webhook: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
