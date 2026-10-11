"""Other freshwater fish keyboards."""

from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.localization import uz
from app.keyboards.navigation import back_home_row


def other_fish_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    buttons = [
        (uz.OTHER_TETRAS, "other:tetras"),
        (uz.OTHER_BARBS, "other:barbs"),
        (uz.OTHER_RASBORA, "other:rasbora"),
        (uz.OTHER_GOURAMI, "other:gourami"),
        (uz.OTHER_BETTA, "other:betta"),
        (uz.OTHER_LIVEBEARERS, "other:livebearers"),
        (uz.OTHER_CATFISH, "other:catfish"),
        (uz.OTHER_PLECOS, "other:plecos"),
        (uz.OTHER_LOACHES, "other:loaches"),
        (uz.OTHER_RAINBOW, "other:rainbow"),
        (uz.OTHER_KILLIFISH, "other:killifish"),
        (uz.OTHER_KNIFE, "other:knife"),
        (uz.OTHER_AROWANA, "other:arowana"),
        (uz.OTHER_BICHIRS, "other:bichirs"),
        (uz.OTHER_SHRIMP, "other:shrimp"),
        (uz.OTHER_SNAILS, "other:snails"),
        (uz.OTHER_OTHER, "other:other"),
    ]
    for text, data in buttons:
        builder.row(InlineKeyboardButton(text=text, callback_data=data))
    builder.row(*back_home_row())
    return builder.as_markup()
