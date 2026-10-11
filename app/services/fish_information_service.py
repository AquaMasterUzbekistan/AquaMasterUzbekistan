"""Fish Information Service — generates comprehensive encyclopedic dossiers/posts for Telegram.

Follows strict structure:
🐠 To'liq nomi (Ilmiy, inglizcha/o'zbekcha, sinonimlar, taksonomiya)
🌍 Tabiiy tarqalishi (Ko'l/Daryo, aniq lokalitet, biotop)
📏 Tashqi ko'rinishi (Maks. o'lcham, ranglar, jinsiy dimorfizm, yosh baliqlar)
🏞️ Xulqi (Agressivlik, hududiylik, munosabatlar)
🍽️ Oziqlanishi (Tabiiy ratsion, akvarium yemi, oziqlantirishdagi xatolar/bloat)
💧 Suv parametrlari (Harorat, pH, GH, KH)
🏡 Akvarium sharoiti (Hajm, guruh, filtratsiya, dekoratsiya, qo'shnilar)
🧬 Ko'payishi (Turi, inkubatsiya, chavoqlar parvarishi, naslni saqlash)
⚠️ Muhim ogohlantirishlar (Gibridlanish, xavflar)
📚 Manbalar (FishBase, Malawi.si, Tanganyika.si, SeriouslyFish, IUCN)
"""

from __future__ import annotations

import html
import logging
import re
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.species import Species
from app.utils.formatting import (
    format_range, format_aggression, format_difficulty,
    format_breeding_type, format_origin, format_reliability,
)
from app.services.ai_service import AIService
from app.localization import uz

logger = logging.getLogger(__name__)


