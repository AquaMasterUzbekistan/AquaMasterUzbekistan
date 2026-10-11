"""Main menu inline keyboard."""

from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.localization import uz


def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    buttons = [
        (uz.MENU_AFRICAN, "african"),
        (uz.MENU_AMERICAN, "american"),
        (uz.MENU_LOCALITY, "locality_atlas"),
        (uz.MENU_FAMILIES, "families"),
        (uz.MENU_GENERA, "genera"),
        (uz.MENU_ALL_SPECIES, "all_species"),
        (uz.MENU_CATFISH_PLECO, "catfish_plecos"),
        (uz.MENU_LNUMBERS, "lnumber_catalog"),
        (uz.MENU_SEARCH, "search"),
        (uz.MENU_SEARCH_IMAGES, "search_images"),
        (uz.MENU_SYNONYMS_TRADES, "synonyms_trades"),
        (uz.MENU_COMPARE, "compare"),
        (uz.MENU_CALCULATORS, "calculators"),
        (uz.MENU_DICTIONARY, "dictionary"),
        (uz.MENU_DB_COVERAGE, "database_coverage"),
        (uz.MENU_SOURCES_INFO, "sources_info"),
        (uz.MENU_AUTHOR, "author"),
    ]
    for text, data in buttons:
        builder.row(InlineKeyboardButton(text=text, callback_data=data))
    return builder.as_markup()
