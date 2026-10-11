"""Logging middleware."""

from __future__ import annotations

import logging
import time
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery

logger = logging.getLogger("bot.access")


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        start = time.monotonic()
        user_id = None
        action = "unknown"

        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
            action = f"msg:{event.text[:50] if event.text else 'media'}"
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id
            action = f"cb:{event.data}"

        result = await handler(event, data)

        elapsed = round((time.monotonic() - start) * 1000, 1)
        logger.info(f"user={user_id} action={action} time={elapsed}ms")

        return result
