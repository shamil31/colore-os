"""P0-005: every route exposing business data requires X-Colore-Api-Key.

The defect this closes: five routes — /growth/events, /growth/events/{id},
/growth/integrations, /conversations, /clients — returned client names,
phone numbers and message text to anyone on the internet, no header required.

The fix is deny-by-default (app/core/security.py), so this file tests the
boundary from both directions: nothing in the public allowlist may ever
demand a key, and nothing outside it may ever be reachable without one —
including endpoints nobody has written yet, which is why the structural
tests at the bottom matter as much as the endpoint-by-endpoint ones.
"""

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.security import PUBLIC_PATHS, PUBLIC_PREFIXES, SELF_AUTHENTICATED, is_public
from app.main import app
from app.tests.testdb import TEST_API_TOKEN, client

# A client carrying no default headers at all — `client` from testdb always
# sends the correct key, which is right for every other test file but wrong
# for this one.
anon = TestClient(app)

API_KEY_HEADER = "X-Colore-Api-Key"

PROTECTED_GET = [
    "/clients",
    "/conversations",
    "/growth/events",
    "/growth/integrations",
    "/db",
]

PUBLIC_GET = ["/", "/docs", "/openapi.json"]


# ------------------------------------------------------------- the five, by name


@pytest.mark.parametrize("path", ["/growth/events", "/growth/integrations", "/conversations", "/clients"])
def test_anonymous_is_rejected(setup_test_db, path):
    response = anon.get(path)
    assert response.status_code in (401, 503), (path, response.status_code)


@pytest.mark.parametrize("path", ["/growth/events", "/growth/integrations", "/conversations", "/clients"])
def test_owner_key_is_accepted(setup_test_db, path):
    response = client.get(path)
    assert response.status_code == 200, (path, response.text)


def test_growth_event_detail_is_protected(setup_test_db, monkeypatch):
    monkeypatch.setattr(settings, "GROWTH_INBOUND_SECRET", "test-inbound-secret")

    created = client.post(
        "/growth/events",
        json={"object": "unknown", "entry": []},
        headers={"X-Colore-Token": "test-inbound-secret"},
    )
    assert created.status_code == 200

    anon_detail = anon.get("/growth/events/1")
    assert anon_detail.status_code in (401, 503)

    owner_detail = client.get("/growth/events/1")
    assert owner_detail.status_code in (200, 404)  # 404 is fine — 401 is not


# --------------------------------------------------- found during the sweep


def test_ai_and_booking_were_also_public_and_are_now_protected():
    """Not named in the mission's minimum list, but found by the sweep it
    asked for: these process conversation content and were reachable by
    anyone before this change."""
    for method, path in (("POST", "/ai/reply"), ("POST", "/ai/analyze"), ("POST", "/booking/proposal")):
        response = anon.request(method, path, json={})
        assert response.status_code in (401, 503), (method, path, response.status_code)


# ------------------------------------------------------------------- no leak


def test_an_anonymous_401_never_contains_business_data():
    """A rejection must be a rejection — not the data with an extra header."""
    response = anon.get("/conversations")

    assert response.status_code in (401, 503)
    assert "phone" not in response.text.lower()
    assert response.json().get("detail")


def test_wrong_key_is_rejected_the_same_as_no_key():
    response = anon.get("/clients", headers={API_KEY_HEADER: "not-the-real-key"})

    assert response.status_code in (401, 503)


def test_empty_key_is_rejected():
    response = anon.get("/clients", headers={API_KEY_HEADER: ""})

    assert response.status_code in (401, 503)


# --------------------------------------------------------- fail closed, not open


def test_an_unconfigured_token_closes_the_endpoint_rather_than_opening_it(monkeypatch):
    """Losing COLORE_API_TOKEN must not silently reopen the API — that is
    exactly how the data ended up public the first time."""
    monkeypatch.setattr(settings, "COLORE_API_TOKEN", "")

    response = anon.get("/clients")

    assert response.status_code == 503
    assert "COLORE_API_TOKEN" in response.json()["detail"]


def test_an_unconfigured_token_rejects_even_the_correct_looking_key(monkeypatch):
    monkeypatch.setattr(settings, "COLORE_API_TOKEN", "")

    response = client.get("/clients")  # sends TEST_API_TOKEN, which is now stale

    assert response.status_code == 503


# --------------------------------------------------------------------- public


@pytest.mark.parametrize("path", PUBLIC_GET)
def test_public_endpoints_never_require_a_key(path):
    response = anon.get(path)
    assert response.status_code == 200, (path, response.status_code)


def test_public_endpoints_ignore_a_present_key_too():
    """A key that happens to be sent must not break a public route."""
    response = client.get("/docs")
    assert response.status_code == 200


# ------------------------------------------------------- self-authenticated


