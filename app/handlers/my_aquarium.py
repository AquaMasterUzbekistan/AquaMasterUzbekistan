"""My aquarium handler."""

from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.localization import uz
from app.keyboards.navigation import back_home_row, build_list_keyboard
from app.database.session import async_session
from app.services import AquariumService
from app.repositories import UserRepository

router = Router(name="my_aquarium")


class AquariumState(StatesGroup):
    name_input = State()
    volume_input = State()


@router.callback_query(F.data == "my_aquarium")
async def my_aquarium_menu(callback: CallbackQuery):
    async with async_session() as session:
        user_repo = UserRepository(session)
        db_user = await user_repo.get_by_telegram_id(callback.from_user.id)
        if not db_user:
            await callback.answer(uz.ERROR_GENERIC, show_alert=True)
            return

        aq_svc = AquariumService(session)
        aquariums = await aq_svc.get_user_aquariums(db_user.id)

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()

    if aquariums:
        for aq in aquariums:
            label = f"🏠 {aq.name}"
            if aq.volume_liters:
                label += f" ({aq.volume_liters} L)"
            builder.row(InlineKeyboardButton(text=label, callback_data=f"aq:{aq.id}"))
    else:
        pass  # Will show empty message

    builder.row(InlineKeyboardButton(text=uz.MY_AQUARIUM_ADD, callback_data="aq:add"))
    builder.row(*back_home_row())

    text = uz.MY_AQUARIUM_TITLE
    if not aquariums:
        text += f"\n\n{uz.MY_AQUARIUM_EMPTY}"

    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "aq:add")
async def add_aquarium_prompt(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(uz.MY_AQUARIUM_NAME_PROMPT, parse_mode="HTML")
    await state.set_state(AquariumState.name_input)
    await callback.answer()


@router.message(AquariumState.name_input)
async def add_aquarium_name(message: Message, state: FSMContext):
    await state.update_data(aq_name=message.text.strip())
    await state.set_state(AquariumState.volume_input)
    await message.answer(uz.MY_AQUARIUM_VOLUME_PROMPT)


@router.message(AquariumState.volume_input)
async def add_aquarium_volume(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    try:
        volume = float(message.text.strip())
    except ValueError:
        volume = None

    async with async_session() as session:
        user_repo = UserRepository(session)
        db_user = await user_repo.get_by_telegram_id(message.from_user.id)
        if db_user:
            aq_svc = AquariumService(session)
            await aq_svc.create_aquarium(db_user.id, data.get("aq_name", "Akvarium"), volume)

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(*back_home_row())
    await message.answer(uz.MY_AQUARIUM_CREATED, reply_markup=builder.as_markup())


@router.callback_query(F.data.regexp(r"^aq:(\d+)$"))
async def view_aquarium(callback: CallbackQuery):
    aq_id = int(callback.data.split(":")[1])
    async with async_session() as session:
        aq_svc = AquariumService(session)
        fish = await aq_svc.get_aquarium_fish(aq_id)

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()

    if fish:
        for f in fish:
            name = f.species.scientific_name if f.species else (f.custom_name or "?")
            counts = f"♂{f.quantity_male} ♀{f.quantity_female} ?{f.quantity_unknown}"
            builder.row(InlineKeyboardButton(
                text=f"🐟 {name} — {counts}", callback_data=f"noop"
            ))

    builder.row(InlineKeyboardButton(text=uz.MY_FISH_ADD, callback_data=f"aq_fish:{aq_id}:add"))
    builder.row(*back_home_row())

    await callback.message.edit_text(
        f"🏠 <b>Akvarium</b>\n\n🐟 Baliqlar soni: {len(fish)}",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )
    await callback.answer()
