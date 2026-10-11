"""L-number, LDA-number, and Catfish Catalog Handlers (Section 4 & Section 10).

Dedicated catalog for Loricariidae, Ancistrus, Hypancistrus, Panaque, Baryancistrus,
and other armored catfishes under DATZ / Transfish aquarium designations.
"""

from __future__ import annotations

import re
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.session import async_session
from app.repositories import LNumberRepository, SpeciesRepository
from app.keyboards.navigation import back_home_row
from app.utils.pagination import Paginator

router = Router(name="lnumber")


class LNumberSearchState(StatesGroup):
    waiting_query = State()


def lnumber_main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📋 Barcha L-raqamlar (A-Z)", callback_data="lnum:list:all:1"))
    builder.row(InlineKeyboardButton(text="🟡 Faqat Ancistrus L-raqamlari", callback_data="lnum:list:ancistrus:1"))
    builder.row(
        InlineKeyboardButton(text="🔢 L-raqamlar", callback_data="lnum:list:L:1"),
        InlineKeyboardButton(text="🔢 LDA-raqamlar", callback_data="lnum:list:LDA:1"),
    )
    builder.row(InlineKeyboardButton(text="🔎 L-raqam / Pleco qidirish", callback_data="lnum:search"))
    builder.row(*back_home_row())
    return builder.as_markup()


@router.callback_query(F.data.in_(["lnumber_catalog", "catfish_plecos"]))
async def lnumber_catalog_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    async with async_session() as session:
        repo = LNumberRepository(session)
        total_count = await repo.count_total()
        anc_count = await repo.count_total(only_ancistrus=True)

    text = (
        "🔢 <b>L-NUMBER VA LDA-NUMBER PLECO KATALOGI</b>\n\n"
        "<i>Loricariidae (Zirhli so'rg'ichli laqqalar) oilasi uchun maxsus ilmiy va akvarium reyestri.</i>\n\n"
        f"📊 <b>Katalogdagi jami L-raqamlar:</b> {total_count} ta\n"
        f"🟡 <b>Ancistrus L-raqamlari:</b> {anc_count} ta\n\n"
        "📌 <b>Muhim qoidalar:</b>\n"
        "• L-raqam — rasmiy biologik tur nomi emas, balki DATZ / Transfish savdo va kolleksiya belgisidir.\n"
        "• Rasmiy ilmiy tavsif olgan turlar (masalan, <i>Hypancistrus zebra</i>) va "
        "hali tavsiflanmagan populyatsiyalar (<i>Hypancistrus sp.</i>) qat'iy ajratilgan.\n"
        "• Har bir L-raqam daryo havzasi, o'lchami, parvarish talablari va manbalari bilan keltirilgan.\n\n"
        "Kerakli bo'limni tanlang:"
    )
    await callback.message.edit_text(text, reply_markup=lnumber_main_keyboard(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("lnum:list:"))
async def lnumber_list_view(callback: CallbackQuery):
    # format: lnum:list:<filter_type>:<page>
    parts = callback.data.split(":")
    filter_type = parts[2]
    page = int(parts[3])

    num_type = None
    only_anc = False
    title_suffix = "Barcha L-raqamlar"

    if filter_type == "ancistrus":
        only_anc = True
        title_suffix = "Ancistrus L-raqamlari"
    elif filter_type in ("L", "LDA"):
        num_type = filter_type
        title_suffix = f"{filter_type}-raqamlar"

    async with async_session() as session:
        repo = LNumberRepository(session)
        total_items = await repo.count_total(number_type=num_type, only_ancistrus=only_anc)
        per_page = 8
        offset = (page - 1) * per_page
        items = await repo.get_all_paged(
            number_type=num_type,
            only_ancistrus=only_anc,
            limit=per_page,
            offset=offset,
        )

    total_pages = max(1, (total_items + per_page - 1) // per_page)

    builder = InlineKeyboardBuilder()
    for item in items:
        sci = item.scientific_name_current or "Undescribed sp."
        label = f"🐟 {item.designation} — {sci}"
        if len(label) > 42:
            label = label[:39] + "..."
        builder.row(InlineKeyboardButton(text=label, callback_data=f"lnum:view:{item.id}"))

    # Pagination navigation
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton(text="◀️", callback_data=f"lnum:list:{filter_type}:{page-1}"))
    nav_row.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="noop"))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton(text="▶️", callback_data=f"lnum:list:{filter_type}:{page+1}"))
    if nav_row:
        builder.row(*nav_row)

    builder.row(InlineKeyboardButton(text="◀️ Katalogga qaytish", callback_data="lnumber_catalog"))
    builder.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="home"))

    text = (
        f"🔢 <b>{title_suffix}</b>\n\n"
        f"Jami yozuvlar: <b>{total_items} ta</b> (Sahifa {page}/{total_pages})\n\n"
        "<i>Batafsil ma'lumot olish uchun quyidagi ro'yxatdan turni tanlang:</i>"
    )
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("lnum:view:"))
async def lnumber_detail_view(callback: CallbackQuery):
    lnum_id = int(callback.data.split(":")[2])
    async with async_session() as session:
        repo = LNumberRepository(session)
        item = await repo.get_by_id(lnum_id)

    if not item:
        await callback.answer("L-raqam topilmadi", show_alert=True)
        return

    # Status badge
    status_map = {
        "verified": "🟢 Ilmiy tasdiqlangan tur",
        "provisional": "🟡 Vaqtincha identifikatsiya",
        "undescribed": "⚪ Hali tasvirlanmagan tur (Undescribed species)",
    }
    status_badge = status_map.get(item.identification_status, "⚪ Maqom noaniq")

    text_parts = [
        f"🔢 <b>{item.designation}</b>" + (f" <i>({item.alternative_numbers})</i>" if item.alternative_numbers else ""),
        f"🏷️ <b>Hozirgi ilmiy nomi:</b> <i>{item.scientific_name_current or 'Tavsiflanmagan / Undescribed'}</i>",
        f"🛡️ <b>Taksonomik maqomi:</b> {status_badge}",
        f"🧬 <b>Klassifikatsiya:</b> {item.family_name} &gt; {item.subfamily_name or 'Ancistrinae'} &gt; <i>{item.genus_name or 'Loricariidae'}</i>\n",
        f"🇺🇿 <b>O'zbekcha nomi:</b> {item.common_name_uz or 'Ko\'rsatilmagan'}",
        f"🇬🇧 <b>Inglizcha nomi:</b> {item.common_name_en or 'Ko\'rsatilmagan'}",
        f"🇷🇺 <b>Ruscha nomi:</b> {item.common_name_ru or 'Ko\'rsatilmagan'}",
        f"🏷️ <b>Savdo nomlari:</b> {item.trade_names or 'Ko\'rsatilmagan'}\n",
        f"🌍 <b>Kelib chiqishi:</b> {item.country or 'Janubiy Amerika'}, {item.river_basin or 'Noma\'lum havza'}",
        f"📍 <b>Biotop tafsiloti:</b> {item.locality_detail or 'Ishonchli maʼlumot topilmadi.'}\n",
        f"📏 <b>Maksimal o'lchami:</b> {item.max_size_cm or '?'} sm",
        f"🌡️ <b>Suv harorati:</b> {item.temp_min or '?'}-{item.temp_max or '?'} °C",
        f"🧪 <b>pH diapazoni:</b> {item.ph_min or '?'}-{item.ph_max or '?'}",
        f"🥗 <b>Oziqlanish toifasi:</b> {item.dietary_category or 'Aufwuchs / Omnivorous'}\n",
        f"📝 <b>Tashqi ko'rinishi va belgilar:</b>\n{item.description or 'Ishonchli maʼlumot topilmadi.'}\n",
        f"🏠 <b>Akvariumda parvarishlash:</b>\n{item.aquarium_care or 'Ishonchli maʼlumot topilmadi.'}\n",
        f"📚 <b>Manba:</b> {item.source_reference or 'DATZ / PlanetCatfish'}",
        f"📅 <b>Oxirgi tekshirish:</b> {item.last_verified_date or '2026-10-11'}",
    ]
    text = "\n".join(text_parts)

    builder = InlineKeyboardBuilder()
    if item.species_list:
        for sp in item.species_list:
            builder.row(InlineKeyboardButton(text=f"🐟 {sp.scientific_name} profiliga o'tish", callback_data=f"{sp.id}:summary"))

    builder.row(InlineKeyboardButton(text="◀️ Ro'yxatga qaytish", callback_data="lnum:list:all:1"))
    builder.row(*back_home_row())

    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "lnum:search")
