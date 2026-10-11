"""Database seeder for AquaMasterUzbekistan Fish Atlas.

Populates categories, subcategories, families, genera, continents, countries, lakes,
species, common names, synonyms, trade names, health conditions, dictionary terms, and articles.
All user-facing text is in Uzbek Latin. Scientific names are preserved in exact Latin.
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.engine import engine
from app.database.session import async_session
from app.models.taxonomy import Category, Subcategory, Family, Genus
from app.models.locality import Continent, Country, Lake, Locality
from app.models.species import (
    Species, CommonName, Synonym, TradeName,
    ReliabilityLevel, AggressionLevel, DifficultyLevel,
    BreedingType, WaterType, OriginType,
    species_categories,
)
from app.models.health import HealthCondition
from app.models.dictionary import DictionaryTerm
from app.models.article import Article, ArticleCategory

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("seed")


async def seed_geography(session: AsyncSession) -> dict[str, int]:
    """Seed continents, countries, and lakes."""
    logger.info("Seeding geography...")

    # Continents
    continents_data = [
        {"name": "Afrika", "emoji": "🌍"},
        {"name": "Janubiy Amerika", "emoji": "🌎"},
        {"name": "Markaziy Amerika", "emoji": "🌎"},
        {"name": "Shimoliy Amerika", "emoji": "🌎"},
        {"name": "Osiyo", "emoji": "🌏"},
        {"name": "Yevropa", "emoji": "🌍"},
        {"name": "Avstraliya va Okeaniya", "emoji": "🌏"},
    ]
    continent_map = {}
    for c_data in continents_data:
        res = await session.execute(select(Continent).where(Continent.name == c_data["name"]))
        existing = res.scalar_one_or_none()
        if not existing:
            continent = Continent(**c_data)
            session.add(continent)
            await session.flush()
            continent_map[c_data["name"]] = continent.id
        else:
            continent_map[c_data["name"]] = existing.id

    # Countries
    countries_data = [
        {"name": "Malavi", "code": "MW", "continent_id": continent_map["Afrika"], "emoji": "🇲🇼"},
        {"name": "Tanzaniya", "code": "TZ", "continent_id": continent_map["Afrika"], "emoji": "🇹🇿"},
        {"name": "Zambiya", "code": "ZM", "continent_id": continent_map["Afrika"], "emoji": "🇿🇲"},
        {"name": "Uganda", "code": "UG", "continent_id": continent_map["Afrika"], "emoji": "🇺🇬"},
        {"name": "Kongo Demokratik Respublikasi", "code": "CD", "continent_id": continent_map["Afrika"], "emoji": "🇨🇩"},
        {"name": "Braziliya", "code": "BR", "continent_id": continent_map["Janubiy Amerika"], "emoji": "🇧🇷"},
        {"name": "Peru", "code": "PE", "continent_id": continent_map["Janubiy Amerika"], "emoji": "🇵🇪"},
        {"name": "Kolumbiya", "code": "CO", "continent_id": continent_map["Janubiy Amerika"], "emoji": "🇨🇴"},
        {"name": "Venesuela", "code": "VE", "continent_id": continent_map["Janubiy Amerika"], "emoji": "🇻🇪"},
        {"name": "Meksika", "code": "MX", "continent_id": continent_map["Markaziy Amerika"], "emoji": "🇲🇽"},
        {"name": "Gvatemala", "code": "GT", "continent_id": continent_map["Markaziy Amerika"], "emoji": "🇬🇹"},
        {"name": "AQSH", "code": "US", "continent_id": continent_map["Shimoliy Amerika"], "emoji": "🇺🇸"},
        {"name": "Tailand", "code": "TH", "continent_id": continent_map["Osiyo"], "emoji": "🇹🇭"},
        {"name": "Indoneziya", "code": "ID", "continent_id": continent_map["Osiyo"], "emoji": "🇮🇩"},
        {"name": "Malayziya", "code": "MY", "continent_id": continent_map["Osiyo"], "emoji": "🇲🇾"},
        {"name": "Hindiston", "code": "IN", "continent_id": continent_map["Osiyo"], "emoji": "🇮🇳"},
    ]
    country_map = {}
    for c_data in countries_data:
        res = await session.execute(select(Country).where(Country.name == c_data["name"]))
        existing = res.scalar_one_or_none()
        if not existing:
            country = Country(**c_data)
            session.add(country)
            await session.flush()
            country_map[c_data["name"]] = country.id
        else:
            country_map[c_data["name"]] = existing.id

    # Lakes
    lakes_data = [
        {"name": "Malavi ko'li (Nyasa)", "country_id": country_map["Malavi"], "description": "Sharqiy Afrika rifti, o'ta tiniq, yuqori pH va minerallashgan suv."},
        {"name": "Tanganika ko'li", "country_id": country_map["Tanzaniya"], "description": "Dunyodagi eng chuqur ikkinchi chuchuk suv ko'li, juda qattiq va ishqoriy suv."},
        {"name": "Viktoriya ko'li", "country_id": country_map["Uganda"], "description": "Afrikaning eng yirik ko'li, endemik Haplochromis turlari vatani."},
        {"name": "Amazonka havzasi", "country_id": country_map["Braziliya"], "description": "Janubiy Amerikaning ulkan daryo tizimi, kislotali va yumshoq qora suv (blackwater)."},
        {"name": "Orinoko havzasi", "country_id": country_map["Venesuela"], "description": "Yumshoq, iliq suvli tropik daryolar tizimi."},
        {"name": "Chao Phraya daryosi", "country_id": country_map["Tailand"], "description": "Janubi-sharqiy Osiyoning asosiy daryosi."},
    ]
    lake_map = {}
    for l_data in lakes_data:
        res = await session.execute(select(Lake).where(Lake.name == l_data["name"]))
        existing = res.scalar_one_or_none()
        if not existing:
            lake = Lake(**l_data)
            session.add(lake)
            await session.flush()
            lake_map[l_data["name"]] = lake.id
        else:
            lake_map[l_data["name"]] = existing.id

    return {"continents": continent_map, "countries": country_map, "lakes": lake_map}


async def seed_taxonomy(session: AsyncSession) -> dict[str, dict]:
    """Seed categories, subcategories, families, and genera."""
    logger.info("Seeding taxonomy structure...")

    # Categories
    categories_data = [
        {"name": "Afrika cichlidlari", "emoji": "🌍", "description": "Malavi, Tanganika va Viktoriya ko'llari cichlidlari", "sort_order": 1},
        {"name": "Amerika cichlidlari", "emoji": "🌎", "description": "Janubiy, Markaziy va Shimoliy Amerika cichlidlari", "sort_order": 2},
        {"name": "Diskuslar", "emoji": "👑", "description": "Symphysodon jinsiga mansub akvarium qirollari", "sort_order": 3},
        {"name": "Boshqa chuchuk suv baliqlari", "emoji": "🐟", "description": "Tetralar, barbuslar, tirik tug'uvchilar, somlar va boshqalar", "sort_order": 4},
    ]
    category_map = {}
    for cat in categories_data:
        res = await session.execute(select(Category).where(Category.name == cat["name"]))
        existing = res.scalar_one_or_none()
        if not existing:
            c = Category(**cat)
            session.add(c)
            await session.flush()
            category_map[cat["name"]] = c.id
        else:
            category_map[cat["name"]] = existing.id

    # Subcategories
    # African
    african_cat_id = category_map["Afrika cichlidlari"]
    subcategories_data = [
        # Malawi
        {"name": "Mbuna", "emoji": "🪨", "category_id": african_cat_id, "description": "Qoyali hudud baliqlari, o'txo'r va baquvvat xulqli"},
        {"name": "Haps", "emoji": "🌊", "category_id": african_cat_id, "description": "Ochiq suv baliqlari, yirikroq va yirtqichroq"},
        {"name": "Aulonocara", "emoji": "🦚", "category_id": african_cat_id, "description": "Tovus cichlidlari (Peacock), yorqin metall tusli ranglar"},
        {"name": "Utaka", "emoji": "🐟", "category_id": african_cat_id, "description": "Planktontxo'r qoyali ochiq suv guruhlari"},
        {"name": "Other Malawi", "emoji": "🇲🇼", "category_id": african_cat_id, "description": "Boshqa Malavi ko'li turlari"},
        # Tanganyika
        {"name": "Shell Dwellers", "emoji": "🐚", "category_id": african_cat_id, "description": "Chig'anoq ichida yashovchi mitti cichlidlar"},
        {"name": "Julidochromis", "emoji": "🦓", "category_id": african_cat_id, "description": "Qoyali tirqishlarda yashovchi nafis chiziqli turlar"},
        {"name": "Neolamprologus", "emoji": "🏰", "category_id": african_cat_id, "description": "Murakkab ijtimoiy oilaviy tuzilmali g'or baliqlari"},
        {"name": "Altolamprologus", "emoji": "🗡️", "category_id": african_cat_id, "description": "Yassi tanali, qoya tirqishlari ovchilari"},
        {"name": "Cyphotilapia", "emoji": "👑", "category_id": african_cat_id, "description": "Frontosa va Gibberosa — chuqur suv qirollari"},
        {"name": "Tropheus", "emoji": "🌿", "category_id": african_cat_id, "description": "Maxsus alg oziqli, jamoaviy qattiq ierarxiyali turlar"},
        {"name": "Xenotilapia", "emoji": "🏖️", "category_id": african_cat_id, "description": "Qumloq hudud qum elovchi cichlidlari"},
        {"name": "Calvus", "emoji": "🗿", "category_id": african_cat_id, "description": "Altolamprologus calvus variatsiyalari"},
        {"name": "Other Tanganyika", "emoji": "🇹🇿", "category_id": african_cat_id, "description": "Boshqa Tanganika turlari"},
        # Victoria & Other Africa
        {"name": "Victoria", "emoji": "🇺🇬", "category_id": african_cat_id, "description": "Viktoriya ko'li endemik yorqin cichlidlari"},
        {"name": "Other Africa", "emoji": "🌍", "category_id": african_cat_id, "description": "Daryo va g'arbiy Afrika cichlidlari (Pelvicachromis, Hemichromis)"},
        # American
        {"name": "North", "emoji": "🇺🇸", "category_id": category_map["Amerika cichlidlari"], "description": "Shimoliy Amerika cichlidlari"},
        {"name": "Central", "emoji": "🌎", "category_id": category_map["Amerika cichlidlari"], "description": "Markaziy Amerika cichlidlari"},
        {"name": "South", "emoji": "🇧🇷", "category_id": category_map["Amerika cichlidlari"], "description": "Janubiy Amerika cichlidlari (Skalyariya, Apistogramma, Astronotus)"},
        # Discus
        {"name": "Wild Discus", "emoji": "🌿", "category_id": category_map["Diskuslar"], "description": "Tabiiy yovvoyi diskus turlari (Heckel, Tarzoo, Haraldi)"},
        {"name": "Selective Discus", "emoji": "🧬", "category_id": category_map["Diskuslar"], "description": "Selektsiya qilingan chiziqlar (Pigeon Blood, Snake Skin)"},
        {"name": "Color Form Discus", "emoji": "🎨", "category_id": category_map["Diskuslar"], "description": "Rangli morflar va mutatsiyalar"},
        # Other Freshwater
        {"name": "Tetralar", "emoji": "✨", "category_id": category_map["Boshqa chuchuk suv baliqlari"], "description": "Characidae oilasi mayda gala baliqlari"},
        {"name": "Barbusslar", "emoji": "⚡", "category_id": category_map["Boshqa chuchuk suv baliqlari"], "description": "Cyprinidae barbuslari"},
        {"name": "Rasboralar", "emoji": "🌟", "category_id": category_map["Boshqa chuchuk suv baliqlari"], "description": "Rasboralar va Danio turlari"},
        {"name": "Guramis", "emoji": "🎐", "category_id": category_map["Boshqa chuchuk suv baliqlari"], "description": "Labirintli guramilar"},
        {"name": "Bettalar", "emoji": "🥊", "category_id": category_map["Boshqa chuchuk suv baliqlari"], "description": "Jangovar Betta turlari"},
        {"name": "Livebearers", "emoji": "👶", "category_id": category_map["Boshqa chuchuk suv baliqlari"], "description": "Guppi, mechenosets, molliya, petsiliya"},
        {"name": "Catfish", "emoji": "🐱", "category_id": category_map["Boshqa chuchuk suv baliqlari"], "description": "Koridoraslar va tub somlari"},
        {"name": "Plecos", "emoji": "🪵", "category_id": category_map["Boshqa chuchuk suv baliqlari"], "description": "Loricariidae zanjirli yopishqoq somlar"},
        {"name": "Loaches", "emoji": "🍜", "category_id": category_map["Boshqa chuchuk suv baliqlari"], "description": "Botiyalar va vyunlar"},
        {"name": "Rainbowfish", "emoji": "🌈", "category_id": category_map["Boshqa chuchuk suv baliqlari"], "description": "Kamalak baliqlari (Melanotaeniidae)"},
        {"name": "Killifish", "emoji": "💎", "category_id": category_map["Boshqa chuchuk suv baliqlari"], "description": "Mavsumiy va nodir killifish turlari"},
        {"name": "Knife Fish", "emoji": "🗡️", "category_id": category_map["Boshqa chuchuk suv baliqlari"], "description": "Pichoq baliqlar"},
        {"name": "Arowana", "emoji": "🐉", "category_id": category_map["Boshqa chuchuk suv baliqlari"], "description": "Aravanalar"},
        {"name": "Bichirs", "emoji": "🐊", "category_id": category_map["Boshqa chuchuk suv baliqlari"], "description": "Polipterus ko'p patlilari"},
        {"name": "Krevetkalar", "emoji": "🦐", "category_id": category_map["Boshqa chuchuk suv baliqlari"], "description": "Neocaridina, Caridina chuchuk suv krevetkalari"},
        {"name": "Mollyuskalar", "emoji": "🐌", "category_id": category_map["Boshqa chuchuk suv baliqlari"], "description": "Ampulyariya, Neritina shilliqqurtlari"},
        {"name": "Boshqa turlar", "emoji": "🐠", "category_id": category_map["Boshqa chuchuk suv baliqlari"], "description": "Boshqa barcha chuchuk suv jonivorlari"},
    ]

    subcategory_map = {}
    for sub in subcategories_data:
        res = await session.execute(select(Subcategory).where(Subcategory.name == sub["name"]))
        existing = res.scalar_one_or_none()
        if not existing:
            s = Subcategory(**sub)
            session.add(s)
            await session.flush()
            subcategory_map[sub["name"]] = s
        else:
            subcategory_map[sub["name"]] = existing

    # Families
    families_data = [
        {"scientific_name": "Cichlidae", "common_name": "Cichlidlar", "description": "Eng boy va rang-barang chuchuk suv baliqlari oilasi"},
        {"scientific_name": "Characidae", "common_name": "Xaratsidlar", "description": "Janubiy va Markaziy Amerika tetralari"},
        {"scientific_name": "Cyprinidae", "common_name": "Karpasimonlar", "description": "Barbuslar, rasboralar va karplar"},
        {"scientific_name": "Danionidae", "common_name": "Daniolar", "description": "Daniolar va mayda Osiyo shoxchali baliqlari"},
        {"scientific_name": "Osphronemidae", "common_name": "Guramisimonlar", "description": "Labirint a'zoli havo nafas oluvchi turlar"},
        {"scientific_name": "Callichthyidae", "common_name": "Qalqonli somlar", "description": "Koridoraslar va zirhli tinch somlar"},
        {"scientific_name": "Loricariidae", "common_name": "Zanjirli somlar", "description": "Pleko va antsistrus yopishqoq somlari"},
        {"scientific_name": "Poeciliidae", "common_name": "Pestiliyasimonlar", "description": "Tirik tug'uvchi go'zal mayda baliqlar"},
        {"scientific_name": "Cobitidae", "common_name": "Vyunsimonlar", "description": "Botiyalar va tub baliqlari"},
        {"scientific_name": "Melanotaeniidae", "common_name": "Kamalaksimonlar", "description": "Avstraliya va Yangi Gvineya kamalak baliqlari"},
        {"scientific_name": "Nothobranchiidae", "common_name": "Notobranxiylar", "description": "Afrika killifishlari"},
        {"scientific_name": "Atyidae", "common_name": "Chuchuk suv krevetkalari", "description": "Mayda o'simlik tozalovchi krevetkalar"},
        {"scientific_name": "Ampullariidae", "common_name": "Ampulyariyalar", "description": "Yirik akvarium shilliqqurtlari"},
    ]
    family_map = {}
    for f in families_data:
        res = await session.execute(select(Family).where(Family.scientific_name == f["scientific_name"]))
        existing = res.scalar_one_or_none()
        if not existing:
            fam = Family(**f)
            session.add(fam)
            await session.flush()
            family_map[f["scientific_name"]] = fam.id
        else:
            family_map[f["scientific_name"]] = existing.id

    # Genera
    genera_data = [
        # African Cichlids
        {"scientific_name": "Pseudotropheus", "family_id": family_map["Cichlidae"], "common_name": "Psevdotsvet"},
        {"scientific_name": "Labidochromis", "family_id": family_map["Cichlidae"], "common_name": "Labidoxromis"},
        {"scientific_name": "Metriaclima", "family_id": family_map["Cichlidae"], "common_name": "Metriaklima"},
        {"scientific_name": "Chindongo", "family_id": family_map["Cichlidae"], "common_name": "Chindongo"},
        {"scientific_name": "Cyrtocara", "family_id": family_map["Cichlidae"], "common_name": "Tsirtokara"},
        {"scientific_name": "Nimbochromis", "family_id": family_map["Cichlidae"], "common_name": "Nimboxromis"},
        {"scientific_name": "Sciaenochromis", "family_id": family_map["Cichlidae"], "common_name": "Stsienoxromis"},
        {"scientific_name": "Aulonocara", "family_id": family_map["Cichlidae"], "common_name": "Aulonokara"},
        {"scientific_name": "Copadichromis", "family_id": family_map["Cichlidae"], "common_name": "Kopadixromis"},
        {"scientific_name": "Protomelas", "family_id": family_map["Cichlidae"], "common_name": "Protomelas"},
        {"scientific_name": "Neolamprologus", "family_id": family_map["Cichlidae"], "common_name": "Neolamprologus"},
        {"scientific_name": "Lamprologus", "family_id": family_map["Cichlidae"], "common_name": "Lamprologus"},
        {"scientific_name": "Julidochromis", "family_id": family_map["Cichlidae"], "common_name": "Yulidoxromis"},
        {"scientific_name": "Altolamprologus", "family_id": family_map["Cichlidae"], "common_name": "Altolamprologus"},
        {"scientific_name": "Cyphotilapia", "family_id": family_map["Cichlidae"], "common_name": "Tsifotilapiya"},
        {"scientific_name": "Tropheus", "family_id": family_map["Cichlidae"], "common_name": "Trofeus"},
        {"scientific_name": "Xenotilapia", "family_id": family_map["Cichlidae"], "common_name": "Ksenotilapiya"},
        {"scientific_name": "Haplochromis", "family_id": family_map["Cichlidae"], "common_name": "Xaploxromis"},
        {"scientific_name": "Pundamilia", "family_id": family_map["Cichlidae"], "common_name": "Pundamiliya"},
        {"scientific_name": "Pelvicachromis", "family_id": family_map["Cichlidae"], "common_name": "Pelvikaxromis"},
        # American Cichlids & Discus
        {"scientific_name": "Pterophyllum", "family_id": family_map["Cichlidae"], "common_name": "Skalyariya"},
        {"scientific_name": "Symphysodon", "family_id": family_map["Cichlidae"], "common_name": "Diskus"},
        {"scientific_name": "Mikrogeophagus", "family_id": family_map["Cichlidae"], "common_name": "Mikrogeofagus"},
        {"scientific_name": "Apistogramma", "family_id": family_map["Cichlidae"], "common_name": "Apistogramma"},
        {"scientific_name": "Astronotus", "family_id": family_map["Cichlidae"], "common_name": "Astronotus"},
        {"scientific_name": "Thorichthys", "family_id": family_map["Cichlidae"], "common_name": "Torixtis"},
        {"scientific_name": "Amatitlania", "family_id": family_map["Cichlidae"], "common_name": "Amatitlaniya"},
        {"scientific_name": "Herichthys", "family_id": family_map["Cichlidae"], "common_name": "Gerixtis"},
        {"scientific_name": "Vieja", "family_id": family_map["Cichlidae"], "common_name": "Viexa"},
        # Other Freshwater
        {"scientific_name": "Paracheirodon", "family_id": family_map["Characidae"], "common_name": "Paraxeyrodon"},
        {"scientific_name": "Hyphessobrycon", "family_id": family_map["Characidae"], "common_name": "Xifessobrikon"},
        {"scientific_name": "Phenacogrammus", "family_id": family_map["Characidae"], "common_name": "Fenakogrammus"},
        {"scientific_name": "Puntigrus", "family_id": family_map["Cyprinidae"], "common_name": "Puntigrus"},
        {"scientific_name": "Sahyadria", "family_id": family_map["Cyprinidae"], "common_name": "Saxiyadriya"},
        {"scientific_name": "Trigonostigma", "family_id": family_map["Danionidae"], "common_name": "Trigonostigma"},
        {"scientific_name": "Danio", "family_id": family_map["Danionidae"], "common_name": "Danio"},
        {"scientific_name": "Betta", "family_id": family_map["Osphronemidae"], "common_name": "Betta"},
        {"scientific_name": "Trichogaster", "family_id": family_map["Osphronemidae"], "common_name": "Trixogaster"},
        {"scientific_name": "Trichopodus", "family_id": family_map["Osphronemidae"], "common_name": "Trixopodus"},
        {"scientific_name": "Corydoras", "family_id": family_map["Callichthyidae"], "common_name": "Koridoras"},
        {"scientific_name": "Ancistrus", "family_id": family_map["Loricariidae"], "common_name": "Antsistrus"},
        {"scientific_name": "Hypancistrus", "family_id": family_map["Loricariidae"], "common_name": "Gipantsistrus"},
        {"scientific_name": "Poecilia", "family_id": family_map["Poeciliidae"], "common_name": "Petsiliya"},
        {"scientific_name": "Xiphophorus", "family_id": family_map["Poeciliidae"], "common_name": "Ksifoforus"},
        {"scientific_name": "Chromobotia", "family_id": family_map["Cobitidae"], "common_name": "Xromobotiya"},
        {"scientific_name": "Pangio", "family_id": family_map["Cobitidae"], "common_name": "Pangio"},
        {"scientific_name": "Melanotaenia", "family_id": family_map["Melanotaeniidae"], "common_name": "Melanoteniya"},
        {"scientific_name": "Aphyosemion", "family_id": family_map["Nothobranchiidae"], "common_name": "Afiosemion"},
        {"scientific_name": "Neocaridina", "family_id": family_map["Atyidae"], "common_name": "Neokaridina"},
        {"scientific_name": "Caridina", "family_id": family_map["Atyidae"], "common_name": "Karidina"},
        {"scientific_name": "Pomacea", "family_id": family_map["Ampullariidae"], "common_name": "Pomatseya"},
    ]
    genus_map = {}
    for g in genera_data:
        res = await session.execute(select(Genus).where(Genus.scientific_name == g["scientific_name"]))
        existing = res.scalar_one_or_none()
        if not existing:
            gen = Genus(**g)
            session.add(gen)
            await session.flush()
            genus_map[g["scientific_name"]] = gen.id
        else:
            genus_map[g["scientific_name"]] = existing.id

    return {
        "categories": category_map,
        "subcategories": subcategory_map,
        "families": family_map,
        "genera": genus_map,
    }


async def seed_species(session: AsyncSession, taxonomy: dict) -> None:
    """Seed comprehensive fish species catalog."""
    logger.info("Seeding fish species catalog...")

    genera = taxonomy["genera"]
    subcategories = taxonomy["subcategories"]

    species_catalog = [
        # ── 1. MALAWI MBUNA ────────────────────────────────────────────────
        {
            "scientific_name": "Pseudotropheus demasoni",
            "genus_id": genera["Pseudotropheus"],
            "author": "Konings",
            "year_described": 1994,
            "origin_type": OriginType.WILD,
            "water_type": WaterType.FRESHWATER,
            "max_size_cm": 7.5,
            "body_shape": "Cho'ziq, tor silindrsimon, qoyalar orasida epchil harakatlanuvchi",
            "coloration": "To'q ko'k va och feruza-moviy vertikal chiziqlar, tiniq kontrast",
            "sexual_dimorphism": "Erkak va urg'ochi rangi deyarli bir xil, erkaklari kattaroq va do'ng peshonali",
            "temp_min": 24.0, "temp_max": 28.0,
            "ph_min": 7.8, "ph_max": 8.6,
            "gh_min": 10.0, "gh_max": 20.0,
            "kh_min": 8.0, "kh_max": 14.0,
            "min_tank_liters": 150, "recommended_tank_liters": 200,
            "group_size_min": 12, "group_size_recommended": "12-15 ta (tajovuzkorlikni tarqatish uchun ko'p sonli)",
            "aggression": AggressionLevel.AGGRESSIVE,
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "diet_description": "Aufwuchs (qoya usti suv o'tlari) va o'simlik tolalari asosiy ratsion",
            "diet_plant": "Spirulina, nori, o'simlik granullalari",
            "diet_protein": "Protein miqdori past bo'lishi shart! Ko'p protein bloat keltirib chiqaradi",
            "breeding_type": BreedingType.MOUTHBROODER,
            "breeding_description": "Onasi tuxumlarni og'zida 21-25 kun davomida saqlaydi (Mouthbrooding)",
            "fry_care": "Chavoqlar erkin suza boshlagach, maydalangan spirulina bilan oziqlanadi",
            "natural_habitat": "Malavi ko'li, Pombo Rocks va Ndumbi Rocks qoyali biotopi",
            "important_note": "Oqsilga boy ovqat bersangiz Malavi Bloat (qorin shishi) yuzaga keladi. Faqat o'simlik ovqati bering!",
            "reliability": ReliabilityLevel.SCIENTIFIC,
            "is_published": True,
            "subcat_names": ["Mbuna"],
            "common_names": [
                ("Demasoni cichlidasi", "uz"),
                ("Demasoni cichlid", "en"),
                ("Псевдотрофеус демасони", "ru"),
            ],
            "synonyms": [("Pseudotropheus demasoni Konings, 1994", "Dastlabki ilmiy tavsif")],
            "trade_names": ["Demasoni Malawi Cichlid", "Pombo Dwarf Cichlid"],
        },
        {
            "scientific_name": "Labidochromis caeruleus",
            "genus_id": genera["Labidochromis"],
            "author": "Fryer",
            "year_described": 1956,
            "origin_type": OriginType.WILD,
            "water_type": WaterType.FRESHWATER,
            "max_size_cm": 10.0,
            "body_shape": "Yon tomondan siqilgan, chaqqon va chiroyli siluet",
            "coloration": "Yorqin quyoshli sariq tana, orqa va qorin suzgichlarida qora chiziq",
            "sexual_dimorphism": "Erkaklarda qora chiziq to'qroq va orqa suzgich uchi o'tkirroq",
            "temp_min": 23.0, "temp_max": 27.0,
            "ph_min": 7.6, "ph_max": 8.6,
            "gh_min": 10.0, "gh_max": 22.0,
            "kh_min": 7.0, "kh_max": 14.0,
            "min_tank_liters": 120, "recommended_tank_liters": 180,
            "group_size_min": 4, "group_size_recommended": "1 erkak va 3-4 urg'ochi (garem)",
            "aggression": AggressionLevel.SEMI_AGGRESSIVE,
            "difficulty": DifficultyLevel.BEGINNER,
            "diet_description": "Har xil oziqlanuvchi (omnivore) — hasharot lichinkalari, mayda umurtqasizlar va suv o'tlari",
            "diet_plant": "Spirulina, o'simlik parchalari",
            "diet_protein": "Artemiya, sifatli siklop va siklid granulalari",
            "breeding_type": BreedingType.MOUTHBROODER,
            "breeding_description": "Urg'ochisi 15-30 ta tuxumni og'zida 3-4 hafta davomida inkubatsiya qiladi",
            "fry_care": "Boshlang'ich davrda artemiya naulpliyalari va maydalangan quruq ovqat",
            "natural_habitat": "Malavi ko'li, Lion's Cove va Ruarwe sohillari, chuqur qoyali hududlar",
            "important_note": "Mbuna guruhidagi eng tinch va yangi boshlovchilar uchun ideal cichlida turi.",
            "reliability": ReliabilityLevel.SCIENTIFIC,
            "is_published": True,
            "subcat_names": ["Mbuna"],
            "common_names": [
                ("Sariq labidochromis", "uz"),
                ("Yellow Lab", "en"),
                ("Electric Yellow Cichlid", "en"),
                ("Еллоу / Лабидохромис желтый", "ru"),
            ],
            "synonyms": [],
            "trade_names": ["Electric Yellow", "Yellow Labido", "Kakusa Cichlid"],
        },
        {
            "scientific_name": "Metriaclima lombardoi",
            "genus_id": genera["Metriaclima"],
            "author": "Burgess",
            "year_described": 1977,
            "origin_type": OriginType.WILD,
            "water_type": WaterType.FRESHWATER,
            "max_size_cm": 13.0,
            "body_shape": "Kuchli, mushakdor, baland tanali mbuna",
            "coloration": "Juda noyob teskari dimorfizm: erkaklar sarg'ish-oltin, urg'ochilar esa havorang-ko'k qora chiziqli",
            "sexual_dimorphism": "Erkaklari sariq/to'q sariq, urg'ochilari ko'k rangda",
            "temp_min": 24.0, "temp_max": 28.0,
            "ph_min": 7.8, "ph_max": 8.6,
            "gh_min": 12.0, "gh_max": 25.0,
            "kh_min": 8.0, "kh_max": 15.0,
            "min_tank_liters": 250, "recommended_tank_liters": 350,
            "group_size_min": 5, "group_size_recommended": "1 erkak, 4-6 urg'ochi",
            "aggression": AggressionLevel.HIGHLY_AGGRESSIVE,
            "difficulty": DifficultyLevel.ADVANCED,
            "diet_description": "O'txo'r mbuna, suv o'tlari va mikroskopik jonivorlar",
            "diet_plant": "Spirulina, xlorella, o'simlik barglari",
            "diet_protein": "Minimal darajada",
            "breeding_type": BreedingType.MOUTHBROODER,
            "breeding_description": "Erkak baliq qoya ostidagi qumni tozalab hududni qattiq himoya qiladi",
            "fry_care": "Onasining og'zidan chiqqanidan so'ng alohida o'stirish tavsiya etiladi",
            "natural_habitat": "Malavi ko'li, Mbenji oroli va Nkhomo Reef",
            "important_note": "O'ta agressiv hududiy xulq-atvorga ega, kichik akvariumlarga qat'iyan tavsiya etilmaydi.",
            "reliability": ReliabilityLevel.SCIENTIFIC,
            "is_published": True,
            "subcat_names": ["Mbuna"],
            "common_names": [
                ("Lombardoi cichlidasi", "uz"),
                ("Kenyi Cichlid", "en"),
                ("Lombardoi", "en"),
                ("Псевдотрофеус ломбардо", "ru"),
            ],
            "synonyms": [("Pseudotropheus lombardoi", "Eski klassifikatsiya")],
            "trade_names": ["Kenyi", "Lombardoi Mbuna"],
        },
        {
            "scientific_name": "Chindongo saulosi",
            "genus_id": genera["Chindongo"],
            "author": "Konings",
            "year_described": 1990,
            "origin_type": OriginType.WILD,
            "water_type": WaterType.FRESHWATER,
            "max_size_cm": 8.5,
            "body_shape": "Mitti, ixcham va faol tana",
            "coloration": "Erkaklari to'q ko'k va qora chiziqli, urg'ochilari yorqin sariq",
            "sexual_dimorphism": "Keskin rang farqi: erkak ko'k-qora, urg'ochi sariq",
            "temp_min": 24.0, "temp_max": 27.5,
            "ph_min": 7.8, "ph_max": 8.6,
            "gh_min": 10.0, "gh_max": 20.0,
            "kh_min": 8.0, "kh_max": 14.0,
            "min_tank_liters": 150, "recommended_tank_liters": 200,
            "group_size_min": 6, "group_size_recommended": "2 erkak va 6-8 urg'ochi",
            "aggression": AggressionLevel.SEMI_AGGRESSIVE,
            "difficulty": DifficultyLevel.BEGINNER,
            "diet_description": "Aufwuchs va o'simlik asosli oziqa",
            "diet_plant": "Spirulina granulalari, sabzavotlar",
            "diet_protein": "Haftada 1 marta yengil dafniya yoki artemiya",
            "breeding_type": BreedingType.MOUTHBROODER,
            "breeding_description": "Urg'ochisi 21 kun davomida og'zida saqlaydi",
            "fry_care": "Boshlang'ich ozuqa maydalangan spirulina",
            "natural_habitat": "Malavi ko'li, Taiwanee Reef, kuchli oqimli qoyalar",
            "important_note": "Mitti hajmiga qaramay juda jozibali, erkak va urg'ochi rangi qarama-qarshiligi ajoyib ko'rinish beradi.",
            "reliability": ReliabilityLevel.SCIENTIFIC,
            "is_published": True,
            "subcat_names": ["Mbuna"],
            "common_names": [
                ("Saulosi cichlidasi", "uz"),
                ("Dwarf Mbuna Saulosi", "en"),
                ("Псевдотрофеус саулози", "ru"),
            ],
            "synonyms": [("Pseudotropheus saulosi", "Avvalgi nomi")],
            "trade_names": ["Saulosi Dwarf Cichlid"],
        },

        # ── 2. MALAWI PEACOCKS & HAPS ──────────────────────────────────────
        {
            "scientific_name": "Aulonocara baenschi",
            "genus_id": genera["Aulonocara"],
            "author": "Meyer & Riehl",
            "year_described": 1985,
            "origin_type": OriginType.WILD,
            "water_type": WaterType.FRESHWATER,
            "max_size_cm": 13.0,
            "body_shape": "Nafis, yondan siqilgan, katta ko'zlar va nozik sezgir teshiklar (lateral line)",
            "coloration": "Erkaklar yorqin metalldek sariq-oltin, boshi va yonoqlari feruza ko'k",
            "sexual_dimorphism": "Erkaklar juda yorqin rangda, urg'ochilar oddiy kulrang-jigarrang",
            "temp_min": 24.0, "temp_max": 28.0,
            "ph_min": 7.6, "ph_max": 8.6,
            "gh_min": 10.0, "gh_max": 20.0,
            "kh_min": 7.0, "kh_max": 12.0,
            "min_tank_liters": 200, "recommended_tank_liters": 300,
            "group_size_min": 4, "group_size_recommended": "1 erkak, 3 urg'ochi",
            "aggression": AggressionLevel.PEACEFUL,
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "diet_description": "Yirtqich/planktontxo'r — qum tubidagi umurtqasizlarni quloq va sezgi a'zolari bilan qidiradi",
            "diet_plant": "O'simlik qo'shimchali granulalar",
            "diet_protein": "Sifatli artemiya, siklop, mysis, mayda krevetka",
            "breeding_type": BreedingType.MOUTHBROODER,
            "breeding_description": "Urg'ochisi 20-40 ta tuxumni og'zida 3 hafta ushlaydi",
            "fry_care": "Yangi chiqqan chavoqlarga yangi ochilgan artemiya naulpliyasi",
            "natural_habitat": "Malavi ko'li, Nkhomo Reef, qum va qoya chegarasidagi oraliq zona",
            "important_note": "Agressiv Mbuna bilan birga saqlamang! Nozik Aulonocara stressdan rangini yo'qotadi.",
            "reliability": ReliabilityLevel.SCIENTIFIC,
            "is_published": True,
            "subcat_names": ["Aulonocara"],
            "common_names": [
                ("Sariq Aulonokara (Bensh)", "uz"),
                ("Benga Peacock", "en"),
                ("Sunshine Peacock", "en"),
                ("Аулонокара бенша", "ru"),
            ],
            "synonyms": [],
            "trade_names": ["Sunshine Peacock", "Yellow Regal Peacock"],
        },
        {
            "scientific_name": "Sciaenochromis fryeri",
            "genus_id": genera["Sciaenochromis"],
            "author": "Konings",
            "year_described": 1993,
            "origin_type": OriginType.WILD,
            "water_type": WaterType.FRESHWATER,
            "max_size_cm": 16.0,
            "body_shape": "Tor, cho'zilgan torpeda shakli, kuchli yirtqich suzuvchi",
            "coloration": "Erkaklar nihoyatda to'yingan elektr-ko'k, orqa suzgichida oq yoki olovrang chiziq",
            "sexual_dimorphism": "Erkaklar to'q elektr ko'k, urg'ochilar kulrang-kumush",
            "temp_min": 24.0, "temp_max": 28.0,
            "ph_min": 7.8, "ph_max": 8.6,
            "gh_min": 10.0, "gh_max": 22.0,
            "kh_min": 8.0, "kh_max": 14.0,
            "min_tank_liters": 300, "recommended_tank_liters": 450,
            "group_size_min": 3, "group_size_recommended": "1 erkak, 2-3 urg'ochi",
            "aggression": AggressionLevel.SEMI_AGGRESSIVE,
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "diet_description": "Tabiatda baliqxo'r yirtqich (chavoqlarni ovlaydi)",
            "diet_plant": "Spirulina qo'shimchasi",
            "diet_protein": "Go'shtdor baliq ovqatlari, artemiya, krill, mayda baliq filesi",
            "breeding_type": BreedingType.MOUTHBROODER,
            "breeding_description": "Qoyali tekislikda juftlashadi, urg'ochi tuxumlarni og'ziga oladi",
            "fry_care": "Chavoqlari tez o'sadi, artemiya bilan boqiladi",
            "natural_habitat": "Malavi ko'li bo'ylab qoyali va oraliq biotoplar",
            "important_note": "Ajoyib 'Elektr ko'k' rangi bilan mashhur, katta hajmli akvarium talab qiladi.",
            "reliability": ReliabilityLevel.SCIENTIFIC,
            "is_published": True,
            "subcat_names": ["Haps"],
            "common_names": [
                ("Elektr ko'k stsiyenoxromis", "uz"),
                ("Electric Blue Hap", "en"),
                ("Васильковый хаплохромис", "ru"),
            ],
            "synonyms": [("Haplochromis fryeri", "Eski nom")],
            "trade_names": ["Electric Blue Fryeri", "Iceberg Fryeri"],
        },
        {
            "scientific_name": "Cyrtocara moorii",
            "genus_id": genera["Cyrtocara"],
            "author": "Boulenger",
            "year_described": 1902,
            "origin_type": OriginType.WILD,
            "water_type": WaterType.FRESHWATER,
            "max_size_cm": 22.0,
            "body_shape": "Yirik, qalin tanali, yoshi ulg'aygach peshonasida ulkan yog'li do'ng (shish) paydo bo'ladi",
            "coloration": "Yumshoq metall feruza-ko'k, baxmaldek jilo",
            "sexual_dimorphism": "Ikkala jins ham ko'k, lekin erkaklarda peshona do'ngi kattaroq bo'ladi",
            "temp_min": 24.0, "temp_max": 27.5,
            "ph_min": 7.8, "ph_max": 8.6,
            "gh_min": 10.0, "gh_max": 20.0,
            "kh_min": 8.0, "kh_max": 14.0,
            "min_tank_liters": 450, "recommended_tank_liters": 600,
            "group_size_min": 4, "group_size_recommended": "1 erkak, 3-4 urg'ochi",
            "aggression": AggressionLevel.PEACEFUL,
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "diet_description": "Qum elovchi yirik cichlida, boshqa baliqlar qo'zg'atgan substrat qoldiqlarini teradi",
            "diet_plant": "O'simlik granulalari",
            "diet_protein": "Artemiya, krill, maxsus cichlid granulalari",
            "breeding_type": BreedingType.MOUTHBROODER,
            "breeding_description": "Qumda chuqurcha qazib juftlashadi, onasi og'zida saqlaydi",
            "fry_care": "Chavoqlari yirik bo'lib tug'iladi",
            "natural_habitat": "Malavi ko'lining sayoz qumloq sohillari",
            "important_note": "Moviy delfin deb nomlanadi. Katta akvarium va mayin qum qoplamasi shart.",
            "reliability": ReliabilityLevel.SCIENTIFIC,
            "is_published": True,
            "subcat_names": ["Haps"],
            "common_names": [
                ("Moviy delfin cichlidasi", "uz"),
                ("Blue Dolphin Cichlid", "en"),
                ("Голубой дельфин", "ru"),
            ],
            "synonyms": [("Haplochromis moorii", "Boulenger 1902")],
            "trade_names": ["Malawi Blue Dolphin", "Moorii Cichlid"],
        },

        # ── 3. TANGANYIKA CICHLIDS ─────────────────────────────────────────
        {
            "scientific_name": "Neolamprologus multifasciatus",
            "genus_id": genera["Neolamprologus"],
            "author": "Pellegrin",
            "year_described": 1904,
            "origin_type": OriginType.WILD,
            "water_type": WaterType.FRESHWATER,
            "max_size_cm": 4.5,
            "body_shape": "Dunyodagi eng mitti cichlidlardan biri, ixcham silindrsimon",
            "coloration": "Och qaymoqrang fonda ko'plab ingichka jigarrang vertikal chiziqlar, ko'zlari feruza jiloli",
            "sexual_dimorphism": "Erkaklar 4-4.5 sm, urg'ochilar esa atigi 2.5-3 sm",
            "temp_min": 24.0, "temp_max": 27.5,
            "ph_min": 8.0, "ph_max": 9.0,
            "gh_min": 12.0, "gh_max": 25.0,
            "kh_min": 10.0, "kh_max": 18.0,
            "min_tank_liters": 50, "recommended_tank_liters": 80,
            "group_size_min": 6, "group_size_recommended": "Mustamlakachilik (koloniya) tarzida 6-12 ta",
            "aggression": AggressionLevel.SEMI_AGGRESSIVE,
            "difficulty": DifficultyLevel.BEGINNER,
            "diet_description": "Mayda plankton, hasharot lichinkalari va artemiya",
            "diet_plant": "Spirulina tolali mayda donalar",
            "diet_protein": "Siklop, yangi ochilgan artemiya, dafniya",
            "breeding_type": BreedingType.SHELL_SPAWNER,
            "breeding_description": "Urg'ochisi Neothauma chig'anog'i ichiga tuxum qo'yadi va ichida yashaydi",
            "fry_care": "Chavoqlar chig'anoq atrofida butun koloniya himoyasida bo'ladi",
            "natural_habitat": "Tanganika ko'li, Neothauma chig'anoqlarining ulkan maydonlari",
            "important_note": "Ulkan qum quruvchilar! Bir necha kunda butun akvarium landshaftini o'zgartirib tashlaydi.",
            "reliability": ReliabilityLevel.SCIENTIFIC,
            "is_published": True,
            "subcat_names": ["Shell Dwellers"],
            "common_names": [
                ("Mitti chig'anoq cichlidasi (Multifassiatus)", "uz"),
                ("Many-banded Shellie", "en"),
                ("Multies", "en"),
                ("Многополосый ракушковый лампрологус", "ru"),
            ],
            "synonyms": [],
            "trade_names": ["Multifasciatus Shell Dweller", "Multies Shellie"],
        },
        {
            "scientific_name": "Cyphotilapia frontosa",
            "genus_id": genera["Cyphotilapia"],
            "author": "Boulenger",
            "year_described": 1906,
            "origin_type": OriginType.WILD,
            "water_type": WaterType.FRESHWATER,
            "max_size_cm": 35.0,
            "body_shape": "Ulkan, mahobatli, baland tanali, ulkan boshli va yirik yog'li do'ngli",
            "coloration": "Oq/och kulrang fonda 6 ta to'q qora vertikal qalin chiziq, moviy suzgichlar",
            "sexual_dimorphism": "Erkaklar ancha yirik va ulkan nuchal hump (bosh do'ngi)ga ega",
            "temp_min": 23.0, "temp_max": 27.0,
            "ph_min": 8.0, "ph_max": 9.2,
            "gh_min": 12.0, "gh_max": 25.0,
            "kh_min": 10.0, "kh_max": 18.0,
            "min_tank_liters": 500, "recommended_tank_liters": 800,
            "group_size_min": 5, "group_size_recommended": "1 erkak, 4-5 urg'ochi (guruh bo'lib yashaydi)",
            "aggression": AggressionLevel.SEMI_AGGRESSIVE,
            "difficulty": DifficultyLevel.ADVANCED,
            "diet_description": "Yirtqich — mayda baliqlar, chuqur suv mollyuskalari va qisqichbaqasimonlar",
            "diet_plant": "Qo'shimcha sifatida",
            "diet_protein": "Krevetka go'shti, midiya, krill, sifatli yirik granulalar",
            "breeding_type": BreedingType.MOUTHBROODER,
            "breeding_description": "Onasi kam miqdordagi (20-50 ta) juda yirik tuxumlarni 4-5 hafta og'zida boqadi",
            "fry_care": "Tug'ilgan chavoqlari allaqachon 2 sm kattalikda bo'ladi",
            "natural_habitat": "Tanganika ko'lining 20-50 metrli chuqur sovuqroq qatlamlari",
            "important_note": "Vaqorli va xotirjam gigant. Shoshqaloqlikni va yorug' o'tkir nurni yoqtirmaydi.",
            "reliability": ReliabilityLevel.SCIENTIFIC,
            "is_published": True,
            "subcat_names": ["Cyphotilapia"],
            "common_names": [
                ("Frontosa", "uz"),
                ("Frontosa Cichlid", "en"),
                ("Фронтоза", "ru"),
            ],
            "synonyms": [],
            "trade_names": ["Frontosa 6-stripe", "Kigoma Frontosa"],
        },
        {
            "scientific_name": "Tropheus moorii",
            "genus_id": genera["Tropheus"],
            "author": "Boulenger",
            "year_described": 1898,
            "origin_type": OriginType.WILD,
            "water_type": WaterType.FRESHWATER,
            "max_size_cm": 14.0,
            "body_shape": "Ixcham, kuchli va do'ng boshli o'txo'r baliq",
            "coloration": "Morfga qarab: Ilangi (sariq-qizil kamalak), Moliro (qip-qizil olov), Kiriza (sariq belbog'li qora)",
            "sexual_dimorphism": "Tashqi ko'rinishdan deyarli farq yo'q, faqat genital papilladan ajratiladi",
            "temp_min": 24.0, "temp_max": 27.5,
            "ph_min": 8.2, "ph_max": 9.2,
            "gh_min": 14.0, "gh_max": 26.0,
            "kh_min": 10.0, "kh_max": 18.0,
            "min_tank_liters": 350, "recommended_tank_liters": 500,
            "group_size_min": 15, "group_size_recommended": "Kamida 15-20 ta bir turdagi gala",
            "aggression": AggressionLevel.HIGHLY_AGGRESSIVE,
            "difficulty": DifficultyLevel.EXPERT,
            "diet_description": "Strikt o'txo'r (obligate herbivore) — faqat diatom va mikrosuvo'tlarni qirib yeydi",
            "diet_plant": "Spirulina, nori, o'simlik peletkalari",
            "diet_protein": "Protein va qonqurt (motil) QAT'IYAN TAQIQLANADI! O'limga olib keladi (Bloat)",
            "breeding_type": BreedingType.MOUTHBROODER,
            "breeding_description": "Onasi 10-15 ta ulkan tuxumni 4 hafta og'zida ehtiyotlaydi",
            "fry_care": "Chavoqlari darhol mayda spirulinani iste'mol qila oladi",
            "natural_habitat": "Tanganika ko'li, to'lqinlar urilib turadigan sayoz qoyalar",
            "important_note": "Akvaskeypda eng qiyin turlardan biri. Suv sifati va ratsiondagi har qanday xatolik fojeali tugaydi.",
            "reliability": ReliabilityLevel.SCIENTIFIC,
            "is_published": True,
            "subcat_names": ["Tropheus"],
            "common_names": [
                ("Trofeus Moori", "uz"),
                ("Blunthead Cichlid", "en"),
                ("Tropheus Moorii", "en"),
                ("Трофеус мури", "ru"),
            ],
            "synonyms": [],
            "trade_names": ["Tropheus Ilangi", "Tropheus Moliro", "Tropheus Kiriza"],
        },
        {
            "scientific_name": "Julidochromis transcriptus",
            "genus_id": genera["Julidochromis"],
            "author": "Matthes",
            "year_described": 1959,
            "origin_type": OriginType.WILD,
            "water_type": WaterType.FRESHWATER,
            "max_size_cm": 7.0,
            "body_shape": "Cho'ziq, tor silindrsimon, doimo qoya yuzasiga qorni bilan yopishib suzadi",
            "coloration": "Och sarg'ish fonda qora shaxmat/panjara shaklidagi naqshlar, suzgichlari moviy hoshiyali",
            "sexual_dimorphism": "Urg'ochisi erkakdan biroz yirikroq bo'lishi mumkin",
            "temp_min": 24.0, "temp_max": 27.0,
            "ph_min": 8.0, "ph_max": 9.0,
            "gh_min": 10.0, "gh_max": 20.0,
            "kh_min": 8.0, "kh_max": 14.0,
            "min_tank_liters": 80, "recommended_tank_liters": 120,
            "group_size_min": 2, "group_size_recommended": "Monogam juftlik (bir marta juftlashsa umrboqiy)",
            "aggression": AggressionLevel.SEMI_AGGRESSIVE,
            "difficulty": DifficultyLevel.BEGINNER,
            "diet_description": "Aufwuchs, mayda qisqichbaqasimonlar va hasharot lichinkalari",
            "diet_plant": "Spirulina kukunlari",
            "diet_protein": "Siklop, dafniya, artemiya",
            "breeding_type": BreedingType.CAVE_SPAWNER,
            "breeding_description": "Qoyadagi tor tirqish yoki g'or shiftiga 20-50 ta tuxum yopishtiradi",
            "fry_care": "Katta avlod chavoqlari yangi tug'ilgan kichik aka-ukalarini himoya qiladi",
            "natural_habitat": "Tanganika ko'lining shimoli-g'arbiy qoyali tirqishlari",
            "important_note": "Orientatsiyasi g'aroyib: qoya gorizontal, vertikal yoki teskari bo'lsa ham unga qarab suzaveradi.",
            "reliability": ReliabilityLevel.SCIENTIFIC,
            "is_published": True,
            "subcat_names": ["Julidochromis"],
            "common_names": [
                ("Mitti Yulidoxromis (Maskali)", "uz"),
                ("Masked Julie", "en"),
                ("Юлидохромис транскриптус", "ru"),
            ],
            "synonyms": [],
            "trade_names": ["Julie Transcriptus", "Gombe Julie"],
        },
        {
            "scientific_name": "Altolamprologus calvus",
            "genus_id": genera["Altolamprologus"],
            "author": "Poll",
            "year_described": 1978,
            "origin_type": OriginType.WILD,
            "water_type": WaterType.FRESHWATER,
            "max_size_cm": 13.0,
            "body_shape": "Yon tomondan o'ta kuchli siqilgan pichoqsimon tana, qalin tangachalar",
            "coloration": "Morfga qarab qora, oq yoki sariq; tanasida yaltiroq marvarid nuqtalar",
            "sexual_dimorphism": "Erkaklar 13 sm gacha, urg'ochilar esa ancha kichik (7-8 sm)",
            "temp_min": 24.0, "temp_max": 27.5,
            "ph_min": 8.0, "ph_max": 9.2,
            "gh_min": 12.0, "gh_max": 25.0,
            "kh_min": 10.0, "kh_max": 16.0,
            "min_tank_liters": 180, "recommended_tank_liters": 250,
            "group_size_min": 2, "group_size_recommended": "Juftlik yoki 1 erkak 2 urg'ochi",
            "aggression": AggressionLevel.SEMI_AGGRESSIVE,
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "diet_description": "Yirtqich — qoya tirqishlaridagi krevetka va mayda chavoqlarni ovlaydi",
            "diet_plant": "Minimal",
            "diet_protein": "Mysis, artemiya, mayda krevetkalar, sifatli quruq granulalar",
            "breeding_type": BreedingType.CAVE_SPAWNER,
            "breeding_description": "Urg'ochisi faqat o'zi sig'adigan tor qoya tirqishi yoki yirik chig'anoqqa tuxum qo'yadi",
            "fry_care": "Chavoqlari juda sekin o'sadi",
            "natural_habitat": "Tanganika ko'li, chuqur qoyali releflar",
            "important_note": "O'ta qattiq tangachalari boshqa yirtqichlarning hujumidan himoya qiladi.",
            "reliability": ReliabilityLevel.SCIENTIFIC,
            "is_published": True,
            "subcat_names": ["Altolamprologus", "Calvus"],
            "common_names": [
                ("Altolamprologus kalvus", "uz"),
                ("Calvus Cichlid", "en"),
                ("Альтолампрологус кальвус", "ru"),
            ],
            "synonyms": [("Lamprologus calvus", "Poll 1978")],
            "trade_names": ["Black Calvus", "White Calvus", "Yellow Calvus"],
        },

        # ── 4. AMERICAN CICHLIDS ───────────────────────────────────────────
        {
            "scientific_name": "Pterophyllum scalare",
            "genus_id": genera["Pterophyllum"],
            "author": "Schultze",
            "year_described": 1823,
            "origin_type": OriginType.TANK_BRED,
            "water_type": WaterType.FRESHWATER,
            "max_size_cm": 15.0,
            "body_shape": "Baland disk shakli, qanotlari bilan birga balandligi 25 sm gacha yetadi",
            "coloration": "Yovvoyi shakli kumushrang 4 ta qora vertikal chiziqli; selektsiyada qora, marmar, oltin, koi",
            "sexual_dimorphism": "Urg'ochilar va erkaklarni ajratish qiyin; voyaga yetgan erkak peshonasida kichik do'ng bo'ladi",
            "temp_min": 24.0, "temp_max": 30.0,
            "ph_min": 6.0, "ph_max": 7.4,
            "gh_min": 3.0, "gh_max": 12.0,
            "kh_min": 2.0, "kh_max": 8.0,
            "min_tank_liters": 150, "recommended_tank_liters": 250,
            "group_size_min": 4, "group_size_recommended": "Yoshligida 5-6 ta gala, keyinchalik juftliklar hosil qiladi",
            "aggression": AggressionLevel.SEMI_AGGRESSIVE,
            "difficulty": DifficultyLevel.BEGINNER,
            "diet_description": "Yirtqich/har xil oziqlanuvchi — hasharotlar, qisqichbaqasimonlar va mayda baliqlar",
            "diet_plant": "Spirulina donalari",
            "diet_protein": "Motil, artemiya, dafniya, maxsus chips va parraklar",
            "breeding_type": BreedingType.SUBSTRATE_SPAWNER,
            "breeding_description": "Keng o'simlik barglariga (Echinodorus) yoki konuslarga 300-1000 ta tuxum qo'yadi",
            "fry_care": "Ota-ona tuxum va chavoqlarni faol yelpig'ichlab qo'riqlaydi",
            "natural_habitat": "Amazonka va Orinoko daryolari, ildizlar va sokin o'simlikli qirg'oqlar",
            "important_note": "Bo'yi baland bo'lgani sababli akvarium balandligi kamida 50 sm bo'lishi kerak. Neon tetralarni yeb qo'yishi mumkin!",
            "reliability": ReliabilityLevel.SCIENTIFIC,
            "is_published": True,
            "subcat_names": ["South"],
            "common_names": [
                ("Skalyariya", "uz"),
                ("Freshwater Angelfish", "en"),
                ("Скалярия обыкновенная", "ru"),
            ],
            "synonyms": [("Zeus scalaris", "Lichtenstein 1823")],
            "trade_names": ["Angelfish", "Koi Angel", "Black Lace Angel", "Altum Angel (savdoda adashtiriladi)"],
        },
        {
            "scientific_name": "Mikrogeophagus ramirezi",
            "genus_id": genera["Mikrogeophagus"],
            "author": "Myers & Harry",
            "year_described": 1948,
            "origin_type": OriginType.WILD,
            "water_type": WaterType.FRESHWATER,
            "max_size_cm": 6.0,
            "body_shape": "Mitti, nozik, nafis va oval shaklli tanali mitti cichlid",
            "coloration": "Moviy, qizil, sariq va qora nuqtalardan iborat kamalakdek yorqin tovlanuvchi ranglar",
            "sexual_dimorphism": "Urg'ochilarining qorni pushti-qizg'ish rangda bo'ladi, orqa suzgichi qisqaroq",
            "temp_min": 26.0, "temp_max": 30.0,
            "ph_min": 5.5, "ph_max": 7.0,
            "gh_min": 2.0, "gh_max": 8.0,
            "kh_min": 1.0, "kh_max": 4.0,
            "min_tank_liters": 60, "recommended_tank_liters": 100,
            "group_size_min": 2, "group_size_recommended": "Monogam juftlik",
            "aggression": AggressionLevel.PEACEFUL,
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "diet_description": "Mayda hasharot lichinkalari, qum tubidagi mikroskopik organizmlar",
            "diet_plant": "Mayda spirulina kukuni",
            "diet_protein": "Artemiya, siklop, mikrogranulalar",
            "breeding_type": BreedingType.SUBSTRATE_SPAWNER,
            "breeding_description": "Silliq tosh yoki chuqurchaga 150-300 ta tuxum qo'yib ikkala ota-ona parvarishlaydi",
            "fry_care": "Infuzoriya va artemiya naulpliyasi",
            "natural_habitat": "Venesuela va Kolumbiyadagi Lyanos daryo tizimlari, iliq va juda yumshoq suv",
            "important_note": "Suvdagi nitratlarga juda sezgir. Issiq suv (27-29°C) va muntazam suv almashtirish talab etiladi.",
            "reliability": ReliabilityLevel.SCIENTIFIC,
            "is_published": True,
            "subcat_names": ["South"],
            "common_names": [
                ("Ramirezi apistogrammasi (Kapalak cichlida)", "uz"),
                ("Ram Cichlid", "en"),
                ("German Blue Ram", "en"),
                ("Апистограмма Рамирези / Бабочка", "ru"),
            ],
            "synonyms": [("Apistogramma ramirezi", "Myers & Harry 1948"), ("Papiliochromis ramirezi", "Kullander 1977")],
            "trade_names": ["German Blue Ram", "Electric Blue Ram", "Gold Ram"],
        },
        {
            "scientific_name": "Astronotus ocellatus",
            "genus_id": genera["Astronotus"],
            "author": "Agassiz",
            "year_described": 1831,
            "origin_type": OriginType.TANK_BRED,
            "water_type": WaterType.FRESHWATER,
            "max_size_cm": 35.0,
            "body_shape": "Massiv, og'ir, keng og'izli va mushakdor yirik cichlida",
            "coloration": "To'q zaytun fonida olovrang va to'q sariq marmar naqshlar, dumida 'ko'z' dog'i bor",
            "sexual_dimorphism": "Jinsiy tafovut tashqi ko'rinishdan deyarli ko'rinmaydi",
            "temp_min": 23.0, "temp_max": 28.0,
            "ph_min": 6.5, "ph_max": 7.5,
            "gh_min": 5.0, "gh_max": 18.0,
            "kh_min": 3.0, "kh_max": 10.0,
            "min_tank_liters": 300, "recommended_tank_liters": 500,
            "group_size_min": 1, "group_size_recommended": "Yakka holda yoki mos tushgan katta juftlik",
            "aggression": AggressionLevel.AGGRESSIVE,
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "diet_description": "Yirtqich ovchi — baliqlar, chuvalchanglar, hasharotlar va mollyuskalar",
            "diet_plant": "O'simlik qo'shimchalari",
            "diet_protein": "Krevetkalar, midiya, baliq filesi, sifatli cichlid stiklari",
            "breeding_type": BreedingType.SUBSTRATE_SPAWNER,
            "breeding_description": "Yassi toshga 1000-2000 tagacha tuxum qo'yib fidokorona qo'riqlaydi",
            "fry_care": "Chavoqlari tez o'sadi va juda ochko'z bo'ladi",
            "natural_habitat": "Amazonka havzasi, sokin o'rmon oraliq ko'llari",
            "important_note": "Yuqori intellektga ega, egasini taniydi va qo'ldan ovqat yeydi. Juda kuchli filtratsiya talab qiladi!",
            "reliability": ReliabilityLevel.SCIENTIFIC,
            "is_published": True,
            "subcat_names": ["South"],
            "common_names": [
                ("Astronotus (Oskar)", "uz"),
                ("Oscar Cichlid", "en"),
                ("Астронотус глазчатый / Оскар", "ru"),
            ],
            "synonyms": [("Lobotes ocellatus", "Agassiz 1831")],
            "trade_names": ["Tiger Oscar", "Albino Oscar", "Red Oscar"],
        },
        {
            "scientific_name": "Thorichthys meeki",
            "genus_id": genera["Thorichthys"],
            "author": "Brind",
            "year_described": 1918,
            "origin_type": OriginType.WILD,
            "water_type": WaterType.FRESHWATER,
            "max_size_cm": 15.0,
            "body_shape": "Baland, o'tkir profilli, tomoq osti kengayuvchi pardali",
            "coloration": "Kumushrang-ko'k tananing tomoq va qorin qismi alanga kabi yorqin qip-qizil",
            "sexual_dimorphism": "Erkaklar yirikroq, tomoq qizili to'qroq va suzgich uchlari cho'zilgan",
            "temp_min": 24.0, "temp_max": 28.0,
            "ph_min": 7.0, "ph_max": 8.2,
            "gh_min": 8.0, "gh_max": 20.0,
            "kh_min": 5.0, "kh_max": 14.0,
            "min_tank_liters": 150, "recommended_tank_liters": 250,
            "group_size_min": 2, "group_size_recommended": "Monogam juftlik yoki 5-6 talik guruh",
            "aggression": AggressionLevel.SEMI_AGGRESSIVE,
            "difficulty": DifficultyLevel.BEGINNER,
            "diet_description": "Substrat elovchi omnivore — qum tubidagi qisqichbaqasimonlar va detrit",
            "diet_plant": "Spirulina, o'simlik barglari",
            "diet_protein": "Artemiya, motil, krevetka",
            "breeding_type": BreedingType.SUBSTRATE_SPAWNER,
            "breeding_description": "Tosh yoki sopol idishga 300-500 ta tuxum qo'yadi",
            "fry_care": "Ota-ona qumda chuqur kovlab chavoqlarni u yerga ko'chiradi",
            "natural_habitat": "Markaziy Amerika, Meksika va Gvatemalaning sekin oqimli daryolari",
            "important_note": "Raqibiga do'q qilish uchun qizil tomog'ini shishiradi (hududiy nishon). Mayin qum shart.",
            "reliability": ReliabilityLevel.SCIENTIFIC,
            "is_published": True,
            "subcat_names": ["Central"],
            "common_names": [
                ("Olovli og'iz cichlidasi (Meeki)", "uz"),
                ("Firemouth Cichlid", "en"),
                ("Цихлазома меека / Масковая цихлазома", "ru"),
            ],
            "synonyms": [("Cichlasoma meeki", "Brind 1918")],
            "trade_names": ["Firemouth Cichlid"],
        },
        {
            "scientific_name": "Amatitlania nigrofasciata",
            "genus_id": genera["Amatitlania"],
            "author": "Günther",
            "year_described": 1867,
            "origin_type": OriginType.WILD,
            "water_type": WaterType.FRESHWATER,
            "max_size_cm": 12.0,
            "body_shape": "Qalin, baquvvat, oval shaklli juda qat'iyatli baliq",
            "coloration": "Kulrang-ko'k fonda 8-9 ta qora vertikal qalin chiziq",
            "sexual_dimorphism": "Urg'ochilarining qorni yorqin to'q sariq/oltin tusda jilolanadi, erkaklar yirikroq",
            "temp_min": 22.0, "temp_max": 27.0,
            "ph_min": 6.8, "ph_max": 8.0,
            "gh_min": 8.0, "gh_max": 20.0,
            "kh_min": 4.0, "kh_max": 12.0,
            "min_tank_liters": 100, "recommended_tank_liters": 150,
            "group_size_min": 2, "group_size_recommended": "Juftlik",
            "aggression": AggressionLevel.AGGRESSIVE,
            "difficulty": DifficultyLevel.BEGINNER,
            "diet_description": "Har narsani yeydi (omnivore) — hasharotlar, o'simliklar, mayda baliqlar",
            "diet_plant": "Har qanday o'simlik peletkasi",
            "diet_protein": "Har qanday quruq va muzlatilgan go'shtli ovqat",
            "breeding_type": BreedingType.CAVE_SPAWNER,
            "breeding_description": "Eng oson ko'payuvchi cichlida; g'or ichiga 100-300 ta tuxum qo'yadi",
            "fry_care": "Ota-onasi chavoqlarini o'z jonini fido qilib bo'lsa ham himoya qiladi",
            "natural_habitat": "Markaziy Amerika, Kosta-Rika, Nikaragua va Salvador daryolari",
            "important_note": "Nasl berish davrida o'zidan 3 barobar katta baliqlarga ham shafqatsiz hujum qiladi.",
            "reliability": ReliabilityLevel.SCIENTIFIC,
            "is_published": True,
            "subcat_names": ["Central"],
            "common_names": [
                ("Qora chiziqli cichlida (Chernopolosaya)", "uz"),
                ("Convict Cichlid", "en"),
                ("Чернополосая цихлазома", "ru"),
            ],
            "synonyms": [("Cichlasoma nigrofasciatum", "Günther 1867"), ("Archocentrus nigrofasciatus", "Schmitter-Soto 2007")],
            "trade_names": ["Convict Cichlid", "Zebra Cichlid"],
        },

        # ── 5. DISCUS (SYMPHYSODON) ────────────────────────────────────────
        {
            "scientific_name": "Symphysodon discus",
            "genus_id": genera["Symphysodon"],
            "author": "Heckel",
            "year_described": 1840,
            "origin_type": OriginType.WILD,
            "water_type": WaterType.FRESHWATER,
            "max_size_cm": 20.0,
            "body_shape": "Dumaloq disk shakli, nihoyatda yassi va ulug'vor",
            "coloration": "Yovvoyi Heckel shakli: 1-, 5- va 9-vertikal chiziqlari (ayniqsa 5-markaziy qalin qora chiziq) yaqqol ajralib turadi",
            "sexual_dimorphism": "Tashqi ko'rinishdan deyarli farqlanmaydi, faqat tuxum qo'yish paytida ovipozitordan ajratiladi",
            "temp_min": 28.0, "temp_max": 31.5,
            "ph_min": 4.5, "ph_max": 6.5,
            "gh_min": 1.0, "gh_max": 5.0,
            "kh_min": 0.5, "kh_max": 3.0,
            "min_tank_liters": 250, "recommended_tank_liters": 400,
            "group_size_min": 6, "group_size_recommended": "Kamida 6-8 ta gala bo'lib yashaydi",
            "aggression": AggressionLevel.PEACEFUL,
            "difficulty": DifficultyLevel.EXPERT,
            "diet_description": "Detrit, hasharot lichinkalari, mayda umurtqasizlar va suv o'tlari",
            "diet_plant": "Spirulina, o'simlik tolali maxsus diskus peletkalari",
            "diet_protein": "Artemiya, oq motil, krill, maxsus tayyorlangan yurak qiyma (discus mix)",
            "breeding_type": BreedingType.SUBSTRATE_SPAWNER,
            "breeding_description": "Vertikal yuzaga tuxum qo'yadi. Tuxumdan chiqqan lichinkalar ota-ona terisidan chiqadigan maxsus 'sut' (shilimshiq) bilan oziqlanadi!",
            "fry_care": "Dastlabki 2-3 hafta ota-onasining terisidagi shilimshiq hisobiga tirik qoladi",
            "natural_habitat": "Rio Negro havzasi (Braziliya), o'ta nordon, yumshoq, barglar bilan to'yingan qora suv",
            "important_note": "Akvarium qiroli. Yuqori harorat (29-30°C) va mutlaqo toza, kam mineralli suv talab qiladi.",
            "reliability": ReliabilityLevel.SCIENTIFIC,
            "is_published": True,
            "subcat_names": ["Wild Discus"],
            "common_names": [
                ("Heckel diskusi", "uz"),
                ("Heckel Discus", "en"),
                ("Дискус Хеккеля", "ru"),
            ],
            "synonyms": [("Symphysodon discus Heckel, 1840", "Asosiy tavsif")],
            "trade_names": ["Heckel Discus", "Wild Rio Negro Discus"],
        },
        {
            "scientific_name": "Symphysodon aequifasciatus",
            "genus_id": genera["Symphysodon"],
            "author": "Pellegrin",
            "year_described": 1904,
            "origin_type": OriginType.SELECTIVE,
            "water_type": WaterType.FRESHWATER,
            "max_size_cm": 20.0,
            "body_shape": "Dumaloq disk shaklidagi mukammal simmetriya",
            "coloration": "Selektsion morflar: Pigeon Blood (oq-qizil shashka), Snake Skin (ingichka ilon terisi), Cobalt Blue (ko'k feruza)",
            "sexual_dimorphism": "Juftlik hosil bo'lgandagina xulqidan ajratish mumkin",
            "temp_min": 28.0, "temp_max": 31.0,
            "ph_min": 6.0, "ph_max": 7.0,
            "gh_min": 3.0, "gh_max": 8.0,
            "kh_min": 1.0, "kh_max": 4.0,
            "min_tank_liters": 250, "recommended_tank_liters": 450,
            "group_size_min": 6, "group_size_recommended": "Kamida 6-10 ta gala",
            "aggression": AggressionLevel.PEACEFUL,
            "difficulty": DifficultyLevel.ADVANCED,
            "diet_description": "Sifatli granula, muzlatilgan artemiya, mysis va maxsus diskus ozuqalari",
            "diet_plant": "Spirulina boyitilgan peletkalar",
            "diet_protein": "Artemiya, krill, sifatli mol yuragi pastasi",
            "breeding_type": BreedingType.SUBSTRATE_SPAWNER,
            "breeding_description": "Konusga tuxum qo'yadi, naslni ikkala ota-ona terisi shilimshig'i bilan boqadi",
            "fry_care": "14 kundan boshlab yangi chiqqan artemiya beriladi",
            "natural_habitat": "Amazonka daryo havzasi selektsion nasllari",
            "important_note": "Ajoyib selektsion ranglar. Akvariumda qum yoki yalang'och tub (bare bottom) ishlatiladi.",
            "reliability": ReliabilityLevel.SCIENTIFIC,
            "is_published": True,
            "subcat_names": ["Selective Discus", "Color Form Discus"],
            "common_names": [
                ("Moviy/Selektsion diskus", "uz"),
                ("Blue Discus / Domestic Discus", "en"),
                ("Голубой дискус / Селекционный дискус", "ru"),
            ],
            "synonyms": [],
            "trade_names": ["Pigeon Blood", "Snake Skin Discus", "Red Turquoise", "Cobalt Blue Discus"],
        },

        # ── 6. OTHER FRESHWATER FISH ──────────────────────────────────────
        {
            "scientific_name": "Paracheirodon innesi",
            "genus_id": genera["Paracheirodon"],
            "author": "Myers",
            "year_described": 1936,
            "origin_type": OriginType.TANK_BRED,
            "water_type": WaterType.FRESHWATER,
            "max_size_cm": 3.5,
            "body_shape": "Mayda, chaqqon va nozik torpeda shakli",
            "coloration": "Ko'zdan dumgacha elektr feruza-ko'k chiziq, tananing orqa yarmi yorqin qip-qizil",
            "sexual_dimorphism": "Urg'ochilarining qorni to'laroq bo'lib, ko'k chiziq biroz egilgan ko'rinadi",
            "temp_min": 21.0, "temp_max": 26.0,
            "ph_min": 5.5, "ph_max": 7.2,
            "gh_min": 2.0, "gh_max": 10.0,
            "kh_min": 1.0, "kh_max": 5.0,
            "min_tank_liters": 40, "recommended_tank_liters": 70,
            "group_size_min": 10, "group_size_recommended": "10-20 ta (uyushqoq gala)",
            "aggression": AggressionLevel.PEACEFUL,
            "difficulty": DifficultyLevel.BEGINNER,
            "diet_description": "Mayda hasharotlar, zooplankton, mikrodonalar",
            "diet_plant": "Spirulina qipiqlari",
            "diet_protein": "Dafniya, siklop, mayda quruq parraklar",
            "breeding_type": BreedingType.EGG_SCATTERER,
            "breeding_description": "Mayda bargli o'simliklar ustiga qorong'ida tuxum sochadi",
            "fry_care": "Infuzoriya va rotiferlar talab etiladi, yorug'likka sezgir",
            "natural_habitat": "Peru, Kolumbiya va Braziliyadagi Amazonka irmoqlari, qora suvli o'rmon soylari",
            "important_note": "Dunyoning eng mashhur akvarium balig'i. Yuqori haroratga (28°C+) chidamsiz.",
            "reliability": ReliabilityLevel.SCIENTIFIC,
            "is_published": True,
            "subcat_names": ["Tetralar"],
            "common_names": [
                ("Neon tetra (Oddiy neon)", "uz"),
                ("Neon Tetra", "en"),
                ("Неон обыкновенный", "ru"),
            ],
            "synonyms": [("Hyphessobrycon innesi", "Myers 1936")],
            "trade_names": ["Neon Tetra"],
        },
        {
            "scientific_name": "Betta splendens",
            "genus_id": genera["Betta"],
            "author": "Regan",
            "year_described": 1910,
            "origin_type": OriginType.TANK_BRED,
            "water_type": WaterType.FRESHWATER,
            "max_size_cm": 7.0,
            "body_shape": "Keng, hashamatli pardasimon suzgichli go'zal baliq",
            "coloration": "Qizil, ko'k, oq, sariq, binafsha, metallik, ko'p rangli morflar",
            "sexual_dimorphism": "Erkaklar ulkan parda suzgichli va yorqin, urg'ochilar kalta suzgichli",
            "temp_min": 24.0, "temp_max": 30.0,
            "ph_min": 6.5, "ph_max": 7.5,
            "gh_min": 5.0, "gh_max": 15.0,
            "kh_min": 3.0, "kh_max": 8.0,
            "min_tank_liters": 20, "recommended_tank_liters": 30,
            "group_size_min": 1, "group_size_recommended": "Erkaklar qat'iyan bir o'zi saqlanadi!",
            "aggression": AggressionLevel.AGGRESSIVE,
            "difficulty": DifficultyLevel.BEGINNER,
            "diet_description": "Karnivor — hasharotlar, lichinkalar va mayda jonivorlar",
            "diet_plant": "Minimal",
            "diet_protein": "Motil, artemiya, maxsus betta granulalari",
            "breeding_type": BreedingType.BUBBLE_NEST,
            "breeding_description": "Erkak suv yuzasida havo pufakchalaridan uya quradi va tuxumni u yerga joylaydi",
            "fry_care": "Infuzoriya va artemiya naulpliyasi",
            "natural_habitat": "Tailand va Kambodjadagi sholizorlar, sayoz turg'un botqoq suvlar",
            "important_note": "Labirint a'zosi bor, atmosfera havosidan nafas oladi. Ikki erkak bir akvariumda bir-birini o'ldiradi!",
            "reliability": ReliabilityLevel.SCIENTIFIC,
            "is_published": True,
            "subcat_names": ["Bettalar"],
            "common_names": [
                ("Xo'rozcha baliq (Betta)", "uz"),
                ("Siamese Fighting Fish", "en"),
                ("Петушок / Бойцовая рыбка", "ru"),
            ],
            "synonyms": [],
            "trade_names": ["Betta Splendens", "Halfmoon Betta", "Crowntail Betta", "Plakat Betta"],
        },
        {
            "scientific_name": "Puntigrus tetrazona",
            "genus_id": genera["Puntigrus"],
            "author": "Bleeker",
            "year_described": 1855,
            "origin_type": OriginType.TANK_BRED,
            "water_type": WaterType.FRESHWATER,
            "max_size_cm": 7.0,
            "body_shape": "Dumaloq, baland, rombsimon chaqqon tana",
            "coloration": "Oltin-sariq tanada 4 ta to'q qora vertikal qalin yo'l, qizil burun va suzgich uchlari",
            "sexual_dimorphism": "Erkaklarining burni qizg'ishroq va tanasi ixcham, urg'ochilar qorni to'la",
            "temp_min": 22.0, "temp_max": 27.0,
            "ph_min": 6.0, "ph_max": 7.5,
            "gh_min": 5.0, "gh_max": 15.0,
            "kh_min": 3.0, "kh_max": 8.0,
            "min_tank_liters": 80, "recommended_tank_liters": 120,
            "group_size_min": 8, "group_size_recommended": "8-12 ta (kam bo'lsa boshqa baliqlarni tishlaydi)",
            "aggression": AggressionLevel.SEMI_AGGRESSIVE,
            "difficulty": DifficultyLevel.BEGINNER,
            "diet_description": "Omnivore — har xil ovqatni yeydi",
            "diet_plant": "Spirulina, sabzavotlar",
            "diet_protein": "Motil, dafniya, sifatli quruq granulalar",
            "breeding_type": BreedingType.EGG_SCATTERER,
            "breeding_description": "O'simliklar orasiga tuxum sochadi, o'z tuxumini yeb qo'yishi mumkin",
            "fry_care": "Chavoqlari artemiya bilan tez o'sadi",
            "natural_habitat": "Indoneziya (Sumatra, Borneo) o'rmon daryolari",
            "important_note": "Parda suzgichli baliqlar (skalyariya, guppi) bilan birga saqlamang — qanotlarini chimchilab tashlaydi!",
            "reliability": ReliabilityLevel.SCIENTIFIC,
            "is_published": True,
            "subcat_names": ["Barbusslar"],
            "common_names": [
                ("Sumatra barbusi", "uz"),
                ("Tiger Barb", "en"),
                ("Суматранский барбус", "ru"),
            ],
            "synonyms": [("Capoeta tetrazona", "Bleeker 1855"), ("Barbus tetrazona", "Eski nom")],
            "trade_names": ["Tiger Barb", "Green Tiger Barb", "Albino Tiger Barb"],
        },
        {
            "scientific_name": "Poecilia reticulata",
            "genus_id": genera["Poecilia"],
            "author": "Peters",
            "year_described": 1859,
            "origin_type": OriginType.TANK_BRED,
            "water_type": WaterType.FRESHWATER,
            "max_size_cm": 6.0,
            "body_shape": "Mitti va chaqqon; erkaklarining dumi ulkan yelpig'ichsimon",
            "coloration": "Selektsiyada son-sanoqsiz ranglar: qizil, ko'k, ilon terisi, moskva ko'ki, tuxedo",
            "sexual_dimorphism": "Erkaklar mayda (3 sm), yorqin va gonopodiyli; urg'ochilar yirik (6 sm), kulrang va qorni to'la",
            "temp_min": 22.0, "temp_max": 28.0,
            "ph_min": 7.0, "ph_max": 8.2,
            "gh_min": 8.0, "gh_max": 25.0,
            "kh_min": 5.0, "kh_max": 14.0,
            "min_tank_liters": 30, "recommended_tank_liters": 50,
            "group_size_min": 4, "group_size_recommended": "1 erkakka 2-3 urg'ochi",
            "aggression": AggressionLevel.PEACEFUL,
            "difficulty": DifficultyLevel.BEGINNER,
            "diet_description": "Mayda hasharotlar, o'simlik qoldiqlari va alglar",
            "diet_plant": "Spirulina kukunlari",
            "diet_protein": "Dafniya, maydalangan quruq parraklar",
            "breeding_type": BreedingType.LIVEBEARER,
            "breeding_description": "Tirik tug'uvchi — har 28-30 kunda 20-80 tagacha to'liq shakllangan chavoq tug'adi",
            "fry_care": "Chavoqlari darhol suzadi va maydalangan quruq ovqatni yeya oladi",
            "natural_habitat": "Venesuela, Trinidad, Barbados soylari",
            "important_note": "Akvaryumchilik olamiga kirish eshigi. Juda tez va to'xtovsiz ko'payadi.",
            "reliability": ReliabilityLevel.SCIENTIFIC,
            "is_published": True,
            "subcat_names": ["Livebearers"],
            "common_names": [
                ("Guppi", "uz"),
                ("Guppy", "en"),
                ("Millionfish", "en"),
                ("Гуппи", "ru"),
            ],
            "synonyms": [],
            "trade_names": ["Fancy Guppy", "Moscow Blue Guppy", "Dumbo Ear Guppy"],
        },
        {
            "scientific_name": "Corydoras paleatus",
            "genus_id": genera["Corydoras"],
            "author": "Jenyns",
            "year_described": 1842,
            "origin_type": OriginType.TANK_BRED,
            "water_type": WaterType.FRESHWATER,
            "max_size_cm": 7.0,
            "body_shape": "Zirhli, suyak plastinkali, pastga qaragan mo'ylovli tub somi",
            "coloration": "Kulrang-zaytun fonda qora marmar dog'lar va metall jiloli yashil tovlanish",
            "sexual_dimorphism": "Urg'ochilar sezilarli darajada yirikroq va qorni kengroq",
            "temp_min": 18.0, "temp_max": 24.0,
            "ph_min": 6.0, "ph_max": 7.5,
            "gh_min": 4.0, "gh_max": 16.0,
            "kh_min": 2.0, "kh_max": 8.0,
            "min_tank_liters": 60, "recommended_tank_liters": 100,
            "group_size_min": 6, "group_size_recommended": "Kamida 6 ta birga saqlanadi",
            "aggression": AggressionLevel.PEACEFUL,
            "difficulty": DifficultyLevel.BEGINNER,
            "diet_description": "Tubdagi ovqat qoldiqlari, chuvalchanglar, botuvchi granulalar",
            "diet_plant": "Spirulina tabletkalari",
            "diet_protein": "Motil, tubifex, botuvchi som tabletkalari",
            "breeding_type": BreedingType.SUBSTRATE_SPAWNER,
            "breeding_description": "T-pozitsiyasida juftlashadi, urg'ochi tuxumlarni shisha va o'simlikka yopishtiradi",
            "fry_care": "Mayda botuvchi artemiya va mikroovqatlar",
            "natural_habitat": "La-Plata daryo havzasi (Argentina, Braziliya), salqin daryolar",
            "important_note": "Mo'ylovlari shikastlanmasligi uchun akvarium tubiga o'tkir toshlar emas, faqat silliq mayin qum solinishi shart!",
            "reliability": ReliabilityLevel.SCIENTIFIC,
            "is_published": True,
            "subcat_names": ["Catfish"],
            "common_names": [
                ("Marmar koridoras somi", "uz"),
                ("Peppered Corydoras", "en"),
                ("Крапчатый сомик", "ru"),
            ],
            "synonyms": [("Callichthys paleatus", "Jenyns 1842")],
            "trade_names": ["Peppered Cory", "Paleatus Catfish"],
        },
        {
            "scientific_name": "Ancistrus cirrhosus",
            "genus_id": genera["Ancistrus"],
            "author": "Valenciennes",
            "year_described": 1836,
            "origin_type": OriginType.TANK_BRED,
            "water_type": WaterType.FRESHWATER,
            "max_size_cm": 13.0,
            "body_shape": "Yassi, qattiq zirhli, so'rg'ich og'izli tub tozalovchisi",
            "coloration": "To'q jigarrang/qora tanada och sariq nuqtalar; albino va super-red turlari bor",
            "sexual_dimorphism": "Erkaklarining burni va peshonasida shoxlangan mo'ylovlar (tentacles) o'sib chiqadi",
            "temp_min": 22.0, "temp_max": 27.5,
            "ph_min": 6.5, "ph_max": 7.8,
            "gh_min": 4.0, "gh_max": 18.0,
            "kh_min": 2.0, "kh_max": 10.0,
            "min_tank_liters": 80, "recommended_tank_liters": 120,
            "group_size_min": 1, "group_size_recommended": "1 juftlik yoki yakka holda",
            "aggression": AggressionLevel.PEACEFUL,
            "difficulty": DifficultyLevel.BEGINNER,
            "diet_description": "Suv o'tlari (alglar), yog'och sellulozasi va botuvchi o'simlik tabletkalari",
            "diet_plant": "Spirulina, bodring, qovoqcha (tsukkini), salat bargi",
            "diet_protein": "Haftada 1 marta yengil protein tabletkasi",
            "breeding_type": BreedingType.CAVE_SPAWNER,
            "breeding_description": "Trubka yoki g'orga to'q sariq tuxum qo'yadi, erkak baliq ularni qattiq qo'riqlaydi",
            "fry_care": "Chavoqlari darhol o'simlik va devorlardagi mikrosuvo'tlarni tozalay boshlaydi",
            "natural_habitat": "Parana daryosi havzasi, oqimli toshli va daraxt ildizli daryolar",
            "important_note": "Akvariumda tabiiy daraxt ildizi (driftwood/koryaga) bo'lishi shart! Ovqat hazm qilish uchun yog'och tolalari zarur.",
            "reliability": ReliabilityLevel.SCIENTIFIC,
            "is_published": True,
            "subcat_names": ["Plecos"],
            "common_names": [
                ("Antsistrus (Yopishqoq som)", "uz"),
                ("Bristlenose Pleco", "en"),
                ("Bushynose Catfish", "en"),
                ("Анциструс обыкновенный / Сом-прилипала", "ru"),
            ],
            "synonyms": [],
            "trade_names": ["Bristlenose Pleco", "Bushynose", "Albino Bristlenose"],
        },
        {
            "scientific_name": "Chromobotia macracanthus",
            "genus_id": genera["Chromobotia"],
            "author": "Bleeker",
            "year_described": 1852,
            "origin_type": OriginType.WILD,
            "water_type": WaterType.FRESHWATER,
            "max_size_cm": 30.0,
            "body_shape": "Uzunchoq, chaqqon, ko'zlari ostida himoya tikanlari bor",
            "coloration": "Yorqin to'q sariq tanada 3 ta qora keng ponasimon yo'l, qip-qizil suzgichlar",
            "sexual_dimorphism": "Erkaklarining dum suzgichi uchi biroz ichkariga bukilgan bo'ladi",
            "temp_min": 25.0, "temp_max": 30.0,
            "ph_min": 6.0, "ph_max": 7.5,
            "gh_min": 4.0, "gh_max": 12.0,
            "kh_min": 2.0, "kh_max": 8.0,
            "min_tank_liters": 350, "recommended_tank_liters": 600,
            "group_size_min": 5, "group_size_recommended": "Kamida 5-6 ta (jamoaviy baliq)",
            "aggression": AggressionLevel.PEACEFUL,
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "diet_description": "Mollyuska (shilliqqurt) kushandasi, hasharotlar, botuvchi ovqatlar",
            "diet_plant": "Bodring, spirulina tabletkalari",
            "diet_protein": "Shilliqqurtlar, motil, artemiya, mayda krevetkalar",
            "breeding_type": BreedingType.EGG_SCATTERER,
            "breeding_description": "Akvariumda tabiiy ko'payishi juda kam uchraydi",
            "fry_care": "Maxsus ozuqalar",
            "natural_habitat": "Sumatra va Borneo daryolari",
            "important_note": "Akvariumdagi barcha zararli shilliqqurtlarni tezda yo'q qiladi. Yonboshlab uxlashi egalarini qo'rqitadi!",
            "reliability": ReliabilityLevel.SCIENTIFIC,
            "is_published": True,
            "subcat_names": ["Loaches"],
            "common_names": [
                ("Botia kloun", "uz"),
                ("Clown Loach", "en"),
                ("Боция-клоун", "ru"),
            ],
            "synonyms": [("Botia macracantha", "Bleeker 1852")],
            "trade_names": ["Clown Loach", "Tiger Botia"],
        },
        {
            "scientific_name": "Neocaridina davidi",
            "genus_id": genera["Neocaridina"],
            "author": "Bouvier",
            "year_described": 1904,
            "origin_type": OriginType.TANK_BRED,
            "water_type": WaterType.FRESHWATER,
            "max_size_cm": 3.0,
            "body_shape": "Mitti chuchuk suv krevetkasi, 10 oyoqli va panjali",
            "coloration": "Selektsiyada: Red Cherry (qizil olcha), Blue Dream (ko'k orzu), Yellow Golden, Orange",
            "sexual_dimorphism": "Urg'ochilari yirikroq, to'qroq rangda va orqasida 'egar' (tuxumdon) ko'rinadi",
            "temp_min": 18.0, "temp_max": 26.0,
            "ph_min": 6.5, "ph_max": 8.0,
            "gh_min": 6.0, "gh_max": 14.0,
            "kh_min": 3.0, "kh_max": 8.0,
            "min_tank_liters": 20, "recommended_tank_liters": 40,
            "group_size_min": 10, "group_size_recommended": "10-20 ta koloniya",
            "aggression": AggressionLevel.PEACEFUL,
            "difficulty": DifficultyLevel.BEGINNER,
            "diet_description": "Biofilm (bakterial parda), suv o'tlari va organik qoldiqlar",
            "diet_plant": "Spirulina, quritilgan qichitqi va bodom barglari",
            "diet_protein": "Krevetka uchun maxsus mineralli oziqalar",
            "breeding_type": BreedingType.OTHER,
            "breeding_description": "Urg'ochisi 20-30 ta tuxumni qorni ostida 3-4 hafta olib yuradi va to'liq krevetkachalar tug'iladi",
            "fry_care": "Biofilm va mayda kukun ovqatlar",
            "natural_habitat": "Tayvan va Xitoyning sovuqroq toza soylari",
            "important_note": "Mis (copper) preparatlari krevetkalar uchun halokatli zahar hisoblanadi! Yirik baliqlar ularni yeb qo'yadi.",
            "reliability": ReliabilityLevel.SCIENTIFIC,
            "is_published": True,
            "subcat_names": ["Krevetkalar"],
            "common_names": [
                ("Qizil olcha krevetkasi (Red Cherry)", "uz"),
                ("Cherry Shrimp", "en"),
                ("Креветка вишня / Ред черри", "ru"),
            ],
            "synonyms": [("Neocaridina heteropoda", "Eski nom")],
            "trade_names": ["Red Cherry Shrimp", "Blue Dream Shrimp", "Sakura Shrimp"],
        },
    ]

    for item in species_catalog:
        res = await session.execute(
            select(Species).where(Species.scientific_name == item["scientific_name"])
        )
        existing = res.scalar_one_or_none()
        if existing:
            continue

        common_names_data = item.pop("common_names", [])
        synonyms_data = item.pop("synonyms", [])
        trade_names_data = item.pop("trade_names", [])
        subcat_names = item.pop("subcat_names", [])

        sp = Species(**item)
        session.add(sp)
        await session.flush()

        # Link subcategories
        for sc_name in subcat_names:
            if sc_name in subcategories:
                await session.execute(
                    species_categories.insert().values(
                        species_id=sp.id,
                        subcategory_id=subcategories[sc_name].id,
                    )
                )

        # Common names
        for cname, lang in common_names_data:
            session.add(CommonName(species_id=sp.id, name=cname, language=lang))

        # Synonyms
        for sname, note in synonyms_data:
            session.add(Synonym(species_id=sp.id, name=sname, note=note))

        # Trade names
        for tname in trade_names_data:
            session.add(TradeName(species_id=sp.id, name=tname))

        await session.flush()

    logger.info("Successfully seeded %d species!", len(species_catalog))


async def seed_health_conditions(session: AsyncSession) -> None:
    """Seed comprehensive health conditions and diseases database."""
    logger.info("Seeding fish health conditions...")

    conditions = [
        {
            "name_uz": "Ixtioftirioz (Oq nuqta kasalligi)",
            "name_en": "Ichthyophthiriasis / White Spot Disease (Ich)",
            "emoji": "⚪",
            "category": "Parazitar",
            "symptoms": (
                "Baliq tanasi va suzgichlarida sho'r sepilgandek mayda oq nuqtalar paydo bo'ladi. "
                "Baliqlar bezovtalanadi, dekoratsiyalar va substratga tanasini qashiydi, suzgichlarini qisib oladi."
            ),
            "possible_causes": (
                "Ichthyophthirius multifiliis bir hujayrali infuzoriyasi. Asosiy turtki — "
                "haroratning keskin tushishi (sovuq suv) va yangi kelgan karantin qilinmagan baliqlar orqali infeksiya kirishi."
            ),
            "treatment_suggestions": (
                "1. Suv haroratini asta-sekin 28-30°C gacha ko'taring (parazit rivojlanish sikli tezlashadi).\n"
                "2. Malaxit ko'ki (Malachite green) yoki maxsus dori (masalan: Sera Costapur, JBL Punktol) qo'llang.\n"
                "3. Aeratsiyani maksimal darajaga ko'taring (issiq suvda kislorod kamayadi).\n"
                "4. Davolash davrida faollashtirilgan ko'mir filtrini olib tashlang."
            ),
            "prevention": "Yangi olingan baliqlarni kamida 2-3 hafta karantinda saqlash, harorat tebranishiga yo'l qo'ymaslik.",
            "important_note": "Diqqat: Bezor va krevetkalar mis va malaxit ko'kiga o'ta sezgir, dozani 2 barobar kamaytiring!",
        },
        {
            "name_uz": "Geksamitoz (Teshik bosh kasalligi)",
            "name_en": "Hexamitiasis / Hole-in-the-Head",
            "emoji": "🕳️",
            "category": "Parazitar",
            "symptoms": (
                "Baliqning bosh va yon chiziqlarida kraterga o'xshash chuqurchalar (teshiklar) hosil bo'ladi. "
                "Oq, shilimshiq va ipsimon najas, ishtaha yo'qolishi, ozib ketish va rang xiralashishi kuzatiladi."
            ),
            "possible_causes": (
                "Spironucleus / Hexamita parazitlari. Asosiy sabab: iflos suv, nitratlarning yuqoriligi, "
                "vitamin yetishmasligi va noto'g'ri bir tomonlama oziqlantirish. Ayniqsa cichlidlar va diskuslarda ko'p uchraydi."
            ),
            "treatment_suggestions": (
                "1. Metronidazol (Metronidazole) dori vositasi: 250 mg har 35-40 litr suvga yoki ovqatiga shimdirib berish.\n"
                "2. Suvni tez-tez (30-40%) almashtirish va organik kirlarni tozalash.\n"
                "3. Ratsionga vitaminli va mineralli boyitilgan ozuqalar qo'shish."
            ),
            "prevention": "Suv sifatini yuqori darajada ushlab turish, nitrat miqdorini 20 mg/l dan oshirmaslik.",
            "important_note": "Kasallik erta bosqichda davolansa teshiklar to'liq bitib ketadi.",
        },
        {
            "name_uz": "Suzgich chirishi (Fin Rot)",
            "name_en": "Fin Rot",
            "emoji": "🩹",
            "category": "Bakterial",
            "symptoms": (
                "Qanot va suzgichlar chetlari tutilgan, oqargan, yemirilgan va teshilgan bo'lib qoladi. "
                "Og'ir bosqichlarda qanotlar tagigacha chirib ketadi va qizil qonli dog'lar paydo bo'ladi."
            ),
            "possible_causes": (
                "Pseudomonas va Aeromonas bakteriyalari. Asosiy sabab — akvarium suvida ammiak va nitrit ko'payishi, "
                "boshqa baliqlar tomonidan suzgichlarning chimchilab shikastlanishi va stress."
            ),
            "treatment_suggestions": (
                "1. Birinchi navbatda akvarium suvini 30-50% yangisiga almashtirish va filtrni yuvish.\n"
                "2. Antibakterial vositalar: Baktopur, Melafix yoki Ciprofloxacin/Levomitsetin.\n"
                "3. Yengil holatlarda tuz qo'shish va suv tozaligi orqali o'z-o'zidan tiklanadi."
            ),
            "prevention": "Toza suv, o'z vaqtida suv almashtirish va agressiv baliqlarni birga saqlamaslik.",
            "important_note": "Fin rot deyarli har doim yomon suv sharoitining to'g'ridan-to'g'ri belgisidir.",
        },
        {
            "name_uz": "Qorin shishi / Malavi Bloat (Dropsy)",
            "name_en": "Dropsy / Malawi Bloat",
            "emoji": "🎈",
            "category": "Bakterial / Ichki",
            "symptoms": (
                "Qorin g'ayritabiiy darajada shishadi, tangachalar qarag'ay g'uddasidek bo'rtib tashqariga chiqadi (pineconing). "
                "Ko'zlar bo'rtib chiqishi (pop-eye) va harakatsizlik kuzatiladi."
            ),
            "possible_causes": (
                "Ichki a'zolar (ayniqsa buyrak) yetishmovchiligi, ichki bakterial infeksiya yoki Malavi o'txo'r cichlidlariga "
                "noto'g'ri oqsilga boy go'shtli ovqat berish natijasidagi o'tkir ichak infarkti."
            ),
            "treatment_suggestions": (
                "1. Kasal baliqni darhol alohida karantin akvariumiga oling.\n"
                "2. Magniy sulfat (ingliz tuzi / Epsom salt) qo'shing: 1 choy qoshiq 20 litr suvga (suyuqlikni chiqarish uchun).\n"
                "3. Keng qamrovli antibiotiklar (Kanamitsin, Sera Baktopur Direct)."
            ),
            "prevention": "O'txo'r cichlidlarga (Mbuna, Tropheus) hech qachon qonqurt, yurak qiyma va yirtqich ovqati bermang!",
            "important_note": "Tangachalar bo'rtib chiqqan bosqichda o'lim ehtimoli 80-90% dan yuqori.",
        },
        {
            "name_uz": "Velvet / Oodinioz (Oltin chang kasalligi)",
            "name_en": "Velvet Disease (Piscinoodinium)",
            "emoji": "✨",
            "category": "Parazitar",
            "symptoms": (
                "Baliq tanasida oltin, sarg'ish yoki zang tusli mayda chang qatlami paydo bo'ladi. "
                "Xuddi oltin baxmal mato qoplagandek ko'rinadi. Nafas olishi tezlashadi, yorug'likdan qochadi."
            ),
            "possible_causes": (
                "Piscinoodinium pillularis parazit mikrosuvo'ti. O'simlik xlorofilliga ega bo'lib, yorug'likda fotosintez qiladi."
            ),
            "treatment_suggestions": (
                "1. Akvarium yorug'ligini butunlay o'chiring va ustini qorong'i mato bilan yoping (yorug'liksiz parazit zaiflashadi).\n"
                "2. Mis asosidagi vositalar (Cupramine) yoki maxsus akvarium dori vositalari.\n"
                "3. Suv haroratini 28°C ga ko'taring va aeratsiyani kuchaytiring."
            ),
            "prevention": "Yangi tirik o'simliklar va baliqlarni karantin qilish.",
            "important_note": "Mis krevetka va shilliqqurtlarni darhol o'ldiradi! Davolash faqat maxsus idishda o'tkazilishi lozim.",
        },
    ]

    for cond in conditions:
        res = await session.execute(
            select(HealthCondition).where(HealthCondition.name_uz == cond["name_uz"])
        )
        if not res.scalar_one_or_none():
            session.add(HealthCondition(**cond))

    logger.info("Successfully seeded %d health conditions!", len(conditions))


async def seed_dictionary_terms(session: AsyncSession) -> None:
    """Seed aquarium glossary and dictionary terms."""
    logger.info("Seeding dictionary terms...")

    terms = [
        {
            "term": "pH (Vodorod ko'rsatkichi)",
            "definition_uz": (
                "Suvning kislotali yoki ishqoriy ekanligini belgilovchi o'lchov birligi (0 dan 14 gacha). "
                "pH 7.0 — neytral, 7 dan past — kislotali (Amazonka suvlari), 7 dan baland — ishqoriy (Malavi va Tanganika ko'llari). "
                "Shkala logarifmik bo'lgani sababli, pH 6 dan 7 ga o'zgarishi kislotalikning 10 barobar o'zgarishini anglatadi."
            ),
            "definition_en": "Potential of Hydrogen — measures acidity or alkalinity on a logarithmic scale from 0 to 14.",
            "category": "Suv kimyosi",
            "sort_order": 1,
        },
        {
            "term": "GH (Umumiy qattiqlik)",
            "definition_uz": (
                "Suvdagi erigan kalsiy (Ca2+) va magniy (Mg2+) ionlarining umumiy konsentratsiyasi (dGH darajasida o'lchanadi). "
                "0-4 dGH — juda yumshoq, 4-8 dGH — yumshoq, 8-15 dGH — o'rtacha, 15+ dGH — qattiq suv."
            ),
            "definition_en": "General Hardness — concentration of dissolved calcium and magnesium ions.",
            "category": "Suv kimyosi",
            "sort_order": 2,
        },
        {
            "term": "KH (Karbonat qattiqligi / Bufer)",
            "definition_uz": (
                "Suvdagi karbonat va gidrokarbonat ionlari miqdori (dKH). Bu suvning pH barqarorligini ta'minlovchi bufer tizimidir. "
                "Agar KH 3 dKH dan past bo'lsa, pH keskin qulashi (pH crash) yuz berishi va barcha baliqlarni halok qilishi mumkin."
            ),
            "definition_en": "Carbonate Hardness / Alkalinity — buffering capacity preventing pH crashes.",
            "category": "Suv kimyosi",
            "sort_order": 3,
        },
        {
            "term": "TDS (Umumiy erigan moddalar)",
            "definition_uz": (
                "Total Dissolved Solids — suvdagi barcha noorganik tuzlar va minerallarning umumiy miqdori (ppm yoki mg/l da). "
                "TDS metri yordamida suv tozaligi va osmos (RO) suvi sifati tekshiriladi."
            ),
            "definition_en": "Total Dissolved Solids — overall concentration of dissolved substances measured in ppm.",
            "category": "Suv kimyosi",
            "sort_order": 4,
        },
        {
            "term": "Azot aylanishi (Nitrogen Cycle)",
            "definition_uz": (
                "Akvariumdagi eng muhim biologik jarayon. Baliq chiqindilari va ozuqa qoldiqlaridan zaharli Ammiak (NH3/NH4+) hosil bo'ladi. "
                "Nitrosomonas bakteriyalari uni Nitritga (NO2-), so'ngra Nitrobacter bakteriyalari uni ancha xavfsizroq Nitratga (NO3-) aylantiradi. "
                "Yangi akvariumda bu sikl to'liq shakllanishi uchun 3-6 hafta vaqt ketadi."
            ),
            "definition_en": "Biological conversion of toxic Ammonia into Nitrite, and then into less harmful Nitrate.",
            "category": "Biologiya",
            "sort_order": 5,
        },
        {
            "term": "Mbuna",
            "definition_uz": (
                "Malavi ko'lidagi tosh-qoyalarga bog'langan, asosan o'txo'r va agressiv cichlidlar guruhi (Tonga tilida 'tosh baliqlari' degani). "
                "Pseudotropheus, Labidochromis, Metriaclima, Chindongo kabi jinslarni o'z ichiga oladi."
            ),
            "definition_en": "Rock-dwelling cichlids from Lake Malawi, primarily herbivorous and territorial.",
            "category": "Ixtiologiya",
            "sort_order": 6,
        },
        {
            "term": "Utaka",
            "definition_uz": (
                "Malavi ko'lining ochiq suvlarida va qoyalar ustida galalar bo'lib yashovchi, asosan zooplankton bilan oziqlanuvchi cichlidlar. "
                "Copadichromis, Protomelas va Mchenga turlari kiradi."
            ),
            "definition_en": "Open-water haplochromine cichlids from Lake Malawi feeding on plankton.",
            "category": "Ixtiologiya",
            "sort_order": 7,
        },
        {
            "term": "Biotop akvarium",
            "definition_uz": (
                "Muayyan tabiiy suv havzasining (masalan: Malavi qoyalari, Amazonka qora suvi) suv parametrlari, tubi, o'simliklari, "
                "dekoratsiyasi va birgalikda yashovchi hayvonot dunyosini 100% tabiiy holatda qayta yaratuvchi akvarium turi."
            ),
            "definition_en": "An aquarium that accurately replicates a specific natural underwater habitat.",
            "category": "Akvaristika",
            "sort_order": 8,
        },
        {
            "term": "Mouthbrooder (Og'izda inkubatsiya qiluvchi)",
            "definition_uz": (
                "Urug'langan tuxumlarni va yangi chiqqan chavoqlarni xavf-xatarlardan himoya qilish uchun o'z og'zida saqlab o'stiruvchi baliqlar. "
                "Malavi cichlidlarining deyarli barchasi ona-og'izda inkubatsiya qiluvchi (maternal mouthbrooder) hisoblanadi."
            ),
            "definition_en": "Fish that care for their eggs and fry inside their mouths until they are ready to swim freely.",
            "category": "Ko'payish",
            "sort_order": 9,
        },
        {
            "term": "Jinsiy dimorfizm (Sexual dimorphism)",
            "definition_uz": (
                "Bitta turga mansub erkak va urg'ochi baliqlarning tashqi ko'rinishi, rangi, hajmi yoki suzgichlari tuzilishidagi aniq ko'zga tashlanadigan farqlar. "
                "Masalan, Aulonocara turlarida erkaklar kamalakdek yorqin, urg'ochilar esa bir xil kulrang bo'ladi."
            ),
            "definition_en": "Distinct difference in size, coloration, or shape between males and females of the same species.",
            "category": "Biologiya",
            "sort_order": 10,
        },
    ]

    for term in terms:
        res = await session.execute(
            select(DictionaryTerm).where(DictionaryTerm.term == term["term"])
        )
        if not res.scalar_one_or_none():
            session.add(DictionaryTerm(**term))

    logger.info("Successfully seeded %d dictionary terms!", len(terms))


async def seed_articles(session: AsyncSession) -> None:
    """Seed comprehensive educational articles."""
    logger.info("Seeding educational articles...")

    # Article Categories
    cat_res = await session.execute(select(ArticleCategory).where(ArticleCategory.name == "Boshlang'ich qo'llanma"))
    cat_guide = cat_res.scalar_one_or_none()
    if not cat_guide:
        cat_guide = ArticleCategory(name="Boshlang'ich qo'llanma", emoji="📖", sort_order=1)
        session.add(cat_guide)
        await session.flush()

    articles_data = [
        {
            "title": "Akvariumda azot aylanishi (Nitrogen Cycle) — muvaffaqiyat garovi",
            "summary": "Yangi akvariumni ishga tushirishda biologik siklni to'g'ri shakllantirish va baliqlar o'limining oldini olish yo'riqnomasi.",
            "category_id": cat_guide.id,
            "author": "AquaMasterUzbekistan mutaxassislari",
            "is_published": True,
            "content": (
                "<b>AZOT AYLANISHI NIMA?</b>\n\n"
                "Ko'plab yangi akvariumchilar yangi idish olib, suv to'ldirib, o'sha kuniyoq baliq solishadi. "
                "3-5 kundan so'ng esa baliqlar nobud bo'ladi. Bu hodisa 'Yangi akvarium sindromi' deb ataladi.\n\n"
                "Baliqlar har kuni nafas oladi va chiqindi chiqaradi. Suvda qolgan ovqat chirishi natijasida o'ta zaharli <b>Ammiak (NH3)</b> to'planadi. "
                "Tabiatda bu moddani foydali bakteriyalar tozalaydi.\n\n"
                "<b>1-bosqich:</b> Nitrosomonas bakteriyalari ammiakni iste'mol qilib, uni <b>Nitritga (NO2)</b> aylantiradi. Nitrit ham o'ta zaharli!\n"
                "<b>2-bosqich:</b> Nitrobacter bakteriyalari nitritni <b>Nitratga (NO3)</b> aylantiradi. Nitrat faqat juda ko'p to'plangandagina zararli.\n\n"
                "<b>QANDAY TO'G'RI ISHGA TUSHIRISH KERAK?</b>\n"
                "1. Akvariumga suv, grunt va filtr o'rnating.\n"
                "2. Filtrni to'xtovsiz 24/7 rejimida yoqing (filtrni hech qachon o'chirmang!).\n"
                "3. Bakteriyalar uchun ozgina ovqat tashlang yoki maxsus bio-start bakteriya kapsulasi qo'shing.\n"
                "4. Baliqlarni faqat 2-3 haftadan keyin, suv testlari ammiak va nitrit 0 ekanligini ko'rsatgandagina oz-ozdan soling."
            ),
        },
        {
            "title": "Malavi cichlidlari: Mbuna va Utaka guruhlari farqi va parvarishi",
            "summary": "Malavi ko'lining o'txo'r va yirtqich cichlidlarini to'g'ri guruhlash, oziqlantirish va akvarium sharoitlari.",
            "category_id": cat_guide.id,
            "author": "AquaMasterUzbekistan mutaxassislari",
            "is_published": True,
            "content": (
                "<b>MALAVI CICHLIDLARI HAQIDA</b>\n\n"
                "Sharqiy Afrikadagi Malavi ko'li o'zining rang-barang, intellektual va g'ayratli cichlidlari bilan mashhur. "
                "Ular asosan ikki katta guruhga bo'linadi:\n\n"
                "<b>1. MBUNA (Tosh baliqlari)</b>\n"
                "• Turlar: Pseudotropheus, Labidochromis, Metriaclima, Chindongo.\n"
                "• Tabiatda qoyalardagi suv o'tlarini (Aufwuchs) qirib yeydi.\n"
                "• ⚠️ Eng muhim qoida: Ratsion faqat o'simlik (spirulina) bo'lishi shart! Go'sht bersangiz Malavi Bloat kasali bilan halok bo'ladi.\n"
                "• Xulqi: Hududiy va baquvvat. Akvariumda toshlardan ko'plab g'orlar va boshpanalar qurilishi kerak.\n\n"
                "<b>2. HAPS VA UTAKA (Ochiq suv baliqlari)</b>\n"
                "• Turlar: Aulonocara, Sciaenochromis, Cyrtocara moorii, Copadichromis.\n"
                "• Ochiq suvda yoki qum ustida yashaydi, asosan plankton va mayda jonivorlarni yeydi.\n"
                "• Xulqi: Tinchroq va vazminroq. Katta suzish maydoni va mayin qum talab qiladi.\n\n"
                "<b>SUV SHAROITI:</b>\n"
                "Malavi suvi juda toza, yuqori minerallashgan bo'lishi kerak:\n"
                "• pH: 7.8 – 8.6\n"
                "• GH: 10 – 20 dGH\n"
                "• Harorat: 24 – 27 °C"
            ),
        },
    ]

    for art in articles_data:
        res = await session.execute(select(Article).where(Article.title == art["title"]))
        if not res.scalar_one_or_none():
            session.add(Article(**art))

    logger.info("Successfully seeded educational articles!")


async def seed_all() -> None:
    """Run all seeding steps inside a transaction."""
    logger.info("Starting complete database seeding...")
    async with async_session() as session:
        async with session.begin():
            await seed_geography(session)
            taxonomy = await seed_taxonomy(session)
            await seed_species(session, taxonomy)
            await seed_health_conditions(session)
            await seed_dictionary_terms(session)
            await seed_articles(session)
    
    from scripts.seed_images_and_localities import seed_localities_and_images
    await seed_localities_and_images()
    logger.info("🎉 Database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_all())
