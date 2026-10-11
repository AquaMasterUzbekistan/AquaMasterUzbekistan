"""Tests for Ingestion pipeline, Completeness Audit, and Advanced Taxonomy Search."""

import pytest
from sqlalchemy import select

from app.database.session import async_session
from app.services.ingestion_service import IngestionService
from app.services.audit_service import AuditService
from app.repositories import SpeciesRepository
from app.models.taxonomy import Family, Genus
from app.models.species import Species


@pytest.mark.asyncio
async def test_audit_service_metrics():
    """Verify AuditService produces valid completeness audit metrics."""
    async with async_session() as session:
        audit_svc = AuditService(session)
        report = await audit_svc.run_full_audit()

        assert report.total_families >= 10
        assert report.total_genera >= 50
        assert report.total_species >= 50
        assert report.total_claims >= 50
        assert len(report.groups) >= 4
        assert report.overall_completeness_pct > 80.0
        assert len(report.lakes) >= 5
        assert len(report.top_genera) > 0

        # Verify formatted output contains key metrics
        md = audit_svc.format_audit_markdown(report)
        assert "AQUAMASTERUZBEKISTAN" in md
        assert "Biologik oilalar" in md
        assert "FishBase.org" in md


@pytest.mark.asyncio
async def test_search_by_genus_family_and_locality():
    """Verify search finds records by Genus, Family, or Locality."""
    async with async_session() as session:
        species_repo = SpeciesRepository(session)

        # 1. Search by Genus name
        aulonocara_results = await species_repo.search("Aulonocara")
        assert len(aulonocara_results) > 0
        assert any("baenschi" in s.scientific_name or "stuartgranti" in s.scientific_name for s in aulonocara_results)

        # 2. Search by Family name
        cichlid_results = await species_repo.search("Cichlidae")
        assert len(cichlid_results) > 0

        # 3. Search by Locality
        locality_results = await species_repo.search("Pombo")
        assert len(locality_results) > 0
        assert any("demasoni" in s.scientific_name for s in locality_results)


@pytest.mark.asyncio
async def test_taxonomy_hierarchy_integrity():
    """Verify that Genera correctly link to Families and Species link to Genera."""
    async with async_session() as session:
        # Pseudotropheus should be a Genus under Cichlidae
        g_stmt = select(Genus).where(Genus.scientific_name == "Pseudotropheus")
        genus = (await session.execute(g_stmt)).scalar_one_or_none()
        assert genus is not None
        assert genus.family is not None
        assert genus.family.scientific_name == "Cichlidae"
        assert genus.family.order_name == "Cichliformes"

        # Demasoni should link to Pseudotropheus
        sp_stmt = select(Species).where(Species.scientific_name == "Pseudotropheus demasoni")
        species = (await session.execute(sp_stmt)).scalar_one_or_none()
        assert species is not None
        assert species.genus_id == genus.id
