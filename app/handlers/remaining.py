"""Breeding journal, health, genetics, locality, identify, articles, dictionary, about, favorites, reports handlers."""

from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.localization import uz
from app.keyboards.navigation import back_home_row, build_list_keyboard
from app.database.session import async_session
from app.repositories import UserRepository

# ── Breeding Journal ────────────────────────────────────────────────
breeding_router = Router(name="breeding_journal")


@breeding_router.callback_query(F.data == "breeding_journal")
async def breeding_journal(callback: CallbackQuery):
    async with async_session() as session:
        user_repo = UserRepository(session)
        db_user = await user_repo.get_by_telegram_id(callback.from_user.id)
        if db_user:
            from app.services import BreedingService
            svc = BreedingService(session)
            records = await svc.get_user_records(db_user.id)
        else:
            records = []

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()

    if records:
        for r in records:
            label = f"🥚 {r.species.scientific_name if r.species else '?'} — {r.spawning_date or '?'}"
            builder.row(InlineKeyboardButton(text=label, callback_data=f"breed:{r.id}"))
    else:
        pass

    builder.row(InlineKeyboardButton(text=uz.BREEDING_ADD, callback_data="breed:add"))
    builder.row(*back_home_row())

    text = uz.BREEDING_TITLE
    if not records:
        text += f"\n\n{uz.BREEDING_EMPTY}"

    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


# ── Health ──────────────────────────────────────────────────────────
health_router = Router(name="health")


@health_router.callback_query(F.data == "health")
async def health_menu(callback: CallbackQuery):
    async with async_session() as session:
        from app.services import HealthService
        svc = HealthService(session)
        conditions = await svc.get_all()

    items = [(f"{c.emoji or '🩺'} {c.name_uz}", str(c.id)) for c in conditions]
    kb = build_list_keyboard(items, "health_cond", columns=1)

    await callback.message.edit_text(
        f"{uz.HEALTH_TITLE}\n\n{uz.HEALTH_DISCLAIMER}",
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


@health_router.callback_query(F.data.regexp(r"^health_cond:(\d+)$"))
async def health_condition_detail(callback: CallbackQuery):
    cond_id = int(callback.data.split(":")[1])
    async with async_session() as session:
        from app.services import HealthService
        svc = HealthService(session)
        cond = await svc.get_condition(cond_id)

    if not cond:
        await callback.answer(uz.ERROR_NOT_FOUND, show_alert=True)
        return

    lines = [f"🩺 <b>{cond.name_uz}</b>"]
    if cond.name_en:
        lines.append(f"({cond.name_en})\n")
    if cond.symptoms:
        lines.append(f"📋 <b>Belgilar:</b>\n{cond.symptoms}")
    if cond.possible_causes:
        lines.append(f"\n❓ <b>Ehtimoliy sabablar:</b>\n{cond.possible_causes}")
    if cond.treatment_suggestions:
        lines.append(f"\n💊 <b>Tavsiyalar:</b>\n{cond.treatment_suggestions}")
    if cond.prevention:
        lines.append(f"\n🛡️ <b>Oldini olish:</b>\n{cond.prevention}")
    if cond.important_note:
        lines.append(f"\n⚠️ {cond.important_note}")
    lines.append(f"\n{uz.HEALTH_DISCLAIMER}")

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(*back_home_row())

    await callback.message.edit_text(
        "\n".join(lines), reply_markup=builder.as_markup(), parse_mode="HTML"
    )
    await callback.answer()


# ── Genetics ────────────────────────────────────────────────────────
genetics_router = Router(name="genetics")


@genetics_router.callback_query(F.data == "genetics")
async def genetics_menu(callback: CallbackQuery):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=uz.GENETICS_TERMS, callback_data="genetics:terms"))
    builder.row(InlineKeyboardButton(text=uz.GENETICS_MORPHS, callback_data="genetics:morphs"))
    builder.row(InlineKeyboardButton(text=uz.GENETICS_BREEDING_LINES, callback_data="genetics:lines"))
    builder.row(*back_home_row())

    await callback.message.edit_text(
        f"{uz.GENETICS_TITLE}\n\n{uz.GENETICS_DISCLAIMER}",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )
    await callback.answer()


