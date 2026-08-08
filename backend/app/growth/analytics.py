"""Business analytics for the "Аналитика" command.

Two sources, deliberately kept apart:

- **Leads** come from `growth_events` — inbound client messages Growth AI
  captured. This is Coloré OS's own data.
- **Bookings** come from Altegio, the system of record.

Conversion is the hard part, and the place where a plausible number would be a
lie. Dividing bookings by leads answers a question nobody asked: most of the
salon's bookings have nothing to do with Growth AI. A conversion figure is only
reported for leads that can actually be **attributed** to a booking, and the
number of leads that could not be attributed — with the reason — is reported
next to it, every time.

Attribution today is a phone match: a WhatsApp `wa_id` is a phone number, so it
joins to an Altegio client. An Instagram `IGSID` is app-scoped and joins to
nothing, which is a stated limitation rather than a silent zero.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any

from app.growth.business_data import (
    ATTENDANCE_ARRIVED,
    ATTENDANCE_LABELS,
    ATTENDANCE_NO_SHOW,
    BusinessSnapshot,
    cached_snapshot,
    phone_key,
)
from app.models.growth import STATUS_PROCESSED, GrowthEvent

logger = logging.getLogger("colore.analytics")

SOURCE_WHATSAPP = "whatsapp"


@dataclass
class LeadStats:
    total: int = 0
    by_source: dict[str, int] = field(default_factory=dict)
    attributable: int = 0
    unattributable: dict[str, int] = field(default_factory=dict)
    error: str = ""


@dataclass
class BookingStats:
    total: int = 0
    by_attendance: dict[int, int] = field(default_factory=dict)
    online: int = 0
    new_clients: int = 0

    @property
    def arrived(self) -> int:
        return self.by_attendance.get(ATTENDANCE_ARRIVED, 0)

    @property
    def no_show(self) -> int:
        return self.by_attendance.get(ATTENDANCE_NO_SHOW, 0)


@dataclass
class AnalyticsReport:
    days: int
    date_from: str
    date_to: str

    leads: LeadStats
    bookings: BookingStats
    snapshot: BusinessSnapshot

    converted: int = 0
    missing_data: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    @property
    def conversion_measurable(self) -> bool:
        return self.leads.attributable > 0

    @property
    def conversion(self) -> float | None:
        if not self.conversion_measurable:
            return None
        return self.converted / self.leads.attributable


# ------------------------------------------------------------------- leads


def collect_leads(session_factory, *, since: datetime) -> tuple[LeadStats, list[GrowthEvent]]:
    stats = LeadStats()

    try:
        session = session_factory()
    except Exception as exc:  # noqa: BLE001
        stats.error = f"нет доступа к базе Coloré OS: {type(exc).__name__}"
        return stats, []

    try:
        events = (
            session.query(GrowthEvent)
            .filter(
                GrowthEvent.status == STATUS_PROCESSED,
                GrowthEvent.received_at >= since,
            )
            .all()
        )
    except Exception as exc:  # noqa: BLE001
        stats.error = f"не удалось прочитать growth_events: {type(exc).__name__}"
        return stats, []
    finally:
        session.close()

    stats.total = len(events)

    for event in events:
        stats.by_source[event.source] = stats.by_source.get(event.source, 0) + 1

        if event.source == SOURCE_WHATSAPP and phone_key(event.sender_ref):
            stats.attributable += 1
        else:
            reason = (
                "Instagram IGSID не является телефоном"
                if event.source == "instagram"
                else f"нет телефона в источнике «{event.source}»"
            )
            stats.unattributable[reason] = stats.unattributable.get(reason, 0) + 1

    return stats, events


# ----------------------------------------------------------------- bookings


def collect_bookings(snapshot: BusinessSnapshot) -> BookingStats:
    stats = BookingStats(total=len(snapshot.records))

    for record in snapshot.records:
        attendance = record.get("attendance")
        if isinstance(attendance, int):
            stats.by_attendance[attendance] = stats.by_attendance.get(attendance, 0) + 1

        if record.get("from_url"):
            stats.online += 1

        client = record.get("client") or {}
        if client.get("is_new"):
            stats.new_clients += 1

    return stats


# -------------------------------------------------------------- attribution


def _parse_created(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    return parsed.replace(tzinfo=None) if parsed.tzinfo else parsed


def attribute(events: list[GrowthEvent], snapshot: BusinessSnapshot) -> int:
    """Leads that produced a booking created after the lead arrived.

    "After" matters: a client who already had an appointment on the books and
    then messaged did not convert because of that message.
    """
    bookings_by_phone: dict[str, list[datetime]] = {}

    for record in snapshot.records:
        client = record.get("client") or {}
        key = phone_key(client.get("phone"))
        if not key:
            continue
        created = _parse_created(record.get("create_date"))
        if created is None:
            continue
        bookings_by_phone.setdefault(key, []).append(created)

    converted = 0
    for event in events:
        if event.source != SOURCE_WHATSAPP:
            continue
        key = phone_key(event.sender_ref)
        if not key:
            continue

        arrived_at = event.received_at
        if any(created >= arrived_at for created in bookings_by_phone.get(key, [])):
            converted += 1

    return converted


# ------------------------------------------------------- gaps and advice


def find_missing_data(report: AnalyticsReport) -> list[str]:
    """Only gaps that were actually observed on this run."""
    missing: list[str] = []
    snapshot = report.snapshot

    if not snapshot.connected:
        missing.append("Altegio не отвечает — бизнес-данных нет вообще")
        return missing

    for error in snapshot.errors:
        missing.append(f"Altegio: {error}")

    for note in snapshot.notes:
        missing.append(f"Конфигурация: {note}")

    if report.leads.error:
        missing.append(report.leads.error)

    if report.leads.total == 0:
        missing.append(
            "Лидов за период нет: Meta не подключена, входящие сообщения "
            "клиентов в Coloré OS не поступают"
        )

    for reason, count in sorted(report.leads.unattributable.items()):
        missing.append(f"{count} лид(ов) невозможно связать с записью — {reason}")

    missing.append(
        "Нет данных о рекламе: Marketing API не подключён, поэтому расходы, "
        "стоимость лида и ROAS не считаются"
    )

    if snapshot.records and not any(
        isinstance(r.get("create_date"), str) for r in snapshot.records
    ):
        missing.append("У записей нет create_date — момент создания записи неизвестен")

    return missing


def build_recommendations(report: AnalyticsReport) -> list[str]:
    """Derived from the gaps above by rule. Never generated text."""
    advice: list[str] = []
    snapshot = report.snapshot

    if not snapshot.connected:
        advice.append(
            "Проверить доступ к Altegio: без него аналитика невозможна "
            "(см. docs/operations/GROWTH_AI_SETUP.md)"
        )
        return advice

    if snapshot.notes:
        advice.append(
            "Исправить ALTEGIO_COMPANY_ID в окружении — сейчас там значение, "
            "которого нет в Altegio"
        )

    if report.leads.total == 0:
        advice.append(
            "Подключить Meta (n8n workflow + Meta App), иначе лидов в системе "
            "не будет и конверсию считать не из чего — шаги 2–3 в "
            "docs/operations/GROWTH_AI_SETUP.md"
        )

    if report.leads.unattributable:
        advice.append(
            "Связать личности между каналами: без сопоставления Instagram-лида "
            "с клиентом Altegio конверсия по Instagram не считается "
            "(в research.md это R-001)"
        )

    if report.bookings.no_show:
        share = report.bookings.no_show / report.bookings.total * 100
        advice.append(
            f"Неявки: {report.bookings.no_show} из {report.bookings.total} "
            f"({share:.0f}%) — напоминание перед визитом снизит потери"
        )

    if report.bookings.total and report.bookings.online == 0:
        advice.append(
            "Ни одна запись за период не сделана через онлайн-форму — "
            "источник записей неизвестен, атрибуция рекламы невозможна"
        )

    advice.append(
        "Настроить Conversions API, чтобы подтверждённые визиты возвращались "
        "в Meta как офлайн-конверсии (архитектура в "
        "docs/research/META_BUSINESS_DECISIONS.md)"
    )

    return advice


# ------------------------------------------------------------------- report


def build_report(
    *,
    days: int = 30,
    session_factory=None,
    snapshot: BusinessSnapshot | None = None,
    today: date | None = None,
) -> AnalyticsReport:
    if session_factory is None:
        from app.db.database import SessionLocal

        session_factory = SessionLocal

    today = today or date.today()
    snapshot = snapshot if snapshot is not None else cached_snapshot(days=days)

    since = datetime.combine(today - timedelta(days=days), datetime.min.time())
    leads, events = collect_leads(session_factory, since=since)
    bookings = collect_bookings(snapshot)

    report = AnalyticsReport(
        days=days,
        date_from=snapshot.date_from or (today - timedelta(days=days)).isoformat(),
        date_to=snapshot.date_to or today.isoformat(),
        leads=leads,
        bookings=bookings,
        snapshot=snapshot,
    )
    report.converted = attribute(events, snapshot)
    report.missing_data = find_missing_data(report)
    report.recommendations = build_recommendations(report)

    return report


# -------------------------------------------------------------- rendering


def render(report: AnalyticsReport) -> str:
    snapshot = report.snapshot
    lines = [f"📈 АНАЛИТИКА — {report.date_from} … {report.date_to} ({report.days} дн.)", ""]

    if not snapshot.connected:
        lines.append("Бизнес-данные недоступны.")
        lines.append("")
        for error in snapshot.errors:
            lines.append(f"• {error}")
        lines.append("")
        lines.append("Рекомендации:")
        for item in report.recommendations:
            lines.append(f"• {item}")
        return "\n".join(lines)

    lines.append(f"Салон: {snapshot.company_title} (id {snapshot.company_id})")
    lines.append(
        f"В базе: {len(snapshot.clients)} клиент(ов), "
        f"{len(snapshot.services)} услуг, {len(snapshot.staff)} мастер(ов)"
    )
    lines.append("")

    # --- leads
    if report.leads.error:
        lines.append(f"Лиды: {report.leads.error}")
    else:
        lines.append(f"Лиды (входящие обращения в Coloré OS): {report.leads.total}")
        for source, count in sorted(report.leads.by_source.items()):
            lines.append(f"   • {source}: {count}")
    lines.append("")

    # --- bookings
    lines.append(f"Записи в Altegio: {report.bookings.total}")
    for attendance, count in sorted(report.bookings.by_attendance.items()):
        label = ATTENDANCE_LABELS.get(attendance, f"статус {attendance}")
        lines.append(f"   • {label}: {count}")
    if report.bookings.total:
        lines.append(f"   • через онлайн-запись: {report.bookings.online}")
        lines.append(f"   • новых клиентов: {report.bookings.new_clients}")
    lines.append("")

    # --- conversion
    if report.conversion_measurable:
        percent = report.conversion * 100
        lines.append(
            f"Конверсия: {report.converted} из {report.leads.attributable} "
            f"сопоставимых лидов = {percent:.0f}%"
        )
        lines.append(
            "   считается только по лидам, которых удалось связать с клиентом "
            "Altegio по телефону"
        )
    else:
        lines.append("Конверсия: не рассчитывается.")
        lines.append(
            "   ни один лид за период нельзя связать с записью в Altegio, "
            "поэтому любое число здесь было бы выдуманным"
        )
    lines.append("")

    # --- gaps
    lines.append("Чего не хватает:")
    for item in report.missing_data:
        lines.append(f"• {item}")
    lines.append("")

    lines.append("Рекомендации:")
    for item in report.recommendations:
        lines.append(f"• {item}")

    return "\n".join(lines)
