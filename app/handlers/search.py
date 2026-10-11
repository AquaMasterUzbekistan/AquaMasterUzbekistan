"""Search handler — Local database search and AI-powered encyclopedic discovery."""

from __future__ import annotations

import io
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from app.localization import uz
from app.keyboards.search import (
    search_results_keyboard,
    search_main_keyboard,
    filter_categories_keyboard,
    filter_options_keyboard,
)
from app.keyboards.navigation import back_home_row
from app.database.session import async_session
from app.services import SearchService, AIService
from app.repositories import UserRepository
from app.utils.pagination import Paginator
from app.utils.formatting import safe_answer_html

router = Router(name="search")


class SearchState(StatesGroup):
    waiting_query = State()


@router.callback_query(F.data == "search")
async def search_prompt(callback: CallbackQuery, state: FSMContext):
    prompt_text = (
        "🔎 <b>BALIQLARNI ILMIY QIDIRISH (ATLAS & AI)</b>\n\n"
        "Qidirilayotgan baliq nomini yozing:\n"
        "• Ilmiy nomi: <i>Labidochromis caeruleus</i>, <i>Symphysodon discus</i>\n"
        "• Ommabop / Xalq nomi: <i>Yellow lab</i>, <i>Skalyariya</i>, <i>Diskus</i>\n"
        "• Savdo nomi: <i>Pigeon Blood</i>, <i>L046</i>, <i>Red Zebra</i>\n"
        "• Jins yoki Oila: <i>Aulonocara</i>, <i>Apistogramma</i>, <i>Characidae</i>\n"
        "• Lokatsiya yoki Havza: <i>Rio Negro</i>, <i>Xingu</i>, <i>Lake Malawi</i>\n\n"
        "⚙️ Shuningdek, quyidagi tugma orqali <b>parametrlar bo'yicha filtrlash</b> mumkin:\n\n"
        "📚 Barcha ma'lumotlar <b>FishBase.org, Eschmeyer, SeriouslyFish, IUCN Red List</b> "
        "kabi xalqaro ilmiy manbalarga tayanadi."
    )
    await callback.message.edit_text(prompt_text, reply_markup=search_main_keyboard(), parse_mode="HTML")
    await state.set_state(SearchState.waiting_query)
    await callback.answer()


