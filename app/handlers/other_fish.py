"""Other freshwater fish handlers."""

from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.localization import uz
from app.keyboards import other_fish_menu_keyboard
from app.keyboards.navigation import build_list_keyboard

router = Router(name="other_fish")


@router.callback_query(F.data == "other_fish")
async def other_fish_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        uz.OTHER_TITLE,
        reply_markup=other_fish_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("other:"))
async def other_fish_subcategory(callback: CallbackQuery):
    parts = callback.data.split(":")
    sub_key = parts[1]
    page = int(parts[3]) if len(parts) >= 4 and parts[2] == "page" else 1

    subcategory_aliases = {
        "tetras": ["Tetralar", "Tetras"],
        "barbs": ["Barbusslar", "Barbs"],
        "rasbora": ["Rasboralar", "Rasbora & Danio"],
        "gourami": ["Guramis", "Gourami"],
        "betta": ["Bettalar", "Betta"],
        "livebearers": ["Livebearers"],
        "catfish": ["Catfish"],
        "plecos": ["Plecos"],
        "loaches": ["Loaches"],
        "rainbow": ["Rainbowfish"],
        "killifish": ["Killifish"],
        "knife": ["Knife Fish"],
        "arowana": ["Arowana"],
        "bichirs": ["Bichirs"],
        "shrimp": ["Krevetkalar", "Shrimp & Snails"],
        "snails": ["Mollyuskalar", "Shrimp & Snails"],
        "other": ["Boshqa turlar"],
    }
    aliases = subcategory_aliases.get(sub_key, [sub_key])
    display_title = aliases[0]

    from app.database.session import async_session
    from sqlalchemy import select
    from app.models.taxonomy import Subcategory
    from app.models.species import Species, species_categories
    from app.utils.pagination import Paginator

    async with async_session() as session:
        sub_stmt = select(Subcategory.id).where(Subcategory.name.in_(aliases))
        sub_ids = (await session.execute(sub_stmt)).scalars().all()

        if sub_ids:
            sp_stmt = (
                select(Species)
                .join(species_categories, species_categories.c.species_id == Species.id)
                .where(species_categories.c.subcategory_id.in_(sub_ids))
                .where(Species.is_published == True)
                .distinct()
                .order_by(Species.scientific_name)
            )
            species_list = (await session.execute(sp_stmt)).scalars().all()
            items = [(f"🐟 {sp.scientific_name}", f"{sp.id}:summary") for sp in species_list]
            paginator = Paginator(items, page=page, per_page=8)
            kb = build_list_keyboard(
                paginator.page_items, "profile",
                paginator.page, paginator.total_pages,
                page_prefix=f"other:{sub_key}",
            )
            verified_count = sum(1 for s in species_list if s.author is not None)
            with_sources_count = sum(1 for s in species_list if len(s.sources) > 0)
            text = (
                f"🐟 <b>{display_title}</b>\n\n"
                f"📊 <b>Guruhdagi jami turlar:</b> {len(species_list)} ta\n"
                f"🟢 <b>Ilmiy tasdiqlangan profillar:</b> {verified_count} ta\n"
                f"📚 <b>Manbalar bilan bog'langan:</b> {with_sources_count} ta\n\n"
                f"📋 <i>Quyidagi ro'yxatdan turni tanlang (Sahifa {paginator.page}/{paginator.total_pages}):</i>"
            )
        else:
            kb = build_list_keyboard([], "profile", 1, 1)
            text = f"🐟 {display_title}\n\nUshbu bo'limda baliqlar topilmadi."

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()
