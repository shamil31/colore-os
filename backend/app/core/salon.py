"""The salon, described once.

Before this, facts about the business were scattered: currency lived in a
Meta-specific setting, the timezone lived in the container's `TZ`, the name
existed only in Altegio's reply, and nothing agreed. Any integration that
needed one of them either invented it or grew its own copy.

This is the single canonical description. Integrations read it and never
declare their own. A second `*_CURRENCY` setting anywhere is a bug.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings


@dataclass(frozen=True)
class SalonProfile:
    name: str = ""
    country: str = ""
    timezone: str = ""
    currency: str = ""
    language: str = ""
    locale: str = ""

    REQUIRED = ("name", "country", "timezone", "currency", "language", "locale")

    def missing(self) -> tuple[str, ...]:
        """Field names that are not set, as SALON_* setting names."""
        return tuple(
            f"SALON_{field.upper()}"
            for field in self.REQUIRED
            if not getattr(self, field)
        )

    @property
    def is_complete(self) -> bool:
        return not self.missing()

    def describe(self) -> dict[str, str]:
        return {
            "name": self.name,
            "country": self.country,
            "timezone": self.timezone,
            "currency": self.currency,
            "language": self.language,
            "locale": self.locale,
        }


def salon_profile() -> SalonProfile:
    """Read the profile from settings.

    Not cached: settings are monkeypatched in tests and re-read after a
    restart, and this is cheap enough that caching would only add a way to be
    wrong.
    """
    return SalonProfile(
        name=(settings.SALON_NAME or "").strip(),
        country=(settings.SALON_COUNTRY or "").strip().upper(),
        timezone=(settings.SALON_TIMEZONE or "").strip(),
        currency=(settings.SALON_CURRENCY or "").strip().upper(),
        language=(settings.SALON_LANGUAGE or "").strip().lower(),
        locale=(settings.SALON_LOCALE or "").strip(),
    )


def salon_currency() -> str:
    """The only source of currency in the platform.

    Anything that needs a currency asks here. An empty answer means the salon
    has not been configured, and callers must omit the amount rather than
    guess one — a wrong currency misstates every value by orders of magnitude.
    """
    return salon_profile().currency
