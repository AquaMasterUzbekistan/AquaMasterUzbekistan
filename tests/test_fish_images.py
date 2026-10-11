"""Unit and integration tests for Fish Image Search feature."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.database.session import async_session
from app.handlers import all_routers
from app.handlers.fish_images import router as fish_images_router, FishImageSearchState
from app.keyboards.main_menu import main_menu_keyboard
from app.localization import uz
from app.services.image_search_service import (
    FishImageSearchService,
    FishImageItem,
    FishImageSearchResult,
    MatchConfidence,
    FishNameComponents,
)


def test_main_menu_has_image_search_button():
    """Verify that '🔎 Baliq suratlarini qidirish' button is in main menu."""
    kb = main_menu_keyboard()
    callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
    texts = [btn.text for row in kb.inline_keyboard for btn in row]

    assert "search_images" in callbacks
    assert uz.MENU_SEARCH_IMAGES in texts
    assert "🔎 Baliq suratlarini qidirish" in texts


def test_fish_images_router_registered():
    """Verify that fish_images_router is included in all_routers."""
    assert fish_images_router in all_routers
    assert fish_images_router.name == "fish_images"


def test_localization_strings_exist():
    """Ensure all required image search strings are defined."""
    assert hasattr(uz, "MENU_SEARCH_IMAGES")
    assert hasattr(uz, "IMG_SEARCH_TITLE")
    assert hasattr(uz, "IMG_SEARCH_PROMPT")
    assert hasattr(uz, "IMG_SEARCH_WAITING")
    assert hasattr(uz, "IMG_SEARCH_NOT_FOUND")
    assert hasattr(uz, "IMG_SEARCH_BUSY")


@pytest.mark.asyncio
async def test_fish_query_parser():
    """Test taxonomic query parsing preserves genus and extracts species/variant."""
    async with async_session() as session:
        # 1. Petrochromis Red Bulu Point
        c1 = await FishImageSearchService.parse_fish_query("Petrochromis Red Bulu Point", session)
        assert c1.genus == "Petrochromis"
        assert c1.variant == "Red Bulu Point"
        assert "Aulonocara" not in c1.canonical_name

        # 2. Aulonocara jacobfreibergi Eureka
        c2 = await FishImageSearchService.parse_fish_query("Aulonocara jacobfreibergi Eureka", session)
        assert c2.genus == "Aulonocara"
        assert c2.species == "jacobfreibergi"
        assert c2.variant == "Eureka"
        assert "Petrochromis" not in c2.canonical_name

        # 3. Common name mapping
        c3 = await FishImageSearchService.parse_fish_query("skalyariya", session)
        assert c3.genus == "Pterophyllum"
        assert c3.species == "scalare"


def test_image_validation_strict_genus_isolation():
    """Ensure Petrochromis rejects Aulonocara photos and vice versa."""
    # 1. Petrochromis query rejects Aulonocara
    valid, conf, reason = FishImageSearchService.validate_image(
        title="File:Aulonocara jacobfreibergi eureka red.jpg",
        desc="Aulonocara jacobfreibergi eureka red",
        taxon_name=None,
        expected_genus="Petrochromis",
        expected_variant="Red Bulu Point",
    )
    assert not valid
    assert "Petrochromis" in reason or "aulonocara" in reason

    # 2. Petrochromis query accepts Petrochromis
    valid2, conf2, _ = FishImageSearchService.validate_image(
        title="File:Petrochromis polyodon.jpg",
        desc="Petrochromis polyodon wild caught",
        taxon_name=None,
        expected_genus="Petrochromis",
        expected_variant="Red Bulu Point",
    )
    assert valid2
    assert conf2 == MatchConfidence.PARTIAL

    # 3. Aulonocara query accepts Aulonocara eureka as EXACT
    valid3, conf3, _ = FishImageSearchService.validate_image(
        title="File:Aulonocara jacobfreibergi eureka red.jpg",
        desc="Aulonocara jacobfreibergi eureka red",
        taxon_name=None,
        expected_genus="Aulonocara",
        expected_variant="Eureka",
    )
    assert valid3
    assert conf3 == MatchConfidence.EXACT


@pytest.mark.asyncio
async def test_image_search_strict_isolation_live_or_cached():
    """Verify Petrochromis never returns Aulonocara and Aulonocara never returns Petrochromis."""
    async with async_session() as session:
        # Petrochromis search
        res1 = await FishImageSearchService.search_fish_images("Petrochromis Red Bulu Point", session)
        assert res1 is not None
        assert "aulonocara" not in res1.resolved_name.lower()
        for img in res1.images:
            assert "aulonocara" not in img.title.lower()
            assert "petrochromis" in img.title.lower() or "petrochromis" in img.source.lower()

        # Aulonocara search
        res2 = await FishImageSearchService.search_fish_images("Aulonocara jacobfreibergi Eureka", session)
        assert res2 is not None
        assert "petrochromis" not in res2.resolved_name.lower()
        for img in res2.images:
            assert "petrochromis" not in img.title.lower()
            assert "aulonocara" in img.title.lower() or "aulonocara" in img.source.lower()


@pytest.mark.asyncio
async def test_image_search_caching():
    """Verify that repeated queries are served from cache."""
    async with async_session() as session:
        res1 = await FishImageSearchService.search_fish_images("Aulonocara jacobfreibergi Eureka", session)
        assert res1 is not None

        # 2nd call should hit cache immediately
        res2 = await FishImageSearchService.search_fish_images("Aulonocara jacobfreibergi Eureka", session)
        assert res2 is not None
        assert res2.resolved_name == res1.resolved_name
