from __future__ import annotations

import os
from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.integrations.altegio import AltegioRequestError
from app.integrations.connectors.altegio_connector import AltegioConnector
from app.integrations.gateway import ConnectorGateway
from app.models.revenue_client import RevenueClient


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required env var: {name}")
    return value


def _resolve_company_id(gateway: ConnectorGateway) -> int:
    companies = gateway.execute(
        "altegio",
        AltegioConnector.GET_COMPANIES_CAPABILITY,
    )
    if not companies:
        raise ValueError("No companies returned by Altegio")

    location_ids = {company.location_id for company in companies}
    company_env = os.getenv("ALTEGIO_COMPANY_ID")
    if company_env and int(company_env) in location_ids:
        return int(company_env)

    return companies[0].location_id


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None

    candidates = [value.strip()]
    if value.endswith("Z"):
        candidates.append(value[:-1] + "+00:00")

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
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    return None


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


def _pick_first_string(source: dict[str, Any], keys: Iterable[str]) -> str | None:
    for key in keys:
        value = source.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _pick_full_name(source: dict[str, Any]) -> str | None:
    fullname = _pick_first_string(source, ("fullname", "name", "full_name"))
    if fullname:
        return fullname

    parts = [
        (source.get("first_name") or "").strip(),
        (source.get("last_name") or "").strip(),
    ]
    merged = " ".join([p for p in parts if p])
    return merged or None


def _pick_phone(source: dict[str, Any]) -> str | None:
    for key in ("phone", "mobile", "mobile_phone", "phone_number"):
        value = source.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _upsert_revenue_client(db: Session, company_id: int, source: dict[str, Any]) -> bool:
    altegio_client_id = _coerce_int(source.get("id"))
    if altegio_client_id is None:
        raise ValueError("Client payload has no numeric id")

    record = db.query(RevenueClient).filter(RevenueClient.altegio_client_id == altegio_client_id).first()
    is_created = record is None

    if record is None:
        record = RevenueClient(
            altegio_client_id=altegio_client_id,
            company_id=company_id,
        )

    last_visit_raw = _pick_first_string(source, ("last_visit_date", "last_visit"))
    last_visit_at = _parse_datetime(last_visit_raw)
    first_visit_at = _parse_datetime(_pick_first_string(source, ("first_visit_date", "first_visit")))

    last_service_id = _coerce_int(source.get("last_service_id") or source.get("service_id"))
    total_visits = _coerce_int(source.get("total_visits") or source.get("visits_count"))
    total_spent = _coerce_float(source.get("total_spent") or source.get("spent") or source.get("money_spent"))

    record.company_id = company_id
    record.full_name = _pick_full_name(source)
    record.phone = _pick_phone(source)
    record.email = _pick_first_string(source, ("email", "mail"))
    record.birthday = _pick_first_string(source, ("birthday", "birth_date", "birthdate"))
    record.last_visit_date = last_visit_at
    record.first_visit_date = first_visit_at
    record.master_id = _coerce_int(source.get("master_id"))
    record.last_service_id = last_service_id
    record.total_visits = total_visits
    record.total_spent = total_spent
    record.raw_data = source

    record.last_visit_at = last_visit_at
    record.last_service_name = _pick_first_string(source, ("service", "category", "last_service_name"))
    record.visit_count = total_visits
    record.is_active = True

    if is_created:
        db.add(record)

    return is_created


def main() -> int:
    base_url = os.getenv("ALTEGIO_BASE_URL", "https://api.alteg.io/api")
    partner_token = os.getenv("ALTEGIO_PARTNER_TOKEN")

    if not partner_token:
        print("ERROR: Missing required env var: ALTEGIO_PARTNER_TOKEN")
        return 1

    try:
        login = _required_env("ALTEGIO_LOGIN")
        password = _required_env("ALTEGIO_PASSWORD")
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1

    gateway = ConnectorGateway()
    gateway.register(
        AltegioConnector(
            base_url=base_url,
            partner_token=partner_token,
            login=login,
            password=password,
            timeout=int(os.getenv("ALTEGIO_TIMEOUT", "20")),
        )
    )

    try:
        gateway.execute(
            "altegio",
            AltegioConnector.AUTHENTICATE_CAPABILITY,
        )

        company_id = _resolve_company_id(gateway)
        page_size = int(os.getenv("ALTEGIO_CLIENTS_PAGE_SIZE", "200"))
        remote_clients = gateway.execute(
            "altegio",
            AltegioConnector.GET_ALL_CLIENTS_RAW_CAPABILITY,
            payload={
                "company_id": company_id,
                "page_size": page_size,
            },
        )

        created = 0
        updated = 0

        with SessionLocal() as db:
            for remote_client in remote_clients:
                if _upsert_revenue_client(db, company_id, remote_client):
                    created += 1
                else:
                    updated += 1

            db.commit()

        print("CLIENTS: WORKING")
        print(f"Downloaded: {len(remote_clients)}")
        print(f"Inserted: {created}")
        print(f"Updated: {updated}")

        first_client = remote_clients[0] if remote_clients else None
        last_client = remote_clients[-1] if remote_clients else None
        available_fields = sorted({key for client in remote_clients for key in client.keys()})

        print(f"First client: {first_client}")
        print(f"Last client: {last_client}")
        print(f"Available fields: {available_fields}")

        return 0
    except (AltegioRequestError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
