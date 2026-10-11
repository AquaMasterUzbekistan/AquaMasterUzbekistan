"""Taxonomy, Family & Genus Pages, Database Coverage, Sources, and Author Handlers (Section 7, 9, 10, 16).

Implements:
- 🧬 Oilalar (Family pages with biological characteristics, genera list, verified counts)
- 🔬 Avlodlar (Genus pages with type species, diagnostic traits, species list)
- 🐟 Barcha turlar (A-Z paginated directory)
- 📚 Sinonimlar va savdo nomlari
- 📊 Ma'lumotlar bazasi qamrovi (Live coverage & audit summary)
- ℹ️ Manbalar haqida (Scientific source directory)
- 🏷️ Muallif (Author attribution: @shoazizoff with configurable sticker)
"""

from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select, func

from app.database.session import async_session
from app.repositories import FamilyRepository, GenusRepository, SpeciesRepository, LNumberRepository
from app.keyboards.navigation import back_home_row
from app.config import settings
from app.localization import uz
from app.models.taxonomy import Family, Genus
from app.models.species import Species, ReliabilityLevel

router = Router(name="taxonomy")


class SynonymSearchState(StatesGroup):
    waiting_query = State()


# ── 1. Oilalar (Families) ─────────────────────────────────────────────

@router.callback_query(F.data == "families")
async def families_list_menu(callback: CallbackQuery):
    async with async_session() as session:
        repo = FamilyRepository(session)
        families = await repo.get_all_ordered()

    builder = InlineKeyboardBuilder()
    for fam in families:
        c_name = f" ({fam.common_name})" if fam.common_name else ""
        builder.row(InlineKeyboardButton(text=f"🧬 {fam.scientific_name}{c_name}", callback_data=f"fam:view:{fam.id}"))

    builder.row(*back_home_row())
    text = (
        "🧬 <b>IXTIOLOGIK OILALAR (FAMILIES)</b>\n\n"
        "Atlasdagi barcha ilmiy tasniflangan baliq oilalari.\n"
        "Oila haqida umumiy biologiya, ekologiya, parvarish farqlari va tegishli avlodlarni "
        "ko'rish uchun oilani tanlang:"
    )
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("fam:view:"))
async def family_detail_view(callback: CallbackQuery):
    fam_id = int(callback.data.split(":")[2])
    async with async_session() as session:
        fam_repo = FamilyRepository(session)
        gen_repo = GenusRepository(session)
        fam = await fam_repo.get_by_id(fam_id)
        if not fam:
            await callback.answer("Oila topilmadi", show_alert=True)
            return

        stats = await fam_repo.get_family_stats(fam_id)
        genera = await gen_repo.get_by_family(fam_id)

    builder = InlineKeyboardBuilder()
    # Genera buttons
    for g in genera[:12]:
        builder.row(InlineKeyboardButton(text=f"🔬 {g.scientific_name}", callback_data=f"gen:view:{g.id}"))
    if len(genera) > 12:
        builder.row(InlineKeyboardButton(text=f"➕ Barcha {len(genera)} ta avlodni ko'rish", callback_data=f"fam:genera:{fam.id}:1"))

    builder.row(InlineKeyboardButton(text="◀️ Oilalar ro'yxatiga", callback_data="families"))
    builder.row(*back_home_row())

    text = (
        f"🧬 <b>OILA: {fam.scientific_name.upper()}</b>\n"
        f"<i>{fam.common_name or ''}</i>\n\n"
        f"📌 <b>Taksonomik o'rni:</b> Sinf: {fam.class_name or 'Actinopterygii'} | Turkum: {fam.order_name or 'Nomaʼlum'}\n\n"
        f"📊 <b>Atlasdagi statistikasi:</b>\n"
        f"• Tegishli avlodlar: <b>{stats['genera_count']} ta</b>\n"
        f"• Ro'yxatdagi turlar: <b>{stats['total_species']} ta</b>\n"
        f"• 🟢 Ilmiy tasdiqlangan profillar: <b>{stats['verified']} ta</b>\n"
        f"• 🟡 Kengaytirilayotgan profillar: <b>{stats['incomplete']} ta</b>\n\n"
        f"🔬 <b>Umumiy biologik xususiyatlari:</b>\n"
        f"{fam.general_biology or fam.description or 'Ishonchli maʼlumot toʻldirilmoqda.'}\n\n"
        f"🌍 <b>Geografik tarqalishi va biotoplar:</b>\n"
        f"{fam.distribution_overview or 'Ishonchli maʼlumot toʻldirilmoqda.'}\n\n"
        f"🥗 <b>Oziqlanish ekologiyasi:</b>\n"
        f"{fam.feeding_ecology or 'Ishonchli maʼlumot toʻldirilmoqda.'}\n\n"
        f"🥚 <b>Ko'payish xususiyatlari:</b>\n"
        f"{fam.reproduction_overview or 'Ishonchli maʼlumot toʻldirilmoqda.'}\n\n"
        f"🏠 <b>Akvariumda parvarishlash farqlari:</b>\n"
        f"{fam.aquarium_care_overview or 'Ishonchli maʼlumot toʻldirilmoqda.'}\n\n"
        "📚 <b>Ilmiy manbalar:</b> FishBase.org, Eschmeyer's Catalog of Fishes, CAS."
    )
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


