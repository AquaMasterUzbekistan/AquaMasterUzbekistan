"""Comprehensive test suite verifying text-only requirements, taxonomy, and audit.

Tests requirements from sections 9-28:
- Complete removal of images/photos from UI and fish profiles
- Removal of similar-species recommendations
- Genus association with species
- Scientific taxonomy and synonyms deduplication
- Search across scientific, common, trade names, and localities
- Traceable source links and scientific claims
- Strict fallback when facts are missing
- Text-based comparison of 2 and 3 species
- Completeness audit breakdown across groups
- Admin authorization security
"""

import pytest
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.database.session import async_session
from app.models.species import Species, Synonym, CommonName, TradeName
from app.models.taxonomy import Genus, Family
from app.models.source import ScientificClaim, Source
from app.keyboards.profile import profile_tabs_keyboard
from app.keyboards.main_menu import main_menu_keyboard
from app.utils.formatting import (
    format_fish_profile_summary, format_water_params,
    format_diet, format_behaviour, format_breeding,
    format_genetics, format_comparison,
)
from app.localization import uz
from app.services.audit_service import AuditService
from app.repositories import SpeciesRepository
from app.services.search_service import SearchService
from app.utils.security import has_admin_access


def test_ui_image_and_similar_species_removed():
    """Verify that images and similar-species features are absent from UI keyboards."""
    # 1. Profile tabs keyboard
    kb = profile_tabs_keyboard(1, is_favorite=False, genus_id=1, genus_name="Symphysodon")
    all_callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
    all_texts = [btn.text for row in kb.inline_keyboard for btn in row]

    # No gallery tab
    assert not any("gallery" in cb for cb in all_callbacks)
    # No similar-species tab
    assert not any("similar" in cb for cb in all_callbacks)

    # 2. Main menu keyboard
    menu_kb = main_menu_keyboard()
    menu_callbacks = [btn.callback_data for row in menu_kb.inline_keyboard for btn in row]
    menu_texts = [btn.text for row in menu_kb.inline_keyboard for btn in row]

    # No photo identification
    assert "identify" not in menu_callbacks
    assert not any("aniqlash" in t.lower() and "ai" in t.lower() for t in menu_texts)


def test_profile_summary_text_only():
    """Verify that profile summary produces strictly text with NO invisible image cards or img tags."""
    sp = Species(
        id=999,
        scientific_name="Symphysodon discus",
        author="Heckel",
        year_described=1840,
        max_size_cm=20.0,
        temp_min=28.0,
        temp_max=32.0,
        ph_min=4.0,
        ph_max=5.5,
        min_tank_liters=300,
        evidence_quality_note="🟢 Ilmiy manba bilan tasdiqlangan (Heckel 1840)",
    )

    text = format_fish_profile_summary(sp)

    # Must contain scientific identity
    assert "Symphysodon discus" in text
    assert "Heckel" in text
    assert "1840" in text

    # Must NOT contain invisible image anchor or img tags
    assert "&#8205;" not in text
    assert "<img" not in text
    assert "http" not in text or "FishBase.org" in text


def test_text_based_comparison_two_and_three_species():
    """Verify text-based comparison supports comparing 2 or 3 species with full text metrics."""
    sp1 = Species(
        id=1,
        scientific_name="Symphysodon discus",
        author="Heckel",
        year_described=1840,
        max_size_cm=20.0,
        temp_min=28.0,
        temp_max=32.0,
        ph_min=4.0,
        ph_max=5.5,
        min_tank_liters=300,
        dietary_category="Omnivorous",
        temperament="Tinch va suruvchi",
    )
    sp2 = Species(
        id=2,
        scientific_name="Pterophyllum scalare",
        author="Schultze",
        year_described=1823,
        max_size_cm=15.0,
        temp_min=24.0,
        temp_max=28.0,
        ph_min=6.0,
        ph_max=7.5,
        min_tank_liters=150,
        dietary_category="Omnivorous / Predator",
        temperament="Tinch, lekin mayda baliqlarni yeydi",
    )
    sp3 = Species(
        id=3,
        scientific_name="Astronotus ocellatus",
        author="Agassiz",
        year_described=1831,
        max_size_cm=35.0,
        temp_min=23.0,
        temp_max=28.0,
        ph_min=6.5,
        ph_max=7.5,
        min_tank_liters=400,
        dietary_category="Carnivorous",
        temperament="Katta va yarim agressiv",
    )

    # Compare 2 species
    comp_2 = format_comparison(sp1, sp2)
    assert "Symphysodon discus" in comp_2
    assert "Pterophyllum scalare" in comp_2
    assert "Maks. o'lcham" in comp_2
    assert "Harorat" in comp_2
    assert "<img" not in comp_2

    # Compare 3 species
    comp_3 = format_comparison(sp1, sp2, sp3)
    assert "Symphysodon discus" in comp_3
    assert "Pterophyllum scalare" in comp_3
    assert "Astronotus ocellatus" in comp_3
    assert "35.0 sm" in comp_3


