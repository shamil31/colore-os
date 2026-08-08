"""One canonical salon configuration, and nothing duplicating it.

The last group is structural: it fails if anyone reintroduces a
currency literal or a second currency setting anywhere in the application.
"""

from pathlib import Path

import pytest

from app.core.config import settings
from app.core.salon import SalonProfile, salon_currency, salon_profile

APP = Path(__file__).resolve().parents[1]


@pytest.fixture
def salon(monkeypatch):
    def configure(**overrides):
        values = {
            "SALON_NAME": "Colore beauty lab",
            "SALON_COUNTRY": "RS",
            "SALON_TIMEZONE": "Europe/Belgrade",
            "SALON_CURRENCY": "RSD",
            "SALON_LANGUAGE": "ru",
            "SALON_LOCALE": "ru_RS",
        }
        values.update(overrides)
        for key, value in values.items():
            monkeypatch.setattr(settings, key, value)
        return salon_profile()

    return configure


# ------------------------------------------------------------------ profile


def test_the_profile_carries_every_required_field(salon):
    profile = salon()

    assert profile.name == "Colore beauty lab"
    assert profile.country == "RS"
    assert profile.timezone == "Europe/Belgrade"
    assert profile.currency == "RSD"
    assert profile.language == "ru"
    assert profile.locale == "ru_RS"
    assert profile.is_complete


def test_values_are_normalised(salon):
    profile = salon(SALON_COUNTRY=" rs ", SALON_CURRENCY=" rsd ", SALON_LANGUAGE=" RU ")

    assert profile.country == "RS"
    assert profile.currency == "RSD"
    assert profile.language == "ru"


def test_missing_fields_are_named_as_settings(salon):
    profile = salon(SALON_CURRENCY="", SALON_LOCALE="")

    assert profile.is_complete is False
    assert set(profile.missing()) == {"SALON_CURRENCY", "SALON_LOCALE"}


def test_an_empty_profile_reports_every_field(monkeypatch):
    for field in SalonProfile.REQUIRED:
        monkeypatch.setattr(settings, f"SALON_{field.upper()}", "")

    assert len(salon_profile().missing()) == 6


# ----------------------------------------------------------------- currency


def test_currency_has_exactly_one_source(salon):
    salon(SALON_CURRENCY="EUR")

    assert salon_currency() == "EUR"


def test_attribution_reads_currency_from_the_salon_profile(salon):
    from app.growth import attribution

    salon(SALON_CURRENCY="RSD")
    value = attribution._value_of({"services": [{"cost_to_pay": 5500}]})

    assert value == {"value": 5500.0, "currency": "RSD"}


def test_changing_the_salon_currency_changes_every_event(salon):
    from app.growth import attribution

    salon(SALON_CURRENCY="EUR")

    assert attribution._value_of({"services": [{"cost": 47}]})["currency"] == "EUR"


def test_no_currency_means_no_value_rather_than_a_guess(salon):
    from app.growth import attribution

    salon(SALON_CURRENCY="")

    assert attribution._value_of({"services": [{"cost_to_pay": 5500}]}) == {}


# --------------------------------------------------------- no duplication


def _application_sources():
    for path in APP.rglob("*.py"):
        if "tests" in path.parts or "__pycache__" in path.parts:
            continue
        yield path


def test_no_currency_code_is_hardcoded_anywhere():
    """A literal currency in the source is the bug this whole change removes."""
    offenders = []
    for path in _application_sources():
        text = path.read_text(encoding="utf-8")
        for code in ("RSD", "EUR", "USD"):
            for quoted in (f'"{code}"', f"'{code}'"):
                if quoted in text:
                    offenders.append(f"{path.relative_to(APP)}: {quoted}")

    assert offenders == [], f"hardcoded currency: {offenders}"


def test_there_is_only_one_currency_setting():
    config = (APP / "core" / "config.py").read_text(encoding="utf-8")
    currency_settings = [
        line.strip()
        for line in config.splitlines()
        if "CURRENCY" in line and ":" in line and not line.strip().startswith("#")
    ]

    assert len(currency_settings) == 1, currency_settings
    assert currency_settings[0].startswith("SALON_CURRENCY")


def test_integrations_do_not_read_salon_settings_directly():
    """Everything goes through app/core/salon.py, so there is one place to change."""
    offenders = []
    for path in _application_sources():
        if path.parts[-2:] == ("core", "salon.py") or path.name in ("config.py", "startup.py"):
            continue
        text = path.read_text(encoding="utf-8")
        if "settings.SALON_" in text:
            offenders.append(str(path.relative_to(APP)))

    assert offenders == [], f"these read SALON_* directly instead of the profile: {offenders}"


# ------------------------------------------------- scheduler stays generic


VENDORS = ("meta", "altegio", "telegram", "instagram", "whatsapp", "openai", "n8n")


def test_the_scheduler_imports_no_integration():
    """Meta must be a registered job, not a special case inside the scheduler.

    Imports and identifiers only — a docstring saying "the scheduler knows
    nothing about Meta" is the opposite of a violation, and a test that cannot
    tell prose from code would force us to stop explaining ourselves.
    """
    import ast

    offenders = []
    for path in (APP / "scheduler").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))

        for node in ast.walk(tree):
            targets = []
            if isinstance(node, ast.Import):
                targets = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                targets = [node.module or ""] + [alias.name for alias in node.names]
            elif isinstance(node, ast.Name):
                targets = [node.id]
            elif isinstance(node, ast.Attribute):
                targets = [node.attr]

            for target in targets:
                lowered = target.lower()
                for vendor in VENDORS:
                    if vendor in lowered:
                        offenders.append(f"{path.name}: {target}")

    assert offenders == [], f"the scheduler references an integration in code: {offenders}"


def test_the_scheduler_does_not_import_growth_or_integrations():
    import ast

    offenders = []
    for path in (APP / "scheduler").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            module = ""
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
            elif isinstance(node, ast.Import):
                module = ",".join(alias.name for alias in node.names)
            if "app.growth" in module or "app.integrations" in module:
                offenders.append(f"{path.name}: {module}")

    assert offenders == [], f"the scheduler reaches into an integration: {offenders}"


def test_the_composition_root_registers_meta():
    from app.core.jobs import build_registry

    assert "meta_conversions" in build_registry().names()
