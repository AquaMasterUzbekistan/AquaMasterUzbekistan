"""Calculators handler — 7 aquarium calculators (Section 9)."""

from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.localization import uz
from app.keyboards import calculators_menu_keyboard
from app.keyboards.navigation import back_home_row
from app.services import CalculatorService

router = Router(name="calculators")


class CalcState(StatesGroup):
    volume_input = State()
    net_volume_input = State()
    water_change_input = State()
    filter_input = State()
    schedule_input = State()
    feeding_input = State()
    power_input = State()


def _back_to_calc_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🧮 Boshqa kalkulyator tanlash", callback_data="calculators"))
    builder.row(*back_home_row())
    return builder.as_markup()


@router.callback_query(F.data == "calculators")
async def calculators_menu(callback: CallbackQuery, state: FSMContext | None = None):
    """Display the 7 calculators menu."""
    if state:
        await state.clear()
    text = (
        "🧮 <b>AKVARIUM KALKULYATORLARI</b>\n\n"
        "<i>Akvarium hajmi, filtratsiya, suv yangilash, ozuqa va elektr xarajatlarini aniq hisoblang:</i>\n\n"
        "Kerakli kalkulyatorni tanlang:"
    )
    await callback.message.edit_text(
        text,
        reply_markup=calculators_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(F.text == "/calc")
async def cmd_calculators(message: Message, state: FSMContext | None = None):
    """Command /calc handler."""
    if state:
        await state.clear()
    text = (
        "🧮 <b>AKVARIUM KALKULYATORLARI</b>\n\n"
        "Kerakli kalkulyatorni tanlang:"
    )
    await message.answer(
        text,
        reply_markup=calculators_menu_keyboard(),
        parse_mode="HTML",
    )


# ── 1. Akvarium hajmi (L x W x H) ──────────────────────────────────
@router.callback_query(F.data == "calc:volume")
async def calc_volume_prompt(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📐 <b>1. Akvarium hajmi kalkulyatori</b>\n\n"
        "Uzunlik, kenglik va balandlikni santimetrda (sm) kiriting, bo'shliq bilan ajrating.\n"
        "Misol: <code>100 40 50</code>",
        reply_markup=_back_to_calc_kb(),
        parse_mode="HTML",
    )
    await state.set_state(CalcState.volume_input)
    await callback.answer()


@router.message(CalcState.volume_input)
async def calc_volume_result(message: Message, state: FSMContext):
    await state.clear()
    try:
        parts = message.text.strip().split()
        length, width, height = float(parts[0]), float(parts[1]), float(parts[2])
        volume = CalculatorService.volume(length, width, height)
        text = (
            f"📐 <b>Akvarium hajmi hisobi:</b>\n\n"
            f"📏 O'lchamlari: <b>{length} × {width} × {height} sm</b>\n"
            f"💧 Brutto hajmi: <b>{volume} litr</b>\n\n"
            "⚠️ <i>Eslatma: Bu shisha bo'yicha to'liq tashqi hajm. Grunt, toshlar va dekoratsiyalar "
            "haqiqiy suv hajmini 10–20% ga kamaytiradi.</i>"
        )
        await message.answer(text, reply_markup=_back_to_calc_kb(), parse_mode="HTML")
    except (ValueError, IndexError):
        await message.answer("❌ Noto'g'ri format. Misol kabi kiriting: <code>100 40 50</code>", reply_markup=_back_to_calc_kb(), parse_mode="HTML")


# ── 2. Haqiqiy suv hajmi (Netto) ────────────────────────────────────
@router.callback_query(F.data == "calc:net_volume")
async def calc_net_volume_prompt(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "💧 <b>2. Haqiqiy suv hajmi (Netto) kalkulyatori</b>\n\n"
        "Akvariumning umumiy litrini va xohlasangiz dekoratsiyalar egallagan foizini kiriting (standart: 15%).\n\n"
        "Misol 1 (faqat litr): <code>200</code>\n"
        "Misol 2 (litr va foiz): <code>200 20</code>",
        reply_markup=_back_to_calc_kb(),
        parse_mode="HTML",
    )
    await state.set_state(CalcState.net_volume_input)
    await callback.answer()


@router.message(CalcState.net_volume_input)
async def calc_net_volume_result(message: Message, state: FSMContext):
    await state.clear()
    try:
        parts = message.text.strip().split()
        gross = float(parts[0])
        disp = float(parts[1]) if len(parts) > 1 else 15.0
        res = CalculatorService.net_water_volume(gross, disp)
        text = (
            f"💧 <b>Haqiqiy suv hajmi (Netto):</b>\n\n"
            f"🏠 Brutto akvarium: <b>{res['gross_liters']} litr</b>\n"
            f"🪨 Dekor/grunt hajmi: <b>{res['displacement_percent']}% ({res['displaced_liters']} litr)</b>\n"
            f"🌊 <b>Haqiqiy erkin suv: {res['net_liters']} litr</b>\n\n"
            "💡 <i>Dori qo'shish, konditsioner yoki o'g'it hisoblashda aynan shu netto hajmdan foydalaning!</i>"
        )
        await message.answer(text, reply_markup=_back_to_calc_kb(), parse_mode="HTML")
    except (ValueError, IndexError):
        await message.answer("❌ Noto'g'ri format. Misol kabi kiriting: <code>200</code> yoki <code>200 15</code>", reply_markup=_back_to_calc_kb(), parse_mode="HTML")


# ── 3. Suv almashtirish hajmi (%) ──────────────────────────────────
@router.callback_query(F.data == "calc:water_change")
async def calc_water_change_prompt(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🪣 <b>3. Suv almashtirish hajmi kalkulyatori</b>\n\n"
        "Akvarium hajmi (litr) va almashtiriladigan foizni kiriting.\n"
        "Misol: <code>200 30</code> (200 litrdan 30%)",
        reply_markup=_back_to_calc_kb(),
        parse_mode="HTML",
    )
    await state.set_state(CalcState.water_change_input)
    await callback.answer()


@router.message(CalcState.water_change_input)
async def calc_water_change_result(message: Message, state: FSMContext):
    await state.clear()
    try:
        parts = message.text.strip().split()
        liters, percent = float(parts[0]), float(parts[1])
        change = CalculatorService.water_change(liters, percent)
        text = (
            f"🪣 <b>Suv almashtirish hisobi:</b>\n\n"
            f"🏠 Akvarium: <b>{liters} litr</b>\n"
            f"📊 Almashtirish foizi: <b>{percent}%</b>\n"
            f"💧 <b>Almashtiriladigan suv: {change} litr</b>\n\n"
            "⚠️ <i>Quyiladigan yangi suv xlorlanmagan va harorati akvarium suviga teng bo'lishi lozim.</i>"
        )
        await message.answer(text, reply_markup=_back_to_calc_kb(), parse_mode="HTML")
    except (ValueError, IndexError):
        await message.answer("❌ Noto'g'ri format. Misol kabi kiriting: <code>200 30</code>", reply_markup=_back_to_calc_kb(), parse_mode="HTML")


# ── 4. Filtr aylanishi (Turnover rate) ──────────────────────────────
@router.callback_query(F.data == "calc:filter")
async def calc_filter_prompt(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🌀 <b>4. Filtr nominal oqimi va suv aylanishi (Turnover)</b>\n\n"
        "Filtr nasosi unumdorligi (litr/soat) va akvarium hajmini (litr) kiriting.\n"
        "Misol: <code>1000 200</code> (1000 L/h filtr, 200 L akvarium)",
        reply_markup=_back_to_calc_kb(),
        parse_mode="HTML",
    )
    await state.set_state(CalcState.filter_input)
    await callback.answer()


@router.message(CalcState.filter_input)
async def calc_filter_result(message: Message, state: FSMContext):
    await state.clear()
    try:
        parts = message.text.strip().split()
        pump, tank = float(parts[0]), float(parts[1])
        res = CalculatorService.filter_turnover(pump, tank)
        text = (
            f"🌀 <b>Filtratsiya aylanish hisobi:</b>\n\n"
            f"⚙️ Nasos unumdorligi: <b>{pump} L/soat</b>\n"
            f"🏠 Akvarium hajmi: <b>{tank} L</b>\n"
            f"🔄 <b>Soatiga aylanish: {res['turnover']} marta (x)</b>\n"
            f"📋 Holati: <b>{res['status']}</b>\n\n"
            f"💡 <i>Tavsiya: {res['advice']}</i>"
        )
        await message.answer(text, reply_markup=_back_to_calc_kb(), parse_mode="HTML")
    except (ValueError, IndexError):
        await message.answer("❌ Noto'g'ri format. Misol kabi kiriting: <code>1000 200</code>", reply_markup=_back_to_calc_kb(), parse_mode="HTML")


# ── 5. Suv almashtirish jadvali ────────────────────────────────────
@router.callback_query(F.data == "calc:schedule")
async def calc_schedule_prompt(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📅 <b>5. Suv almashtirish jadvali va miqdori</b>\n\n"
        "Akvarium hajmini (litr) kiriting.\n"
        "Misol: <code>250</code>",
        reply_markup=_back_to_calc_kb(),
        parse_mode="HTML",
    )
    await state.set_state(CalcState.schedule_input)
    await callback.answer()


@router.message(CalcState.schedule_input)
async def calc_schedule_result(message: Message, state: FSMContext):
    await state.clear()
    try:
        tank_l = float(message.text.strip().split()[0])
        med = CalculatorService.water_change_schedule(tank_l, "medium")
        high = CalculatorService.water_change_schedule(tank_l, "high")
        text = (
            f"📅 <b>Suv almashtirish grafigi ({tank_l} L akvarium uchun):</b>\n\n"
            f"🟢 <b>Standart jamoat akvariumi:</b>\n"
            f"• Har 7 kunda: <b>{med['percent']}% ({med['liters_to_change']} litr)</b>\n"
            f"• <i>{med['note']}</i>\n\n"
            f"🔴 <b>Cichlidlar / Katta baliqlar / Zich akvarium:</b>\n"
            f"• Har 7 kunda: <b>{high['percent']}% ({high['liters_to_change']} litr)</b>\n"
            f"• <i>{high['note']}</i>\n\n"
            "💡 <i>Filtr gubkalarini faqat almashtirilayotgan eski akvarium suvida yuvishni unutmang!</i>"
        )
        await message.answer(text, reply_markup=_back_to_calc_kb(), parse_mode="HTML")
    except (ValueError, IndexError):
        await message.answer("❌ Noto'g'ri format. Misol kabi son kiriting: <code>250</code>", reply_markup=_back_to_calc_kb(), parse_mode="HTML")


# ── 6. Ozuqa miqdori tavsiyasi ─────────────────────────────────────
@router.callback_query(F.data == "calc:feeding")
async def calc_feeding_prompt(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🍽️ <b>6. Ozuqa miqdori bo‘yicha yordamchi tavsiyalar</b>\n\n"
        "Baliqlar soni va ularning o'rtacha o'lchamini (sm) kiriting.\n"
        "Misol: <code>15 8</code> (15 ta baliq, o'rtacha 8 sm)",
        reply_markup=_back_to_calc_kb(),
        parse_mode="HTML",
    )
    await state.set_state(CalcState.feeding_input)
    await callback.answer()


@router.message(CalcState.feeding_input)
async def calc_feeding_result(message: Message, state: FSMContext):
    await state.clear()
    try:
        parts = message.text.strip().split()
        count = int(parts[0])
        size = float(parts[1]) if len(parts) > 1 else 6.0
        res = CalculatorService.feeding_advice(count, size)
        text = (
            f"🍽️ <b>Oziqlantirish hisobi ({count} ta baliq, ~{size} sm):</b>\n\n"
            f"{res['advice']}\n\n"
            "⚠️ <i>Kalkulyator biologik mutlaq kafolat emas: baliq turi (o'txo'r yoki yirtqich) "
            "va faolligiga qarab ratsion o'zgaradi.</i>"
        )
        await message.answer(text, reply_markup=_back_to_calc_kb(), parse_mode="HTML")
    except (ValueError, IndexError):
        await message.answer("❌ Noto'g'ri format. Misol kabi kiriting: <code>15 8</code>", reply_markup=_back_to_calc_kb(), parse_mode="HTML")


# ── 7. Elektr energiyasi sarfi ─────────────────────────────────────
@router.callback_query(F.data == "calc:power")
async def calc_power_prompt(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "⚡ <b>7. Elektr energiyasi sarfi kalkulyatori</b>\n\n"
        "Jihozlar quvvatini Vattda (W) kiriting: Filtr_Vt Isitgich_Vt Chiroq_Vt\n"
        "Misol: <code>15 100 20</code> (15W filtr, 100W isitgich, 20W yorug'lik)",
        reply_markup=_back_to_calc_kb(),
        parse_mode="HTML",
    )
    await state.set_state(CalcState.power_input)
    await callback.answer()


@router.message(CalcState.power_input)
async def calc_power_result(message: Message, state: FSMContext):
    await state.clear()
    try:
        parts = message.text.strip().split()
        f_w = float(parts[0])
        h_w = float(parts[1]) if len(parts) > 1 else 100.0
        l_w = float(parts[2]) if len(parts) > 2 else 20.0

        res = CalculatorService.electricity_consumption(
            filter_watts=f_w,
            heater_watts=h_w,
            light_watts=l_w,
        )
        text = (
            f"⚡ <b>Elektr energiyasi sarfi hisobi:</b>\n\n"
            f"⚙️ Filtr ({f_w} W, 24 soat): <b>{res['breakdown']['filter']} kVt·soat/oy</b>\n"
            f"🌡️ Isitgich ({h_w} W, o'rtacha 8 soat): <b>{res['breakdown']['heater']} kVt·soat/oy</b>\n"
            f"💡 Chiroq ({l_w} W, 8 soat): <b>{res['breakdown']['light']} kVt·soat/oy</b>\n\n"
            f"🔋 <b>Jami oylik sarf: {res['total_monthly_kwh']} kVt·soat</b>\n"
            f"💰 <b>Taxminiy oylik xarajat: ~{res['monthly_cost_som']:,} so'm</b> (450 so'm/kVt tarifida)\n\n"
            "💡 <i>Qishda xona sovuq bo'lsa isitgich ko'proq ishlashi mumkin.</i>"
        )
        await message.answer(text, reply_markup=_back_to_calc_kb(), parse_mode="HTML")
    except (ValueError, IndexError):
        await message.answer("❌ Noto'g'ri format. Misol kabi kiriting: <code>15 100 20</code>", reply_markup=_back_to_calc_kb(), parse_mode="HTML")