def test_meta_handshake_needs_no_api_key(monkeypatch):
    """Meta calls this with query parameters, never our header."""
    monkeypatch.setattr(settings, "META_VERIFY_TOKEN", "verify-me")
    from app.integrations.gateway import reset_connector_gateway_for_tests

    reset_connector_gateway_for_tests()

    response = anon.get(
        "/growth/webhook/meta",
        params={"hub.mode": "subscribe", "hub.verify_token": "verify-me", "hub.challenge": "1"},
    )

    assert response.status_code == 200
    reset_connector_gateway_for_tests()


def test_n8n_ingest_needs_no_api_key_only_its_own_secret(monkeypatch):
    """This endpoint has always required X-Colore-Token; it must not now also
    require X-Colore-Api-Key, or the n8n integration breaks."""
    monkeypatch.setattr(settings, "GROWTH_INBOUND_SECRET", "test-inbound-secret")

    response = anon.post(
        "/growth/events",
        json={"object": "unknown", "entry": []},
        headers={"X-Colore-Token": "wrong"},
    )

    # Rejected for the *inbound* secret, proving the check ran — not for a
    # missing API key, which would also be 401 but for the wrong reason.
    assert response.status_code == 401
    assert "Colore-Token" in response.json()["detail"]


# --------------------------------------------------------------- the doctor


def test_doctor_checks_security():
    from pathlib import Path

    doctor = Path(__file__).resolve().parents[3] / "scripts" / "doctor.sh"
    text = doctor.read_text(encoding="utf-8")

    assert "COLORE_API_TOKEN" in text
    assert "/clients" in text
    assert "correctly rejected" in text


# ---------------------------------------------------- structural: deny by default


def _flatten_routes(routes):
    """This FastAPI build wraps included routers as an opaque `_IncludedRouter`
    with the real APIRoute objects one level down, at `.original_router.routes`
    — a plain `for route in app.routes` walk sees only the five framework
    routes FastAPI adds itself and silently skips every router this project
    wrote. A coverage test built on that walk would pass with nothing checked,
    which is worse than no test: it would look like proof."""
    flat = []
    for route in routes:
        if type(route).__name__ == "_IncludedRouter":
            flat += _flatten_routes(route.original_router.routes)
        elif hasattr(route, "routes"):
            flat += _flatten_routes(route.routes)
        else:
            flat.append(route)
    return flat


def test_every_router_is_covered_by_public_or_default_deny():
    """Enumerate the live route table and prove each route is one of:
    explicitly public, self-authenticated, or falls through to the deny-by-
    default branch. There is no fourth outcome — that is the point."""
    business_prefixes = ("/clients", "/conversations", "/growth", "/ai", "/booking")
    seen_business_routes = 0

    for route in _flatten_routes(app.routes):
        methods = getattr(route, "methods", None)
        path = getattr(route, "path", "")
        if not methods or not path:
            continue
        for method in methods:
            if method == "HEAD":
                continue
            public = is_public(method, path)
            self_auth = (method, path.rstrip("/") or path) in SELF_AUTHENTICATED
            assert isinstance(public, bool)
            assert isinstance(self_auth, bool)

            if path.startswith(business_prefixes):
                seen_business_routes += 1
                is_ingest = (method, path) == ("POST", "/growth/events")
                is_meta_webhook = path == "/growth/webhook/meta"
                if not (is_ingest or is_meta_webhook):
                    assert not public, f"{method} {path} is public and serves business data"

    # A route walk that silently found nothing is the exact failure mode this
    # test exists to catch — assert the walk actually reached real routes.
    assert seen_business_routes >= 15, (
        f"only found {seen_business_routes} business routes — "
        "the route walk is not reaching the real route table"
    )


def test_public_allowlist_contains_no_business_data_route():
    """A route landing in the allowlist by accident is the exact failure
    mode this whole change exists to prevent."""
    forbidden_fragments = ("client", "conversation", "growth", "booking", "ai")

    for method, path in PUBLIC_PATHS:
        lowered = path.lower()
        assert not any(fragment in lowered for fragment in forbidden_fragments), (method, path)

    for prefix in PUBLIC_PREFIXES:
        assert not any(fragment in prefix.lower() for fragment in forbidden_fragments), prefix


def test_a_brand_new_route_is_protected_without_being_told_to_be():
    """The core guarantee: a route nobody has explicitly protected is still
    protected, because protection is the default, not an opt-in."""
    assert is_public("GET", "/some/route/nobody/has/written/yet") is False


def test_self_authenticated_routes_are_named_explicitly():
    """No wildcard, no prefix match — every self-authenticated route is one
    exact (method, path) pair, so adding one is a deliberate, reviewable act."""
    for method, path in SELF_AUTHENTICATED:
        assert method in ("GET", "POST", "PUT", "DELETE", "PATCH")
        assert path.startswith("/")
