"""Ingest Atlas Expansion: Rich Families, Genera, and L-numbers.

Fulfills Master Prompt requirements:
- Section 4: L-numbers and LDA-numbers catalog
- Section 7: Family and Genus pages with scientific overviews
- Section 8: Repeatable, idempotent ingestion pipeline
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from sqlalchemy import select, func, insert
from app.database.session import async_session
from app.models.taxonomy import Family, Genus
from app.models.species import Species
from app.models.lnumber import LNumberDesignation, lnumber_species
from app.data.lnumber_data import L_NUMBER_CATALOG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ingest_atlas_expansion")

FAMILY_RICH_PROFILES = {
    "Cichlidae": {
        "general_biology": "Sixlidlar (Cichlidae) — chuchuk suv akvariumchiligidagi eng yuksak xulq-atvorga ega va intellektual baliqlar oilasi. Ular farengeal jag' apparati, bitta juft burun teshigi va yuqori darajada rivojlangan nasl parvarishi instinkti bilan ajralib turadi.",
        "distribution_overview": "Afrika (Buyuk Rift vodiysi ko'llari: Malavi, Tanganika, Viktoriya; Kongo, Niger daryolari), Markaziy va Janubiy Amerika (Amazonka, Orinoko, Parana havzalari), Yaqin Sharq va Janubiy Osiyo (Hindiston, Shri-Lanka).",
        "feeding_ecology": "O'ta xilma-xil trofik ixtisoslashuv: tosh usti suvo'tlarini qiruvchi aufwuchs-xo'rlar (Mbuna, Tropheus), yirtqich piscivorelar (Champsochromis, Bathybates), qum elovchilar (Aulonocara, Geophagus, Satanoperca) va detritxo'rlar.",
        "reproduction_overview": "Barcha vakillarda intensiv nasl parvarishi: og'izda urug' yetishtiruvchilar (Mouthbrooders — barcha Malavi Mbuna/Utaka, ko'plab Viktoriya va Tanganika turlari) va substratga tuxum qo'yuvchilar (Substrate spawners — Amerika cichlidlari, Diskus, Neolamprologus).",
        "aquarium_care_overview": "Afrika ko'llari vakillari uchun qattiq, ishqoriy (pH 7.8-8.6) suv va toshli hududlar zarur. Janubiy Amerika vakillari uchun esa yumshoq, nordon (pH 5.5-7.0) suv, yog'ochlar (driftwood) va sokin oqim tavsiya etiladi.",
    },
    "Loricariidae": {
        "general_biology": "Loricariidae (Zirhli so'rg'ichli laqqalar) — dunyodagi eng yirik laqqa oilasi bo'lib, 1000 dan ortiq turni o'z ichiga oladi. Tanasi suyak plastinkalar (dermik sovut) bilan qoplangan, og'zi so'rg'ich diskka aylangan, ko'zlarida o'ziga xos 'omega-mushuk' pardasi (iris operculum) mavjud.",
        "distribution_overview": "Markaziy va Janubiy Amerika: Kosta-Rikadan Argentinagacha, xususan Amazonka, Orinoko, Parana, San-Fransisko daryolari hamda And tog'oldi tez oqar daryo irmoqlari.",
        "feeding_ecology": "Aufwuchs va bio-film qirg'ichlar (Ancistrus), ksilo-faglar (yog'och hazm qiluvchi Panaque, Panaqolus), bentik yirtqichlar va hasharotxo'rlar (Hypancistrus, Leporacanthicus), hamda detritxo'rlar.",
        "reproduction_overview": "G'orlarda tuxum qo'yuvchilar (Cave brooders). Urg'ochisi tosh yoki daraxt kovagiga yirik yopishqoq tuxum qo'ygach, erkagi g'orga kirib tuxumlarni suzgichlari bilan yelpig'ichlab kislorod bilan ta'minlaydi va lichinkalar chiqquncha qo'riqlaydi.",
        "aquarium_care_overview": "Yuqori kislorodli toza suv, yaxshi oqim va aeratsiya talab qilinadi. Ko'pchilik turlar uchun akvariumda tabiiy daraxt ildizlari (yog'och kletchatkasi hazm uchun zarur) va maxsus sopol g'orlar (slate/clay caves) bo'lishi shart.",
    },
    "Callichthyidae": {
        "general_biology": "Callichthyidae (Sovutli laqqachalar / Koridoraslar) — tanasi ikki qatorli yon suyak plastinkalari bilan himoyalangan, kichik o'lchamli, o'ta tinch va ijtimoiy tub baliqlari. Ichak nafasi (atmosfera havosidan foydalanish) qobiliyatiga ega.",
        "distribution_overview": "Janubiy Amerika daryo va botqoqliklari: Amazonka, Orinoko, La-Plata havzalari.",
        "feeding_ecology": "Bentik mikroyirtqichlar: nozik qum ichidan mo'ylovlari yordamida tub umurtqasizlari, qurtlar va detritni qidirib topadi.",
        "reproduction_overview": "T-pozitsiyasi orqali urug'lanish. Urg'ochi qorin suzgichlari orasida tuxum ushlab, o'simlik barglari yoki shishaga yopishtirib chiqadi.",
        "aquarium_care_overview": "Yumshoq mayda daryo qumi (o'tkir qirrali shag'al mo'ylovlarini shikastlaydi), kamida 6-8 donadan iborat to'dada boqish, toza va mo''tadil haroratli suv.",
    },
    "Characidae": {
        "general_biology": "Characidae (Tetralar) — yog' suzgichi (adipose fin) va jag' tishlariga ega, yorqin rangli, tez suzuvchi suruvchi baliqlar.",
        "distribution_overview": "Janubiy va Markaziy Amerika o'rmon daryolari va irmoqlari.",
        "feeding_ecology": "Mikroyirtqich va hammaxo'rlar: suv yuzasi va qatlamidagi hasharotlar, zooplankton, mayda qisqichbaqasimonlar.",
        "reproduction_overview": "Tuxum sochuvchilar (Egg scatterers). O'simliklar orasiga yopishmaydigan mayda tuxumlar sochadi, nasl parvarishi kuzatilmaydi.",
        "aquarium_care_overview": "O'simliklar bilan mo'l ekilgan, yoritilishi yumshatilgan, yumshoq va ozroq nordon suvli akvariumlar.",
    },
}

GENUS_RICH_PROFILES = {
    "Hypancistrus": {
        "type_species": "Hypancistrus zebra Isbrücker & Nijssen, 1991",
        "diagnostic_traits": "Og'iz so'rg'ich apparatida tishlar soni kamaygan; pastki jag' tishlari uzun va chuqur qoshiqsimon. Suv o'tlarini qirishga emas, oqsil va go'shtdor ozuqalarni tutishga moslashgan. Qora va oq kontrastli chiziqlar.",
        "distribution": "Rio Xingu, Rio Negro, Rio Orinoco (Braziliya, Venesuela).",
        "taxonomic_notes": "L-number tizimida eng ko'p bahsli turlarga ega avlod: L046, L066, L236, L260, L333 va boshqalar.",
    },
    "Ancistrus": {
        "type_species": "Ancistrus cirrhosus (Valenciennes, 1836)",
        "diagnostic_traits": "Erkaklarining burni va tumshug'ida shoxlangan terili o'simtalar (tentakullar) mavjud; urg'ochilarda bu o'simtalar yo'q yoki juda kichik. Keng so'rg'ich og'iz, kuchli aufwuchs qirg'ich tishlar.",
        "distribution": "Janubiy va Markaziy Amerikaning barcha chuchuk suv havzalari.",
        "taxonomic_notes": "100 dan ortiq ilmiy tavsiflangan turlari bor. Akvariumlarda eng keng tarqalgan turlari: Ancistrus ranunculus (L034), Ancistrus sp. 'L144', Ancistrus dolichopterus (L183).",
    },
    "Pterophyllum": {
        "type_species": "Platax scalaris Cuvier, 1831 (= Pterophyllum scalare)",
        "diagnostic_traits": "Disk shaklidagi lateral yassi tana, nihoyatda uzun orqa va anal suzgichlari, ipsimon qorin suzgichlari.",
        "distribution": "Amazonka, Orinoko va Essekibo daryolari havzalari.",
        "taxonomic_notes": "Uchta ilmiy tasdiqlangan tur: Pterophyllum scalare, Pterophyllum altum, Pterophyllum leopoldi.",
    },
    "Symphysodon": {
        "type_species": "Symphysodon discus Heckel, 1840",
        "diagnostic_traits": "Deyarli dumaloq yassi tana profili, ota-onalik terisi orqali maxsus ozuqaviy shilimshiq ajratish xususiyati.",
        "distribution": "Amazonka pasttekisligining qora va tiniq suvli irmoqlari (Rio Negro, Rio Madeira, Rio Tapajos).",
        "taxonomic_notes": "Zamonaviy taksonomiyada asosan Symphysodon discus, Symphysodon aequifasciatus va Symphysodon tarzoo tan olingan.",
    },
    "Aulonocara": {
        "type_species": "Aulonocara nyassae Regan, 1922",
        "diagnostic_traits": "Bosh suyagidagi kengaygan sensor teshiklar (akustik-lateral tizim) qum ostidagi umurtqasizlar harakatini eshitish imkonini beradi.",
        "distribution": "Malavi ko'li (endemik).",
        "taxonomic_notes": "Peacock cichlidlar deb ataladi; 20 dan ortiq rasmiy turlar va ko'plab lokatsiya morflari mavjud.",
    },
    "Labidochromis": {
        "type_species": "Labidochromis vellicans Trewavas, 1935",
        "diagnostic_traits": "Ingichka qisqichsimon old tishlar tosh yoriqlaridagi hasharotlar va mayda qisqichbaqasimonlarni terib olishga moslashgan.",
        "distribution": "Malavi ko'li (endemik).",
        "taxonomic_notes": "Mbuna guruhiga kiradi; eng mashhur turi — Labidochromis caeruleus (Yellow Lab).",
    },
    "Neolamprologus": {
        "type_species": "Neolamprologus tetracanthus (Boulenger, 1899)",
        "diagnostic_traits": "Uzunchoq tana, mayda tangachalar, o'ta xilma-xil biotopik moslashuv (tosh yoriqlari, chig'anoqlar).",
        "distribution": "Tanganika ko'li (endemik).",
        "taxonomic_notes": "Tanganika ko'lidagi eng yirik avlodlardan biri: N. brichardi, N. leleupi, N. multifasciatus va boshqalar.",
    },
}


async def main():
    logger.info("Starting Atlas Expansion Ingestion...")
    async with async_session() as session:
        # 1. Enrich Families
        logger.info("Enriching Families with Section 7 overviews...")
        for fam_name, profile in FAMILY_RICH_PROFILES.items():
            stmt = select(Family).where(func.lower(Family.scientific_name) == fam_name.lower())
            res = await session.execute(stmt)
            fam = res.scalar_one_or_none()
            if fam:
                fam.general_biology = profile["general_biology"]
                fam.distribution_overview = profile["distribution_overview"]
                fam.feeding_ecology = profile["feeding_ecology"]
                fam.reproduction_overview = profile["reproduction_overview"]
                fam.aquarium_care_overview = profile["aquarium_care_overview"]
                logger.info(f"Updated Family: {fam_name}")

        # 2. Enrich Genera
        logger.info("Enriching Genera with Section 7 overviews...")
        for gen_name, profile in GENUS_RICH_PROFILES.items():
            stmt = select(Genus).where(func.lower(Genus.scientific_name) == gen_name.lower())
            res = await session.execute(stmt)
            gen = res.scalar_one_or_none()
            if gen:
                gen.type_species = profile["type_species"]
                gen.diagnostic_traits = profile["diagnostic_traits"]
                gen.distribution = profile["distribution"]
                gen.taxonomic_notes = profile["taxonomic_notes"]
                logger.info(f"Updated Genus: {gen_name}")

        await session.commit()

        # 3. Ingest L-number catalog
        logger.info(f"Ingesting {len(L_NUMBER_CATALOG)} L-number / LDA-number designations...")
        added_lnum = 0
        updated_lnum = 0
        linked_species_count = 0

        for item in L_NUMBER_CATALOG:
            stmt = select(LNumberDesignation).where(LNumberDesignation.designation == item["designation"])
            res = await session.execute(stmt)
            existing = res.scalar_one_or_none()

            if not existing:
                lnum = LNumberDesignation(
                    designation=item["designation"],
                    number_type=item["number_type"],
                    code_number=item["code_number"],
                    scientific_name_current=item["scientific_name_current"],
                    identification_status=item["identification_status"],
                    genus_name=item["genus_name"],
                    family_name=item["family_name"],
                    subfamily_name=item["subfamily_name"],
                    common_name_uz=item.get("common_name_uz"),
                    common_name_en=item.get("common_name_en"),
                    common_name_ru=item.get("common_name_ru"),
                    trade_names=item.get("trade_names"),
                    alternative_numbers=item.get("alternative_numbers"),
                    river_basin=item.get("river_basin"),
                    country=item.get("country"),
                    locality_detail=item.get("locality_detail"),
                    max_size_cm=item.get("max_size_cm"),
                    temp_min=item.get("temp_min"),
                    temp_max=item.get("temp_max"),
                    ph_min=item.get("ph_min"),
                    ph_max=item.get("ph_max"),
                    dietary_category=item.get("dietary_category"),
                    description=item.get("description"),
                    aquarium_care=item.get("aquarium_care"),
                    source_reference=item.get("source_reference"),
                    last_verified_date=item.get("last_verified_date", "2026-10-11"),
                    is_ancistrus=item.get("is_ancistrus", False),
                )
                session.add(lnum)
                await session.flush()
                added_lnum += 1
            else:
                lnum = existing
                lnum.scientific_name_current = item["scientific_name_current"]
                lnum.identification_status = item["identification_status"]
                lnum.genus_name = item["genus_name"]
                lnum.common_name_uz = item.get("common_name_uz")
                lnum.common_name_en = item.get("common_name_en")
                lnum.common_name_ru = item.get("common_name_ru")
                lnum.trade_names = item.get("trade_names")
                lnum.alternative_numbers = item.get("alternative_numbers")
                lnum.river_basin = item.get("river_basin")
                lnum.country = item.get("country")
                lnum.locality_detail = item.get("locality_detail")
                lnum.max_size_cm = item.get("max_size_cm")
                lnum.temp_min = item.get("temp_min")
                lnum.temp_max = item.get("temp_max")
                lnum.ph_min = item.get("ph_min")
                lnum.ph_max = item.get("ph_max")
                lnum.dietary_category = item.get("dietary_category")
                lnum.description = item.get("description")
                lnum.aquarium_care = item.get("aquarium_care")
                lnum.source_reference = item.get("source_reference")
                lnum.is_ancistrus = item.get("is_ancistrus", False)
                await session.flush()
                updated_lnum += 1

            # 4. Link with Species if scientific_name_current is a described species
            sci_name = item.get("scientific_name_current")
            if sci_name and "sp." not in sci_name:
                sp_stmt = select(Species).where(func.lower(Species.scientific_name) == sci_name.lower())
                sp_res = await session.execute(sp_stmt)
                sp = sp_res.scalar_one_or_none()
                if sp:
                    # check link
                    link_check = select(lnumber_species).where(
                        lnumber_species.c.lnumber_id == lnum.id,
                        lnumber_species.c.species_id == sp.id,
                    )
                    if not (await session.execute(link_check)).first():
                        ins = insert(lnumber_species).values(
                            lnumber_id=lnum.id,
                            species_id=sp.id,
                            is_primary=True,
                            notes=f"Described species for {lnum.designation}",
                        )
                        await session.execute(ins)
                        linked_species_count += 1
                        logger.info(f"Linked {lnum.designation} <-> Species {sp.scientific_name}")

        await session.commit()
        logger.info(
            f"L-number ingestion completed: {added_lnum} added, {updated_lnum} updated, "
            f"{linked_species_count} linked to species records."
        )


if __name__ == "__main__":
    asyncio.run(main())