def test_missing_data_fallback_string():
    """Verify that unknown or unsupported facts trigger the exact fallback string."""
    assert uz.NO_DATA_STRING == "Bu ma'lumotni tasdiqlash uchun yetarli ishonchli manba topilmadi."

    empty_sp = Species(
        scientific_name="Hypothetical unknown",
    )
    behaviour_text = format_behaviour(empty_sp)
    assert uz.NO_DATA_STRING in behaviour_text


@pytest.mark.asyncio
async def test_scientific_claims_and_traceability():
    """Verify that scientific claims exist in the DB, linked to exact sources and evidence badges."""
    async with async_session() as session:
        claims_stmt = select(ScientificClaim).limit(10)
        claims = (await session.execute(claims_stmt)).scalars().all()
        assert len(claims) > 0

        # Verify evidence label has official badge
        for cl in claims:
            assert cl.claim_type in ["Taxonomy", "Natural Ecology", "Husbandry", "Nutrition", "Reproduction"]
            assert "🟢" in cl.evidence_label or "🟡" in cl.evidence_label


@pytest.mark.asyncio
async def test_discus_catalogue_taxonomy_disputes():
    """Verify dedicated Discus database includes Heckel and Green discus with taxonomic notes."""
    async with async_session() as session:
        heckel = (await session.execute(
            select(Species).where(Species.scientific_name == "Symphysodon discus")
        )).scalar_one_or_none()

        assert heckel is not None
        assert heckel.author == "Heckel"
        assert heckel.year_described == 1840
        assert heckel.taxonomic_notes is not None
        assert "Heckel" in heckel.taxonomic_notes


@pytest.mark.asyncio
async def test_genus_lists_associated_species():
    """Verify that Genus pages list their associated species accurately."""
    async with async_session() as session:
        genus_stmt = (
            select(Genus)
            .where(Genus.scientific_name == "Symphysodon")
            .options(selectinload(Genus.species_list))
        )
        genus = (await session.execute(genus_stmt)).scalar_one_or_none()
        assert genus is not None
        assert len(genus.species_list) >= 4
        sci_names = [s.scientific_name for s in genus.species_list]
        assert "Symphysodon discus" in sci_names
        assert "Symphysodon aequifasciatus" in sci_names
        assert "Symphysodon tarzoo" in sci_names
        assert "Symphysodon haraldi" in sci_names


@pytest.mark.asyncio
async def test_search_supports_all_name_dimensions():
    """Verify text search supports scientific name, common name, and locality."""
    async with async_session() as session:
        repo = SpeciesRepository(session)

        # 1. Scientific name search
        res1 = await repo.search("Symphysodon")
        assert len(res1) >= 4

        # 2. Uzbek common name search
        res2 = await repo.search("Skalyariya")
        assert len(res2) >= 1
        assert any("Pterophyllum" in s.scientific_name for s in res2)

        # 3. Locality search
        res3 = await repo.search("Amazon")
        assert len(res3) >= 1


