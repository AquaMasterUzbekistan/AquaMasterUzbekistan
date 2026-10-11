"""Error handling middleware — never show raw errors to users."""

from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Update, CallbackQuery, Message

from app.localization import uz

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            err_str = str(e).lower()
            if "query is too old" in err_str or "message is not modified" in err_str:
                return None
            logger.error(f"Unhandled error: {e}", exc_info=True)
            # Try to send friendly error message
            if isinstance(event, CallbackQuery):
                try:
                    await event.answer(uz.ERROR_GENERIC, show_alert=True)
                except Exception:
                    pass
            elif isinstance(event, Message):
                try:
                    await event.answer(uz.ERROR_GENERIC)
                except Exception:
                    pass
            return None