# ── 2. Avlodlar (Genera) ──────────────────────────────────────────────

@router.callback_query(F.data.startswith("genera"))
async def genera_list_menu(callback: CallbackQuery):
    page = 1
    if ":" in callback.data:
        try:
            page = int(callback.data.split(":")[1])
        except (ValueError, IndexError):
            page = 1

    per_page = 10
    offset = (page - 1) * per_page
    async with async_session() as session:
        repo = GenusRepository(session)
        total_genera = await repo.count_total()
        genera = await repo.get_all_ordered(limit=per_page, offset=offset)

    total_pages = max(1, (total_genera + per_page - 1) // per_page)
    builder = InlineKeyboardBuilder()
    for g in genera:
        builder.row(InlineKeyboardButton(text=f"🔬 {g.scientific_name}", callback_data=f"gen:view:{g.id}"))

    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton(text="◀️", callback_data=f"genera:{page-1}"))
    nav_row.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="noop"))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton(text="▶️", callback_data=f"genera:{page+1}"))
    if nav_row:
        builder.row(*nav_row)

    builder.row(*back_home_row())
    text = (
        "🔬 <b>BALIQ AVLODLARI (GENERA)</b>\n\n"
        f"Atlasda jami: <b>{total_genera} ta</b> avlod ro'yxatga olingan.\n"
        f"<i>(Sahifa {page}/{total_pages})</i>\n\n"
        "Avlod sahifasini ochish uchun quyidagilardan birini tanlang:"
    )
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("gen:view:"))
async def genus_detail_view(callback: CallbackQuery):
    parts = callback.data.split(":")
    gen_id = int(parts[2])
    page = int(parts[3]) if len(parts) >= 4 else 1

    per_page = 8
    offset = (page - 1) * per_page

    async with async_session() as session:
        gen_repo = GenusRepository(session)
        sp_repo = SpeciesRepository(session)
        gen = await gen_repo.get_by_id(gen_id)
        if not gen:
            await callback.answer("Avlod topilmadi", show_alert=True)
            return

        stats = await gen_repo.get_genus_stats(gen_id)
        species_list = await sp_repo.get_by_genus(gen_id, limit=per_page, offset=offset)

    total_species = stats["total"]
    total_pages = max(1, (total_species + per_page - 1) // per_page)

    builder = InlineKeyboardBuilder()
    for sp in species_list:
        badge = "🟢" if sp.reliability == ReliabilityLevel.SCIENTIFIC else "🟡"
        builder.row(InlineKeyboardButton(text=f"{badge} {sp.scientific_name}", callback_data=f"{sp.id}:summary"))

    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton(text="◀️", callback_data=f"gen:view:{gen_id}:{page-1}"))
    if total_pages > 1:
        nav_row.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="noop"))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton(text="▶️", callback_data=f"gen:view:{gen_id}:{page+1}"))
    if nav_row:
        builder.row(*nav_row)

    if gen.family_id:
        builder.row(InlineKeyboardButton(text="🧬 Oila sahifasiga o'tish", callback_data=f"fam:view:{gen.family_id}"))
    builder.row(InlineKeyboardButton(text="◀️ Avlodlar ro'yxatiga", callback_data="genera:1"))
    builder.row(*back_home_row())

    text = (
        f"🔬 <b>AVLOD: {gen.scientific_name.upper()}</b>\n"
        f"<i>Muallif: {gen.author or 'Nomaʼlum'}, {gen.year_described or ''}</i>\n\n"
        f"🏷️ <b>Tipik tur (Type species):</b> <i>{gen.type_species or 'Tavsiflanmagan'}</i>\n\n"
        f"📊 <b>Statistika:</b>\n"
        f"• Atlasdagi jami turlar: <b>{total_species} ta</b>\n"
        f"• 🟢 Ilmiy tasdiqlangan: <b>{stats['verified']} ta</b>\n"
        f"• 🟡 Qayta tekshirilayotgan: <b>{stats['incomplete']} ta</b>\n\n"
        f"📝 <b>Diagnostik xususiyatlari:</b>\n"
        f"{gen.diagnostic_traits or gen.description or 'Ishonchli maʼlumot toʻldirilmoqda.'}\n\n"
        f"🌍 <b>Tarqalishi:</b> {gen.distribution or 'Ishonchli maʼlumot toʻldirilmoqda.'}\n"
        f"📌 <b>Taksonomik eslatma:</b> {gen.taxonomic_notes or 'Monofiletik avlod.'}\n\n"
        f"🐟 <b>Avlodga tegishli turlar (Sahifa {page}/{total_pages}):</b>"
    )
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


