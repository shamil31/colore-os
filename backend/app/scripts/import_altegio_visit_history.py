from __future__ import annotations

import os
from collections.abc import Iterable
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.integrations.altegio import (
    AltegioAuthClient,
    AltegioCredentials,
    AltegioDataClient,
    AltegioEndpoints,
    AltegioHttpClient,
    AltegioRequestError,
)
from app.models.revenue_client import RevenueClient
from app.models.revenue_client_visit import RevenueClientVisit


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required env var: {name}")
    return value


def _resolve_company_id(data_client: AltegioDataClient) -> int:
    companies = data_client.get_companies()
    if not companies:
        raise ValueError("No companies returned by Altegio")

    location_ids = {company.location_id for company in companies}
    company_env = os.getenv("ALTEGIO_COMPANY_ID")
    if company_env and int(company_env) in location_ids:
        return int(company_env)

    return companies[0].location_id


def _coerce_int(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def _coerce_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        normalized = value.replace(" ", "").replace(",", ".")
        try:
            return float(normalized)
        except ValueError:
            return None
    return None


def _parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None

    text = value.strip()
    candidates = [text]
    if text.endswith("Z"):
        candidates.append(text[:-1] + "+00:00")

    for item in candidates:
        try:
            dt = datetime.fromisoformat(item)
            if dt.tzinfo is not None:
                return dt.astimezone(timezone.utc).replace(tzinfo=None)
            return dt
        except ValueError:
            continue

    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue

    return None


def _pick_first_string(source: dict[str, Any], keys: Iterable[str]) -> str | None:
    for key in keys:
        value = source.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _pick_services(source: dict[str, Any]) -> list | dict | None:
    services = source.get("services")
    if isinstance(services, (list, dict)):
        return services
    return None


def _pick_master(source: dict[str, Any]) -> str | None:
    direct = _pick_first_string(source, ("master", "staff_name", "employee_name"))
    if direct:
        return direct

    staff = source.get("staff")
    if isinstance(staff, dict):
        return _pick_first_string(staff, ("name", "fullname", "title"))
    return None


def _pick_amount(source: dict[str, Any]) -> float | None:
    for key in ("amount", "cost", "total", "paid", "paid_full", "sum"):
        value = _coerce_float(source.get(key))
        if value is not None:
            return value

    services = source.get("services")
    if isinstance(services, list):
        total = 0.0
        seen = False
        for item in services:
            if not isinstance(item, dict):
                continue
            value = _coerce_float(item.get("cost") or item.get("amount") or item.get("price"))
            if value is None:
                continue
            seen = True
            total += value
        if seen:
            return total

    return None


def _pick_status(source: dict[str, Any]) -> str | None:
    raw = source.get("visit_status")
    if isinstance(raw, str) and raw.strip():
        return raw.strip()

    status = source.get("status")
    if isinstance(status, str) and status.strip():
        return status.strip()

    attendance = source.get("attendance")
    if isinstance(attendance, int):
        return str(attendance)

    return None


def _pick_visit_date(source: dict[str, Any]) -> datetime | None:
    for key in ("datetime", "visit_date", "date", "start_time", "time"):
        dt = _parse_datetime(source.get(key))
        if dt is not None:
            return dt
    return None


def _incremental_date_from(client: RevenueClient) -> str | None:
    if client.visit_history_synced_at is None:
        return None

    if client.last_visit_date is None and client.visit_history_synced_at is not None:
        return None

    if client.last_visit_date and client.visit_history_synced_at >= client.last_visit_date:
        return None

    if client.last_visit_date is None:
        return None

    return (client.last_visit_date - timedelta(days=1)).date().isoformat()


def _upsert_visit(
    db: Session,
    *,
    revenue_client_id: int,
    source: dict[str, Any],
) -> bool:
    record_id = _coerce_int(source.get("id") or source.get("record_id"))
    if record_id is None:
        raise ValueError("Visit payload has no numeric id")

    visit = db.query(RevenueClientVisit).filter(RevenueClientVisit.altegio_record_id == record_id).first()
    is_created = visit is None

    if visit is None:
        visit = RevenueClientVisit(
            revenue_client_id=revenue_client_id,
            altegio_record_id=record_id,
        )

    visit.revenue_client_id = revenue_client_id
    visit.last_visit_date = _pick_visit_date(source)
    visit.services = _pick_services(source)
    visit.master = _pick_master(source)
    visit.amount = _pick_amount(source)
    visit.visit_status = _pick_status(source)
    visit.raw_data = source

    if is_created:
        db.add(visit)

    return is_created


def _rebuild_previous_visit_dates(db: Session, revenue_client_id: int) -> None:
    visits = (
        db.query(RevenueClientVisit)
        .filter(RevenueClientVisit.revenue_client_id == revenue_client_id)
        .order_by(RevenueClientVisit.last_visit_date.asc(), RevenueClientVisit.id.asc())
        .all()
    )

    previous: datetime | None = None
    for visit in visits:
        visit.previous_visit_date = previous
        if visit.last_visit_date is not None:
            previous = visit.last_visit_date


def main() -> int:
    base_url = os.getenv("ALTEGIO_BASE_URL", "https://api.alteg.io/api")
    partner_token = os.getenv("ALTEGIO_PARTNER_TOKEN")

    if not partner_token:
        print("ERROR: Missing required env var: ALTEGIO_PARTNER_TOKEN")
        return 1

    try:
        credentials = AltegioCredentials(
            login=_required_env("ALTEGIO_LOGIN"),
            password=_required_env("ALTEGIO_PASSWORD"),
        )
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1

    endpoints = AltegioEndpoints(base_url=base_url)
    http_client = AltegioHttpClient(timeout=int(os.getenv("ALTEGIO_TIMEOUT", "20")))

    try:
        auth_client = AltegioAuthClient(
            endpoints=endpoints,
            partner_token=partner_token,
            credentials=credentials,
            http_client=http_client,
        )
        token = auth_client.authenticate()

        data_client = AltegioDataClient(
            endpoints=endpoints,
            partner_token=partner_token,
            token=token,
            http_client=http_client,
        )

        company_id = _resolve_company_id(data_client)
        page_size = int(os.getenv("ALTEGIO_VISITS_PAGE_SIZE", "200"))

        imported_total = 0
        inserted_total = 0
        updated_total = 0

        with SessionLocal() as db:
            clients = (
                db.query(RevenueClient)
                .filter(RevenueClient.company_id == company_id)
                .filter(RevenueClient.is_active.is_(True))
                .all()
            )

            now = datetime.utcnow()

            for client in clients:
                date_from = _incremental_date_from(client)
                visits_raw = data_client.get_all_client_records_raw(
                    company_id,
                    client_id=client.altegio_client_id,
                    page_size=page_size,
                    date_from=date_from,
                )

                if not visits_raw:
                    client.visit_history_synced_at = now
                    continue

                for item in visits_raw:
                    if _upsert_visit(db, revenue_client_id=client.id, source=item):
                        inserted_total += 1
                    else:
                        updated_total += 1
                    imported_total += 1

                _rebuild_previous_visit_dates(db, client.id)
                client.visit_history_synced_at = now

            db.commit()

        print("VISIT_HISTORY: WORKING")
        print(f"Imported: {imported_total}")
        print(f"Inserted: {inserted_total}")
        print(f"Updated: {updated_total}")

        return 0
    except (AltegioRequestError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
