"""Rate limiting middleware."""

from __future__ import annotations

import time
import logging
from collections import defaultdict
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery

from app.config.settings import settings
from app.localization import uz

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self):
        self._requests: dict[int, list[float]] = defaultdict(list)
        self._limit = settings.RATE_LIMIT_PER_MINUTE
        self._window = 60.0

    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        user_id = None
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id

        if user_id:
            now = time.time()
            # Clean old entries
            self._requests[user_id] = [
                t for t in self._requests[user_id] if now - t < self._window
            ]
            if len(self._requests[user_id]) >= self._limit:
                logger.warning(f"Rate limit hit for user {user_id}")
                if isinstance(event, CallbackQuery):
                    await event.answer(uz.ERROR_RATE_LIMIT, show_alert=True)
                elif isinstance(event, Message):
                    await event.answer(uz.ERROR_RATE_LIMIT)
                return None
            self._requests[user_id].append(now)

        return await handler(event, data)
