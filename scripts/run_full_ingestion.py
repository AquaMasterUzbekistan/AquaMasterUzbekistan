"""Script to execute full authoritative database ingestion and completeness audit."""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from app.database.session import async_session
from app.services.ingestion_service import IngestionService
from app.services.audit_service import AuditService
from app.data import (
    MALAWI_GENERA, MALAWI_SPECIES,
    TANGANYIKA_GENERA, TANGANYIKA_SPECIES,
    VICTORIA_AFRICA_GENERA, VICTORIA_AFRICA_SPECIES,
    AMERICAN_GENERA, AMERICAN_SPECIES,
    DISCUS_GENERA, DISCUS_SPECIES,
    OTHER_FRESHWATER_GENERA, OTHER_FRESHWATER_SPECIES,
)
from app.data.expanded_species_data import (
    EXPANDED_AMERICAN_SPECIES,
    EXPANDED_VICTORIA_AFRICA_SPECIES,
    EXPANDED_OTHER_FRESHWATER_SPECIES,
)

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("run_ingestion")


async def main():
    logger.info("Starting Master Ingestion Pipeline for AquaMasterUzbekistan...")

    async with async_session() as session:
        ingestion = IngestionService(session)

        # 1. Ensure families
        logger.info("Step 1: Ensuring taxonomic families with Order and Class data...")
        fam_map = await ingestion.ensure_families()
        logger.info("Families verified: %d", len(fam_map))

        # 2. Ingest Genera
        logger.info("Step 2: Ingesting Lake Malawi Genera...")
        g_map = await ingestion.ingest_genera(MALAWI_GENERA, fam_map)

        logger.info("Step 3: Ingesting Lake Tanganyika Genera...")
        g_map.update(await ingestion.ingest_genera(TANGANYIKA_GENERA, fam_map))

        logger.info("Step 4: Ingesting Victoria & Other Africa Genera...")
        g_map.update(await ingestion.ingest_genera(VICTORIA_AFRICA_GENERA, fam_map))

        logger.info("Step 5: Ingesting American Cichlids Genera...")
        g_map.update(await ingestion.ingest_genera(AMERICAN_GENERA, fam_map))

        logger.info("Step 6: Ingesting Discus Genera (Symphysodon)...")
        g_map.update(await ingestion.ingest_genera(DISCUS_GENERA, fam_map))

        logger.info("Step 7: Ingesting Other Freshwater Genera...")
        g_map.update(await ingestion.ingest_genera(OTHER_FRESHWATER_GENERA, fam_map))

        logger.info("Genera database synced. Total active genera mapped: %d", len(g_map))

        # 3. Ingest Species batches
        logger.info("Step 8: Ingesting Lake Malawi Species (%d species)...", len(MALAWI_SPECIES))
        await ingestion.ingest_species_batch(MALAWI_SPECIES, g_map, category_hint="Afrika Cichlidlari")

        logger.info("Step 9: Ingesting Lake Tanganyika Species (%d species)...", len(TANGANYIKA_SPECIES))
        await ingestion.ingest_species_batch(TANGANYIKA_SPECIES, g_map, category_hint="Afrika Cichlidlari")

        logger.info("Step 10: Ingesting Victoria & Other Africa Species (%d species)...", len(VICTORIA_AFRICA_SPECIES) + len(EXPANDED_VICTORIA_AFRICA_SPECIES))
        await ingestion.ingest_species_batch(VICTORIA_AFRICA_SPECIES, g_map, category_hint="Afrika Cichlidlari")
        await ingestion.ingest_species_batch(EXPANDED_VICTORIA_AFRICA_SPECIES, g_map, category_hint="Afrika Cichlidlari")

        logger.info("Step 11: Ingesting American Cichlids (%d species)...", len(AMERICAN_SPECIES) + len(EXPANDED_AMERICAN_SPECIES))
        await ingestion.ingest_species_batch(AMERICAN_SPECIES, g_map, category_hint="Amerika Cichlidlari")
        await ingestion.ingest_species_batch(EXPANDED_AMERICAN_SPECIES, g_map, category_hint="Amerika Cichlidlari")

        logger.info("Step 12: Ingesting Discus Catalogue (%d species)...", len(DISCUS_SPECIES))
        await ingestion.ingest_species_batch(DISCUS_SPECIES, g_map, category_hint="Diskuslar")

        logger.info("Step 13: Ingesting Other Freshwater Species & Invertebrates (%d species)...", len(OTHER_FRESHWATER_SPECIES) + len(EXPANDED_OTHER_FRESHWATER_SPECIES))
        await ingestion.ingest_species_batch(OTHER_FRESHWATER_SPECIES, g_map, category_hint="Boshqa Baliqlar")
        await ingestion.ingest_species_batch(EXPANDED_OTHER_FRESHWATER_SPECIES, g_map, category_hint="Boshqa Baliqlar")

        ingestion.report.finish()
        logger.info(
            "Ingestion finished in %.2fs. New Species: %d, Updated: %d, Duplicates prevented: %d, New Images: %d",
            ingestion.report.duration_seconds(),
            ingestion.report.new_species,
            ingestion.report.updated_species,
            ingestion.report.duplicates_prevented,
            ingestion.report.new_images,
        )

        # 4. Completeness Audit
        logger.info("Step 12: Running Completeness Audit...")
        audit_svc = AuditService(session)
        audit_report = await audit_svc.run_full_audit()

        print("\n" + "=" * 60)
        print("          COMPLETENESS AUDIT REPORT")
        print("=" * 60)
        report_text = audit_svc.format_audit_markdown(audit_report)
        print(report_text)
        print("=" * 60)

        report_path = Path(__file__).resolve().parent.parent / "completeness_audit_report.txt"
        report_path.write_text(report_text, encoding="utf-8")
        logger.info("Saved full audit report to %s", report_path)


if __name__ == "__main__":
    asyncio.run(main())
