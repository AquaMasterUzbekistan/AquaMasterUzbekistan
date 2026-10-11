"""Comprehensive tests for Fish Dossier Generation and Enhanced Image Search.

Verifies requirements from Sections 4, 5, 6, 7, 8, and 10:
1. Strict Genus Isolation & Typo Handling (Section 4 & 10)
2. 10-section Telegram Dossier / Full Post Formatting (Section 5)
3. 5-10 Verified Photos Search via Wikimedia & iNaturalist (Section 6)
4. "Boshqa suratlarni izlash" (pagination / URL deduplication)
5. Strict Fallbacks and Rejection of Non-existent Queries
"""

import pytest
from sqlalchemy import select

from app.database.session import async_session
from app.models.species import Species
from app.services.fish_information_service import FishInformationService
from app.services.image_search_service import (
    FishImageSearchService,
    MatchConfidence,
    FishImageItem,
)


@pytest.mark.asyncio
async def test_eight_scenarios_resolution_and_isolation():
    """Verify the 8 specific test scenarios from Section 10."""
    async with async_session() as session:
        # Scenario 1: Petrochromis Red Bulu Point (Must strictly isolate Petrochromis, never Aulonocara)
        c1 = await FishImageSearchService.parse_fish_query("Petrochromis Red Bulu Point", session)
        assert c1.genus == "Petrochromis"
        assert c1.variant == "Red Bulu Point"
        assert "Aulonocara" not in c1.canonical_name

        # Scenario 2: Placidochromis phenochilus Mdoka White Lips
        c2 = await FishImageSearchService.parse_fish_query("Placidochromis phenochilus Mdoka White Lips", session)
        assert c2.genus == "Placidochromis"
        assert c2.species == "phenochilus"
        assert "Mdoka White Lips" in (c2.variant or "")

        # Scenario 3: Aulonocara jacobfreibergi Eureka (Strictly Aulonocara, never Petrochromis)
        c3 = await FishImageSearchService.parse_fish_query("Aulonocara jacobfreibergi Eureka", session)
        assert c3.genus == "Aulonocara"
        assert c3.species == "jacobfreibergi"
        assert c3.variant == "Eureka"
        assert "Petrochromis" not in c3.canonical_name

        # Scenario 4: Labeotropheus trewavasae OB
        c4 = await FishImageSearchService.parse_fish_query("Labeotropheus trewavasae OB", session)
        assert c4.genus == "Labeotropheus"
        assert c4.species == "trewavasae"
        assert c4.variant == "OB"

        # Scenario 5: Ancistrus L144 (Resolves to Ancistrus genus)
        c5 = await FishImageSearchService.parse_fish_query("Ancistrus L144", session)
        assert c5.genus == "Ancistrus"
        assert "L144" in (c5.variant or "") or "L144" in c5.canonical_name

        # Scenario 6: L333 pleco (Resolves via L-number database to Hypancistrus)
        c6 = await FishImageSearchService.parse_fish_query("L333 pleco", session)
        assert c6.genus == "Hypancistrus"
        assert "333" in (c6.variant or "") or "333" in c6.canonical_name or "Porto de Moz" in c6.canonical_name

        # Scenario 7: Misspelled fish names (Fuzzy correction with genus preserved)
        c7_a = await FishImageSearchService.parse_fish_query("Petrachromis Red Bulu Point", session)
        assert c7_a.genus == "Petrochromis"

        c7_b = await FishImageSearchService.parse_fish_query("Aulonacara Eureka", session)
        assert c7_b.genus == "Aulonocara"

        # Scenario 8: Non-existent fish name (Must return UNVERIFIED, zero bogus photos)
        c8 = await FishImageSearchService.parse_fish_query("FakeAlienFishSpecies 9999", session)
        assert c8.genus is None
        res8 = await FishImageSearchService.search_fish_images("FakeAlienFishSpecies 9999", session)
        assert res8.confidence == MatchConfidence.UNVERIFIED
        assert len(res8.images) == 0


@pytest.mark.asyncio
async def test_full_dossier_contains_ten_sections():
    """Verify that FishInformationService generates a complete 10-section Telegram post."""
    async with async_session() as session:
        # Load a species from the database (e.g. Symphysodon discus or first species)
        sp = (await session.execute(select(Species).limit(1))).scalars().first()
        assert sp is not None

        post = FishInformationService.generate_post_from_model(sp)

        # 10 Standardized Sections Check:
        assert "TO'LIQ NOMI" in post
        assert "TABIIY TARQALISHI" in post
        assert "TASHQI KO'RINISHI" in post
        assert "XULQ-ATVORI" in post
        assert "OZIQLANISH RATSIONI" in post
        assert "SUV PARAMETRLARI" in post
        assert "AKVARIUM TALABLARI" in post
        assert "KO'PAYISH" in post
        assert "ISHOCHLI MANBALAR" in post
        assert "FishBase.org" in post

        # Must conform to Telegram maximum length limit
        assert len(post) <= 4096


@pytest.mark.asyncio
async def test_search_more_images_deduplication():
    """Verify that 'Boshqa suratlarni izlash' excludes previously seen URLs."""
    async with async_session() as session:
        res1 = await FishImageSearchService.search_fish_images(
            query="Petrochromis Red Bulu Point",
            session=session,
            max_images=3,
        )
        assert len(res1.images) > 0
        seen = {img.url for img in res1.images}

        # Query again with seen_urls passed
        res2 = await FishImageSearchService.search_fish_images(
            query="Petrochromis Red Bulu Point",
            session=session,
            max_images=3,
            seen_urls=seen,
        )

        for img in res2.images:
            assert img.url not in seen, f"Duplicate image URL returned: {img.url}"


def test_confidence_tagging():
    """Verify confidence tagging values."""
    assert MatchConfidence.EXACT == "ANIQ MOSLIK"
    assert MatchConfidence.PARTIAL == "QISMAN MOSLIK"
    assert MatchConfidence.UNVERIFIED == "TASDIQLANMAGAN"
