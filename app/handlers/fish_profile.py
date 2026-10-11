"""Fish profile handlers — full species view with tabs."""

from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.localization import uz
from app.keyboards.profile import profile_tabs_keyboard
from app.keyboards.navigation import back_home_row, build_list_keyboard
from app.database.session import async_session
from app.services import FishService
from app.repositories import UserRepository
from app.utils.formatting import (
    format_fish_profile_summary, format_water_params,
    format_diet, format_breeding, format_genetics,
    format_reliability,
)

router = Router(name="fish_profile")


@router.callback_query(F.data.regexp(r"^profile:(\d+):(.+)$"))
async def fish_profile(callback: CallbackQuery):
    parts = callback.data.split(":")
    species_id = int(parts[1])
    tab = parts[2]

    async with async_session() as session:
        fish_svc = FishService(session)
        sp = await fish_svc.get_species(species_id)

        if not sp:
            await callback.answer(uz.ERROR_NOT_FOUND, show_alert=True)
            return

        # Check if favorite
        user_repo = UserRepository(session)
        from_user = callback.from_user
        db_user = await user_repo.get_by_telegram_id(from_user.id)
        is_fav = False
        if db_user:
            is_fav = await user_repo.is_favorite(db_user.id, species_id)
            # Track recently viewed
            await user_repo.add_recently_viewed(db_user.id, species_id)

        genus_name = sp.genus.scientific_name if sp.genus else None
        genus_id = sp.genus_id

        def _get_tabs_kb():
            return profile_tabs_keyboard(species_id, is_fav, genus_id, genus_name)

        if tab in ("summary", "full_post"):
            from app.utils.formatting import format_standard_reference_card
            text = format_standard_reference_card(sp)
            kb = _get_tabs_kb()
        elif tab == "info":
            lines = [f"🔬 <b>ILMIY IDENTIFIKATSIYA VA TANA TUZILISHI</b>\n<i>{sp.scientific_name}</i>\n"]
            lines.append("<b>A. Ilmiy tasnif (Scientific Identity):</b>")
            lines.append(f"• Qabul qilingan ilmiy nomi: <i>{sp.scientific_name}</i>")
            if sp.author:
                lines.append(f"• Muallif va yili: {sp.author} ({sp.year_described or 'nomaʼlum'})")
            if sp.genus and sp.genus.family:
                lines.append(f"• Oila (Family): {sp.genus.family.scientific_name}")
            if sp.genus and sp.genus.subfamily:
                lines.append(f"• Kichik oila (Subfamily): {sp.genus.subfamily}")
            if sp.genus:
                lines.append(f"• Jins (Genus): <i>{sp.genus.scientific_name}</i>")
            if sp.subspecies:
                lines.append(f"• Kichik tur (Subspecies): <i>{sp.subspecies}</i>")
            lines.append(f"• Taksonomik maqomi: {sp.taxonomic_status or 'Valid (qabul qilingan)'}")

            if sp.common_names:
                c_list = [f"{cn.name} ({cn.language.upper()})" for cn in sp.common_names]
                lines.append(f"• Xalq nomlari: {', '.join(c_list)}")
            if sp.synonyms:
                s_list = [syn.name for syn in sp.synonyms]
                lines.append(f"• Tarixiy sinonimlar: {', '.join(s_list)}")
            if sp.trade_names:
                t_list = [tn.name for tn in sp.trade_names]
                lines.append(f"• Savdo nomlari: {', '.join(t_list)}")
            if sp.taxonomic_notes:
                lines.append(f"\n📝 <b>Taksonomik izohlar:</b>\n{sp.taxonomic_notes}")

            lines.append("\n<b>C. Jismoniy xususiyatlar (Physical characteristics):</b>")
            if sp.max_size_cm:
                lines.append(f"• Maksimal hujjatlashtirilgan o'lcham: {sp.max_size_cm} sm")
            if sp.body_shape:
                lines.append(f"• Tana shakli: {sp.body_shape}")
            if sp.coloration:
                lines.append(f"• Rang xususiyatlari: {sp.coloration}")
            if sp.sexual_dimorphism:
                lines.append(f"• Jinsiy dimorfizm: {sp.sexual_dimorphism}")
            if sp.male_description:
                lines.append(f"• Erkak: {sp.male_description}")
            if sp.female_description:
                lines.append(f"• Urg'ochi: {sp.female_description}")

            lines.append(f"\n{sp.evidence_quality_note or format_reliability(sp.reliability)}")
            text = "\n".join(lines)
            kb = _get_tabs_kb()
        elif tab == "water":
            text = format_water_params(sp)
            kb = _get_tabs_kb()
        elif tab == "diet":
            text = format_diet(sp)
            kb = _get_tabs_kb()
        elif tab == "behaviour":
            from app.utils.formatting import format_behaviour
            text = format_behaviour(sp)
            kb = _get_tabs_kb()
        elif tab == "breeding":
            text = format_breeding(sp)
            kb = _get_tabs_kb()
        elif tab == "genetics":
            text = format_genetics(sp)
            kb = _get_tabs_kb()
        elif tab == "locality":
            lines = [f"🗺️ <b>TABIIY TARQALISHI VA LOKATSIYA ATLASI</b>\n<i>{sp.scientific_name}</i>\n"]
            lines.append("<b>B. Tabiiy ekologiya va areali:</b>")
            if sp.natural_habitat:
                lines.append(f"• Tabiiy biotop muhiti:\n{sp.natural_habitat}\n")
            if sp.depth_range:
                lines.append(f"• Yashash chuqurligi: {sp.depth_range}")
            if sp.conservation_status:
                lines.append(f"• IUCN Muhofaza maqomi: <b>{sp.conservation_status}</b>\n")

            if sp.localities:
                lines.append("📍 <b>Hujjatlashtirilgan lokatsiyalar:</b>")
                for loc in sp.localities:
                    lines.append(f"▫️ <b>{loc.name}</b>")
                    if loc.lake:
                        lines.append(f"   🏞️ Ko'l/Daryo: {loc.lake.name}")
                    if loc.country:
                        flag = loc.country.emoji or "🌍"
                        lines.append(f"   {flag} Davlat: {loc.country.name}")
                    if loc.habitat:
                        lines.append(f"   🪨 Biotop: {loc.habitat}")
                    if loc.description:
                        lines.append(f"   📝 Tavsif: {loc.description}")
                    if loc.latitude is not None and loc.longitude is not None:
                        lines.append(f"   🧭 Koordinatalar: <code>{loc.latitude}, {loc.longitude}</code>")
                lines.append("")
            else:
                lines.append(f"🌍 Kelib chiqish mintaqasi: {format_origin(sp.origin_type)}\n")

            lines.append("📚 Manbalar: <i>FishBase.org, Eschmeyer, SeriouslyFish, IUCN</i>")
            text = "\n".join(lines)
            kb = _get_tabs_kb()
        elif tab == "sources":
            lines = [f"📚 <b>MANBALAR VA DALILLAR SIFATI</b>\n<i>{sp.scientific_name}</i>\n"]
            lines.append(f"Status: {sp.evidence_quality_note or '🟢 Ilmiy manba bilan tasdiqlangan'}")
            if sp.last_verified_date:
                lines.append(f"📅 Oxirgi tekshirilgan sana: {sp.last_verified_date}\n")

            # Scientific claims
            from sqlalchemy import select
            from app.models.source import ScientificClaim
            claims_stmt = select(ScientificClaim).where(ScientificClaim.species_id == species_id)
            claims_res = await session.execute(claims_stmt)
            claims_list = list(claims_res.scalars().all())

            if claims_list:
                lines.append("🔬 <b>Hujjatlashtirilgan ilmiy daʼvolar:</b>")
                for cl in claims_list:
                    lines.append(f"• <b>{cl.claim_type}:</b> {cl.claim_text}")
                    if cl.exact_source_url:
                        lines.append(f"  🔗 <a href=\"{cl.exact_source_url}\">{cl.exact_source_url}</a>")
                    lines.append(f"  Daraja: {cl.evidence_label} (Tekshirildi: {cl.verified_date or '2026-10-10'})")
                lines.append("")

            if sp.sources:
                lines.append("📖 <b>Avtoritativ manbalar ro'yxati:</b>")
                for ss in sp.sources:
                    src = ss.source
                    lines.append(f"• <b>{src.name}</b>")
                    if src.url:
                        lines.append(f"  🔗 <a href=\"{src.url}\">{src.url}</a>")
                    if ss.relevant_section:
                        lines.append(f"  📑 Bo'lim: {ss.relevant_section}")
                    if ss.access_date:
                        lines.append(f"  📅 Kirish sanasi: {ss.access_date}")
            else:
                lines.append("• FishBase.org (Ichthyological database)")
                lines.append("• Eschmeyer's Catalog of Fishes")
                lines.append("• SeriouslyFish.com")

            text = "\n".join(lines)
            kb = _get_tabs_kb()
        elif tab == "full_post":
            from app.services.fish_information_service import FishInformationService
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            await user_repo.log_activity(from_user.id, "full_info", sp.scientific_name)
            text = FishInformationService.generate_post_from_model(sp)
            kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="🖼️ Suratlarini izlash", callback_data=f"fish_images:fetch:{species_id}"),
                    ],
                    [
                        InlineKeyboardButton(text="📋 Qisqa ma'lumot", callback_data=f"profile:{species_id}:summary"),
                        InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="home"),
                    ]
                ]
            )
        else:
            text = format_fish_profile_summary(sp)
            kb = _get_tabs_kb()

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.regexp(r"^fav:(\d+)$"))
async def add_favorite(callback: CallbackQuery):
    species_id = int(callback.data.split(":")[1])
    async with async_session() as session:
        user_repo = UserRepository(session)
        db_user = await user_repo.get_by_telegram_id(callback.from_user.id)
        if db_user:
            await user_repo.add_favorite(db_user.id, species_id)
            await callback.answer("⭐ Saqlandi!", show_alert=False)
        else:
            await callback.answer(uz.ERROR_GENERIC, show_alert=True)


@router.callback_query(F.data.regexp(r"^unfav:(\d+)$"))
async def remove_favorite(callback: CallbackQuery):
    species_id = int(callback.data.split(":")[1])
    async with async_session() as session:
        user_repo = UserRepository(session)
        db_user = await user_repo.get_by_telegram_id(callback.from_user.id)
        if db_user:
            await user_repo.remove_favorite(db_user.id, species_id)
            await callback.answer("💔 O'chirildi!", show_alert=False)
        else:
            await callback.answer(uz.ERROR_GENERIC, show_alert=True)
