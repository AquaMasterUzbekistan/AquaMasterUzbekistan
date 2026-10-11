"""Authentication and user registration middleware."""

from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery

from app.database.session import async_session
from app.repositories.user_repo import UserRepository
from app.localization import uz

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseMiddleware):
    """Registers users on first contact and blocks banned users."""

    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        from_user = None
        if isinstance(event, Message) and event.from_user:
            from_user = event.from_user
        elif isinstance(event, CallbackQuery) and event.from_user:
            from_user = event.from_user

        if from_user:
            async with async_session() as session:
                user_repo = UserRepository(session)
                user = await user_repo.get_or_create(
                    telegram_id=from_user.id,
                    username=from_user.username,
                    first_name=from_user.first_name,
                    last_name=from_user.last_name,
                    language_code=from_user.language_code,
                )

                if user.is_banned:
                    if isinstance(event, CallbackQuery):
                        await event.answer(uz.ERROR_BANNED, show_alert=True)
                    elif isinstance(event, Message):
                        await event.answer(uz.ERROR_BANNED)
                    return None

                data["db_user"] = user
                data["db_session"] = session
                return await handler(event, data)

        return await handler(event, data)
