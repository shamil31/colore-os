from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from openpyxl import Workbook

from app.scripts.generate_campaign_report import _assign_segment, _has_phone
from app.scripts.generate_priority_report import _collect_priority_rows

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class IntegrillaRow:
    phone: str
    name: str
    template_id: str


def _clean_phone(phone: str | None) -> str | None:
    """Extract digits only from phone number, validate country code."""
    if not phone or not _has_phone(phone):
        return None

    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)

    # Must have digits and should include country code (8+ digits typical)
    if not digits_only or len(digits_only) < 8:
        return None

    return digits_only


def main() -> int:
    # Collect priority rows (same process as campaign report)
    rows = _collect_priority_rows()
    rows.sort(key=lambda r: r.priority_score, reverse=True)

    # Deduplicate by client_id
    deduped_rows: list = []
    seen_client_ids: set[int] = set()
    for row in rows:
        if row.client_id in seen_client_ids:
            continue
        seen_client_ids.add(row.client_id)
        deduped_rows.append(row)

    # Process for Integrilla export
    export_rows: list[IntegrillaRow] = []
    excluded_count = 0

    for row in deduped_rows:
        assignment = _assign_segment(row)

        # Export only READY clients
        send_status = "READY" if _has_phone(row.phone) and assignment.segment != "Gone Quiet" else "HOLD"
        if send_status != "READY":
            continue

        # Validate and clean phone
        clean_phone = _clean_phone(row.phone)
        if not clean_phone:
            logger.warning(
                f"Excluded client {row.client_id} ({row.name}): invalid phone '{row.phone}'"
            )
            excluded_count += 1
            continue

        export_rows.append(
            IntegrillaRow(
                phone=clean_phone,
                name=row.name or "Unknown",
                template_id=assignment.template_id,
            )
        )

    # Write to Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Campaign"

    # Headers
    ws.append(("phone", "name", "template_id"))

    # Data rows
    for export_row in export_rows:
        ws.append((export_row.phone, export_row.name, export_row.template_id))

    wb.save("campaign.xlsx")

    # Summary
    logger.info(f"Exported: {len(export_rows)} clients")
    logger.info(f"Excluded: {excluded_count} clients (invalid phone)")
    logger.info("Output: campaign.xlsx")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
