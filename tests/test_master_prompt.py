"""Comprehensive validation tests for Master Prompt requirements (AquaMasterUzbekistan Atlas)."""

import pytest
from app.database.session import async_session
from app.data.knowledge_base_data import KNOWLEDGE_ARTICLES
from app.data.glossary_data import GLOSSARY_TERMS
from app.keyboards.main_menu import main_menu_keyboard
from app.localization import uz
from app.services.calculator_service import CalculatorService
from app.services.search_service import SearchService
from app.utils.formatting import format_standard_reference_card


def test_master_prompt_5_panels():
    """Verify Section 4: Exactly 5 primary panels in the main menu."""
    kb = main_menu_keyboard()
    button_texts = [btn.text for row in kb.inline_keyboard for btn in row]
    button_callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]

    expected_panels = [
        ("🐠 Baliq qidirish", "search"),
        ("📚 Akvarium bilimlari", "knowledge_articles"),
        ("🧮 Akvarium kalkulyatorlari", "calculators"),
        ("📖 Atamalar lug‘ati", "dictionary"),
        ("ℹ️ Bot haqida ma'lumot", "about_suggest"),
    ]

    for text, cb in expected_panels:
        assert text in button_texts, f"Expected panel text '{text}' missing"
        assert cb in button_callbacks, f"Expected callback '{cb}' missing"

    assert len(button_callbacks) == 5, f"Expected exactly 5 panels, got {len(button_callbacks)}"

    # Section 3: 8 legacy navigation menus must NOT be present
    legacy_menus = [
        "african", "american", "genera", "all_species",
        "catfish_plecos", "lnumber_catalog", "compare"
    ]
    for menu in legacy_menus:
        assert menu not in button_callbacks, f"Legacy menu '{menu}' must not be in main menu"


@pytest.mark.asyncio
async def test_master_prompt_search_queries():
    """Verify Section 5.1: Specific test search queries from the prompt."""
    async with async_session() as session:
        search_service = SearchService(session)

        # 1. Full scientific name
        res = await search_service.search_unified("Placidochromis phenochilus")
        assert len(res) > 0
        assert any("phenochilus" in item["scientific_name"].lower() for item in res)

        # 2. Trade name
        res = await search_service.search_unified("Mdoka White Lips")
        assert len(res) > 0
        assert any("phenochilus" in item["scientific_name"].lower() or "mdoka" in item.get("subtitle", "").lower() or "mdoka" in item.get("display_title", "").lower() for item in res)

        # 3. L-number query
        res = await search_service.search_unified("L333")
        assert len(res) > 0
        assert any(item["type"] == "lnumber" and "333" in item["display_title"] for item in res)

        # 4. Ancistrus L144
        res = await search_service.search_unified("Ancistrus L144")
        assert len(res) > 0
        assert any("ancistrus" in item["scientific_name"].lower() for item in res)

        # 5. Tropheops Chilumba Orange
        res = await search_service.search_unified("Tropheops Chilumba Orange")
        assert len(res) > 0
        assert any("tropheops" in item["scientific_name"].lower() for item in res)

        # 6. Demasoni
        res = await search_service.search_unified("Demasoni")
        assert len(res) > 0
        assert any("demasoni" in item["scientific_name"].lower() or "demasoni" in item.get("display_title", "").lower() or "demasoni" in item.get("subtitle", "").lower() for item in res)

        # 7. Labidochromis caeruleus
        res = await search_service.search_unified("Labidochromis caeruleus")
        assert len(res) > 0
        assert any("caeruleus" in item["scientific_name"].lower() for item in res)

        # 8. Typo: frontoza -> Cyphotilapia frontosa
        res = await search_service.search_unified("frontoza")
        assert len(res) > 0
        assert any("frontosa" in item["scientific_name"].lower() for item in res)

        # 9. Typo: ansictrus -> Ancistrus
        res = await search_service.search_unified("ansictrus")
        assert len(res) > 0
        assert any("ancistrus" in item["scientific_name"].lower() for item in res)


@pytest.mark.asyncio
async def test_master_prompt_not_found_handling():
    """Verify Section 5.3: Unknown fish returns 0 results and uses exact specified prompt."""
    async with async_session() as session:
        search_service = SearchService(session)
        res = await search_service.search_unified("NonExistentAlienFishXYZ99999")
        assert len(res) == 0

        # Exact localized string requirement contains prompt text
        assert "Bu nom bo‘yicha aniq ma’lumot topilmadi" in uz.SEARCH_NOT_FOUND_MSG
        assert "yangi tur qo‘shish uchun taklif qoldirishingiz mumkin" in uz.SEARCH_NOT_FOUND_MSG


