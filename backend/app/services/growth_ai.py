"""Growth AI — decide what a new inbound message is worth, and tell a human.

Today's action is always the same: alert the salon operator over Telegram.
Nothing is sent to a client automatically (ADR-002 decision 5), so the first
live run is observable and reversible.

The decision is deliberately rule-first, with the LLM used only to name the
intent. Priority drives whether a person is interrupted, and that must be
explainable to the salon owner and identical on every replay of the same
message. `decision_reason` records why, in words, on every event.
"""

from __future__ import annotations

import logging

from app.growth.normalize import NormalisedEvent
from app.services.llm_service import LLMService

logger = logging.getLogger("colore.growth")

PRIORITY_HIGH = "high"
PRIORITY_NORMAL = "normal"
PRIORITY_LOW = "low"

INTENT_UNKNOWN = "UNKNOWN"

# Intents that mean money is on the table right now.
REVENUE_INTENTS = frozenset({"BOOKING", "RESCHEDULE", "PRICE"})

# Intents where a slow answer costs a client.
URGENT_INTENTS = frozenset({"COMPLAINT", "CANCEL"})


class Decision:
    def __init__(self, *, intent: str, priority: str, reason: str, alert_text: str):
        self.intent = intent
        self.priority = priority
        self.reason = reason
        self.alert_text = alert_text

    def to_dict(self) -> dict:
        return {
            "intent": self.intent,
            "priority": self.priority,
            "reason": self.reason,
            "alert_text": self.alert_text,
        }


class GrowthAI:
    def __init__(self, llm: LLMService | None = None) -> None:
        self._llm = llm

    async def decide(self, event: NormalisedEvent) -> Decision:
        intent, intent_note = await self._classify(event)
        priority, priority_note = self._prioritise(intent)

        reason = f"{intent_note} {priority_note}".strip()

        return Decision(
            intent=intent,
            priority=priority,
            reason=reason,
            alert_text=self._compose_alert(event, intent=intent, priority=priority),
        )

    async def _classify(self, event: NormalisedEvent) -> tuple[str, str]:
        if self._llm is None:
            return INTENT_UNKNOWN, "Intent not classified: LLM is not configured."

        try:
            result = await self._llm.classify([{"role": "user", "content": event.text}])
        except Exception as exc:  # noqa: BLE001
            # A classifier outage must not swallow a client's message. Fall
            # back to UNKNOWN, which routes to the operator anyway.
            logger.warning("growth: intent classification failed: %s", exc)
            return INTENT_UNKNOWN, f"Intent not classified: {type(exc).__name__}."

        intent = result.get("intent") or INTENT_UNKNOWN
        confidence = result.get("confidence", 0.0)
        return intent, f"Intent {intent} at confidence {confidence:.2f}."

    def _prioritise(self, intent: str) -> tuple[str, str]:
        if intent in URGENT_INTENTS:
            return PRIORITY_HIGH, "High: a slow answer here loses the client."
        if intent in REVENUE_INTENTS:
            return PRIORITY_HIGH, "High: revenue intent, answer inside the 24h window."
        if intent == INTENT_UNKNOWN:
            # Unknown routes up, not down. A message nobody understood is
            # exactly the one a human should read.
            return PRIORITY_NORMAL, "Normal: unclassified, so a human decides."
        return PRIORITY_NORMAL, "Normal: no revenue or urgency signal."

    def _compose_alert(self, event: NormalisedEvent, *, intent: str, priority: str) -> str:
        who = event.sender_name or event.sender_ref or "unknown sender"
        marker = "🔴" if priority == PRIORITY_HIGH else "🟡"

        # Plain text on purpose: the connector sends without parse_mode, so a
        # client writing "50_000" or "*best*" cannot break this alert.
        return (
            f"{marker} {event.source.upper()} — {intent}\n"
            f"From: {who}\n"
            f"\n"
            f"{event.text}\n"
            f"\n"
            f"Reply in {event.source} within 24h."
        )