@genetics_router.callback_query(F.data == "genetics:terms")
async def genetics_terms(callback: CallbackQuery):
    text = (
        "🧬 <b>Genetika atamalari</b>\n\n"
        "🌿 <b>F0</b> — Yovvoyidan tutilgan baliq (Wild Caught)\n"
        "🐟 <b>F1</b> — F0 juftliklarning avlodi (birinchi avlod)\n"
        "🐟 <b>F2</b> — F1 juftliklarning avlodi (ikkinchi avlod)\n"
        "🐟 <b>F3+</b> — Keyingi avlodlar\n\n"
        "🏷️ <b>WC</b> — Wild Caught (yovvoyidan tutilgan)\n"
        "🏠 <b>TB</b> — Tank Bred (akvariumda ko'paytirilgan)\n"
        "🧬 <b>Line breeding</b> — Muayyan xususiyatlarni kuchaytirish uchun seleksiya\n"
        "🔀 <b>Hybrid</b> — Turlararo chatishma\n\n"
        "⚠️ Gibridlar odatda ilmiy jihatdan yangi tur hisoblanmaydi."
    )
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(*back_home_row())

    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@genetics_router.callback_query(F.data == "genetics:morphs")
async def genetics_morphs(callback: CallbackQuery):
    text = (
        "🎨 <b>Rang shakllari (Morphs)</b>\n\n"
        "🟠 <b>OB</b> — Orange Blotch (to'q dog'li rang)\n"
        "🔵 <b>MC</b> — Marmalade Cat (ko'p rangli)\n"
        "⚪ <b>Albino</b> — Pigmentsiz oq rang\n"
        "✨ <b>Longfin</b> — Uzaytirilgan suzgichlar\n"
        "🌿 <b>Wild form</b> — Tabiiy rang shakli\n\n"
        "⚠️ Rang shakllari o'zgaruvchan bo'lishi mumkin.\n"
        "Rang meros qolish mexanizmlari hali to'liq o'rganilmagan."
    )
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(*back_home_row())

    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@genetics_router.callback_query(F.data == "genetics:lines")
async def genetics_lines(callback: CallbackQuery):
    text = (
        "🧬 <b>Seleksiya liniyalari</b>\n\n"
        "Seleksiya — muayyan xususiyatlarni (rang, o'lcham, shakl) kuchaytirish uchun\n"
        "tanlangan juftliklarni chatishtirishdir.\n\n"
        "📌 Muhim qoidalar:\n"
        "• F0 (Wild) dan boshlanadi\n"
        "• Har bir avlodda eng yaxshi namunalar tanlanadi\n"
        "• Yaqin qarindoshlar chatishmasidan saqlanish kerak\n"
        "• Genetik xilma-xillik saqlanishi muhim\n\n"
        "⚠️ Seleksiya natijalari kafolatlanmaydi.\n"
        "Ilmiy tasdiqlangan va hobbyist tajribalarini aralashtirmang."
    )
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(*back_home_row())

    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


# ── Locality Atlas ──────────────────────────────────────────────────
locality_router = Router(name="locality")


