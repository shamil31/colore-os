from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from app.db.database import SessionLocal
from app.models.revenue_client import RevenueClient
from app.models.revenue_client_visit import RevenueClientVisit


@dataclass
class ClientPriorityRow:
    client_id: int
    name: str
    phone: str
    total_revenue: float
    total_visits: int
    average_interval_days: float | None
    days_since_last_visit: int | None
    delay_days: int
    expected_visit_date: datetime | None
    recency_score: float
    frequency_score: float
    monetary_score: float
    delay_weight: float
    monetary_weight: float
    frequency_weight: float
    priority_score: float


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


def _normalize(value: float, min_value: float, max_value: float) -> float:
    if max_value <= min_value:
        return 1.0 if value > 0 else 0.0
    normalized = (value - min_value) / (max_value - min_value)
    if normalized < 0:
        return 0.0
    if normalized > 1:
        return 1.0
    return normalized


def _band(score_0_100: float) -> str:
    if score_0_100 >= 66.0:
        return "High"
    if score_0_100 >= 33.0:
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


def _collect_priority_rows() -> list[ClientPriorityRow]:
    now = datetime.utcnow()
    draft_rows: list[dict] = []

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
            amounts = [float(v.amount) for v in visits if isinstance(v.amount, (int, float))]

            total_revenue = sum(amounts)
            if total_revenue == 0 and client.total_spent is not None:
                total_revenue = float(client.total_spent)

            total_visits = len(visit_dates)
            if total_visits == 0:
                total_visits = client.total_visits or 0

            last_visit = visit_dates[-1] if visit_dates else client.last_visit_date
            days_since = _days_since(last_visit, now)

            avg_interval = _average_interval_days(visit_dates)
            expected_next: datetime | None = None
            delay_days = 0

            if avg_interval is not None and last_visit is not None:
                expected_next = last_visit + timedelta(days=round(avg_interval))
                if now > expected_next:
                    delay_days = (now - expected_next).days

            draft_rows.append(
                {
                    "client_id": client.id,
                    "name": client.full_name or "Unknown",
                    "phone": client.phone or "N/A",
                    "total_revenue": total_revenue,
                    "total_visits": total_visits,
                    "average_interval_days": avg_interval,
                    "days_since_last_visit": days_since,
                    "delay_days": delay_days,
                    "expected_visit_date": expected_next,
                }
            )

    if not draft_rows:
        return []

    revenue_values = [float(r["total_revenue"]) for r in draft_rows]
    visits_values = [float(r["total_visits"]) for r in draft_rows]
    delay_values = [float(r["delay_days"]) for r in draft_rows]
    recency_values = [float(r["days_since_last_visit"] or 0) for r in draft_rows]

    min_revenue, max_revenue = min(revenue_values), max(revenue_values)
    min_visits, max_visits = min(visits_values), max(visits_values)
    min_delay, max_delay = min(delay_values), max(delay_values)
    min_recency, max_recency = min(recency_values), max(recency_values)

    final_rows: list[ClientPriorityRow] = []

    for row in draft_rows:
        monetary_weight = _normalize(float(row["total_revenue"]), min_revenue, max_revenue)
        frequency_weight = _normalize(float(row["total_visits"]), min_visits, max_visits)
        delay_weight = _normalize(float(row["delay_days"]), min_delay, max_delay)

        recency_weight = _normalize(float(row["days_since_last_visit"] or 0), min_recency, max_recency)

        priority_score = delay_weight * monetary_weight * frequency_weight * 100.0

        final_rows.append(
            ClientPriorityRow(
                client_id=int(row["client_id"]),
                name=str(row["name"]),
                phone=str(row["phone"]),
                total_revenue=float(row["total_revenue"]),
                total_visits=int(row["total_visits"]),
                average_interval_days=row["average_interval_days"],
                days_since_last_visit=row["days_since_last_visit"],
                delay_days=int(row["delay_days"]),
                expected_visit_date=row["expected_visit_date"],
                recency_score=recency_weight * 100.0,
                frequency_score=frequency_weight * 100.0,
                monetary_score=monetary_weight * 100.0,
                delay_weight=delay_weight,
                monetary_weight=monetary_weight,
                frequency_weight=frequency_weight,
                priority_score=priority_score,
            )
        )

    return final_rows


def _print_client_line(row: ClientPriorityRow) -> None:
    avg = _format_float(row.average_interval_days)
    expected = _format_date(row.expected_visit_date)

    revenue_band = _band(row.monetary_score)
    delay_band = _band(row.delay_weight * 100.0)
    visits_band = _band(row.frequency_score)

    print(
        " | ".join(
            [
                f"Name: {row.name}",
                f"Phone: {row.phone}",
                f"Priority Score: {row.priority_score:.1f}",
                f"Revenue: {row.total_revenue:.2f}",
                f"Visits: {row.total_visits}",
                f"Delay: {row.delay_days}",
                f"Average Interval: {avg}",
                f"Expected Visit Date: {expected}",
                (
                    f"Explain score: Priority: {row.priority_score:.1f} "
                    f"because Revenue: {revenue_band}, Delay: {delay_band}, Visits: {visits_band}"
                ),
            ]
        )
    )


def main() -> int:
    rows = _collect_priority_rows()
    rows.sort(key=lambda r: r.priority_score, reverse=True)
    top20 = rows[:20]

    print("TOP 20 CLIENTS BY BUSINESS PRIORITY")
    for row in top20:
        _print_client_line(row)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())