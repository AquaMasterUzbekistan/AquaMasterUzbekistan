"""African cichlids browsing handlers."""

from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.localization import uz
from app.keyboards import (
    african_menu_keyboard, malawi_menu_keyboard,
    tanganyika_menu_keyboard,
)
from app.keyboards.navigation import build_list_keyboard
from app.database.session import async_session
from app.services import FishService
from app.utils.pagination import Paginator

router = Router(name="african_cichlids")

# ── Subcategory mapping to DB subcategory names ─────────────────
MALAWI_MAP = {
    "mbuna": "Mbuna",
    "haps": "Haps",
    "peacock": "Aulonocara",
    "utaka": "Utaka",
    "other": "Other Malawi",
}

TANGANYIKA_MAP = {
    "shell": "Shell Dwellers",
    "julido": "Julidochromis",
    "neolamp": "Neolamprologus",
    "alto": "Altolamprologus",
    "frontosa": "Cyphotilapia",
    "tropheus": "Tropheus",
    "xeno": "Xenotilapia",
    "calvus": "Calvus",
    "other": "Other Tanganyika",
}


@router.callback_query(F.data == "african")
async def african_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        uz.AFRICAN_TITLE,
        reply_markup=african_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "african:malawi")
async def malawi_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        uz.MALAWI_TITLE,
        reply_markup=malawi_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "african:tanganyika")
async def tanganyika_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        uz.TANGANYIKA_TITLE,
        reply_markup=tanganyika_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "african:victoria")