@router.callback_query(F.data == "search:filters")
async def search_filters_menu(callback: CallbackQuery, state: FSMContext):
    """Show filter categories."""
    await state.clear()
    text = (
        "⚙️ <b>BALIQLARNI PARAMETRLAR BO'YICHA FILTRLASH</b>\n\n"
        "Quyidagi toifalardan birini tanlang:\n"
        "• 🌍 <b>Havza va Ko'llar:</b> Malavi, Tanganika, Viktoriya, Amazonka va boshqalar\n"
        "• 🥗 <b>Oziqlanish ratsioni:</b> O'txo'r, Yirtqich, Hammaxo'r, Mikroyirtqich\n"
        "• 📏 <b>Baliq o'lchami:</b> Kichik (&lt;8 sm), O'rta (8-15 sm), Yirik (&gt;15 sm)\n"
        "• ⚔️ <b>Tajovuzkorlik:</b> Tinch, O'rtacha, Agressiv, O'ta agressiv\n"
        "• 🧪 <b>Suv muhiti (pH):</b> Kislotali, Neytral, Ishqoriy\n"
        "• 🛡️ <b>Muhofaza maqomi:</b> IUCN CR, EN, VU, LC"
    )
    await callback.message.edit_text(text, reply_markup=filter_categories_keyboard(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("flt:cat:"))
async def search_filter_category_options(callback: CallbackQuery):
    """Show options for the chosen filter category."""
    category = callback.data.split(":")[2]
    cat_names = {
        "lake": "🌍 Havza va Ko'llar bo'yicha",
        "diet": "🥗 Oziqlanish ratsioni bo'yicha",
        "size": "📏 Baliq o'lchami bo'yicha",
        "agg": "⚔️ Tajovuzkorlik darajasi bo'yicha",
        "ph": "🧪 Suv pH darajasi bo'yicha",
        "iucn": "🛡️ IUCN Qizil Kitob maqomi bo'yicha",
    }
    title = cat_names.get(category, "Filtr parametrlari")
    text = f"⚙️ <b>{title}</b>\n\nKerakli filtr variantini tanlang:"
    await callback.message.edit_text(text, reply_markup=filter_options_keyboard(category), parse_mode="HTML")
    await callback.answer()


async def _execute_filter_search(cat: str, val: str, session) -> list:
    """Helper to query filter_search according to category and value."""
    search_svc = SearchService(session)
    kwargs = {}
    if cat == "lake":
        kwargs["lake_name"] = val
    elif cat == "diet":
        kwargs["dietary_category"] = val
    elif cat == "size":
        if val == "small":
            kwargs["max_size"] = 8.0
        elif val == "medium":
            kwargs["min_size"] = 8.0
            kwargs["max_size"] = 15.0
        elif val == "large":
            kwargs["min_size"] = 15.0
    elif cat == "agg":
        kwargs["aggression"] = val
    elif cat == "ph":
        if val == "acidic":
            kwargs["ph_target"] = 6.0
        elif val == "neutral":
            kwargs["ph_target"] = 7.0
        elif val == "alkaline":
            kwargs["ph_target"] = 8.2
    elif cat == "iucn":
        kwargs["conservation_status"] = val

    return await search_svc.filter_search(**kwargs)


@router.callback_query(F.data.startswith("flt:do:"))
async def search_filter_apply(callback: CallbackQuery):
    """Execute filter search and display results."""
    parts = callback.data.split(":")
    cat = parts[2]
    val = parts[3]

    async with async_session() as session:
        results = await _execute_filter_search(cat, val, session)

    flt_code = f"{cat}_{val}"
    if not results:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="⚙️ Boshqa filtr tanlash", callback_data="search:filters"))
        builder.row(*back_home_row())
        await callback.message.edit_text(
            f"ℹ️ Ushbu filtr bo'yicha hech qanday tur topilmadi.\n\n"
            f"<i>Parametr: {cat} = {val}</i>",
            reply_markup=builder.as_markup(),
            parse_mode="HTML",
        )
        await callback.answer()
        return

    paginator = Paginator(results, page=1, per_page=8)
    kb = search_results_keyboard(
        paginator.page_items,
        page=paginator.page,
        total_pages=paginator.total_pages,
        filter_code=flt_code,
    )
    await callback.message.edit_text(
        f"⚙️ <b>Filtr natijalari: {len(results)} ta tur topildi</b>\n"
        f"<i>Parametr: {cat.upper()} = {val}</i>",
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("spg:"))
async def search_results_paginate(callback: CallbackQuery):
    """Handle pagination for search and filter results."""
    parts = callback.data.split(":", 2)
    page = int(parts[1])
    tag = parts[2]

    results = []
    header_text = ""
    query = ""
    flt_code = ""

    async with async_session() as session:
        if tag.startswith("f_"):
            flt_code = tag[2:]
            cat, val = flt_code.split("_", 1)
            results = await _execute_filter_search(cat, val, session)
            header_text = (
                f"⚙️ <b>Filtr natijalari: {len(results)} ta tur topildi</b>\n"
                f"<i>Parametr: {cat.upper()} = {val} (Sahifa: {page})</i>"
            )
        elif tag.startswith("q_"):
            query = tag[2:]
            search_svc = SearchService(session)
            results = await search_svc.search(query)
            header_text = (
                f"🔍 <b>Qidiruv natijalari: {len(results)} ta tur topildi</b>\n"
                f"<i>\"{query}\" so'rovi bo'yicha (Sahifa: {page}):</i>"
            )

    if not results:
        await callback.answer("Natijalar topilmadi", show_alert=True)
        return

    paginator = Paginator(results, page=page, per_page=8)
    kb = search_results_keyboard(
        paginator.page_items,
        page=paginator.page,
        total_pages=paginator.total_pages,
        query=query,
        filter_code=flt_code,
    )
    await callback.message.edit_text(header_text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.message(SearchState.waiting_query, F.photo)
async def process_search_photo_disabled(message: Message, state: FSMContext):
    """Notify user that search is strictly text-based."""
    await message.answer(
        "ℹ️ <b>AquaMasterUzbekistan — qat'iy matnli ilmiy atlasdir.</b>\n\n"
        "Fotosuratlardan noto'g'ri identifikatsiya qilish xatolarining oldini olish uchun "
        "qidiruv faqat ilmiy nomlar, sinonimlar, savdo nomlari va lokatsiyalar orqali amalga oshiriladi.\n\n"
        "Iltimos, baliq nomini matn ko'rinishida yozing:",
        parse_mode="HTML",
    )


@router.message(SearchState.waiting_query, F.text, ~F.text.startswith("/"))
async def process_search_text(message: Message, state: FSMContext):
    """Search fish by text query in local DB and AI."""
    query = message.text.strip()
    await state.clear()
    user_id = message.from_user.id if message.from_user else 0

    async with async_session() as session:
        user_repo = UserRepository(session)
        await user_repo.log_activity(user_id, "search", query)
        search_svc = SearchService(session)
        results = await search_svc.search(query)
        lnum_results = await search_svc.search_lnumbers(query) if not results else []

    if results:
        paginator = Paginator(results, page=1, per_page=8)
        kb = search_results_keyboard(paginator.page_items, paginator.page, paginator.total_pages, query=query)
        await message.answer(
            f"🔍 <b>Qidiruv natijalari: {len(results)} ta tur topildi</b>\n"
            f"<i>\"{query}\" so'rovi bo'yicha:</i>",
            reply_markup=kb,
            parse_mode="HTML",
        )
        return

    if lnum_results:
        builder = InlineKeyboardBuilder()
        for item in lnum_results:
            sci = item.scientific_name_current or "Undescribed"
            builder.row(InlineKeyboardButton(text=f"🔢 {item.designation} — {sci}", callback_data=f"lnum:view:{item.id}"))
        builder.row(InlineKeyboardButton(text="◀️ Bosh menyu", callback_data="home"))
        await message.answer(
            f"🔍 <b>L-raqam katalogidan topildi ({len(lnum_results)} ta):</b>\n"
            f"<i>\"{query}\" so'rovi bo'yicha:</i>",
            reply_markup=builder.as_markup(),
            parse_mode="HTML",
        )
        return

    # No local DB results -> Fallback to AI Search automatically
    wait_msg = await message.answer(
        f"🔍 <i>\"{query}\" atlas bazasida topilmadi.</i>\n\n"
        "🤖 <b>AI ilmiy qidiruvi olib bormoqda...</b>\n"
        "<i>FishBase.org, SeriouslyFish, IUCN, Malawi.si va Tanganyika.si dan to'liq ilmiy ma'lumot izlanmoqda...</i>",
        parse_mode="HTML",
    )

    ai_svc = AIService()
    ai_text = await ai_svc.search_and_explain(query)

    try:
        await wait_msg.delete()
    except Exception:
        pass

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔎 Boshqa baliq qidirish", callback_data="search"))
    builder.row(*back_home_row())

    await safe_answer_html(message, ai_text, reply_markup=builder.as_markup())


@router.callback_query(F.data.regexp(r"^ai_search:(.+)$"))
async def explicit_ai_search(callback: CallbackQuery):
    """Explicit AI deep dive search requested by user."""
    query = callback.data.split(":", 1)[1]

    wait_msg = await callback.message.answer(
        f"🤖 <b>AI chuqur tahlili olib bormoqda: \"{query}\"</b>\n\n"
        "<i>FishBase.org, SeriouslyFish.com, IUCN, Malawi.si va Tanganyika.si ma'lumotlariga tayanmoqda...</i>",
        parse_mode="HTML",
    )
    await callback.answer()

    ai_svc = AIService()
    ai_text = await ai_svc.search_and_explain(query)

    try:
        await wait_msg.delete()
    except Exception:
        pass

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔎 Yangi qidiruv", callback_data="search"))
    builder.row(*back_home_row())

    await safe_answer_html(callback.message, ai_text, reply_markup=builder.as_markup())
