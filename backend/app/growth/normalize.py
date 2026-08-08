"""Turn a Meta webhook payload into one Coloré OS event, or explain why not.

Verified 2026-08-08 against the payload shapes in
`docs/research/GROWTH_AI_INTEGRATION_RESEARCH.md` §2 and §3.

WhatsApp and Instagram do **not** share a shape:

    WhatsApp   object=whatsapp_business_account
               entry[].changes[].value.messages[]

    Instagram  object=instagram
               entry[].messaging[]

A single parser that assumes one of them silently drops the other, so the
branch is explicit and each side is tested.

Most inbound traffic is not a conversation. Delivery receipts, read receipts
and our own echoed messages all arrive on the same subscription, and every one
of them must be acknowledged with 200 and then dropped. `SKIP_*` says which.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

SOURCE_WHATSAPP = "whatsapp"
SOURCE_INSTAGRAM = "instagram"

SKIP_ECHO = "echo"
"""Our own outbound message, reflected back. Answering it talks to ourselves."""

SKIP_STATUS_ONLY = "status_only"
"""A delivery or read receipt, not a message."""

SKIP_NO_MESSAGE = "no_message"
"""A subscribed event that carries no message at all."""

SKIP_UNSUPPORTED_TYPE = "unsupported_type"
"""A message we can read but cannot act on yet (image, audio, sticker...)."""

SKIP_UNKNOWN_SHAPE = "unknown_shape"
"""Not a payload shape this parser knows."""


@dataclass
class NormalisedEvent:
    source: str
    external_id: str
    sender_ref: str
    text: str
    sender_name: str = ""
    channel_ref: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class SkippedEvent:
    reason: str
    detail: str = ""
    external_id: str = ""


def unwrap(payload: dict[str, Any]) -> dict[str, Any]:
    """Return the Meta payload, whether or not n8n wrapped it.

    An n8n HTTP Request node commonly forwards the original webhook under
    `body`, and some workflows nest it again under `payload`. Accepting both
    means a workflow author does not have to get the mapping exactly right
    before anything works at all.
    """
    current = payload
    for _ in range(3):
        if not isinstance(current, dict):
            break
        if "object" in current and "entry" in current:
            return current
        nested = current.get("body") or current.get("payload")
        if not isinstance(nested, dict):
            break
        current = nested
    return payload if isinstance(payload, dict) else {}


def normalise(payload: dict[str, Any]) -> NormalisedEvent | SkippedEvent:
    body = unwrap(payload)
    obj = body.get("object")

    if obj == "whatsapp_business_account":
        return _normalise_whatsapp(body)

    if obj in ("instagram", "page", "user"):
        return _normalise_instagram(body, source=SOURCE_INSTAGRAM)

    return SkippedEvent(
        reason=SKIP_UNKNOWN_SHAPE,
        detail=f"object={obj!r}",
    )


# ------------------------------------------------------------------ whatsapp


def _normalise_whatsapp(body: dict[str, Any]) -> NormalisedEvent | SkippedEvent:
    for entry in _as_list(body.get("entry")):
        for change in _as_list(entry.get("changes")):
            value = change.get("value")
            if not isinstance(value, dict):
                continue

            messages = _as_list(value.get("messages"))
            if not messages:
                if _as_list(value.get("statuses")):
                    return SkippedEvent(
                        reason=SKIP_STATUS_ONLY,
                        detail="delivery or read receipt",
                    )
                continue

            message = messages[0]
            external_id = str(message.get("id") or "")
            message_type = message.get("type")

            if message_type != "text":
                return SkippedEvent(
                    reason=SKIP_UNSUPPORTED_TYPE,
                    detail=f"type={message_type!r}",
                    external_id=external_id,
                )

            text = ((message.get("text") or {}).get("body") or "").strip()
            if not text:
                return SkippedEvent(
                    reason=SKIP_NO_MESSAGE,
                    detail="empty text body",
                    external_id=external_id,
                )

            metadata = value.get("metadata") or {}
            contacts = _as_list(value.get("contacts"))
            profile_name = ""
            if contacts:
                profile_name = str((contacts[0].get("profile") or {}).get("name") or "")

            return NormalisedEvent(
                source=SOURCE_WHATSAPP,
                external_id=external_id,
                # wa_id is a phone number, so it joins directly against Altegio
                # clients — the cheapest identity resolution available here.
                sender_ref=str(message.get("from") or ""),
                sender_name=profile_name,
                channel_ref=str(metadata.get("phone_number_id") or ""),
                text=text,
                raw=body,
            )

    return SkippedEvent(reason=SKIP_NO_MESSAGE, detail="no messages in payload")


# ----------------------------------------------------------------- instagram


def _normalise_instagram(body: dict[str, Any], *, source: str) -> NormalisedEvent | SkippedEvent:
    # Meta can bundle more than one messaging item in a single delivery — an
    # echo of our own reply alongside the client's next message, for example.
    # Returning on the first skippable item would abandon the rest of the
    # payload and silently drop a real message sitting right behind it, so a
    # skip only ends the scan once nothing actionable was found anywhere in
    # the delivery. `fallback` keeps the first reason encountered, since that
    # is the one worth reporting if the scan never finds a real message.
    fallback: SkippedEvent | None = None

    for entry in _as_list(body.get("entry")):
        for item in _as_list(entry.get("messaging")):
            message = item.get("message")
            if not isinstance(message, dict):
                continue

            external_id = str(message.get("mid") or message.get("id") or "")

            # Instagram reflects our own sends back on the same subscription.
            # Without this check Growth AI answers itself, in a loop, on the
            # first live message.
            if message.get("is_echo") or item.get("is_self"):
                fallback = fallback or SkippedEvent(
                    reason=SKIP_ECHO,
                    detail="message echoed back by Instagram",
                    external_id=external_id,
                )
                continue

            text = str(message.get("text") or "").strip()
            if not text:
                fallback = fallback or SkippedEvent(
                    reason=SKIP_UNSUPPORTED_TYPE,
                    detail="non-text message",
                    external_id=external_id,
                )
                continue

            return NormalisedEvent(
                source=source,
                external_id=external_id,
                # IGSID: app-scoped, not the username. It cannot be matched
                # against Altegio by name.
                sender_ref=str((item.get("sender") or {}).get("id") or ""),
                channel_ref=str((item.get("recipient") or {}).get("id") or ""),
                text=text,
                raw=body,
            )

    return fallback or SkippedEvent(reason=SKIP_NO_MESSAGE, detail="no messaging entries in payload")


def _as_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]
