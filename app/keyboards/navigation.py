"""Common navigation keyboard builders."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.localization import uz


def back_home_row() -> list[InlineKeyboardButton]:
    """Standard back + home buttons."""
    return [
        InlineKeyboardButton(text=uz.NAV_BACK, callback_data="back"),
        InlineKeyboardButton(text=uz.NAV_HOME, callback_data="home"),
    ]


def pagination_row(prefix: str, page: int, total_pages: int) -> list[InlineKeyboardButton]:
    """Prev / page info / next row."""
    buttons = []
    if page > 1:
        buttons.append(InlineKeyboardButton(
            text=uz.NAV_PREV, callback_data=f"{prefix}:page:{page - 1}"
        ))
    buttons.append(InlineKeyboardButton(
        text=uz.NAV_PAGE.format(current=page, total=total_pages),
        callback_data="noop"
    ))
    if page < total_pages:
        buttons.append(InlineKeyboardButton(
            text=uz.NAV_NEXT, callback_data=f"{prefix}:page:{page + 1}"
        ))
    return buttons


def build_list_keyboard(
    items: list[tuple[str, str]],
    prefix: str,
    page: int = 1,
    total_pages: int = 1,
    columns: int = 1,
    page_prefix: str | None = None,
) -> InlineKeyboardMarkup:
    """Build a paginated list keyboard.

    items: list of (display_text, callback_data_suffix)
    """
    builder = InlineKeyboardBuilder()
    for text, data_suffix in items:
        builder.add(InlineKeyboardButton(
            text=text, callback_data=f"{prefix}:{data_suffix}"
        ))
    builder.adjust(columns)

    # Pagination if needed
    if total_pages > 1:
        builder.row(*pagination_row(page_prefix or prefix, page, total_pages))

    # Back + Home
    builder.row(*back_home_row())

    return builder.as_markup()
