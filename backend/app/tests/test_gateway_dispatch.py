"""Capability dispatch, dry-run behaviour and rate limiting.

These cover the three properties ADR-002 requires of the connector layer and
that `execute()` alone does not provide.
"""

import pytest

from app.integrations.gateway import capabilities
from app.integrations.gateway.base_connector import BaseConnector
from app.integrations.gateway.connector_gateway import ConnectorGateway
from app.integrations.gateway.rate_limit import RateLimiter, RateLimitExceeded
from app.integrations.gateway.results import STATUS_DRY_RUN, STATUS_ERROR, STATUS_OK


class FakeChannel(BaseConnector):
    """A message channel that may or may not hold a token."""

    def __init__(self, name: str, token: str = "", *, min_interval: float = 0.0):
        self.integration_name = name
        self.token = token
        self.min_interval_seconds = min_interval
        self.sent: list[dict] = []

    @property
    def capabilities(self) -> set[str]:
        return {capabilities.MESSAGE_SEND}

    def is_configured(self) -> bool:
        return bool(self.token)

    def missing_configuration(self) -> tuple[str, ...]:
        return () if self.token else (f"{self.integration_name.upper()}_TOKEN",)

    def rate_limit_key(self, capability, payload):
        return f"{self.integration_name}:{(payload or {}).get('chat_id', '-')}"

    def execute(self, capability, *, payload=None):
        self.sent.append(payload or {})
        return {"delivered_to": (payload or {}).get("chat_id")}


class ExplodingChannel(FakeChannel):
    def execute(self, capability, *, payload=None):
        raise RuntimeError("platform said no")


class AsyncChannel(FakeChannel):
    async def _call(self):
        return "never awaited"

    def execute(self, capability, *, payload=None):
        return self._call()


# ---------------------------------------------------------------- dry run


def test_unconfigured_connector_reports_dry_run_and_sends_nothing():
    gateway = ConnectorGateway()
    channel = FakeChannel("telegram")  # no token
    gateway.register(channel)

    result = gateway.dispatch(capabilities.MESSAGE_SEND, {"text": "hi"})

    assert result.status == STATUS_DRY_RUN
    assert result.ok is True, "a dry run is not a failure"
    assert result.delivered is False, "but nothing actually left the building"
    assert channel.sent == []
    assert result.request == {"text": "hi"}


def test_dry_run_names_the_missing_setting_but_never_a_value():
    gateway = ConnectorGateway()
    gateway.register(FakeChannel("telegram"))

    result = gateway.dispatch(capabilities.MESSAGE_SEND, {"text": "hi"})

    assert "TELEGRAM_TOKEN" in result.data["reason"]


def test_configured_connector_actually_sends():
    gateway = ConnectorGateway()
    channel = FakeChannel("telegram", token="secret")
    gateway.register(channel)

    result = gateway.dispatch(capabilities.MESSAGE_SEND, {"chat_id": 42, "text": "hi"})

    assert result.status == STATUS_OK
    assert result.delivered is True
    assert channel.sent == [{"chat_id": 42, "text": "hi"}]


# ------------------------------------------------------------- resolution


def test_configured_provider_wins_over_unconfigured_one():
    gateway = ConnectorGateway()
    gateway.register(FakeChannel("telegram"))  # registered first, no token
    gateway.register(FakeChannel("whatsapp", token="t"))

    result = gateway.dispatch(capabilities.MESSAGE_SEND, {"text": "hi"})

    assert result.connector == "whatsapp"
    assert result.status == STATUS_OK


def test_prefer_pins_the_provider():
    gateway = ConnectorGateway()
    gateway.register(FakeChannel("telegram", token="t"))
    gateway.register(FakeChannel("whatsapp", token="t"))

    result = gateway.dispatch(capabilities.MESSAGE_SEND, {"text": "hi"}, prefer="whatsapp")

    assert result.connector == "whatsapp"


def test_prefer_an_integration_that_does_not_provide_the_capability_is_an_error():
    gateway = ConnectorGateway()
    gateway.register(FakeChannel("telegram", token="t"))

    result = gateway.dispatch(capabilities.MESSAGE_SEND, {}, prefer="carrier-pigeon")

    assert result.status == STATUS_ERROR
    assert "carrier-pigeon" in result.error


