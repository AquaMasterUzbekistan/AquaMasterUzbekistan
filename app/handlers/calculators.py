"""Calculators handler."""

from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.localization import uz
from app.keyboards import calculators_menu_keyboard
from app.keyboards.navigation import back_home_row
from app.services import CalculatorService

router = Router(name="calculators")


class CalcState(StatesGroup):
    volume_input = State()
    water_change_input = State()
    heater_input = State()
    filter_input = State()
    stocking_input = State()


@router.callback_query(F.data == "calculators")
async def calculators_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        uz.CALC_TITLE,
        reply_markup=calculators_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "calc:volume")
async def calc_volume_prompt(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📐 <b>Akvarium hajmi kalkulyatori</b>\n\n"
        "Uzunlik, kenglik va balandlikni santimetrda kiriting, bo'shliq bilan ajrating.\n"
        "Misol: <code>100 40 50</code>",
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
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        from aiogram.types import InlineKeyboardButton
        builder = InlineKeyboardBuilder()
        builder.row(*back_home_row())
        await message.answer(
            f"📐 <b>Akvarium hajmi</b>\n\n"
            f"📏 {length} × {width} × {height} sm\n"
            f"💧 <b>{volume} litr</b>\n\n"
            f"⚠️ Bu hisob taxminiy — filtr, substrat va dekorlar hajmni kamaytiradi.",
            reply_markup=builder.as_markup(),
            parse_mode="HTML",
        )
    except (ValueError, IndexError):
        await message.answer(uz.ERROR_INVALID_INPUT)


@router.callback_query(F.data == "calc:water_change")
async def calc_water_change_prompt(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "💧 <b>Suv almashtirish kalkulyatori</b>\n\n"
        "Akvarium hajmi (litr) va foizni kiriting.\n"
        "Misol: <code>250 30</code>",
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
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        from aiogram.types import InlineKeyboardButton
        builder = InlineKeyboardBuilder()
        builder.row(*back_home_row())
        await message.answer(
            f"💧 <b>Suv almashtirish</b>\n\n"
            f"🏠 Akvarium: {liters} L\n"
            f"📊 Foiz: {percent}%\n"
            f"💧 <b>Almashtirish: {change} L</b>",
            reply_markup=builder.as_markup(),
            parse_mode="HTML",
        )
    except (ValueError, IndexError):
        await message.answer(uz.ERROR_INVALID_INPUT)


@router.callback_query(F.data == "calc:heater")
async def calc_heater_prompt(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🌡️ <b>Isitgich quvvati</b>\n\nAkvarium hajmini litrda kiriting.\nMisol: <code>200</code>",
        parse_mode="HTML",
    )
    await state.set_state(CalcState.heater_input)
    await callback.answer()


@router.message(CalcState.heater_input)
async def calc_heater_result(message: Message, state: FSMContext):
    await state.clear()
    try:
        liters = float(message.text.strip())
        watts = CalculatorService.heater_wattage(liters)
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        from aiogram.types import InlineKeyboardButton
        builder = InlineKeyboardBuilder()
        builder.row(*back_home_row())
        await message.answer(
            f"🌡️ <b>Isitgich quvvati</b>\n\n"
            f"🏠 Akvarium: {liters} L\n"
            f"⚡ <b>Tavsiya: {watts}</b>\n\n"
            f"⚠️ Xona haroratiga qarab farq qilishi mumkin.",
            reply_markup=builder.as_markup(),
            parse_mode="HTML",
        )
    except ValueError:
        await message.answer(uz.ERROR_INVALID_INPUT)


@router.callback_query(F.data == "calc:filter")
async def calc_filter_prompt(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🔄 <b>Filtr sig'imi</b>\n\nAkvarium hajmini litrda kiriting.\nMisol: <code>300</code>",
        parse_mode="HTML",
    )
    await state.set_state(CalcState.filter_input)
    await callback.answer()


@router.message(CalcState.filter_input)
async def calc_filter_result(message: Message, state: FSMContext):
    await state.clear()
    try:
        liters = float(message.text.strip())
        flow = CalculatorService.filter_flow(liters)
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        from aiogram.types import InlineKeyboardButton
        builder = InlineKeyboardBuilder()
        builder.row(*back_home_row())
        await message.answer(
            f"🔄 <b>Filtr sig'imi</b>\n\n"
            f"🏠 Akvarium: {liters} L\n"
            f"💧 <b>Tavsiya: {flow} L/soat</b> (4x aylanish)\n\n"
            f"⚠️ Cichlidlar uchun 6-10x tavsiya etiladi.",
            reply_markup=builder.as_markup(),
            parse_mode="HTML",
        )
    except ValueError:
        await message.answer(uz.ERROR_INVALID_INPUT)


@router.callback_query(F.data == "calc:stocking")
async def calc_stocking_prompt(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🐟 <b>Baliq sig'imi</b>\n\n"
        "Akvarium hajmi (litr) va o'rtacha baliq o'lchami (sm) kiriting.\n"
        "Misol: <code>250 8</code>",
        parse_mode="HTML",
    )
    await state.set_state(CalcState.stocking_input)
    await callback.answer()


@router.message(CalcState.stocking_input)
async def calc_stocking_result(message: Message, state: FSMContext):
    await state.clear()
    try:
        parts = message.text.strip().split()
        liters, size = float(parts[0]), float(parts[1])
        count = CalculatorService.stocking_estimate(liters, size)
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        from aiogram.types import InlineKeyboardButton
        builder = InlineKeyboardBuilder()
        builder.row(*back_home_row())
        await message.answer(
            f"🐟 <b>Baliq sig'imi (taxminiy)</b>\n\n"
            f"🏠 Akvarium: {liters} L\n"
            f"📏 O'rtacha o'lcham: {size} sm\n"
            f"🐟 <b>Taxminiy sig'im: {count} ta baliq</b>\n\n"
            f"⚠️ Bu faqat taxminiy hisob. Turga, agressivlikka va filtratsiyaga qarab farq qiladi.",
            reply_markup=builder.as_markup(),
            parse_mode="HTML",
        )
    except (ValueError, IndexError):
        await message.answer(uz.ERROR_INVALID_INPUT)


# Remaining calculators: air pump, salt, feeding — same pattern
@router.callback_query(F.data == "calc:air_pump")
async def calc_air_pump(callback: CallbackQuery):
    await callback.message.edit_text(
        "💨 <b>Havo kompressori</b>\n\n"
        "Umumiy qoida: akvarium hajmiga teng L/soat.\n"
        "200 L akvarium → 200 L/soat kompressor.\n\n"
        "⚠️ Baliq turiga qarab ko'proq yoki kamroq bo'lishi mumkin.",
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "calc:salt")
async def calc_salt(callback: CallbackQuery):
    await callback.message.edit_text(
        "🧂 <b>Tuz/mineral hisoblash</b>\n\n"
        "Umumiy qoida: 1 g/L tuz konsentratsiyasi uchun\n"
        "Hajm (L) × kerakli g/L = umumiy gramm\n\n"
        "Misol: 200 L × 1 g/L = 200 g tuz\n\n"
        "⚠️ Baliq turiga qarab ehtiyot bo'ling!",
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "calc:feeding")
async def calc_feeding(callback: CallbackQuery):
    await callback.message.edit_text(
        "🍽️ <b>Ozuqa miqdori</b>\n\n"
        "Umumiy qoida: baliq tana og'irligining 2-3%\n"
        "Kuniga 2-3 marta, 2-3 daqiqada yeyiladigan miqdor.\n\n"
        "⚠️ Ortiqcha ovqatlantirish suv sifatini yomonlashtiradi.",
        parse_mode="HTML",
    )
    await callback.answer()
