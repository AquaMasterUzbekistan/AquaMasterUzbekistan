"""Comparison handler."""

from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.localization import uz
from app.keyboards.navigation import back_home_row
from app.database.session import async_session
from app.services import CompareService

router = Router(name="compare")


class CompareState(StatesGroup):
    select_second = State()
    select_third = State()


@router.callback_query(F.data == "compare")
async def compare_start(callback: CallbackQuery):
    await callback.message.edit_text(
        uz.COMPARE_SELECT + "\n\n🔎 Baliq profilidan ⚖️ Taqqoslash tugmasini bosing.",
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.regexp(r"^compare:select:(\d+)$"))
async def compare_select_first(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CompareState.select_third.state:
        # Handled in compare_select_third
        return

    species_id = int(callback.data.split(":")[2])
    await state.update_data(first_species_id=species_id)
    await state.set_state(CompareState.select_second)
    await callback.message.edit_text(
        uz.COMPARE_SELECT_SECOND + "\n\n🔎 Ikkinchi baliq profilidan ⚖️ Taqqoslash tugmasini bosing.",
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(CompareState.select_second, F.data.regexp(r"^compare:select:(\d+)$"))
async def compare_select_second(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    first_id = data.get("first_species_id")
    second_id = int(callback.data.split(":")[2])

    if not first_id:
        await state.clear()
        await callback.answer(uz.ERROR_GENERIC, show_alert=True)
        return

    async with async_session() as session:
        compare_svc = CompareService(session)
        result_text = await compare_svc.compare(first_id, second_id)

    if result_text:
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        from aiogram.types import InlineKeyboardButton
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(
            text="➕ 3-turni qo'shish (3 ta turni solishtirish)",
            callback_data=f"compare:prompt_third:{first_id}:{second_id}",
        ))
        builder.row(*back_home_row())
        await callback.message.edit_text(
            result_text,
            reply_markup=builder.as_markup(),
            parse_mode="HTML",
        )
    else:
        await callback.answer(uz.ERROR_NOT_FOUND, show_alert=True)

    await state.clear()
    await callback.answer()


@router.callback_query(F.data.regexp(r"^compare:prompt_third:(\d+):(\d+)$"))
async def prompt_third(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    first_id = int(parts[2])
    second_id = int(parts[3])
    await state.update_data(first_species_id=first_id, second_species_id=second_id)
    await state.set_state(CompareState.select_third)
    await callback.message.edit_text(
        "⚖️ <b>Uchinchi turni tanlang:</b>\n\n🔎 Istalgan baliq profiliga o'ting va ⚖️ Taqqoslash tugmasini bosing.",
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(CompareState.select_third, F.data.regexp(r"^compare:select:(\d+)$"))
async def compare_select_third(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    first_id = data.get("first_species_id")
    second_id = data.get("second_species_id")
    third_id = int(callback.data.split(":")[2])
    await state.clear()

    if not first_id or not second_id:
        await callback.answer(uz.ERROR_GENERIC, show_alert=True)
        return

    async with async_session() as session:
        compare_svc = CompareService(session)
        result_text = await compare_svc.compare(first_id, second_id, third_id)

    if result_text:
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        builder = InlineKeyboardBuilder()
        builder.row(*back_home_row())
        await callback.message.edit_text(
            result_text,
            reply_markup=builder.as_markup(),
            parse_mode="HTML",
        )
    else:
        await callback.answer(uz.ERROR_NOT_FOUND, show_alert=True)

    await callback.answer()