class FishInformationService:
    """Service generating comprehensive, publication-ready Telegram fish posts."""

    @classmethod
    def generate_post_from_model(cls, sp: Species) -> str:
        """Create a complete encyclopedic post directly from database model attributes."""
        lines: list[str] = []

        # 🐠 1. To'liq nomi
        lines.append(f"🐠 <b>TO'LIQ NOMI VA TAKSONOMIYASI</b>")
        lines.append(f"• <b>Ilmiy nomi:</b> <i>{sp.scientific_name}</i>")
        if sp.author:
            yr = f", {sp.year_described}" if sp.year_described else ""
            lines.append(f"• <b>Muallif va yili:</b> {sp.author}{yr}")
        if sp.genus:
            fam = f" | Oila: <b>{sp.genus.family.scientific_name}</b>" if sp.genus.family else ""
            subfam = f" ({sp.genus.subfamily})" if sp.genus.subfamily else ""
            lines.append(f"• <b>Tasnifi:</b> Avlod (Genus): <i>{sp.genus.scientific_name}</i>{subfam}{fam}")
        if sp.common_names:
            c_str = ", ".join(f"{cn.name} ({cn.language.upper()})" for cn in sp.common_names[:4])
            lines.append(f"• <b>Xalq nomlari:</b> {c_str}")
        if getattr(sp, "trade_names", None) and sp.trade_names:
            t_str = ", ".join(tn.name for tn in sp.trade_names[:4])
            lines.append(f"• <b>Savdo nomlari:</b> {t_str}")
        if sp.synonyms:
            s_str = ", ".join(f"<i>{syn.name}</i>" for syn in sp.synonyms[:3])
            lines.append(f"• <b>Tarixiy sinonimlari:</b> {s_str}")
        lines.append(f"• <b>Holati:</b> {sp.taxonomic_status or 'Valid (ilmiy qabul qilingan)'}")

        # 🌍 2. Tabiiy tarqalishi
        lines.append(f"\n🌍 <b>TABIIY TARQALISHI VA LOKALITETI</b>")
        lake_name = None
        locality_names = []
        if getattr(sp, "localities", None) and sp.localities:
            for loc in sp.localities:
                if loc.lake and not lake_name:
                    lake_name = loc.lake.name
                locality_names.append(loc.name)
        if lake_name:
            lines.append(f"• <b>Havza/Ko'l:</b> {lake_name}")
        elif sp.origin_type:
            lines.append(f"• <b>Kelib chiqishi:</b> {format_origin(sp.origin_type)}")
        if locality_names:
            lines.append(f"• <b>Hujjatlashtirilgan lokalitetlar:</b> {', '.join(locality_names[:4])}")
        if sp.natural_habitat:
            lines.append(f"• <b>Tabiiy biotop:</b> {sp.natural_habitat}")
        if sp.depth_range:
            lines.append(f"• <b>Yashash chuqurligi:</b> {sp.depth_range}")

        # 📏 3. Tashqi ko'rinishi
        lines.append(f"\n📏 <b>TASHQI KO'RINISHI VA O'LCHAMI</b>")
        if sp.max_size_cm:
            lines.append(f"• <b>Maksimal o'lchami:</b> {sp.max_size_cm} sm")
        if sp.body_shape:
            lines.append(f"• <b>Tana shakli:</b> {sp.body_shape}")
        if sp.coloration:
            lines.append(f"• <b>Rang xususiyatlari:</b> {sp.coloration}")
        if sp.sexual_dimorphism:
            lines.append(f"• <b>Jinsiy dimorfizm:</b> {sp.sexual_dimorphism}")
        if sp.male_description:
            lines.append(f"• <b>Erkak:</b> {sp.male_description}")
        if sp.female_description:
            lines.append(f"• <b>Urg'ochi:</b> {sp.female_description}")
        if sp.color_morphs:
            lines.append(f"• <b>Rang shakllari / morflar:</b> {sp.color_morphs}")

        # 🏞️ 4. Xulqi
        lines.append(f"\n🏞️ <b>XULQ-ATVORI VA TEMPERAMENTI</b>")
        lines.append(f"• <b>Agressivlik darajasi:</b> {format_aggression(sp.aggression)}")
        if sp.temperament:
            lines.append(f"• <b>Xarakteri:</b> {sp.temperament}")
        if sp.conspecific_aggression:
            lines.append(f"• <b>O'z turi bilan munosabat:</b> {sp.conspecific_aggression}")
        if sp.interspecific_aggression:
            lines.append(f"• <b>Boshqa turlar bilan munosabat:</b> {sp.interspecific_aggression}")

        # 🍽️ 5. Oziqlanishi
        lines.append(f"\n🍽️ <b>OZIQLANISH RATSIONI</b>")
        if sp.dietary_category:
            lines.append(f"• <b>Oziqlanish turi:</b> {sp.dietary_category}")
        if sp.diet_description:
            lines.append(f"• <b>Tavsif:</b> {sp.diet_description}")
        if sp.diet_plant:
            lines.append(f"• <b>O'simlikli ozuqalar:</b> {sp.diet_plant}")
        if sp.diet_protein:
            lines.append(f"• <b>Oqsilli ozuqalar:</b> {sp.diet_protein}")

        # 💧 6. Suv parametrlari
        lines.append(f"\n💧 <b>SUV PARAMETRLARI</b>")
        lines.append(f"• <b>Harorat:</b> {format_range(sp.temp_min, sp.temp_max, '°C')}")
        lines.append(f"• <b>Kislotalilik (pH):</b> {format_range(sp.ph_min, sp.ph_max)}")
        lines.append(f"• <b>Umumiy qattiqlik (GH):</b> {format_range(sp.gh_min, sp.gh_max, '°dGH')}")
        lines.append(f"• <b>Karbonat qattiqlik (KH):</b> {format_range(sp.kh_min, sp.kh_max, '°dKH')}")

        # 🏡 7. Akvarium sharoiti
        lines.append(f"\n🏡 <b>AKVARIUM TALABLARI</b>")
        if sp.min_tank_liters:
            lines.append(f"• <b>Minimal hajm:</b> {sp.min_tank_liters} litr")
        if sp.recommended_tank_liters:
            lines.append(f"• <b>Tavsiya etilgan hajm:</b> {sp.recommended_tank_liters} litr")
        if sp.group_size_recommended:
            lines.append(f"• <b>Guruh tarkibi:</b> {sp.group_size_recommended}")
        if sp.tank_setup_notes:
            lines.append(f"• <b>Dekoratsiya:</b> {sp.tank_setup_notes}")
        if sp.filtration_notes:
            lines.append(f"• <b>Filtratsiya va kislorod:</b> {sp.filtration_notes}")
        if sp.difficulty:
            lines.append(f"• <b>Parvarishlash darajasi:</b> {format_difficulty(sp.difficulty)}")

        # 🧬 8. Ko'payishi
        lines.append(f"\n🧬 <b>KO'PAYISH XUSUSIYATLARI</b>")
        lines.append(f"• <b>Ko'payish usuli:</b> {format_breeding_type(sp.breeding_type)}")
        if sp.breeding_description:
            lines.append(f"• <b>Jarayon tavsifi:</b> {sp.breeding_description}")
        if sp.fry_care:
            lines.append(f"• <b>Chavoqlar parvarishi:</b> {sp.fry_care}")

        # ⚠️ 9. Muhim ogohlantirishlar
        if sp.important_note:
            lines.append(f"\n⚠️ <b>MUHIM OGOHLANTIRISHLAR</b>")
            lines.append(f"{sp.important_note}")

        # 📚 10. Manbalar
        lines.append(f"\n📚 <b>ISHOCHLI MANBALAR</b>")
        lines.append(f"• {format_reliability(sp.reliability)}")
        lines.append("• <a href=\"https://www.fishbase.se\">FishBase.org</a> (Jahon ixtiologiya bazasi)")
        lines.append("• <a href=\"https://www.seriouslyfish.com\">SeriouslyFish.com</a> (Akvarium profillari)")
        if lake_name and "malawi" in lake_name.lower():
            lines.append("• <a href=\"https://malawi.si\">Malawi.si</a> (Malavi ko'li atlasi)")
        if lake_name and "tanganyika" in lake_name.lower():
            lines.append("• <a href=\"https://tanganyika.si\">Tanganyika.si</a> (Tanganika ko'li turlari)")
        lines.append("• IUCN Red List of Threatened Species")

        post_text = "\n".join(lines)
        if len(post_text) > 4000:
            post_text = post_text[:3980] + "...\n\n<i>[Batafsil ma'lumot qisqartirildi]</i>"
        return post_text

    @classmethod
    async def generate_full_dossier_by_name(
        cls,
        fish_name: str,
        session: AsyncSession,
        ai_service: AIService | None = None,
    ) -> str:
        """Generate a complete dossier for any fish query using DB or AI fallback."""
        from app.repositories import SpeciesRepository
        species_repo = SpeciesRepository(session)

        # 1. Try local DB
        candidates = await species_repo.search(fish_name, limit=1)
        if candidates:
            return cls.generate_post_from_model(candidates[0])

        # 2. If not found in DB, query AI Service with strict template
        if ai_service:
            ai_prompt = f"""Foydalanuvchi quyidagi akvarium balig'i haqida to'liq ensiklopedik ma'lumot (Telegram posti) so'radi:
Baliq nomi: "{fish_name}"

Iltimos, nufuzli ilmiy manbalar (FishBase, SeriouslyFish, IUCN, Malawi.si, Tanganyika.si) asosida quyidagi 10 ta bo'limdan iborat to'liq, mukammal o'zbekcha (lotin yozuvida) post tayyorlang:

🐠 <b>TO'LIQ NOMI VA TAKSONOMIYASI</b>
• Ilmiy nomi (aniq lotincha)
• Oila va Avlod (Genus)
• Inglizcha va savdo nomlari
• Sinonimlari

🌍 <b>TABIIY TARQALISHI VA LOKALITETI</b>
• Ko'l/Daryo havzasi
• Aniq lokalitet (agar ma'lum bo'lsa)
• Yashash biotopi

📏 <b>TASHQI KO'RINISHI VA O'LCHAMI</b>
• Maksimal o'lchami (sm)
• Rangi va jinsiy dimorfizm (erkak va urg'ochi farqi)

🏞️ <b>XULQ-ATVORI</b>
• Agressivlik va hududiylik
• Qo'shnilar bilan munosabati

🍽️ <b>OZIQLANISH RATSIONI</b>
• Tabiiy ozuqasi
• Akvariumda tavsiya etiladigan yemlar
• Oziqlantirishdagi xatolar va Bloat xavfi

💧 <b>SUV PARAMETRLARI</b>
• Harorat (°C)
• pH
• Qattiqlik (GH, KH)

🏡 <b>AKVARIUM TALABLARI</b>
• Minimal hajm (litr)
• Filtratsiya va bezatish
• Mos qo'shnilar

🧬 <b>KO'PAYISHI</b>
• Ko'payish turi (Mouthbrooder yoki substrat)
• Chavoqlar parvarishi

⚠️ <b>MUHIM OGOHLANTIRISHLAR</b>
• Gibridlanish xavfi yoki saqlashdagi muhim qoidalar

📚 <b>ISHOCHLI MANBALAR</b>
• FishBase.org, SeriouslyFish.com, IUCN Red List

QOIDALAR:
- Faqat ishonchli faktlarni yozing, uydirma ma'lumot kiritmang.
- Telegram HTML teglaridan (<b>, <i>, <code>) to'g'ri foydalaning va ularni yoping.
- Uzunligi 3800 belgidan oshmasin."""

            try:
                ai_post = await ai_service.search_and_explain(ai_prompt)
                if len(ai_post) > 4000:
                    ai_post = ai_post[:3980] + "..."
                return ai_post
            except Exception as e:
                logger.error(f"AI dossier generation failed: {e}")

        return f"❌ «{html.escape(fish_name)}» bo'yicha to'liq ensiklopedik ma'lumot topilmadi."