@locality_router.callback_query(F.data == "locality_atlas")
async def locality_atlas(callback: CallbackQuery):
    async with async_session() as session:
        from app.repositories.search_repo import LakeRepository
        lake_repo = LakeRepository(session)
        lakes = await lake_repo.get_all(limit=50)

    items = [(f"🏞️ {lake.name}", str(lake.id)) for lake in lakes]
    kb = build_list_keyboard(items, "lake", columns=1)

    await callback.message.edit_text(
        "🗺️ <b>LOCALITY ATLAS</b>\n\nKo'lni tanlang:",
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


@locality_router.callback_query(F.data.regexp(r"^lake:(\d+)$"))
async def lake_localities(callback: CallbackQuery):
    lake_id = int(callback.data.split(":")[1])
    async with async_session() as session:
        from app.repositories.search_repo import LocalityRepository
        loc_repo = LocalityRepository(session)
        localities = await loc_repo.get_by_lake(lake_id)

    items = [(f"📍 {loc.name}", str(loc.id)) for loc in localities]
    kb = build_list_keyboard(items, "locality_detail", columns=1)

    await callback.message.edit_text(
        "📍 <b>Localitylar</b>\n\nBatafsil ma'lumot va turlarni ko'rish uchun tanlang:",
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


@locality_router.callback_query(F.data.regexp(r"^locality_detail:(\d+)$"))
async def locality_detail_view(callback: CallbackQuery):
    loc_id = int(callback.data.split(":")[1])
    async with async_session() as session:
        from app.repositories.search_repo import LocalityRepository
        loc_repo = LocalityRepository(session)
        loc = await loc_repo.get_by_id(loc_id)
        if not loc:
            await callback.answer(uz.ERROR_NOT_FOUND, show_alert=True)
            return
        species_list = await loc_repo.get_species_for_locality(loc_id)

    lines = [f"🗺️ <b>LOCALITY ATLAS: {loc.name}</b>\n"]
    if loc.lake:
        lines.append(f"🏞️ <b>Ko'l/Havza:</b> {loc.lake.name}")
    if loc.country:
        flag = loc.country.emoji or "🌍"
        lines.append(f"{flag} <b>Davlat:</b> {loc.country.name}")
    if loc.habitat:
        lines.append(f"\n🪨 <b>Biotop tavsifi:</b>\n{loc.habitat}")
    if loc.description:
        lines.append(f"\n📝 <b>Batafsil ma'lumot:</b>\n{loc.description}")

    if loc.latitude is not None and loc.longitude is not None:
        gmaps = f"https://www.google.com/maps/search/?api=1&query={loc.latitude},{loc.longitude}"
        osm = f"https://www.openstreetmap.org/?mlat={loc.latitude}&mlon={loc.longitude}#map=12/{loc.latitude}/{loc.longitude}"
        lines.append(f"\n🧭 <b>GPS Koordinatalari:</b> <code>{loc.latitude}, {loc.longitude}</code>")
        lines.append(f"🗺️ <a href=\"{gmaps}\">Google Maps orqali ochish</a>")
        lines.append(f"🌍 <a href=\"{osm}\">OpenStreetMap orqali ochish</a>")

    if species_list:
        lines.append(f"\n🐟 <b>Ushbu biotopda yashovchi turlar ({len(species_list)}):</b>")
        for s in species_list:
            lines.append(f"• <i>{s.scientific_name}</i>")

    lines.append("\n📚 <i>Manbalar: FishBase.org, Malawi.si, Tanganyika.si, SeriouslyFish</i>")

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()

    for s in species_list:
        builder.row(InlineKeyboardButton(
            text=f"🐟 {s.scientific_name}",
            callback_data=f"profile:{s.id}:summary"
        ))

    if loc.lake_id:
        builder.row(InlineKeyboardButton(text="◀️ Ko'l localitylari", callback_data=f"lake:{loc.lake_id}"))
    builder.row(InlineKeyboardButton(text="🗺️ Locality Atlas", callback_data="locality_atlas"))
    builder.row(*back_home_row())

    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )
    await callback.answer()


# ── Identification (Disabled in favor of 100% verified text-only atlas) ──
identify_router = Router(name="identify")


@identify_router.callback_query(F.data == "identify")
async def identify_prompt(callback: CallbackQuery):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔎 Qidiruv bo'limiga o'tish", callback_data="search"))
    builder.row(*back_home_row())

    text = (
        "ℹ️ <b>AQUAMASTERUZBEKISTAN — QAT'IY MATNLI ILMIY ATLAS</b>\n\n"
        "Fotosuratlardan noaniq va noto'g'ri identifikatsiyani oldini olish maqsadida "
        "foto-identifikatsiya moduli o'chirildi.\n\n"
        "Barcha turlar, sinonimlar, savdo nomlari va gidrokimyoviy parametrlar "
        "<b>Qidiruv (Search)</b> moduli orqali ilmiy nomlar yoki kalit so'zlar bilan qidiriladi."
    )

    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )
    await callback.answer()


