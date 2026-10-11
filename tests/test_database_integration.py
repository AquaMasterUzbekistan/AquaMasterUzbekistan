"""Integration tests verifying database queries, fuzzy search, and service workflows."""

import asyncio
import unittest
from pathlib import Path
import sys

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.session import async_session
from app.services import FishService, SearchService, CompareService
from app.repositories import SpeciesRepository, SubcategoryRepository


class TestDatabaseIntegration(unittest.IsolatedAsyncioTestCase):
    async def test_species_querying(self):
        async with async_session() as session:
            repo = SpeciesRepository(session)
            species = await repo.get_by_scientific_name("Pseudotropheus demasoni")
            self.assertIsNotNone(species)
            self.assertEqual(species.scientific_name, "Pseudotropheus demasoni")
            self.assertEqual(species.ph_min, 7.8)
            self.assertEqual(species.ph_max, 8.6)
            self.assertEqual(species.temp_min, 24.0)
            self.assertGreater(len(species.common_names), 0)

    async def test_search_service_scientific_and_common(self):
        async with async_session() as session:
            search_svc = SearchService(session)

            # Search by scientific name
            results = await search_svc.search("demasoni")
            self.assertTrue(any("demasoni" in sp.scientific_name.lower() for sp in results))

            # Search by common name in Uzbek
            results_uz = await search_svc.search("Skalyariya")
            self.assertTrue(len(results_uz) > 0)

            # Search by discus
            discus_results = await search_svc.search("Discus")
            self.assertTrue(len(discus_results) > 0)

    async def test_compare_service(self):
        async with async_session() as session:
            repo = SpeciesRepository(session)
            demasoni = await repo.get_by_scientific_name("Pseudotropheus demasoni")
            heckel = await repo.get_by_scientific_name("Symphysodon discus")
            self.assertIsNotNone(demasoni)
            self.assertIsNotNone(heckel)

            compare_svc = CompareService(session)
            comparison_text = await compare_svc.compare(demasoni.id, heckel.id)
            self.assertIsNotNone(comparison_text)
            self.assertIn("TAQQOSLASH", comparison_text)
            self.assertIn("Pseudotropheus demasoni", comparison_text)
            self.assertIn("Symphysodon discus", comparison_text)
            self.assertIn("Harorat", comparison_text)
            self.assertIn("pH", comparison_text)


if __name__ == "__main__":
    unittest.main()