def test_capability_with_no_provider_is_an_error_not_a_crash():
    gateway = ConnectorGateway()

    result = gateway.dispatch(capabilities.MESSAGE_SEND, {"text": "hi"})

    assert result.status == STATUS_ERROR
    assert "no connector provides it" in result.error


# ----------------------------------------------------------------- failure


def test_connector_exception_becomes_a_result_and_never_escapes():
    gateway = ConnectorGateway()
    gateway.register(ExplodingChannel("telegram", token="t"))

    result = gateway.dispatch(capabilities.MESSAGE_SEND, {"text": "hi"})

    assert result.status == STATUS_ERROR
    assert result.ok is False
    assert "platform said no" in result.error


def test_async_connector_on_the_dispatch_path_is_reported_not_leaked():
    gateway = ConnectorGateway()
    gateway.register(AsyncChannel("openai-ish", token="t"))

    result = gateway.dispatch(capabilities.MESSAGE_SEND, {})

    assert result.status == STATUS_ERROR
    assert "execute_async" in result.error


# -------------------------------------------------------------- rate limit


def test_rate_limiter_spaces_calls_in_the_same_bucket():
    slept: list[float] = []
    now = [0.0]
    limiter = RateLimiter(clock=lambda: now[0], sleeper=slept.append)

    assert limiter.acquire("telegram:42", 1.0) == 0.0
    waited = limiter.acquire("telegram:42", 1.0)

    assert waited == pytest.approx(1.0)
    assert slept == [pytest.approx(1.0)]


def test_rate_limiter_keeps_separate_buckets_independent():
    slept: list[float] = []
    limiter = RateLimiter(clock=lambda: 0.0, sleeper=slept.append)

    limiter.acquire("telegram:42", 1.0)
    limiter.acquire("telegram:99", 1.0)

    assert slept == [], "a busy chat must not throttle a different chat"


def test_rate_limiter_refuses_to_wait_longer_than_max_wait():
    limiter = RateLimiter(max_wait=0.5, clock=lambda: 0.0, sleeper=lambda _: None)
    limiter.acquire("altegio", 2.0)

    with pytest.raises(RateLimitExceeded):
        limiter.acquire("altegio", 2.0)


def test_dispatch_reports_rate_limiting_instead_of_raising():
    limiter = RateLimiter(max_wait=0.0, clock=lambda: 0.0, sleeper=lambda _: None)
    gateway = ConnectorGateway(rate_limiter=limiter)
    channel = FakeChannel("telegram", token="t", min_interval=1.0)
    gateway.register(channel)

    first = gateway.dispatch(capabilities.MESSAGE_SEND, {"chat_id": 1, "text": "a"})
    second = gateway.dispatch(capabilities.MESSAGE_SEND, {"chat_id": 1, "text": "b"})

    assert first.status == STATUS_OK
    assert second.status == STATUS_ERROR
    assert "rate limited" in second.error
    assert len(channel.sent) == 1, "the throttled message must not reach the platform"


def test_dispatch_rate_limits_per_chat_not_per_bot():
    limiter = RateLimiter(max_wait=0.0, clock=lambda: 0.0, sleeper=lambda _: None)
    gateway = ConnectorGateway(rate_limiter=limiter)
    channel = FakeChannel("telegram", token="t", min_interval=1.0)
    gateway.register(channel)

    first = gateway.dispatch(capabilities.MESSAGE_SEND, {"chat_id": 1, "text": "a"})
    other = gateway.dispatch(capabilities.MESSAGE_SEND, {"chat_id": 2, "text": "b"})

    assert first.status == STATUS_OK
    assert other.status == STATUS_OK


# -------------------------------------------------------------------- status


def test_status_reports_configuration_without_leaking_secrets():
    gateway = ConnectorGateway()
    gateway.register(FakeChannel("telegram"))
    gateway.register(FakeChannel("whatsapp", token="super-secret"))

    status = gateway.status()
    by_name = {i["name"]: i for i in status["integrations"]}

    assert by_name["telegram"]["configured"] is False
    assert by_name["telegram"]["missing_configuration"] == ["TELEGRAM_TOKEN"]
    assert by_name["whatsapp"]["configured"] is True

    send = status["capabilities"][capabilities.MESSAGE_SEND]
    assert sorted(send["providers"]) == ["telegram", "whatsapp"]
    assert send["configured_providers"] == ["whatsapp"]

    assert "super-secret" not in repr(status)
