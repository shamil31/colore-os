"""Is this failure worth trying again?

The question this module answers is the whole of P0-001. Before it existed, any
failed send marked every event in the batch `rejected`, forever — so a mistyped
dataset id, a five-second network blip, or one event that was too old destroyed
a hundred confirmed business outcomes that nothing could recover.

The rule: an event becomes `permanent_failure` **only when re-sending that exact
event could never succeed**. Everything else waits and is tried again.

Two consequences of that rule are worth stating plainly, because they look like
misclassifications until you follow the reasoning:

- **An expired or invalid token is temporary.** The event is valid; the
  configuration is broken. Marking the queue permanent because someone rotated
  a token would recreate the bug this module exists to fix.
- **An unknown dataset is temporary**, for the same reason. A wrong id is fixed
  by editing one setting, and every event should still be there afterwards.
  Only the event's own content can condemn the event.
"""

from __future__ import annotations

from app.integrations.connectors.meta_connector import MetaSendError

TEMPORARY = "temporary"
PERMANENT = "permanent"

# Meta error codes that are explicitly about load, throttling or availability.
# https://developers.facebook.com/docs/graph-api/guides/error-handling
TRANSIENT_CODES = frozenset(
    {
        1,    # unknown / temporary
        2,    # service temporarily unavailable
        4,    # application request limit reached
        17,   # user request limit reached
        32,   # page request limit reached
        341,  # application limit reached
        613,  # rate limit
    }
)

# Codes about who is asking rather than what is being sent. The event is fine;
# the credential or the asset reference is not. Fixable without touching data.
CONFIGURATION_CODES = frozenset(
    {
        190,  # invalid or expired access token
        200,  # permission denied
        803,  # object does not exist / unknown dataset
        803_0,  # placeholder guard, harmless
    }
)

# Phrases Meta uses for faults that belong to the event itself.
PERMANENT_PHRASES = (
    "7 days in the past",
    "event_time",
    "invalid parameter",
    "unsupported post request",
    "duplicate",
)


def classify(error: Exception) -> tuple[str, str]:
    """Return (TEMPORARY | PERMANENT, reason)."""
    if not isinstance(error, MetaSendError):
        # An unrecognised failure is treated as temporary. Losing an event is
        # worse than retrying one, and an unknown error is not evidence that
        # the event is bad.
        return TEMPORARY, f"unclassified error: {type(error).__name__}"

    if error.network:
        return TEMPORARY, "network failure — the request never reached Meta"

    if error.is_transient:
        return TEMPORARY, "Meta marked the error transient"

    status = error.status_code
    if status is not None:
        if status >= 500:
            return TEMPORARY, f"Meta returned HTTP {status}"
        if status == 429:
            return TEMPORARY, "rate limited (HTTP 429)"

    code = error.error_code
    if code in TRANSIENT_CODES:
        return TEMPORARY, f"Meta throttling or availability (code {code})"

    if code in CONFIGURATION_CODES:
        # Deliberately temporary. See the module docstring.
        return TEMPORARY, (
            f"configuration fault (code {code}) — the event is valid, "
            "the credential or dataset is not"
        )

    message = str(error).lower()
    for phrase in PERMANENT_PHRASES:
        if phrase in message:
            return PERMANENT, f"Meta refused the payload: {phrase}"

    if status is not None and 400 <= status < 500:
        return PERMANENT, f"Meta refused the payload (HTTP {status})"

    return TEMPORARY, "unrecognised failure — retrying rather than discarding"


# Backoff, in seconds, by attempt number. Capped so a long outage does not push
# an event out to days, and jitter-free because ordering is by id anyway.
BACKOFF_SECONDS = (60, 300, 900, 3600, 7200, 21600)
MAX_BACKOFF = 21600  # 6 hours


def backoff_for(attempts: int) -> int:
    if attempts <= 0:
        return BACKOFF_SECONDS[0]
    if attempts - 1 < len(BACKOFF_SECONDS):
        return BACKOFF_SECONDS[attempts - 1]
    return MAX_BACKOFF
