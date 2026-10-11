"""Comprehensive tests for Atlas Expansion, L-Numbers, Taxonomy, and Master Requirements."""

import pytest
from sqlalchemy import select
from app.localization import uz
from app.config import settings
from app.keyboards.main_menu import main_menu_keyboard
from app.database.session import async_session
from app.repositories import LNumberRepository, FamilyRepository, GenusRepository, SpeciesRepository
from app.models.lnumber import LNumberDesignation
from app.models.taxonomy import Family, Genus
from app.services.audit_service import AuditService


def test_author_identity_display():
    """Verify that author identity is strictly '🏷️ Muallif: @shoazizoff'."""
    assert uz.AUTHOR_DISPLAY == "🏷️ Muallif: @shoazizoff"
    assert "@shoazizoff" in uz.ABOUT_TEXT
    assert "🏷️ <b>Muallif: @shoazizoff</b>" in uz.ABOUT_TEXT
    assert "shoazizoff" in uz.ABOUT_TEXT.lower()


def test_author_sticker_configuration():
    """Verify that AUTHOR_STICKER_ID is configurable in settings."""
    assert hasattr(settings, "AUTHOR_STICKER_ID")
    # By default in testing environment it can be None or a string
    assert settings.AUTHOR_STICKER_ID is None or isinstance(settings.AUTHOR_STICKER_ID, str)


def test_main_menu_5_panels():
    """Verify that main menu has the exact 5 primary panels specified in Section 4."""
    kb = main_menu_keyboard()
    button_texts = [btn.text for row in kb.inline_keyboard for btn in row]
    button_callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]

    expected_texts = [
        "🐠 Baliq qidirish",
        "📚 Akvarium bilimlari",
        "🧮 Akvarium kalkulyatorlari",
        "📖 Atamalar lug‘ati",
        "ℹ️ Bot haqida va taklif yuborish",
    ]

    for expected in expected_texts:
        assert expected in button_texts, f"Missing expected menu button: {expected}"

    expected_callbacks = [
        "search",
        "knowledge_articles",
        "calculators",
        "dictionary",
        "about_suggest",
    ]

    for cb in expected_callbacks:
        assert cb in button_callbacks, f"Missing expected callback: {cb}"

    # Verify that the 8 legacy navigation menus have been removed from the main keyboard
    removed_callbacks = [
        "african", "american", "genera", "all_species",
        "catfish_plecos", "lnumber_catalog", "compare"
    ]
    for removed in removed_callbacks:
        assert removed not in button_callbacks, f"Removed callback {removed} should not be in main menu"


@pytest.mark.asyncio
async def test_lnumber_catalog_and_ancistrus():
    """Verify L-number database records, normalization, and Ancistrus filtering."""
    async with async_session() as session:
        repo = LNumberRepository(session)

        # 1. Total records check
        total = await repo.count_total()
        assert total >= 15, f"Expected at least 15 L-numbers, got {total}"

        # 2. Designation lookup and normalization
        l046 = await repo.get_by_designation("L046")
        assert l046 is not None
        assert l046.code_number == 46
        assert "Hypancistrus zebra" in l046.scientific_name_current

        # Normalized lookup (e.g. L-46 or l46)
        l046_alt = await repo.get_by_designation("L-46")
        assert l046_alt is not None
        assert l046_alt.id == l046.id

        # LDA number lookup
        lda016 = await repo.get_by_designation("LDA016")
        assert lda016 is not None
        assert lda016.number_type == "LDA"
        assert lda016.code_number == 16
        assert lda016.is_ancistrus is True

        # Ancistrus count and filtering
        anc_count = await repo.count_total(only_ancistrus=True)
        assert anc_count >= 3
        anc_items = await repo.get_all_paged(only_ancistrus=True)
        for item in anc_items:
            assert item.is_ancistrus is True

        # Search functionality
        xingu_results = await repo.search("Xingu")
        assert len(xingu_results) > 0
        assert any(r.designation == "L046" for r in xingu_results)


@pytest.mark.asyncio
async def test_family_and_genus_section7_overviews():
    """Verify Section 7 biological and diagnostic fields in Family and Genus."""
    async with async_session() as session:
        fam_repo = FamilyRepository(session)
        gen_repo = GenusRepository(session)

        # Family check
        cichlidae = await fam_repo.get_by_name("Cichlidae")
        assert cichlidae is not None
        assert cichlidae.general_biology is not None
        assert len(cichlidae.general_biology) > 30
        assert cichlidae.feeding_ecology is not None
        assert cichlidae.reproduction_overview is not None

        loricariidae = await fam_repo.get_by_name("Loricariidae")
        assert loricariidae is not None
        assert loricariidae.aquarium_care_overview is not None

        # Genus check
        hypancistrus = await gen_repo.get_by_name("Hypancistrus")
        assert hypancistrus is not None
        assert hypancistrus.type_species is not None
        assert "Hypancistrus zebra" in hypancistrus.type_species
        assert hypancistrus.diagnostic_traits is not None

        ancistrus = await gen_repo.get_by_name("Ancistrus")
        assert ancistrus is not None
        assert ancistrus.diagnostic_traits is not None
        assert "tentakullar" in ancistrus.diagnostic_traits or "o'simtalar" in ancistrus.diagnostic_traits


@pytest.mark.asyncio
async def test_completeness_audit_accuracy():
    """Verify that Completeness Audit returns real counts without mock/fabricated data."""
    async with async_session() as session:
        audit_svc = AuditService(session)
        report = await audit_svc.run_full_audit()

        assert report.total_families >= 10
        assert report.total_genera >= 100
        assert report.total_species >= 100
        assert report.total_lnumbers >= 15
        assert report.total_claims >= 400
        assert report.fully_documented_profiles > 80
        assert report.overall_completeness_pct > 80.0
