"""Discus section keyboards."""

from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.localization import uz
from app.keyboards.navigation import back_home_row


def discus_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    buttons = [
        (uz.DISCUS_WILD, "discus:wild"),
        (uz.DISCUS_SELECTIVE, "discus:selective"),
        (uz.DISCUS_COLOR, "discus:color"),
    ]
    for text, data in buttons:
        builder.row(InlineKeyboardButton(text=text, callback_data=data))
    builder.row(*back_home_row())
    return builder.as_markup()