# ── 3. Barcha Turlar (All Species A-Z) ────────────────────────────────

@router.callback_query(F.data.startswith("all_species"))
async def all_species_paged(callback: CallbackQuery):
    page = 1
    if ":" in callback.data:
        try:
            page = int(callback.data.split(":")[1])
        except (ValueError, IndexError):
            page = 1

    per_page = 8
    offset = (page - 1) * per_page
    async with async_session() as session:
        sp_repo = SpeciesRepository(session)
        species_list = await sp_repo.get_published(limit=per_page, offset=offset)
        count_stmt = select(func.count(Species.id)).where(Species.is_published == True)
        total_sp = (await session.execute(count_stmt)).scalar_one() or 0

    total_pages = max(1, (total_sp + per_page - 1) // per_page)
    builder = InlineKeyboardBuilder()
    for sp in species_list:
        badge = "🟢" if sp.reliability == ReliabilityLevel.SCIENTIFIC else "🟡"
        builder.row(InlineKeyboardButton(text=f"{badge} {sp.scientific_name}", callback_data=f"{sp.id}:summary"))

    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton(text="◀️", callback_data=f"all_species:{page-1}"))
    nav_row.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="noop"))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton(text="▶️", callback_data=f"all_species:{page+1}"))
    if nav_row:
        builder.row(*nav_row)

    builder.row(*back_home_row())
    text = (
        "🐟 <b>BARCHA BALIQ TURLARI (A-Z)</b>\n\n"
        f"Atlasda jami chop etilgan turlar: <b>{total_sp} ta</b>\n"
        f"<i>(Sahifa {page}/{total_pages})</i>\n\n"
        "🟢 = Ilmiy tasdiqlangan | 🟡 = Havaskor kuzatuvi / Qayta tekshirilayotgan\n\n"
        "Turni tanlang:"
    )
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


# ── 4. Sinonimlar va Savdo Nomlari ───────────────────────────────────

