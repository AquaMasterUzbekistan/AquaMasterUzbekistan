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
    """Show the prompt to enter fish name."""
    await callback.message.edit_text(
        uz.SEARCH_PROMPT_MSG,
        reply_markup=search_main_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(SearchState.waiting_query)
    await callback.answer()


@router.message(F.text == "/search")
async def cmd_search_prompt(message: Message, state: FSMContext):
    """Command /search handler."""
    await message.answer(
        uz.SEARCH_PROMPT_MSG,
        reply_markup=search_main_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(SearchState.waiting_query)


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
            results = await search_svc.search_unified(query)
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


@router.message(SearchState.waiting_query, F.text, ~F.text.startswith("/"))
async def process_search_text(message: Message, state: FSMContext):
    """Search fish by text query — unified exact, token, and fuzzy matching."""
    from app.services import FishService
    from app.utils.formatting import format_standard_reference_card, format_lnumber_reference_card
    from app.keyboards.profile import profile_tabs_keyboard
    from app.repositories import LNumberRepository

    query = message.text.strip()
    await state.clear()
    user_id = message.from_user.id if message.from_user else 0

    async with async_session() as session:
        user_repo = UserRepository(session)
        await user_repo.log_activity(user_id, "search", query)
        search_svc = SearchService(session)
        results = await search_svc.search_unified(query)

        # ── Case 1: Exactly 1 result found -> Direct Dossier with Photo ──
        if len(results) == 1:
            item = results[0]
            if item["type"] == "species":
                fish_svc = FishService(session)
                sp = await fish_svc.get_species(item["id"])
                if sp:
                    # Check if favorite
                    db_user = await user_repo.get_by_telegram_id(user_id)
                    is_fav = await user_repo.is_favorite(db_user.id, sp.id) if db_user else False
                    if db_user:
                        await user_repo.add_recently_viewed(db_user.id, sp.id)

                    genus_name = sp.genus.scientific_name if sp.genus else None
                    kb = profile_tabs_keyboard(sp.id, is_fav, sp.genus_id, genus_name)

                    # Send verified photo if exists
                    verified_img = None
                    if getattr(sp, "images", None) and sp.images:
                        verified_img = next(
                            (img for img in sp.images if img.verification.value == "verified" and (img.telegram_file_id or img.image_url)),
                            sp.images[0]
                        )

                    card_text = format_standard_reference_card(sp)
                    if verified_img and (verified_img.telegram_file_id or verified_img.image_url):
                        photo_target = verified_img.telegram_file_id or verified_img.image_url
                        caption = (
                            f"🐠 <b>{sp.scientific_name}</b>\n"
                            f"📸 <i>Manba: {verified_img.source or 'FishBase / Wikimedia'}</i>"
                        )
                        try:
                            sent_photo = await message.answer_photo(
                                photo=photo_target,
                                caption=caption,
                                parse_mode="HTML"
                            )
                            if not verified_img.telegram_file_id and sent_photo.photo:
                                verified_img.telegram_file_id = sent_photo.photo[-1].file_id
                                await session.commit()
                        except Exception:
                            pass
                    else:
                        card_text = "ℹ️ <i>Ishonchli surat: Ushbu tur uchun tasdiqlangan fotosurat hozircha bazada mavjud emas.</i>\n\n" + card_text

                    await safe_answer_html(message, card_text, reply_markup=kb)
                    return

            elif item["type"] == "lnumber":
                lnum_repo = LNumberRepository(session)
                lnum_item = await lnum_repo.get_by_id(item["id"])
                if lnum_item:
                    card_text = format_lnumber_reference_card(lnum_item)
                    builder = InlineKeyboardBuilder()
                    if lnum_item.species_list:
                        for s in lnum_item.species_list:
                            builder.row(InlineKeyboardButton(text=f"🐟 {s.scientific_name} profiliga o'tish", callback_data=f"profile:{s.id}:summary"))
                    builder.row(InlineKeyboardButton(text="🔎 Yangi qidiruv", callback_data="search"))
                    builder.row(*back_home_row())
                    await safe_answer_html(message, card_text, reply_markup=builder.as_markup())
                    return

        # ── Case 2: Multiple matching results found ──
        if len(results) > 1:
            paginator = Paginator(results, page=1, per_page=8)
            kb = search_results_keyboard(paginator.page_items, paginator.page, paginator.total_pages, query=query)
            await message.answer(
                f"🔍 <b>Qidiruv natijalari: {len(results)} ta mos tur topildi</b>\n"
                f"<i>\"{query}\" so'rovi bo'yicha:</i>",
                reply_markup=kb,
                parse_mode="HTML",
            )
            return

        # ── Case 3: No results found -> Strict Unverified fallback (NO AI) ──
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="✍️ Taklif qoldirish", callback_data=f"suggest:fish:{query[:30]}"))
        builder.row(InlineKeyboardButton(text="🔎 Qayta qidirish", callback_data="search"))
        builder.row(*back_home_row())

        await message.answer(
            uz.SEARCH_NOT_FOUND_MSG,
            reply_markup=builder.as_markup(),
            parse_mode="HTML",
        )