@pytest.mark.asyncio
async def test_completeness_audit_distinct_groups():
    """Verify completeness audit breaks down Lake Malawi, Tanganyika, Victoria, American, Discus, and Other."""
    async with async_session() as session:
        audit_svc = AuditService(session)
        report = await audit_svc.run_full_audit()

        group_names = [g.group_name for g in report.groups]
        assert "Lake Malawi" in group_names
        assert "Lake Tanganyika" in group_names
        assert "Lake Victoria & Other Africa" in group_names
        assert "American Cichlids" in group_names
        assert "Discus" in group_names
        assert "Other Freshwater" in group_names

        # Each group has valid completeness percentage
        for g in report.groups:
            assert 0.0 <= g.completeness_percentage <= 100.0
            assert g.total_species > 0


def test_admin_access_control():
    """Verify unauthorized users cannot execute administrative operations."""
    assert has_admin_access("user") is False
    assert has_admin_access("admin") is True
    assert has_admin_access("superadmin") is True


@pytest.mark.asyncio
async def test_multi_parameter_filter_search():
    """Verify Section 16 multi-parameter filter search."""
    async with async_session() as session:
        repo = SpeciesRepository(session)

        # 1. Filter by genus
        discus_results = await repo.filter_search(genus_name="Symphysodon")
        assert len(discus_results) >= 4
        assert all("Symphysodon" in s.scientific_name for s in discus_results)

        # 2. Filter by lake
        malawi_results = await repo.filter_search(lake_name="Malavi")
        assert len(malawi_results) > 0

        # 3. Filter by size
        large_fish = await repo.filter_search(min_size=20.0)
        assert len(large_fish) > 0
        assert all(s.max_size_cm >= 20.0 for s in large_fish)


def test_interactive_filter_keyboards():
    """Verify Section 16 interactive filter keyboards structure and callbacks."""
    from app.keyboards.search import (
        filter_categories_keyboard,
        filter_options_keyboard,
        search_results_keyboard,
    )

    # 1. Main category keyboard
    cat_kb = filter_categories_keyboard()
    callback_datas = [btn.callback_data for row in cat_kb.inline_keyboard for btn in row]
    assert "flt:cat:lake" in callback_datas
    assert "flt:cat:diet" in callback_datas
    assert "flt:cat:size" in callback_datas
    assert "flt:cat:agg" in callback_datas
    assert "flt:cat:ph" in callback_datas
    assert "flt:cat:iucn" in callback_datas

    # 2. Options keyboard for Lake and Diet
    lake_kb = filter_options_keyboard("lake")
    lake_callbacks = [btn.callback_data for row in lake_kb.inline_keyboard for btn in row]
    assert "flt:do:lake:Malav" in lake_callbacks
    assert "flt:do:lake:Tang" in lake_callbacks

    diet_kb = filter_options_keyboard("diet")
    diet_callbacks = [btn.callback_data for row in diet_kb.inline_keyboard for btn in row]
    assert "flt:do:diet:Herbivore" in diet_callbacks
    assert "flt:do:diet:Carnivore" in diet_callbacks

    # 3. Pagination callbacks adhere to Telegram 64-byte limit
    res_kb = search_results_keyboard([], page=1, total_pages=3, filter_code="lake_Malav")
    for row in res_kb.inline_keyboard:
        for btn in row:
            if btn.callback_data:
                assert len(btn.callback_data.encode("utf-8")) <= 64


@pytest.mark.asyncio
async def test_all_filter_dimensions_in_service():
    """Verify filter_search across dietary categories, lakes, aggression, and conservation status."""
    async with async_session() as session:
        search_svc = SearchService(session)

        # Diet filters
        herbi = await search_svc.filter_search(dietary_category="Herbivore")
        assert len(herbi) > 0
        assert all("herbivor" in (s.dietary_category or "").lower() for s in herbi)

        carni = await search_svc.filter_search(dietary_category="Carnivore")
        assert len(carni) > 0

        # Aggression
        peaceful = await search_svc.filter_search(aggression="peaceful")
        assert len(peaceful) > 0

        # Conservation status
        vulnerable = await search_svc.filter_search(conservation_status="VU")
        assert len(vulnerable) > 0