@router.callback_query(F.data == "synonyms_trades")
async def synonyms_trades_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        "📚 <b>SINONIMLAR VA SAVDO NOMLARI KATALOGI</b>\n\n"
        "Ixtiologiyada ko'plab turlar bir necha marta tavsiflangan yoki keyinchalik boshqa "
        "avlodga ko'chirilgan (masalan: <i>Maylandia</i> vs <i>Pseudotropheus</i>, <i>Cichlasoma</i> tarixi).\n\n"
        "Shuningdek, akvarium savdosida tijoriy nomlar va rangli morflar (masalan: <i>OB Peacock</i>, "
        "<i>Red Zebra</i>, <i>Pigeon Blood Discus</i>, <i>Gold Nugget</i>) keng qo'llaniladi.\n\n"
        "🔍 <b>Ushbu qidiruv orqali siz:</b>\n"
        "• Tarixiy ilmiy sinonimlar bo'yicha haqiqiy qabul qilingan ilmiy turni topishingiz;\n"
        "• Tijoriy savdo nomlarining qaysi yovvoyi turga tegishli ekanligini aniqlashingiz mumkin.\n\n"
        "Qidirish uchun quyidagi tugmani bosing:"
    )
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔎 Sinonim yoki Savdo nomini qidirish", callback_data="syn:search"))
    builder.row(*back_home_row())
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "syn:search")
async def synonym_search_prompt(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SynonymSearchState.waiting_query)
    text = (
        "🔎 <b>SINONIM YOKI SAVDO NOMINI YOZING:</b>\n\n"
        "Misol uchun:\n"
        "• <i>Red Zebra</i>, <i>Yellow Lab</i>, <i>OB Peacock</i>\n"
        "• <i>Pseudotropheus zebra</i>, <i>Tilapia calliptera</i>\n"
        "• <i>Pigeon Blood</i>, <i>Blue Diamond</i>, <i>Gold Nugget</i>"
    )
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ Bekor qilish", callback_data="synonyms_trades"))
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@router.message(SynonymSearchState.waiting_query, F.text, ~F.text.startswith("/"))
async def synonym_search_execute(message: Message, state: FSMContext):
    query = message.text.strip()
    await state.clear()

    async with async_session() as session:
        sp_repo = SpeciesRepository(session)
        results = await sp_repo.search(query, limit=12)

    if not results:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="🔄 Qayta qidirish", callback_data="syn:search"))
        builder.row(InlineKeyboardButton(text="◀️ Ortga", callback_data="synonyms_trades"))
        await message.answer(
            f"🔍 <i>\"{query}\"</i> bo'yicha sinonim yoki savdo nomi topilmadi.",
            reply_markup=builder.as_markup(),
            parse_mode="HTML",
        )
        return

    builder = InlineKeyboardBuilder()
    for sp in results:
        builder.row(InlineKeyboardButton(text=f"🐟 {sp.scientific_name}", callback_data=f"{sp.id}:summary"))
    builder.row(InlineKeyboardButton(text="◀️ Ortga", callback_data="synonyms_trades"))
    builder.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="home"))

    await message.answer(
        f"🔍 <b>Sinonim / Savdo nomi bo'yicha topildi ({len(results)} ta):</b>\n"
        f"<i>\"{query}\" so'rovi uchun mos turlar:</i>",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )


# ── 5. Ma'lumotlar Bazasi Qamrovi (Completeness Coverage) ────────────

@router.callback_query(F.data == "database_coverage")
async def database_coverage_report(callback: CallbackQuery):
    async with async_session() as session:
        sp_count = (await session.execute(select(func.count(Species.id)))).scalar_one() or 0
        fam_count = (await session.execute(select(func.count(Family.id)))).scalar_one() or 0
        gen_count = (await session.execute(select(func.count(Genus.id)))).scalar_one() or 0
        lnum_repo = LNumberRepository(session)
        lnum_count = await lnum_repo.count_total()

        ver_stmt = select(func.count(Species.id)).where(Species.reliability == ReliabilityLevel.SCIENTIFIC)
        ver_count = (await session.execute(ver_stmt)).scalar_one() or 0

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="ℹ️ Manbalar haqida", callback_data="sources_info"))
    builder.row(*back_home_row())

    text = (
        "📊 <b>MA'LUMOTLAR BAZASI QAMROVI VA AUDIT HISOBOTI</b>\n\n"
        "AquaMasterUzbekistan doimiy avtomatlashtirilgan ixtiologik audit tizimiga ega.\n\n"
        "📈 <b>Joriy holat ko'rsatkichlari:</b>\n"
        f"• Jami ilmiy turlar: <b>{sp_count} ta</b>\n"
        f"• Ro'yxatdagi oilalar: <b>{fam_count} ta</b>\n"
        f"• Ro'yxatdagi avlodlar: <b>{gen_count} ta</b>\n"
        f"• L-number / LDA-number yozuvlari: <b>{lnum_count} ta</b>\n"
        f"• 🟢 To'liq ilmiy tasdiqlangan profillar: <b>{ver_count} ta ({ver_count*100//max(1, sp_count)}%)</b>\n\n"
        "🌍 <b>Mintaqaviy qamrov holati:</b>\n"
        "• <b>Malawi ko'li:</b> Mbuna, Haps, Peacock, Utaka to'liq qamrab olingan.\n"
        "• <b>Tanganyika ko'li:</b> Barcha asosiy avlodlar kiritilgan.\n"
        "• <b>Victoria ko'li:</b> Haplochromis guruhi va muhofaza maqomlari ko'rsatilgan.\n"
        "• <b>Janubiy Amerika:</b> Cichlidae, Loricariidae, Callichthyidae, Characidae.\n"
        "• <b>L-raqamlar:</b> Ancistrus, Hypancistrus, Panaque, Baryancistrus.\n\n"
        "🛡️ <i>Auditorlik holati: <b>Coverage regularly verified</b>. "
        "Yangi tavsiflangan turlar FishBase va Eschmeyer bazalari orqali muntazam sinxronlashtiriladi.</i>"
    )
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


