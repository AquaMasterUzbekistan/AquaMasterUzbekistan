"""African cichlid navigation keyboards."""

from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.localization import uz
from app.keyboards.navigation import back_home_row


def african_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    buttons = [
        (uz.AFRICAN_MALAWI, "african:malawi"),
        (uz.AFRICAN_TANGANYIKA, "african:tanganyika"),
        (uz.AFRICAN_VICTORIA, "african:victoria"),
        (uz.AFRICAN_OTHER, "african:other"),
    ]
    for text, data in buttons:
        builder.row(InlineKeyboardButton(text=text, callback_data=data))
    builder.row(*back_home_row())
    return builder.as_markup()


def malawi_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    buttons = [
        (uz.MALAWI_MBUNA, "malawi:mbuna"),
        (uz.MALAWI_HAPS, "malawi:haps"),
        (uz.MALAWI_PEACOCK, "malawi:peacock"),
        (uz.MALAWI_UTAKA, "malawi:utaka"),
        (uz.MALAWI_OTHER, "malawi:other"),
    ]
    for text, data in buttons:
        builder.row(InlineKeyboardButton(text=text, callback_data=data))
    builder.row(*back_home_row())
    return builder.as_markup()


def tanganyika_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    buttons = [
        (uz.TANG_SHELL, "tang:shell"),
        (uz.TANG_JULIDO, "tang:julido"),
        (uz.TANG_NEOLAMP, "tang:neolamp"),
        (uz.TANG_ALTO, "tang:alto"),
        (uz.TANG_FRONTOSA, "tang:frontosa"),
        (uz.TANG_TROPHEUS, "tang:tropheus"),
        (uz.TANG_XENO, "tang:xeno"),
        (uz.TANG_CALVUS, "tang:calvus"),
        (uz.TANG_OTHER, "tang:other"),
    ]
    for text, data in buttons:
        builder.row(InlineKeyboardButton(text=text, callback_data=data))
    builder.row(*back_home_row())
    return builder.as_markup()


def victoria_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    # Victoria species will be listed dynamically
    builder.row(*back_home_row())
    return builder.as_markup()