async def victoria_menu(callback: CallbackQuery):
    async with async_session() as session:
        from sqlalchemy import select
        from app.models.taxonomy import Subcategory
        stmt = select(Subcategory).where(Subcategory.name == "Victoria")
        result = await session.execute(stmt)
        subcat = result.scalar_one_or_none()

        if subcat:
            fish_svc = FishService(session)
            species_list = await fish_svc.get_species_by_subcategory(subcat.id)
            items = [(f"🐟 {sp.scientific_name}", f"{sp.id}:summary") for sp in species_list]
            paginator = Paginator(items, page=1, per_page=8)
            kb = build_list_keyboard(
                paginator.page_items, "profile",
                paginator.page, paginator.total_pages
            )
        else:
            kb = build_list_keyboard([], "profile", 1, 1)

    await callback.message.edit_text(
        uz.VICTORIA_TITLE,
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "african:other")
async def other_african_menu(callback: CallbackQuery):
    async with async_session() as session:
        from sqlalchemy import select
        from app.models.taxonomy import Subcategory
        stmt = select(Subcategory).where(Subcategory.name == "Other Africa")
        result = await session.execute(stmt)
        subcat = result.scalar_one_or_none()

        if subcat:
            fish_svc = FishService(session)
            species_list = await fish_svc.get_species_by_subcategory(subcat.id)
            items = [(f"🐟 {sp.scientific_name}", f"{sp.id}:summary") for sp in species_list]
            paginator = Paginator(items, page=1, per_page=8)
            kb = build_list_keyboard(
                paginator.page_items, "profile",
                paginator.page, paginator.total_pages
            )
        else:
            kb = build_list_keyboard([], "profile", 1, 1)

    await callback.message.edit_text(
        "🌍 Boshqa Afrika Cichlidlari",
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


MALAWI_DESCRIPTIONS = {
    "Mbuna": "Qoyali hududlarda yashovchi Aufwuchs o'txo'r va baquvvat Malavi cichlidlari guruhi (Pseudotropheus, Chindongo, Labidochromis, Metriaclima).",
    "Haps": "Qumli va oraliq zonalarda yashovchi erkin suzuvchi, yorqin rangdor Haplochromine cichlidlari (Sciaenochromis, Cyrtocara, Placidochromis).",
    "Aulonocara": "Tovus cichlidlari (Peacocks): bosh sensor teshiklari orqali qum ostidagi o'ljani aniqlovchi ajoyib yorqin jins.",
    "Utaka": "Katta qoyalar ustidagi ochiq suvda zooplankton bilan oziqlanuvchi nay og'izli pelagik guruh (Copadichromis).",
    "Other Malawi": "Malavi ko'lining chuqur suv va yirtqich noyob cichlidalari (Dimidiochromis, Nimbochromis, Champsochromis).",
}

TANGANYIKA_DESCRIPTIONS = {
    "Shell Dwellers": "Tanganyika ko'lining bo'sh Neothauma chig'anoqlarida yashovchi va ko'payuvchi pakana cichlidalari (Multies, Similis, Brevis, Ocellatus).",
    "Julidochromis": "Tor silindrsimon tanali, qoyalar yuzasida g'orlarda juft bo'lib yashovchi nafis chiziqli cichlidlar (Marlieri, Transcriptus, Ornatus).",
    "Neolamprologus": "G'or quruvchi, oilaviy koloniya hosil qiluvchi va qoyali biotopga moslashgan cichlidlar (Brichardi, Leleupi, Tretocephalus).",
    "Altolamprologus": "O'ta yassi pichoqsimon tanali, qoyalardagi tor yoriqlarga kirib o'lja ovlovchi ixtisoslashgan yirtqichlar (Calvus, Compressiceps).",
    "Cyphotilapia": "Tanganyika ko'lining qiroli Frontosa: chuqur suv qatlamlarida yashovchi bahaybat va salobatli jins (C. frontosa, C. gibberosa).",
    "Tropheus": "Aufwuchs suv o'tlarini qiruvchi, o'ta faol va murakkab ijtimoiy ierarxiyaga ega rang-barang o'txo'rlar (Duboisi, Moorii).",
    "Xenotilapia": "Ko'lning qumli tubida suruv bo'lib yashovchi, nozik kumushrang va bentik qum elovchilar (X. flavipinnis).",
    "Other Tanganyika": "Tanganyika ko'lining ochiq suv (Cyprichromis), patqanot (Featherfin) va to'lqin zonasi buqasimon (Eretmodus) turlari.",
}


@router.callback_query(F.data.startswith("malawi:"))
async def malawi_subcategory(callback: CallbackQuery):
    parts = callback.data.split(":")
    sub_key = parts[1]
    sub_name = MALAWI_MAP.get(sub_key, sub_key)
    page = int(parts[3]) if len(parts) >= 4 and parts[2] == "page" else 1

    async with async_session() as session:
        fish_svc = FishService(session)
        from sqlalchemy import select
        from app.models.taxonomy import Subcategory
        stmt = select(Subcategory).where(Subcategory.name == sub_name)
        result = await session.execute(stmt)
        subcat = result.scalar_one_or_none()

        if subcat:
            species_list = await fish_svc.get_species_by_subcategory(subcat.id)
            items = [(f"🐟 {sp.scientific_name}", f"{sp.id}:summary") for sp in species_list]
            paginator = Paginator(items, page=page, per_page=8)
            kb = build_list_keyboard(
                paginator.page_items, "profile",
                paginator.page, paginator.total_pages,
                page_prefix=f"malawi:{sub_key}",
            )
            verified_count = sum(1 for s in species_list if s.author is not None)
            with_sources_count = sum(1 for s in species_list if len(s.sources) > 0)
            desc = MALAWI_DESCRIPTIONS.get(sub_name, subcat.description or "")
            text = (
                f"🇲🇼 <b>{sub_name}</b> (Malavi ko'li)\n\n"
                f"📝 <i>{desc}</i>\n\n"
                f"📊 <b>Guruhdagi jami turlar:</b> {len(species_list)} ta\n"
                f"🟢 <b>Ilmiy tasdiqlangan profillar:</b> {verified_count} ta\n"
                f"📚 <b>Manbalar bilan bog'langan:</b> {with_sources_count} ta\n\n"
                f"📋 <i>Quyidagi ro'yxatdan turni tanlang (Sahifa {paginator.page}/{paginator.total_pages}):</i>"
            )
        else:
            kb = build_list_keyboard([], "profile", 1, 1)
            text = f"🇲🇼 {sub_name}\n\nUshbu bo'limda baliqlar topilmadi."

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("tang:"))
async def tanganyika_subcategory(callback: CallbackQuery):
    parts = callback.data.split(":")
    sub_key = parts[1]
    sub_name = TANGANYIKA_MAP.get(sub_key, sub_key)
    page = int(parts[3]) if len(parts) >= 4 and parts[2] == "page" else 1

    async with async_session() as session:
        from sqlalchemy import select
        from app.models.taxonomy import Subcategory
        stmt = select(Subcategory).where(Subcategory.name == sub_name)
        result = await session.execute(stmt)
        subcat = result.scalar_one_or_none()

        if subcat:
            fish_svc = FishService(session)
            species_list = await fish_svc.get_species_by_subcategory(subcat.id)
            items = [(f"🐟 {sp.scientific_name}", f"{sp.id}:summary") for sp in species_list]
            paginator = Paginator(items, page=page, per_page=8)
            kb = build_list_keyboard(
                paginator.page_items, "profile",
                paginator.page, paginator.total_pages,
                page_prefix=f"tang:{sub_key}",
            )
            verified_count = sum(1 for s in species_list if s.author is not None)
            with_sources_count = sum(1 for s in species_list if len(s.sources) > 0)
            desc = TANGANYIKA_DESCRIPTIONS.get(sub_name, subcat.description or "")
            text = (
                f"🇹🇿 <b>{sub_name}</b> (Tanganyika ko'li)\n\n"
                f"📝 <i>{desc}</i>\n\n"
                f"📊 <b>Guruhdagi jami turlar:</b> {len(species_list)} ta\n"
                f"🟢 <b>Ilmiy tasdiqlangan profillar:</b> {verified_count} ta\n"
                f"📚 <b>Manbalar bilan bog'langan:</b> {with_sources_count} ta\n\n"
                f"📋 <i>Quyidagi ro'yxatdan turni tanlang (Sahifa {paginator.page}/{paginator.total_pages}):</i>"
            )
        else:
            kb = build_list_keyboard([], "profile", 1, 1)
            text = f"🇹🇿 {sub_name}\n\nUshbu bo'limda baliqlar topilmadi."

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("genus:"))
async def genus_view(callback: CallbackQuery):
    parts = callback.data.split(":")
    genus_id = int(parts[1])
    page = int(parts[3]) if len(parts) >= 4 and parts[2] == "page" else 1

    async with async_session() as session:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        from app.models.taxonomy import Genus
        from app.utils.pagination import Paginator

        stmt = (
            select(Genus)
            .options(selectinload(Genus.family), selectinload(Genus.species_list))
            .where(Genus.id == genus_id)
        )
        res = await session.execute(stmt)
        genus = res.scalar_one_or_none()

        if not genus:
            await callback.answer("Jins topilmadi.", show_alert=True)
            return

        species_list = [sp for sp in genus.species_list if sp.is_published]
        items = [(f"🐟 {sp.scientific_name}", f"{sp.id}:summary") for sp in species_list]
        paginator = Paginator(items, page=page, per_page=8)
        kb = build_list_keyboard(
            paginator.page_items, "profile",
            paginator.page, paginator.total_pages,
            page_prefix=f"genus:{genus_id}",
        )

        author_str = f" ({genus.author}, {genus.year_described})" if genus.author else ""
        subfam_str = f" | <b>Subfamily:</b> {genus.subfamily}" if genus.subfamily else ""
        fam_str = genus.family.scientific_name if genus.family else "Cichlidae"
        desc_str = f"\n\n📝 <i>{genus.description}</i>" if genus.description else ""
        verified_count = sum(1 for s in species_list if s.author is not None)
        with_sources_count = sum(1 for s in species_list if len(s.sources) > 0)

        text = (
            f"🔬 <b>Jins: {genus.scientific_name}</b>{author_str}\n"
            f"🏛 <b>Oila:</b> {fam_str}{subfam_str}{desc_str}\n\n"
            f"📊 <b>Bazadagi turlar:</b> {len(species_list)} ta\n"
            f"🟢 <b>Ilmiy tasdiqlangan:</b> {verified_count} ta\n"
            f"📚 <b>Manbalar bilan bog'langan:</b> {with_sources_count} ta\n\n"
            f"📋 <i>Jinsdagi turlar ro'yxati (Sahifa {paginator.page}/{paginator.total_pages}):</i>"
        )

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "back")
async def generic_back(callback: CallbackQuery):
    """Generic back handler — goes to main menu (specific handlers can override)."""
    from app.keyboards import main_menu_keyboard
    await callback.message.edit_text(
        uz.BOT_WELCOME,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()