# ── 6. Manbalar Haqida (Scientific Sources) ──────────────────────────

@router.callback_query(F.data == "sources_info")
async def sources_info_page(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(*back_home_row())

    text = (
        "ℹ️ <b>ISHLATILADIGAN ASOSIY ILMIY MANBALAR</b>\n\n"
        "Atlasdagi barcha ma'lumotlar faqat nufuzli, ilmiy tekshirilgan va "
        "xalqaro ixtiologik jamoatchilik tomonidan qabul qilingan manbalarga tayanadi:\n\n"
        "1. 🌍 <a href=\"https://www.fishbase.org\">FishBase.org</a> — Dunyo baliqlarining eng yirik ilmiy ma'lumotlar bazasi.\n"
        "2. 🏛️ <a href=\"https://researcharchive.calacademy.org/research/ichthyology/catalog/fishcatmain.asp\">Eschmeyer’s Catalog of Fishes</a> — Kaliforniya Fanlar Akademiyasi (CAS) rasmiy taksonomik kodi.\n"
        "3. 🇲🇼 <a href=\"https://malawi.si\">Malawi Cichlid Database (Malawi.si)</a> — Malavi ko'li turlari, biotoplari va GPS lokatsiyalari.\n"
        "4. 🇹🇿 <a href=\"https://tanganyika.si\">Tanganyika Cichlid Database (Tanganyika.si)</a> — Tanganika ko'li taksonomiyasi.\n"
        "5. 🔬 <a href=\"https://www.seriouslyfish.com\">Seriously Fish</a> — Akvarium sharoitidagi parametrlar va biotopik profillar.\n"
        "6. 🛡️ <a href=\"https://www.iucnredlist.org\">IUCN Red List</a> — Yo'qolib ketish xavfi ostidagi turlarning rasmiy maqomi.\n"
        "7. 📚 <a href=\"https://www.cichlidae.com\">Cichlidae.com</a> — Xalqaro Sixlidlar Assotsiatsiyasi jurnali.\n"
        "8. 🐈 <b>DATZ & Ingo Seidel (Back to Nature L-Welse)</b> — L-number va LDA-number katalogi.\n\n"
        "⚠️ <i>Atlasda shaxsiy taxminlar yoki noaniq forum postlariga asoslangan xulosalarga yo'l qo'yilmaydi.</i>"
    )
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


# ── 7. Muallif (Author Attribution) ───────────────────────────────────

@router.callback_query(F.data == "author")
async def author_attribution_page(callback: CallbackQuery):
    # Optional sticker if configured in settings
    if settings.AUTHOR_STICKER_ID:
        try:
            await callback.message.answer_sticker(settings.AUTHOR_STICKER_ID)
        except Exception:
            pass

    builder = InlineKeyboardBuilder()
    builder.row(*back_home_row())

    text = (
        "🏷️ <b>Muallif: @shoazizoff</b>\n\n"
        "👨‍💻 <b>Loyiha yaratuvchisi va ishlab chiquvchisi:</b>\n"
        "Ushbu loyiha <b>shoazizoff</b> tomonidan ishlab chiqilidi.\n\n"
        "📢 <b>Telegram kanal va bog'lanish:</b>\n"
        "• Profil: @shoazizoff\n"
        "• Loyiha: <b>AquaMasterUzbekistan Fish Atlas</b>\n\n"
        "🇺🇿 <i>AquaMasterUzbekistan — O'zbekiston akvariumchilari uchun to'liq ilmiy va ishonchli elektron qo'llanmadir.</i>"
    )
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()
