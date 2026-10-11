"""About and User Suggestion Handler (Master Prompt Section 4 & Section 5.3 & Section 11)."""

from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.localization import uz
from app.database.session import async_session
from app.repositories import UserRepository
from app.models.report import Report, ReportType, ReportStatus
from app.keyboards.navigation import back_home_row

router = Router(name="about_suggest")


class SuggestionState(StatesGroup):
    waiting_text = State()


@router.callback_query(F.data.in_(["about_suggest", "about"]))
async def about_suggest_menu(callback: CallbackQuery, state: FSMContext | None = None):
    """Show the About & Suggestion panel."""
    if state:
        await state.clear()

    text = (
        "ℹ️ <b>BOT HAQIDA VA TAKLIF YUBORISH</b>\n\n"
        "🐠 <b>AquaMasterUzbekistan Atlas</b> — akvarium baliqlari bo'yicha "
        "professional, ilmiy asoslangan va doimiy rivojlanuvchi elektron ma'lumotnoma tizimidir.\n\n"
        "🎯 <b>Asosiy maqsad:</b>\n"
        "Akvarium ixlosmandlariga har bir turning to'g'ri fotosurati, aniq ilmiy tasnifi, "
        "tabiiy biotopi, suv parametrlari va to'g'ri parvarish bo'yicha ishonchli bilimlarni taqdim etish.\n\n"
        "📚 <b>Ilmiy manbalar:</b>\n"
        "• <b>FishBase.org</b> — baliqlar biologiyasi va taksonomiyasi\n"
        "• <b>Eschmeyer's Catalog of Fishes</b> — ilmiy nomlar va sinonimlar\n"
        "• <b>Malawi.si & Tanganyika.si</b> — Afrika ko'l cichlidlari va biotoplari\n"
        "• <b>SeriouslyFish.com</b> — akvarium sharoiti va gidrokimyoviy parvarish\n"
        "• <b>DATZ / PlanetCatfish</b> — L-raqamlar va zirhli laqqalar\n\n"
        "🏷️ <b>Muallif va ishlab chiquvchi:</b> @shoazizoff\n"
        "📦 <b>Versiya:</b> 2.0 (Master Edition)\n\n"
        "Fikrlaringiz, yangi turlar yoki tuzatishlar bo'yicha takliflaringizni mamnuniyat bilan qabul qilamiz!"
    )

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✍️ Yangi tur yoki tuzatish taklif qilish", callback_data="suggest:start"))
    builder.row(
        InlineKeyboardButton(text="📊 Baza qamrovi", callback_data="database_coverage"),
        InlineKeyboardButton(text="ℹ️ Manbalar tafsiloti", callback_data="sources_info"),
    )
    builder.row(
        InlineKeyboardButton(text="⭐ Saqlanganlar", callback_data="favorites"),
        InlineKeyboardButton(text="🕘 So'nggi ko'rilganlar", callback_data="recent"),
    )
    builder.row(*back_home_row())

    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@router.message(F.text == "/about")
async def cmd_about(message: Message, state: FSMContext | None = None):
    """Command /about handler."""
    if state:
        await state.clear()

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✍️ Taklif yoki yangi tur yuborish", callback_data="suggest:start"))
    builder.row(*back_home_row())

    text = (
        "ℹ️ <b>AquaMasterUzbekistan Atlas</b>\n\n"
        "Akvarium ixlosmandlari uchun zamonaviy elektron ensiklopediya.\n"
        "Muallif: @shoazizoff\n\n"
        "Taklif qoldirish uchun quyidagi tugmani bosing:"
    )
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.callback_query(F.data == "suggest:start")
async def suggest_start(callback: CallbackQuery, state: FSMContext):
    """Start interactive suggestion submission."""
    await state.set_state(SuggestionState.waiting_text)
    await state.update_data(fish_hint=None)

    text = (
        "✍️ <b>TAKLIF YOKI YANGI TUR YUBORISH</b>\n\n"
        "Iltimos, taklif qilmoqchi bo'lgan baliq nomi, qo'shilishi kerak bo'lgan ma'lumot "
        "yoki aniqlangan noaniqlik haqida yozing.\n\n"
        "<i>Agar mavjud bo'lsa, ma'lumot manbasi (masalan, havola yoki maqola)ni ham ko'rsatishingiz mumkin.</i>"
    )
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ Bekor qilish", callback_data="about_suggest"))
    builder.row(*back_home_row())

    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("suggest:fish:"))
async def suggest_specific_fish(callback: CallbackQuery, state: FSMContext):
    """Start suggestion pre-filled with query not found."""
    fish_name = callback.data.split(":", 2)[2]
    await state.set_state(SuggestionState.waiting_text)
    await state.update_data(fish_hint=fish_name)

    text = (
        f"✍️ <b>\"{fish_name}\" BO'YICHA TAKLIF YUBORISH</b>\n\n"
        "Ushbu tur haqida bilgan ma'lumotlaringizni (ilmiy nomi, xalq nomi, rasmi yoki havolasi) yozing:\n\n"
        "<i>Administratorlar uni tekshirib, ma'lumotlar bazasiga kiritadilar.</i>"
    )
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ Bekor qilish", callback_data="search"))
    builder.row(*back_home_row())

    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@router.message(SuggestionState.waiting_text, F.text, ~F.text.startswith("/"))
async def suggest_process_text(message: Message, state: FSMContext):
    """Save submitted suggestion into reports table."""
    data = await state.get_data()
    fish_hint = data.get("fish_hint")
    await state.clear()

    user_text = message.text.strip()
    full_desc = f"[Nom: {fish_hint}] {user_text}" if fish_hint else user_text
    user_id = message.from_user.id if message.from_user else 0

    async with async_session() as session:
        user_repo = UserRepository(session)
        db_user = await user_repo.get_by_telegram_id(user_id)
        if db_user:
            await user_repo.log_activity(user_id, "suggestion", full_desc[:100])
            report = Report(
                user_id=db_user.id,
                species_id=None,
                report_type=ReportType.OTHER,
                description=full_desc,
                status=ReportStatus.PENDING,
            )
            session.add(report)
            await session.commit()

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔎 Yangi baliq qidirish", callback_data="search"))
    builder.row(*back_home_row())

    response_text = (
        "✅ <b>Taklifingiz qabul qilindi!</b>\n\n"
        "Kiritilgan ma'lumotlar administratorlarimiz tomonidan rasmiy manbalar "
        "(FishBase, SeriouslyFish, Malawi.si) orqali tekshiriladi va tasdiqlansa bazaga qo'shiladi.\n\n"
        "Atlasimizni rivojlantirishga qo'shgan hissangiz uchun tashakkur!"
    )
    await message.answer(response_text, reply_markup=builder.as_markup(), parse_mode="HTML")
