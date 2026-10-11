"""Run Completeness Audit and generate completeness_audit_report.txt."""

import asyncio
import logging
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.database.session import async_session
from app.services.audit_service import AuditService

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("audit_run")


async def main():
    logger.info("Executing comprehensive database completeness audit...")
    async with async_session() as session:
        audit_svc = AuditService(session)
        audit_report = await audit_svc.run_full_audit()
        report_text = audit_svc.format_audit_markdown(audit_report)

        report_path = project_root / "completeness_audit_report.txt"
        report_path.write_text(report_text, encoding="utf-8")
        logger.info(f"Report written to {report_path}")
        print("\n" + report_text + "\n")


if __name__ == "__main__":
    asyncio.run(main())
