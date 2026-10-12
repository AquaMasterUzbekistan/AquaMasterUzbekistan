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


ABOUT_TEXT = (
    "ℹ️ <b>BOT HAQIDA MA'LUMOT</b>\n\n"
    "🐠 <b>AquaMasterUzbekistan Atlas</b> — akvarium baliqlari bo'yicha "
    "professional, ilmiy asoslangan va doimiy yangilanib boruvchi elektron ensiklopediya.\n\n"
    "👨‍💻 <b>Loyiha muallifi va ishlab chiquvchisi:</b> @shoazizoff\n"
    "Ushbu bot akvarium ixlosmandlari uchun <b>@shoazizoff</b> tomonidan ishlab chiqilgan.\n\n"
    "📩 <b>Talab va takliflar:</b>\n"
    "Agarda sizda biron-bir talab, taklif, yangi baliq turlarini qo'shish yoki "
    "savollar bo'lsa, to'g'ridan-to'g'ri <b>@shoazizoff</b> ga murojaat qilishingiz mumkin!\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "🌐 <b>BALIQLARGA OID RASMIY SAYTLAR VA TO'LIQ IP MANZILLARI:</b>\n\n"
    "1. 🇲🇼 <b>Malawi Cichlids Database</b>\n"
    "• Sayt: <a href=\"https://malawi.si\">malawi.si</a>\n"
    "• IP manzil: <code>193.243.141.75</code>\n"
    "• Yo'nalish: Malavi ko'li turlari, tabiiy biotoplari, variatsiyalari va GPS lokatsiyalari.\n\n"
    "2. 🇹🇿 <b>Tanganyika Cichlids Database</b>\n"
    "• Sayt: <a href=\"https://tanganyika.si\">tanganyika.si</a>\n"
    "• IP manzil: <code>193.243.141.75</code>\n"
    "• Yo'nalish: Tanganika ko'li sixlidlari taksonomiyasi va morfologik shakllari.\n\n"
    "3. 🌍 <b>FishBase (Dunyo baliqlari ensiklopediyasi)</b>\n"
    "• Sayt: <a href=\"https://www.fishbase.se\">fishbase.se</a> | <a href=\"https://www.fishbase.org\">fishbase.org</a>\n"
    "• IP manzil: <code>193.10.57.58</code> / <code>104.21.21.57</code>\n"
    "• Yo'nalish: 34,000+ dan ziyod baliqlar taksonomiyasi, biologiyasi va ko'rsatkichlari.\n\n"
    "4. 🔬 <b>Seriously Fish</b>\n"
    "• Sayt: <a href=\"https://www.seriouslyfish.com\">seriouslyfish.com</a>\n"
    "• IP manzil: <code>188.114.97.11</code>\n"
    "• Yo'nalish: Akvarium sharoitlari, harorat, pH, GH, parvarish va moslik tahlili.\n\n"
    "5. 🐱 <b>Planet Catfish</b>\n"
    "• Sayt: <a href=\"https://www.planetcatfish.com\">planetcatfish.com</a>\n"
    "• IP manzil: <code>172.67.70.147</code>\n"
    "• Yo'nalish: L-raqamlar (Loricariidae), Corydoras va dunyo laqqasimonlari.\n\n"
    "6. 📚 <b>Cichlid Room Companion (CRC)</b>\n"
    "• Sayt: <a href=\"https://www.cichlidae.com\">cichlidae.com</a>\n"
    "• IP manzil: <code>104.26.3.49</code>\n"
    "• Yo'nalish: Xalqaro sixlidologlar ilmiy maqolalari, fotosuratlari va biotoplari.\n\n"
    "7. 🐈 <b>ScotCat Catfish Reference</b>\n"
    "• Sayt: <a href=\"https://www.scotcat.com\">scotcat.com</a>\n"
    "• IP manzil: <code>208.113.159.23</code>\n"
    "• Yo'nalish: Zirhli va noan'anaviy chuchuk suv laqqalari ma'lumotnomasi.\n\n"
    "8. 🏛️ <b>Eschmeyer's Catalog of Fishes (CAS)</b>\n"
    "• Sayt: <a href=\"https://researcharchive.calacademy.org\">researcharchive.calacademy.org</a>\n"
    "• IP manzil: <code>192.40.158.77</code>\n"
    "• Yo'nalish: Kaliforniya Fanlar Akademiyasi ilmiy nomlar va sinonimlar reyestri."
)


def get_about_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="💬 @shoazizoff ga yozish", url="https://t.me/shoazizoff"),
        InlineKeyboardButton(text="✍️ Taklif qoldirish", callback_data="suggest:start"),
    )
    builder.row(
        InlineKeyboardButton(text="📊 Baza qamrovi", callback_data="database_coverage"),
        InlineKeyboardButton(text="⭐ Saqlanganlar", callback_data="favorites"),
    )
    builder.row(*back_home_row())
    return builder


@router.callback_query(F.data.in_(["about_suggest", "about", "about_info"]))
async def about_suggest_menu(callback: CallbackQuery, state: FSMContext | None = None):
    """Show the About & Suggestion panel."""
    if state:
        await state.clear()

    builder = get_about_keyboard()
    await callback.message.edit_text(ABOUT_TEXT, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@router.message(F.text == "/about")
async def cmd_about(message: Message, state: FSMContext | None = None):
    """Command /about handler."""
    if state:
        await state.clear()

    builder = get_about_keyboard()
    await message.answer(ABOUT_TEXT, reply_markup=builder.as_markup(), parse_mode="HTML")


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