@pytest.mark.asyncio
async def test_master_prompt_standard_reference_card_sections():
    """Verify Section 6: Standard Reference Card Sections A-H."""
    async with async_session() as session:
        search_service = SearchService(session)
        res = await search_service.search_unified("Labidochromis caeruleus")
        assert len(res) > 0

        fish_id = res[0]["id"]
        from app.services.fish_service import FishService
        fish_service = FishService(session)
        fish = await fish_service.get_species(fish_id)
        assert fish is not None

        card = format_standard_reference_card(fish)

        # Check required standard sections A through H
        assert "A. Asosiy identifikatsiya" in card
        assert "B. Tabiiy yashash muhiti" in card
        assert "C. Akvarium sharoiti" in card
        assert "D. Xulq va moslik" in card
        assert "E. Oziqlantirish" in card
        assert "F. Ko‘paytirish" in card
        assert "G. Genetika va lokalitet" in card
        assert "H. Qo‘shimcha ma’lumot" in card


def test_master_prompt_14_knowledge_articles():
    """Verify Section 8: All 14 aquarium knowledge guides are available."""
    assert len(KNOWLEDGE_ARTICLES) == 14

    required_keywords = [
        "azot", "ammiak", "ph", "harorat", "filtratsiya",
        "material", "almashtirish", "oziqlantirish", "kasallik",
        "karantin", "ko‘paytirish", "xatolar", "elektr", "moslig"
    ]

    titles_combined = " ".join([art["title"].lower() for art in KNOWLEDGE_ARTICLES])
    for kw in required_keywords:
        assert kw in titles_combined, f"Keyword '{kw}' not found in knowledge article titles"


def test_master_prompt_7_calculators():
    """Verify Section 9: All 7 interactive calculators produce accurate results."""
    # 1. Aquarium volume (100 x 40 x 50 cm = 200 L)
    vol = CalculatorService.volume(100, 40, 50)
    assert vol == 200.0

    # 2. Net water volume (200 L gross, 15% displacement)
    net_res = CalculatorService.net_water_volume(200.0, displacement_percent=15.0)
    assert net_res["net_liters"] == 170.0
    assert net_res["displaced_liters"] == 30.0

    # 3. Water change volume (200 L, 25%)
    wc_liters = CalculatorService.water_change(200.0, 25.0)
    assert wc_liters == 50.0

    # 4. Filter nominal flow turnover (200 L, 1000 L/h)
    flt_res = CalculatorService.filter_turnover(1000.0, 200.0)
    assert flt_res["turnover"] == 5.0
    assert "Maqbul" in flt_res["status"]

    # 5. Water change schedule (200 L, high load)
    sched_res = CalculatorService.water_change_schedule(200.0, bioload="high")
    assert sched_res["percent"] == 35
    assert sched_res["liters_to_change"] == 70.0

    # 6. Feeding advice
    feed_res = CalculatorService.feeding_advice(15, avg_size_cm=6.0)
    assert feed_res["daily_grams"] > 0
    assert "2–3 daqiqa" in feed_res["advice"]

    # 7. Power consumption (filter 20W, heater 150W 8h, light 30W 8h, 450 UZS/kWh)
    pwr_res = CalculatorService.electricity_consumption(
        filter_watts=20.0,
        heater_watts=150.0,
        heater_hours_day=8.0,
        light_watts=30.0,
        light_hours_day=8.0,
        tariff_som_kwh=450.0,
    )
    assert pwr_res["total_daily_kwh"] == 1.92
    assert pwr_res["monthly_cost_som"] > 0


def test_master_prompt_glossary_terms():
    """Verify Section 10: Aquarium glossary has key scientific and hobby terms."""
    assert len(GLOSSARY_TERMS) >= 30

    term_keys = [t["term"].upper() for t in GLOSSARY_TERMS]
    required_terms = [
        "F0", "F1", "F2", "PURE LINE", "GIBRID", "OB", "MC", "ALBINO",
        "MBUNA", "HAP", "UTAKA", "PEACOCK", "WILD-CAUGHT", "TANK-BRED",
        "LOCALITY", "L-NUMBER", "LDA", "PH", "GH", "KH", "AMMIAK",
        "NITRIT", "NITRAT"
    ]

    for req in required_terms:
        assert any(req in k for k in term_keys), f"Term '{req}' not found in glossary"
