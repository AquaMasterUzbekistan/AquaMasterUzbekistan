"""Main menu inline keyboard."""

from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.localization import uz


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Build the clean 5-panel main navigation keyboard."""
    builder = InlineKeyboardBuilder()
    buttons = [
        (uz.MENU_PANEL_SEARCH, "search"),
        (uz.MENU_PANEL_KNOWLEDGE, "knowledge_articles"),
        (uz.MENU_PANEL_CALCULATORS, "calculators"),
        (uz.MENU_PANEL_GLOSSARY, "dictionary"),
        (uz.MENU_PANEL_ABOUT_SUGGEST, "about_suggest"),
    ]
    for text, data in buttons:
        builder.row(InlineKeyboardButton(text=text, callback_data=data))
    return builder.as_markup()
