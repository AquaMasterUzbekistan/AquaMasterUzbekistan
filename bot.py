"""AquaMasterUzbekistan Telegram Bot 24/7 entrypoint with auto-reconnect."""

import asyncio
import logging
import sys
import time

from main import main

logger = logging.getLogger("aquamaster")

if __name__ == "__main__":
    print("=== AquaMasterUzbekistan 24/7 Bot Started ===")
    while True:
        try:
            asyncio.run(main())
        except (KeyboardInterrupt, SystemExit):
            print("Bot shutdown requested by user/system.")
            break
        except Exception as exc:
            print(f"[RECONNECT] Network or runtime exception: {exc}")
            print("[RECONNECT] Re-establishing connection in 5 seconds...")
            time.sleep(5)
