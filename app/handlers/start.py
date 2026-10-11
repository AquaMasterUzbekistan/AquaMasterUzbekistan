"""Start handler and main menu."""

from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from app.localization import uz
from app.keyboards import main_menu_keyboard
from app.database.session import async_session
from app.repositories import UserRepository

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Handle /start — show main menu and register/update user."""
    from_user = message.from_user
    if from_user:
        async with async_session() as session:
            user_repo = UserRepository(session)
            await user_repo.get_or_create(
                telegram_id=from_user.id,
                username=from_user.username,
                first_name=from_user.first_name,
                last_name=from_user.last_name,
                language_code=from_user.language_code,
            )

    await message.answer(
        uz.BOT_WELCOME,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "home")
async def go_home(callback: CallbackQuery):
    """Return to main menu."""
    await callback.message.edit_text(
        uz.BOT_WELCOME,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "noop")
async def noop_handler(callback: CallbackQuery):
    """Ignore noop button clicks (page info)."""
    await callback.answer()