@identify_router.message(F.photo)
async def process_identification_photo(message: Message):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔎 Qidiruv bo'limiga o'tish", callback_data="search"))
    builder.row(*back_home_row())

    await message.answer(
        "ℹ️ <b>AquaMasterUzbekistan — qat'iy matnli ilmiy atlasdir.</b>\n\n"
        "Tizimda fotosuratlar orqali avtomatik tahlil funksiyasi o'chirilgan. "
        "Iltimos, baliqning ilmiy nomi yoki xalq nomini yozma ravishda yuboring.",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )


# ── Articles ────────────────────────────────────────────────────────
articles_router = Router(name="articles")


@articles_router.callback_query(F.data == "articles")
async def articles_menu(callback: CallbackQuery):
    async with async_session() as session:
        from app.services import ArticleService
        svc = ArticleService(session)
        categories = await svc.get_categories()

    items = [(f"{cat.emoji or '📚'} {cat.name}", str(cat.id)) for cat in categories]
    kb = build_list_keyboard(items, "art_cat", columns=1)

    await callback.message.edit_text(
        uz.ARTICLES_TITLE,
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


@articles_router.callback_query(F.data.regexp(r"^art_cat:(\d+)$"))
async def articles_by_category(callback: CallbackQuery):
    cat_id = int(callback.data.split(":")[1])
    async with async_session() as session:
        from app.services import ArticleService
        svc = ArticleService(session)
        articles = await svc.get_articles(cat_id)

    items = [(f"📄 {a.title}", str(a.id)) for a in articles]
    kb = build_list_keyboard(items, "article", columns=1)

    await callback.message.edit_text(
        "📚 <b>Maqolalar</b>",
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


@articles_router.callback_query(F.data.regexp(r"^article:(\d+)$"))
async def article_detail(callback: CallbackQuery):
    article_id = int(callback.data.split(":")[1])
    async with async_session() as session:
        from app.services import ArticleService
        svc = ArticleService(session)
        article = await svc.get_article(article_id)

    if not article:
        await callback.answer(uz.ERROR_NOT_FOUND, show_alert=True)
        return

    text = f"📄 <b>{article.title}</b>\n\n{article.content or article.summary or uz.DATA_INSUFFICIENT}"
    if article.sources:
        text += f"\n\n📚 Manbalar:\n{article.sources}"
    if article.author:
        text += f"\n\n✍️ {article.author}"

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(*back_home_row())

    # Truncate if too long for Telegram
    if len(text) > 4000:
        text = text[:3990] + "..."

    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


# ── Dictionary ──────────────────────────────────────────────────────
dictionary_router = Router(name="dictionary")


@dictionary_router.callback_query(F.data == "dictionary")
async def dictionary_menu(callback: CallbackQuery):
    async with async_session() as session:
        from app.repositories.search_repo import DictionaryRepository
        dict_repo = DictionaryRepository(session)
        terms = await dict_repo.get_all_sorted()

    from app.utils.pagination import Paginator
    paginator = Paginator(terms, page=1, per_page=10)
    items = [(f"📖 {t.term}", str(t.id)) for t in paginator.page_items]
    kb = build_list_keyboard(items, "dict_term", paginator.page, paginator.total_pages)

    await callback.message.edit_text(
        uz.DICTIONARY_TITLE,
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


@dictionary_router.callback_query(F.data.regexp(r"^dict_term:(\d+)$"))
async def dictionary_term_detail(callback: CallbackQuery):
    term_id = int(callback.data.split(":")[1])
    async with async_session() as session:
        from app.repositories.search_repo import DictionaryRepository
        dict_repo = DictionaryRepository(session)
        term = await dict_repo.get_by_id(term_id)

    if not term:
        await callback.answer(uz.ERROR_NOT_FOUND, show_alert=True)
        return

    text = f"📖 <b>{term.term}</b>\n\n{term.definition_uz}"
    if term.definition_en:
        text += f"\n\n🇬🇧 {term.definition_en}"

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(*back_home_row())

    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


# ── About ───────────────────────────────────────────────────────────
about_router = Router(name="about")


@about_router.callback_query(F.data == "about")
async def about_page(callback: CallbackQuery):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=uz.MENU_FAVORITES, callback_data="favorites"))
    builder.row(InlineKeyboardButton(text=uz.MENU_RECENT, callback_data="recent"))
    builder.row(*back_home_row())

    await callback.message.edit_text(
        uz.ABOUT_TEXT,
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )
    await callback.answer()


# ── Favorites ───────────────────────────────────────────────────────
favorites_router = Router(name="favorites")


@favorites_router.callback_query(F.data == "favorites")
async def favorites_list(callback: CallbackQuery):
    async with async_session() as session:
        user_repo = UserRepository(session)
        db_user = await user_repo.get_by_telegram_id(callback.from_user.id)
        if db_user:
            favs = await user_repo.get_favorites(db_user.id)
        else:
            favs = []

    items = [(f"⭐ {f.species.scientific_name}", f"{f.species_id}:summary") for f in favs if f.species]
    kb = build_list_keyboard(items, "profile", columns=1)

    await callback.message.edit_text(
        uz.MENU_FAVORITES,
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


@favorites_router.callback_query(F.data == "recent")
async def recent_list(callback: CallbackQuery):
    async with async_session() as session:
        user_repo = UserRepository(session)
        db_user = await user_repo.get_by_telegram_id(callback.from_user.id)
        if db_user:
            recent = await user_repo.get_recently_viewed(db_user.id)
        else:
            recent = []

    items = [(f"🕘 {r.species.scientific_name}", f"{r.species_id}:summary") for r in recent if r.species]
    kb = build_list_keyboard(items, "profile", columns=1)

    await callback.message.edit_text(
        uz.MENU_RECENT,
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


# ── Reports ─────────────────────────────────────────────────────────
reports_router = Router(name="reports")


class ReportState(StatesGroup):
    select_type = State()
    description = State()


@reports_router.callback_query(F.data.regexp(r"^report:(\d+)$"))
async def report_start(callback: CallbackQuery, state: FSMContext):
    species_id = int(callback.data.split(":")[1])
    await state.update_data(report_species_id=species_id)

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()

    for key, label in uz.REPORT_TYPES.items():
        builder.row(InlineKeyboardButton(text=label, callback_data=f"report_type:{key}"))
    builder.row(*back_home_row())

    await callback.message.edit_text(
        uz.REPORT_TITLE,
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )
    await state.set_state(ReportState.select_type)
    await callback.answer()


@reports_router.callback_query(ReportState.select_type, F.data.startswith("report_type:"))
async def report_select_type(callback: CallbackQuery, state: FSMContext):
    report_type = callback.data.split(":")[1]
    await state.update_data(report_type=report_type)
    await state.set_state(ReportState.description)
    await callback.message.edit_text(uz.REPORT_DESCRIPTION_PROMPT, parse_mode="HTML")
    await callback.answer()


@reports_router.message(ReportState.description)
async def report_submit(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    async with async_session() as session:
        user_repo = UserRepository(session)
        db_user = await user_repo.get_by_telegram_id(message.from_user.id)
        if db_user:
            from app.services import ReportService
            svc = ReportService(session)
            await svc.submit_report(
                user_id=db_user.id,
                species_id=data.get("report_species_id"),
                report_type=data.get("report_type", "other"),
                description=message.text.strip(),
            )

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(*back_home_row())

    await message.answer(uz.REPORT_SUBMITTED, reply_markup=builder.as_markup())
