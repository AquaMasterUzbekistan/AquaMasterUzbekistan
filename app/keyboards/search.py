"""Calculator and search keyboards."""

from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.localization import uz
from app.keyboards.navigation import back_home_row


def calculators_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    buttons = [
        (uz.CALC_VOLUME, "calc:volume"),
        (uz.CALC_WATER_CHANGE, "calc:water_change"),
        (uz.CALC_HEATER, "calc:heater"),
        (uz.CALC_FILTER, "calc:filter"),
        (uz.CALC_AIR_PUMP, "calc:air_pump"),
        (uz.CALC_STOCKING, "calc:stocking"),
        (uz.CALC_SALT, "calc:salt"),
        (uz.CALC_FEEDING, "calc:feeding"),
    ]
    for text, data in buttons:
        builder.row(InlineKeyboardButton(text=text, callback_data=data))
    builder.row(*back_home_row())
    return builder.as_markup()


def search_main_keyboard() -> InlineKeyboardMarkup:
    """Main keyboard displayed on search prompt screen."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⚙️ Parametrlar bo'yicha filtrlar", callback_data="search:filters"))
    builder.row(*back_home_row())
    return builder.as_markup()


def filter_categories_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for selecting a filter dimension."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🌍 Havza va Ko'llar", callback_data="flt:cat:lake"))
    builder.row(InlineKeyboardButton(text="🥗 Oziqlanish ratsioni", callback_data="flt:cat:diet"))
    builder.row(InlineKeyboardButton(text="📏 Baliq o'lchami", callback_data="flt:cat:size"))
    builder.row(InlineKeyboardButton(text="⚔️ Tajovuzkorlik darajasi", callback_data="flt:cat:agg"))
    builder.row(InlineKeyboardButton(text="🧪 Suv muhiti (pH)", callback_data="flt:cat:ph"))
    builder.row(InlineKeyboardButton(text="🛡️ Muhofaza maqomi (IUCN)", callback_data="flt:cat:iucn"))
    builder.row(InlineKeyboardButton(text="◀️ Qidiruvga qaytish", callback_data="search"))
    builder.row(*back_home_row())
    return builder.as_markup()


def filter_options_keyboard(category: str) -> InlineKeyboardMarkup:
    """Options keyboard for the selected filter category."""
    builder = InlineKeyboardBuilder()
    if category == "lake":
        options = [
            ("🏝️ Malavi ko'li (Mbuna / Haps / Peacock)", "flt:do:lake:Malav"),
            ("🏞️ Tanganika ko'li (Tanganyika)", "flt:do:lake:Tang"),
            ("🌅 Viktoriya ko'li va Afrika daryolari", "flt:do:lake:Viktor"),
            ("🌴 Amazonka va Janubiy Amerika", "flt:do:lake:Amazon"),
            ("🌎 Markaziy va Shimoliy Amerika", "flt:do:lake:Amerika"),
            ("🎋 Osiyo va boshqa tropik daryolar", "flt:do:lake:Osiyo"),
        ]
    elif category == "diet":
        options = [
            ("🌿 O'txo'r / Aufwuchs Grazer (Herbivore)", "flt:do:diet:Herbivore"),
            ("🥩 Yirtqich / Piscivore (Carnivore)", "flt:do:diet:Carnivore"),
            ("🍲 Hammaxo'r (Omnivore)", "flt:do:diet:Omnivore"),
            ("🐜 Hasharotxo'r / Mikroyirtqich", "flt:do:diet:Micropredator"),
        ]
    elif category == "size":
        options = [
            ("🐟 Kichik baliqlar (< 8 sm)", "flt:do:size:small"),
            ("🐠 O'rta baliqlar (8 – 15 sm)", "flt:do:size:medium"),
            ("🐡 Yirik baliqlar (> 15 sm)", "flt:do:size:large"),
        ]
    elif category == "agg":
        options = [
            ("🕊️ Tinch baliqlar (Peaceful)", "flt:do:agg:peaceful"),
            ("⚖️ O'rtacha tajovuzkor (Semi-aggressive)", "flt:do:agg:semi_aggressive"),
            ("🔥 Agressiv va hududiy (Aggressive)", "flt:do:agg:aggressive"),
            ("⚡ O'ta agressiv (Highly aggressive)", "flt:do:agg:highly_aggressive"),
        ]
    elif category == "ph":
        options = [
            ("💧 Yumshoq kislotali (pH 5.0 – 6.8)", "flt:do:ph:acidic"),
            ("⚖️ Neytral suv (pH 6.8 – 7.4)", "flt:do:ph:neutral"),
            ("💎 Qattiq ishqoriy (pH 7.5 – 8.8)", "flt:do:ph:alkaline"),
        ]
    elif category == "iucn":
        options = [
            ("🔴 O'ta xavf ostida (CR - Critically Endangered)", "flt:do:iucn:CR"),
            ("🟠 Yo'qolib ketish arafasida (EN - Endangered)", "flt:do:iucn:EN"),
            ("🟡 Zaif (VU - Vulnerable)", "flt:do:iucn:VU"),
            ("🟢 Xavf kam (LC - Least Concern)", "flt:do:iucn:LC"),
        ]
    else:
        options = []

    for label, cdata in options:
        builder.row(InlineKeyboardButton(text=label, callback_data=cdata))

    builder.row(InlineKeyboardButton(text="◀️ Filtr toifalariga qaytish", callback_data="search:filters"))
    builder.row(*back_home_row())
    return builder.as_markup()


def search_results_keyboard(
    results: list,
    page: int = 1,
    total_pages: int = 1,
    query: str = "",
    filter_code: str = "",
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if query:
        builder.row(InlineKeyboardButton(
            text="🤖 AI chuqur tahlili (FishBase / SeriouslyFish)",
            callback_data=f"ai_search:{query[:35]}"
        ))
    for sp in results:
        builder.row(InlineKeyboardButton(
            text=f"🐟 {sp.scientific_name}",
            callback_data=f"profile:{sp.id}:summary"
        ))
    if total_pages > 1:
        nav = []
        # Encode pagination callback: "spg:page:flt_code" or "spg:page:q:query"
        tag = f"f_{filter_code}" if filter_code else f"q_{query[:20]}"
        if page > 1:
            nav.append(InlineKeyboardButton(text=uz.NAV_PREV, callback_data=f"spg:{page - 1}:{tag}"))
        nav.append(InlineKeyboardButton(text=f"📄 {page}/{total_pages}", callback_data="noop"))
        if page < total_pages:
            nav.append(InlineKeyboardButton(text=uz.NAV_NEXT, callback_data=f"spg:{page + 1}:{tag}"))
        builder.row(*nav)

    if filter_code:
        builder.row(InlineKeyboardButton(text="⚙️ Boshqa filtr tanlash", callback_data="search:filters"))
    else:
        builder.row(InlineKeyboardButton(text="🔎 Yangi matnli qidiruv", callback_data="search"))

    builder.row(*back_home_row())
    return builder.as_markup()
