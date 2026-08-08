"""Load the salon's real operating data from Altegio.

Read-only. Altegio stays the system of record; Coloré OS writes nothing to it
(ADR-002 decision 6).

Every fetch either produces data or an explicit, quoted failure. A partially
loaded snapshot reports exactly which datasets are missing and why, because
analytics computed on a silently short dataset is worse than no analytics.

The company id is resolved from `/companies` at load time rather than read from
`ALTEGIO_COMPANY_ID`. That setting was found stale on 2026-08-08 — it held
`2403`, and Altegio answers "No location with identifier 2403 found". A
mismatch is reported rather than silently preferred either way.
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

from app.core.config import settings
from app.integrations.connectors.altegio_connector import AltegioConnector
from app.integrations.gateway.connector_gateway import ConnectorGateway
from app.integrations.gateway.factory import get_connector_gateway

logger = logging.getLogger("colore.business")

CACHE_TTL_SECONDS = 300
"""Altegio allows 5 req/sec; a snapshot costs several calls. Repeated questions
within five minutes reuse the answer instead of re-billing the salon's quota."""

# Official Altegio visit statuses. Source: Altegio support, "Appointments" —
# "Appointment status (number): No-show = -1, Pending = 0, Arrived = 1,
# Confirmed = 2".
ATTENDANCE_NO_SHOW = -1
ATTENDANCE_PENDING = 0
ATTENDANCE_ARRIVED = 1
ATTENDANCE_CONFIRMED = 2

ATTENDANCE_LABELS = {
    ATTENDANCE_NO_SHOW: "не пришёл",
    ATTENDANCE_PENDING: "ожидает",
    ATTENDANCE_ARRIVED: "пришёл",
    ATTENDANCE_CONFIRMED: "подтверждена",
}


@dataclass
class BusinessSnapshot:
    """What the salon actually looks like right now, or why it is not known."""

    company_id: int | None = None
    company_title: str = ""
    services: list[Any] = field(default_factory=list)
    staff: list[Any] = field(default_factory=list)
    clients: list[dict[str, Any]] = field(default_factory=list)
    records: list[dict[str, Any]] = field(default_factory=list)

    date_from: str = ""
    date_to: str = ""

    errors: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    loaded_at: float = 0.0

    @property
    def connected(self) -> bool:
        """True when Altegio answered at all."""
        return self.company_id is not None

    @property
    def complete(self) -> bool:
        return self.connected and not self.errors

    def missing_datasets(self) -> list[str]:
        missing = []
        if not self.services:
            missing.append("услуги")
        if not self.staff:
            missing.append("мастера")
        if not self.clients:
            missing.append("клиенты")
        if not self.records:
            missing.append("записи")
        return missing


def normalise_phone(value: Any) -> str:
    """Digits only, for comparing a WhatsApp wa_id with an Altegio phone.

    Altegio stores phones inconsistently (`+381…`, `381…`, spaces, dashes) and
    a wa_id is bare digits with a country code. Reducing both to digits is the
    only comparison that holds across those forms.
    """
    if value is None:
        return ""
    return re.sub(r"\D", "", str(value))


def phone_key(value: Any) -> str:
    """Last 9 digits — the part that survives country-code inconsistency.

    Serbian and Russian numbers are stored here both with and without the
    leading country code. Nine digits is short enough to match across that and
    long enough that a collision inside one salon's 334 clients is not a
    practical concern.
    """
    digits = normalise_phone(value)
    return digits[-9:] if len(digits) >= 9 else digits


def _dispatch(gateway: ConnectorGateway, capability: str, payload: dict[str, Any]):
    return gateway.dispatch(capability, payload, prefer="altegio")


def load_snapshot(
    *,
    days: int = 30,
    gateway: ConnectorGateway | None = None,
    today: date | None = None,
) -> BusinessSnapshot:
    gateway = gateway or get_connector_gateway()
    today = today or date.today()

    snapshot = BusinessSnapshot(
        date_from=(today - timedelta(days=days)).isoformat(),
        date_to=today.isoformat(),
        loaded_at=time.time(),
    )

    connector = None
    try:
        connector = gateway.integration_registry.get("altegio")
    except KeyError:
        snapshot.errors.append("коннектор Altegio не зарегистрирован")
        return snapshot

    if not connector.is_configured():
        missing = ", ".join(connector.missing_configuration())
        snapshot.errors.append(f"Altegio не настроен — отсутствует: {missing}")
        return snapshot

    companies = _dispatch(gateway, AltegioConnector.GET_COMPANIES_CAPABILITY, {})
    if not companies.ok or not companies.data:
        snapshot.errors.append(
            f"не удалось получить список филиалов: {companies.error or 'пустой ответ'}"
        )
        return snapshot

    company = companies.data[0]
    snapshot.company_id = company.location_id
    snapshot.company_title = company.title or company.name or ""

    configured = str(getattr(settings, "ALTEGIO_COMPANY_ID", "") or "").strip()
    if configured and configured != str(snapshot.company_id):
        snapshot.notes.append(
            f"ALTEGIO_COMPANY_ID={configured} не совпадает с реальным "
            f"{snapshot.company_id} — используется значение из API"
        )

    cid = snapshot.company_id

    services = _dispatch(gateway, AltegioConnector.GET_SERVICES_CAPABILITY, {"company_id": cid})
    if services.ok:
        snapshot.services = services.data or []
    else:
        snapshot.errors.append(f"услуги: {services.error}")

    staff = _dispatch(gateway, AltegioConnector.GET_STAFF_CAPABILITY, {"company_id": cid})
    if staff.ok:
        snapshot.staff = staff.data or []
    else:
        snapshot.errors.append(f"мастера: {staff.error}")

    clients = _dispatch(
        gateway,
        AltegioConnector.GET_ALL_CLIENTS_RAW_CAPABILITY,
        {"company_id": cid, "page_size": 200},
    )
    if clients.ok:
        snapshot.clients = clients.data or []
    else:
        snapshot.errors.append(f"клиенты: {clients.error}")

    records = _dispatch(
        gateway,
        AltegioConnector.GET_RECORDS_RANGE_CAPABILITY,
        {
            "company_id": cid,
            "date_from": snapshot.date_from,
            "date_to": snapshot.date_to,
            "page_size": 200,
        },
    )
    if records.ok:
        snapshot.records = [r for r in (records.data or []) if not r.get("deleted")]
    else:
        snapshot.errors.append(f"записи: {records.error}")

    return snapshot


_cache: tuple[int, BusinessSnapshot] | None = None


def cached_snapshot(*, days: int = 30, force: bool = False) -> BusinessSnapshot:
    global _cache

    if not force and _cache is not None:
        cached_days, snapshot = _cache
        if cached_days == days and (time.time() - snapshot.loaded_at) < CACHE_TTL_SECONDS:
            return snapshot

    snapshot = load_snapshot(days=days)
    _cache = (days, snapshot)
    return snapshot


def reset_cache() -> None:
    global _cache
    _cache = None
