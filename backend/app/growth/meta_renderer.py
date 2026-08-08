from __future__ import annotations

from datetime import date, datetime

from app.growth.meta_sync import MetaStatus
from app.growth.response_builder import ResponseBuilder

MISSING_EXPLANATIONS = {
    "META_ACCESS_TOKEN": "system user access token — Meta App Dashboard → System Users",
    "META_DATASET_ID": "dataset (offline event set) id — Events Manager",
    "META_VERIFY_TOKEN": "webhook verify token — any string you choose, given to Meta",
    "META_APP_SECRET": "app secret — Meta App Dashboard → Settings → Basic",
}

OUTCOME_LABELS = {
    "lead_created": "Lead created",
    "appointment_booked": "Appointment booked",
    "appointment_cancelled": "Appointment cancelled",
    "client_arrived": "Client arrived",
    "no_show": "No-show",
}


class MetaRenderer:
    """Renders `Meta` — never a secret, only names of what is absent."""

    def render(self, status: MetaStatus, *, limit: int, now: datetime | None = None) -> str:
        builder = ResponseBuilder().heading("🔗 META STATUS")

        builder.section("Connected")
        builder.line("YES" if status.connected else "NO")

        builder.section("Events waiting")
        builder.line(str(status.waiting))
        for outcome, count in sorted(status.by_outcome.items()):
            builder.detail(f"{OUTCOME_LABELS.get(outcome, outcome)}: {count}")

        builder.section("Events sent")
        builder.line(str(status.sent))

        builder.section("Accepted")
        builder.line(str(status.accepted))

        builder.section("Rejected")
        builder.line(str(status.rejected))

        builder.section("Last synchronization")
        builder.line(self._when(status.last_sync, now=now))

        if not status.connected:
            builder.section("Missing configuration")
            for name in dict.fromkeys(status.missing):
                explanation = MISSING_EXPLANATIONS.get(name, "")
                builder.bullet(f"{name} — {explanation}" if explanation else name)
            builder.line()
            builder.line(
                "Events are queued, not lost. They will be sent once these exist."
            )

        if status.errors:
            builder.section("Problems")
            for error in dict.fromkeys(status.errors):
                builder.bullet(error)

        return builder.build(limit=limit)

    def _when(self, moment: datetime | None, *, now: datetime | None = None) -> str:
        if moment is None:
            return "never"

        now = now or datetime.utcnow()
        stamp = moment.strftime("%H:%M")

        if moment.date() == now.date():
            return f"Today {stamp}"
        if moment.date() == now.date() - _one_day():
            return f"Yesterday {stamp}"
        return moment.strftime("%Y-%m-%d %H:%M")


def _one_day():
    from datetime import timedelta

    return timedelta(days=1)


def today() -> date:
    return date.today()
