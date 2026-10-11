"""Common/shared keyboard helpers."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def confirm_cancel_keyboard(confirm_data: str, cancel_data: str = "back") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=confirm_data),
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data=cancel_data),
    )
    return builder.as_markup()


def yes_no_keyboard(prefix: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Ha", callback_data=f"{prefix}:yes"),
        InlineKeyboardButton(text="❌ Yo'q", callback_data=f"{prefix}:no"),
    )
    return builder.as_markup()