async def lnumber_search_prompt(callback: CallbackQuery, state: FSMContext):
    await state.set_state(LNumberSearchState.waiting_query)
    text = (
        "🔎 <b>L-NUMBER VA PLECO QIDIRUVI</b>\n\n"
        "Qidirilayotgan L-raqam, avlod yoki daryo havzasi nomini yozing:\n"
        "• <i>L046</i>, <i>L-46</i>, <i>LDA016</i>, <i>L144</i>, <i>L236</i>\n"
        "• <i>Zebra</i>, <i>King Tiger</i>, <i>Medusa</i>, <i>Lemon</i>\n"
        "• <i>Hypancistrus</i>, <i>Ancistrus</i>, <i>Panaque</i>\n"
        "• <i>Rio Xingu</i>, <i>Tapajos</i>, <i>Rio Negro</i>"
    )
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ Bekor qilish", callback_data="lnumber_catalog"))
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@router.message(LNumberSearchState.waiting_query, F.text, ~F.text.startswith("/"))
async def lnumber_search_process(message: Message, state: FSMContext):
    query = message.text.strip()
    await state.clear()

    async with async_session() as session:
        repo = LNumberRepository(session)
        # Try exact or normalized designation first
        exact_item = await repo.get_by_designation(query)
        if exact_item:
            results = [exact_item]
        else:
            results = await repo.search(query, limit=15)

    if not results:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="🔄 Qayta qidirish", callback_data="lnum:search"))
        builder.row(InlineKeyboardButton(text="◀️ Katalogga qaytish", callback_data="lnumber_catalog"))
        await message.answer(
            f"🔍 <i>\"{query}\"</i> bo'yicha L-raqamlar topilmadi.\n\n"
            "Iltimos, kodni tekshiring (masalan: <b>L046</b> yoki <b>L144</b>).",
            reply_markup=builder.as_markup(),
            parse_mode="HTML",
        )
        return

    builder = InlineKeyboardBuilder()
    for item in results:
        sci = item.scientific_name_current or "Undescribed"
        builder.row(InlineKeyboardButton(text=f"🐟 {item.designation} — {sci}", callback_data=f"lnum:view:{item.id}"))

    builder.row(InlineKeyboardButton(text="◀️ Katalogga qaytish", callback_data="lnumber_catalog"))
    builder.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="home"))

    await message.answer(
        f"🔍 <b>L-raqam qidiruv natijalari: {len(results)} ta topildi</b>\n"
        f"<i>\"{query}\" so'rovi bo'yicha:</i>",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )
