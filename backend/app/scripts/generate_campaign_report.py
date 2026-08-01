from __future__ import annotations

from dataclasses import dataclass

from app.scripts.generate_priority_report import ClientPriorityRow, _collect_priority_rows


@dataclass(frozen=True)
class SegmentAssignment:
    segment: str
    channel: str
    template_id: str
    reason: str


def _band(score_0_100: float) -> str:
    if score_0_100 >= 66.0:
        return "High"
    if score_0_100 >= 33.0:
        return "Medium"
    return "Low"


def _assign_segment(row: ClientPriorityRow) -> SegmentAssignment:
    phone = (row.phone or "").strip()
    has_phone = phone not in {"", "N/A", "None", "null"}

    # Placeholder segment when we cannot safely route campaign communication.
    if not has_phone:
        return SegmentAssignment(
            segment="Gone Quiet",
            channel="Manual Review",
            template_id="GONE_QUIET_01",
            reason="Data unavailable: missing phone",
        )

    if row.total_visits <= 0:
        return SegmentAssignment(
            segment="Gone Quiet",
            channel="Manual Review",
            template_id="GONE_QUIET_01",
            reason="Data unavailable: no visit history",
        )

    if row.total_visits == 1:
        return SegmentAssignment(
            segment="First Visit",
            channel="WhatsApp",
            template_id="FIRST_VISIT_01",
            reason="First Visit",
        )

    if row.delay_days > 30:
        revenue_band = _band(row.monetary_score)
        return SegmentAssignment(
            segment="Long Absence",
            channel="SMS",
            template_id="LONG_ABSENCE_01",
            reason=f"{revenue_band} Revenue + High Delay",
        )

    if 15 <= row.delay_days <= 30:
        revenue_band = _band(row.monetary_score)
        return SegmentAssignment(
            segment="Fresh Lapse (15-30 days overdue)",
            channel="WhatsApp",
            template_id="FRESH_LAPSE_01",
            reason=f"{revenue_band} Revenue + Fresh Lapse",
        )

    if row.monetary_score >= 66.0 and row.frequency_score >= 66.0:
        return SegmentAssignment(
            segment="VIP",
            channel="Phone Call",
            template_id="VIP_01",
            reason="VIP Regular",
        )

    return SegmentAssignment(
        segment="Regular",
        channel="WhatsApp",
        template_id="REGULAR_01",
        reason="Regular: inside expected window",
    )


def _print_campaign_line(row: ClientPriorityRow, assignment: SegmentAssignment) -> None:
    print(
        " | ".join(
            [
                f"Name: {row.name}",
                f"Phone: {row.phone}",
                f"Priority Score: {row.priority_score:.1f}",
                f"Segment: {assignment.segment}",
                f"Channel: {assignment.channel}",
                f"Template: {assignment.template_id}",
                f"Reason: {assignment.reason}",
                f"Revenue: {row.total_revenue:.2f}",
                f"Delay: {row.delay_days}",
                f"Visits: {row.total_visits}",
            ]
        )
    )


def main() -> int:
    rows = _collect_priority_rows()
    rows.sort(key=lambda r: r.priority_score, reverse=True)

    print("CAMPAIGN READY CLIENT LIST")
    for row in rows:
        assignment = _assign_segment(row)
        _print_campaign_line(row, assignment)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
