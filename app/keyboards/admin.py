"""Admin panel keyboards."""

from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.localization import uz
from app.keyboards.navigation import back_home_row


def admin_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    buttons = [
        (uz.ADMIN_ADD_SPECIES, "admin:add_species"),
        (uz.ADMIN_EDIT_SPECIES, "admin:edit_species"),
        (uz.ADMIN_DELETE_SPECIES, "admin:delete_species"),
        (uz.ADMIN_ADD_IMAGE, "admin:add_image"),
        (uz.ADMIN_MANAGE_ARTICLES, "admin:articles"),
        (uz.ADMIN_MANAGE_USERS, "admin:users"),
        (uz.ADMIN_STATS, "admin:stats"),
        ("📊 Baza taksonomiya auditi", "admin:audit"),
        ("🔄 Baza sinxronlash (Ingestion)", "admin:sync_db"),
    ]
    for text, data in buttons:
        builder.row(InlineKeyboardButton(text=text, callback_data=data))
    builder.row(InlineKeyboardButton(text=uz.NAV_HOME, callback_data="home"))
    return builder.as_markup()
