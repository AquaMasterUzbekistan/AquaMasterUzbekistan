"""Fish profile detail keyboards."""

from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.localization import uz
from app.keyboards.navigation import back_home_row


def profile_tabs_keyboard(
    species_id: int,
    is_favorite: bool = False,
    genus_id: int | None = None,
    genus_name: str | None = None,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if genus_id and genus_name:
        builder.row(InlineKeyboardButton(
            text=f"🔬 Jins: {genus_name} (barcha turlari)",
            callback_data=f"genus:{genus_id}"
        ))

    tabs = [
        ("📋 Standart ma'lumotnoma (A-H)", f"profile:{species_id}:summary"),
        (uz.PROFILE_INFO, f"profile:{species_id}:info"),
        (uz.PROFILE_WATER, f"profile:{species_id}:water"),
        (uz.PROFILE_DIET, f"profile:{species_id}:diet"),
        (uz.PROFILE_BEHAVIOUR, f"profile:{species_id}:behaviour"),
        (uz.PROFILE_BREEDING, f"profile:{species_id}:breeding"),
        (uz.PROFILE_GENETICS, f"profile:{species_id}:genetics"),
        (uz.PROFILE_LOCALITY, f"profile:{species_id}:locality"),
        (uz.PROFILE_SOURCES, f"profile:{species_id}:sources"),
        (uz.PROFILE_FIND_IMAGES, f"fish_images:fetch:{species_id}"),
        (uz.PROFILE_REPORT, f"report:{species_id}"),
    ]
    for text, data in tabs:
        builder.row(InlineKeyboardButton(text=text, callback_data=data))

    # Favorite toggle
    if is_favorite:
        builder.row(InlineKeyboardButton(
            text=uz.PROFILE_UNFAVORITE, callback_data=f"unfav:{species_id}"
        ))
    else:
        builder.row(InlineKeyboardButton(
            text=uz.PROFILE_FAVORITE, callback_data=f"fav:{species_id}"
        ))

    builder.row(InlineKeyboardButton(text="🔎 Yangi qidiruv", callback_data="search"))
    builder.row(*back_home_row())
    return builder.as_markup()
