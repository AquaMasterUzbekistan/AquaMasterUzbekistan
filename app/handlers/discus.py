"""Discus section handlers."""

from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.localization import uz
from app.keyboards import discus_menu_keyboard
from app.keyboards.navigation import build_list_keyboard

router = Router(name="discus")


@router.callback_query(F.data == "discus")
async def discus_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        uz.DISCUS_TITLE,
        reply_markup=discus_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("discus:"))
async def discus_subcategory(callback: CallbackQuery):
    parts = callback.data.split(":")
    sub = parts[1]
    page = int(parts[3]) if len(parts) >= 4 and parts[2] == "page" else 1

    titles = {
        "wild": "🌿 Wild Diskuslar (Yovvoyi Discus)",
        "selective": "🧬 Selective Breeding Diskuslar",
        "color": "🎨 Color Forms (Rang morfllari)",
    }
    title = titles.get(sub, "Diskuslar")

    sub_aliases = {
        "wild": ["Wild Discus", "Discus"],
        "selective": ["Selective Discus", "Discus"],
        "color": ["Color Form Discus", "Discus"],
    }
    aliases = sub_aliases.get(sub, [sub])

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
                page_prefix=f"discus:{sub}",
            )
            verified_count = sum(1 for s in species_list if s.author is not None)
            with_sources_count = sum(1 for s in species_list if len(s.sources) > 0)
            text = (
                f"<b>{title}</b>\n\n"
                f"📊 <b>Guruhdagi jami turlar:</b> {len(species_list)} ta\n"
                f"🟢 <b>Ilmiy tasdiqlangan profillar:</b> {verified_count} ta\n"
                f"📚 <b>Manbalar bilan bog'langan:</b> {with_sources_count} ta\n\n"
                f"📋 <i>Quyidagi ro'yxatdan turni tanlang (Sahifa {paginator.page}/{paginator.total_pages}):</i>"
            )
        else:
            kb = build_list_keyboard([], "profile", 1, 1)
            text = f"{title}\n\nUshbu bo'limda baliqlar topilmadi."

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()
