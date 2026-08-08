# ADR-002: Growth AI Foundation — Connector Layer Before Channels

**Decision Owner:** Product (scope), Architecture (structure)
**Status:** Accepted
**Date:** 2026-08-08

---

## Context

`sprint.md` and `roadmap.md` defer **Messenger** and **AI Administrator** until after the FIRST REVENUE exit criterion is met. Product has directed that Growth AI — an intelligence layer reading Meta / Instagram / WhatsApp signals and acting through Telegram — be stood up now, ahead of that exit criterion.

Taken literally, that direction contradicts the Runtime. Rather than let the Runtime quietly become wrong, this ADR records the change.

The substantive question is not *whether* to build Growth AI, but *how much* of it to build so that the FIRST REVENUE doctrine is not abandoned. The failure mode being avoided is the one the project already knows: `docs/INTEGRATION_STATUS.md` and R-001 both record work that was built once and then could not be found or reused.

## Decision

**1. Scope.** Growth AI enters as a sub-sprint *inside* FIRST REVENUE, named `GROWTH AI FOUNDATION`. FIRST REVENUE is not closed and its exit criterion is unchanged: a real client booking in Altegio, initiated by Coloré OS.

**2. Justification against Revenue First.** The Priority → Integrilla loop moves one segment through one channel by manual XLSX export. Growth AI's connector layer is the mechanism by which *any* channel — including Integrilla's replacement — is reached programmatically. It is upstream of the revenue loop, not a detour around it.

**3. Structure: connectors before channels.** The unit of work is the **connector layer**, not any individual platform:

```
Connector Gateway   — one entry point for every outbound call and inbound event
Integration Registry — which integrations exist, and are they configured
Capability Registry  — what each integration can actually do, declared not inferred
Connectors           — n8n, Telegram, Altegio, Meta
```

A connector declares its capabilities. Growth AI asks the Capability Registry for a capability and never names a vendor. Adding a channel is registering a connector; it is not editing Growth AI.

**4. Meta stays behind n8n.** Coloré OS does not hold the Meta webhook subscription today. n8n owns the Meta edge (handshake, 36-hour retries, credential storage) and calls one authenticated Coloré OS endpoint. Rationale in `docs/research/GROWTH_AI_INTEGRATION_RESEARCH.md` §1, §6.

**5. Outbound goes to the operator, not the client.** Today's Telegram leg alerts the salon operator. No message reaches a paying client without a human seeing it. This makes the first live run observable and reversible.

**6. Altegio remains read-only.** Unchanged from `architecture.md`. The Altegio Connector wraps the existing `backend/app/integrations/altegio/` client and declares read capabilities only. Write-back stays deferred.

**7. Credential-optional by construction.** Every connector reports `configured: false` when its secret is absent and refuses to execute, rather than failing at call time. The system is startable, testable and deployable with zero channel credentials present.

## Consequences

**Positive:**
- Adding WhatsApp, Instagram outbound, or Integrilla later is a connector registration, not a Growth AI change.
- The system deploys today with no credentials, so infrastructure is verified before secrets exist.
- Meta's operational complexity stays in n8n, where it is already solved.

**Negative:**
- A registry layer is indirection that a single hardcoded Telegram call would not need. Accepted deliberately: the project's recorded failure mode is losing work, not writing too little of it.
- FIRST REVENUE now contains work that does not directly produce the first booking. Bounded by keeping the sub-sprint to the connector layer and one end-to-end trace — not to building each channel out.

## Alternatives rejected

- **Close FIRST REVENUE and open a GROWTH AI sprint.** Rejected: the first booking has not happened, and declaring the sprint done because attention moved would make `sprint.md` untrue.
- **Build Growth AI without touching `.colore/`.** Rejected: it makes the Runtime lie about project state, which is the exact failure ADR-001 exists to prevent.
- **Point Meta webhooks directly at Coloré OS.** Rejected for today: it imports signature verification, deduplication over a 36-hour retry window, and credential storage into our codebase, all of which n8n already provides. The Meta Connector still implements `X-Hub-Signature-256` verification so the direct path is available later without new design.

## Related Decisions

- [`ADR-001`](ADR-001-runtime-first-development.md) — why this change is recorded rather than made silently
- `docs/adr/ADR-0001-Business-First.md` — Revenue First, addressed in decision 2
- R-001 in [`../research.md`](../research.md) — the `identity` module models cross-channel identity; review before building identity resolution

## Research basis

`docs/research/GROWTH_AI_INTEGRATION_RESEARCH.md` (2026-08-08) — official vendor documentation for all six integrations, with open gaps recorded.
