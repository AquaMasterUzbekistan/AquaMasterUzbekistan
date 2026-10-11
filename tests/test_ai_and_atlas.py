"""Tests for AI Service, Locality Atlas, Images, and About Attribution."""

import pytest
from app.localization import uz
from app.services.ai_service import AIService
from app.database.session import async_session
from app.repositories.search_repo import LocalityRepository, ImageRepository
from app.models.species import Species
from sqlalchemy import select


def test_about_text_author_attribution():
    """Verify that 'ushbu loyiha shoazizoff tomonidan ishlab chiqilidi.' is present."""
    text_lower = uz.ABOUT_TEXT.lower()
    assert "shoazizoff" in text_lower
    assert "ushbu loyiha" in text_lower
    assert "tomonidan ishlab" in text_lower
    assert "ushbu loyiha shoazizoff tomonidan ishlab chiqilidi." in uz.ABOUT_TEXT.lower().replace("<b>", "").replace("</b>", "")


def test_trusted_sources_mentioned():
    """Verify that trusted sources are explicitly mentioned."""
    assert "FishBase" in uz.ABOUT_TEXT
    assert "IUCN" in uz.ABOUT_TEXT
    assert "SeriouslyFish" in uz.ABOUT_TEXT
    assert "Malawi.si" in uz.ABOUT_TEXT
    assert "Tanganyika.si" in uz.ABOUT_TEXT


@pytest.mark.asyncio
async def test_species_images_exist_in_db():
    """Verify that species have verified images in the database."""
    async with async_session() as session:
        img_repo = ImageRepository(session)
        # Check demasoni (ID: 1) or first species
        res = await session.execute(select(Species).limit(5))
        species_list = res.scalars().all()
        assert len(species_list) > 0

        for sp in species_list:
            images = await img_repo.get_by_species(sp.id)
            assert len(images) > 0, f"Species {sp.scientific_name} has no images!"
            assert images[0].image_url.startswith("http")


@pytest.mark.asyncio
async def test_locality_atlas_mapping():
    """Verify that localities have GPS coordinates and linked species."""
    async with async_session() as session:
        loc_repo = LocalityRepository(session)
        localities = await loc_repo.get_all(limit=10)
        assert len(localities) > 0

        for loc in localities:
            assert loc.name
            assert loc.latitude is not None
            assert loc.longitude is not None
            species = await loc_repo.get_species_for_locality(loc.id)
            assert len(species) > 0, f"Locality {loc.name} has no linked species!"


def test_ai_service_has_google_fallback():
    """Verify that AIService is configured with Google Gemini fallback."""
    svc = AIService()
    assert svc.google_key is not None and len(svc.google_key) > 0
    assert "gemini" in svc.google_model.lower()
