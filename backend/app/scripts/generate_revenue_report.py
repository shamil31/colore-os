from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from app.db.database import SessionLocal
from app.models.revenue_client import RevenueClient
from app.models.revenue_client_visit import RevenueClientVisit


@dataclass
class ClientRevenueRow:
    client_id: int
    name: str
    phone: str
    last_visit: datetime | None
    days_since_last_visit: int | None
    total_visits: int
    total_revenue: float
    average_interval_days: float | None
    expected_next_visit_date: datetime | None
    delay_days: int
    revenue_score: str


def _days_since(last_visit: datetime | None, now: datetime) -> int | None:
    if last_visit is None:
        return None
    return max((now - last_visit).days, 0)


def _average_interval_days(visits: list[datetime]) -> float | None:
    if len(visits) < 2:
        return None

    intervals: list[int] = []
    for i in range(1, len(visits)):
        interval = (visits[i] - visits[i - 1]).days
        if interval > 0:
            intervals.append(interval)

    if not intervals:
        return None

    return sum(intervals) / len(intervals)


def _score_revenue(total_revenue: float) -> str:
    if total_revenue >= 1000:
        return "High"
    if total_revenue >= 300:
        return "Medium"
    return "Low"


def _format_date(value: datetime | None) -> str:
    if value is None:
        return "N/A"
    return value.strftime("%Y-%m-%d")


def _format_float(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value:.2f}"


def _print_client_line(row: ClientRevenueRow) -> None:
    avg = _format_float(row.average_interval_days)
    last_visit = _format_date(row.last_visit)

    print(
        " | ".join(
            [
                f"Name: {row.name}",
                f"Phone: {row.phone}",
                f"Last visit: {last_visit}",
                f"Days since last visit: {row.days_since_last_visit if row.days_since_last_visit is not None else 'N/A'}",
                f"Average interval: {avg}",
                f"Delay: {row.delay_days}",
                f"Total revenue: {row.total_revenue:.2f}",
                f"Total visits: {row.total_visits}",
            ]
        )
    )


def _collect_rows() -> list[ClientRevenueRow]:
    now = datetime.utcnow()
    rows: list[ClientRevenueRow] = []

    with SessionLocal() as db:
        clients = db.query(RevenueClient).filter(RevenueClient.is_active.is_(True)).all()

        for client in clients:
            visits = (
                db.query(RevenueClientVisit)
                .filter(RevenueClientVisit.revenue_client_id == client.id)
                .filter(RevenueClientVisit.last_visit_date.is_not(None))
                .order_by(RevenueClientVisit.last_visit_date.asc())
                .all()
            )

            visit_dates = [v.last_visit_date for v in visits if v.last_visit_date is not None]
            amounts = [v.amount for v in visits if isinstance(v.amount, (int, float))]

            last_visit = visit_dates[-1] if visit_dates else client.last_visit_date
            days_since = _days_since(last_visit, now)

            total_visits = len(visit_dates)
            if total_visits == 0:
                total_visits = client.total_visits or 0

            total_revenue = sum(float(v) for v in amounts)
            if total_revenue == 0 and client.total_spent is not None:
                total_revenue = float(client.total_spent)

            avg_interval = _average_interval_days(visit_dates)
            expected_next: datetime | None = None
            delay_days = 0

            if avg_interval is not None and last_visit is not None:
                expected_next = last_visit + timedelta(days=round(avg_interval))
                if now > expected_next:
                    delay_days = (now - expected_next).days

            row = ClientRevenueRow(
                client_id=client.id,
                name=client.full_name or "Unknown",
                phone=client.phone or "N/A",
                last_visit=last_visit,
                days_since_last_visit=days_since,
                total_visits=total_visits,
                total_revenue=total_revenue,
                average_interval_days=avg_interval,
                expected_next_visit_date=expected_next,
                delay_days=delay_days,
                revenue_score=_score_revenue(total_revenue),
            )
            rows.append(row)

    return rows


def main() -> int:
    rows = _collect_rows()

    high = [r for r in rows if r.revenue_score == "High" and r.delay_days > 0]
    medium = [r for r in rows if r.revenue_score == "Medium" and r.delay_days > 0]
    low = [r for r in rows if r.revenue_score == "Low" and r.delay_days > 0]

    high.sort(key=lambda r: (r.delay_days, r.total_revenue), reverse=True)
    medium.sort(key=lambda r: (r.delay_days, r.total_revenue), reverse=True)
    low.sort(key=lambda r: (r.delay_days, r.total_revenue), reverse=True)

    all_overdue = [r for r in rows if r.delay_days > 0]
    all_overdue.sort(key=lambda r: (r.delay_days, r.total_revenue), reverse=True)
    top20 = all_overdue[:20]

    print(f"CLIENTS ANALYZED: {len(rows)}")
    print()

    print("HIGH VALUE OVERDUE:")
    for row in high:
        _print_client_line(row)
    print()

    print("MEDIUM VALUE OVERDUE:")
    for row in medium:
        _print_client_line(row)
    print()

    print("LOW VALUE OVERDUE:")
    for row in low:
        _print_client_line(row)
    print()

    print("TOP 20 CLIENTS TO REACTIVATE")
    for row in top20:
        _print_client_line(row)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
