# Research Registry

Last updated: 2026-08-08

## Purpose

Registry of every idea found, unfinished investigation, architectural discovery and recovered development in this project.

**This is NOT a backlog.** A backlog holds work that is agreed and waiting to be built.

**This is NOT a roadmap.** A roadmap holds sequenced delivery stages.

**This is project memory.** It exists so that a finding survives the session that produced it — without depending on any model, any chat history, or any person remembering it.

## Review Queue

Research to come back to. Check this before starting work.

| ID | Title | When to return | Status |
|---|---|---|---|
| R-001 | Recovered OpenHands Domain Model | Before Altegio | Pending |
| R-002 | Growth AI integration gaps (4 unverified contracts) | Before the integration each gap blocks | Pending |
| R-003 | Meta Business decisions required from Product Owner (5) | Before Meta goes live | Pending |
| R-004 | Altegio `with_deleted=1` — undocumented, required for cancellations | Before relying on cancellation events | Pending |

## Rules

- Every entry has a permanent ID: `R-001`, `R-002`, …
- IDs are never reused and never renumbered.
- An entry is never deleted. When it is finished, its **Status** becomes `Closed` with the outcome recorded.
- Anything marked **Deletion risk: High** must not be deleted, moved or cleaned up until its research is complete.
- Every agent reads this file during the Runtime Entry Procedure, before starting new development. See [`runtime.md`](runtime.md).

## Entry Format

```
ID
Title
Status
Source
Discovered
Description
Why it matters
When to return
Related Roadmap Phase
Related ADR
Deletion risk
Recommendation
```

Status values: `Pending Review` · `Under Review` · `Adopted` · `Rejected` · `Closed`

---

## R-001 — Recovered OpenHands Domain Model

| Field | Value |
|---|---|
| **ID** | R-001 |
| **Title** | Recovered OpenHands Domain Model |
| **Status** | Pending Review |
| **Source** | `/opt/colore-os/app` (working tree, not committed) |
| **Discovered** | 2026-08-06 (AUDIT-001) |
| **Deletion risk** | **High** |

### Description

A parallel implementation that never reached git. Roughly **1700 lines of Python** plus 585 lines of tests, present only in the working tree of an old clone of this repository.

Key domains:

| Module | Contents | Size |
|---|---|---|
| `knowledge` | Service catalogue, masters, business info, FAQ; YAML-backed repository with seed data | 205 lines |
| `schedule` | `WorkingHours`, `TimeSlot`, `Schedule`, `Appointment`, slot and appointment statuses | 133 lines |
| `conversation` | Entity extraction by rules: hair length, service, master, preferred date, preferred time, plus `detect_intent` | 308 lines |
| `identity` | Cross-channel identity mapping (`Identity`, `ChannelIdentity`, `ChannelType`) | 119 lines |
| `client` | Client statuses, communication channels, contacts | 140 lines |
| `booking` | `BookingRequest`, booking statuses | 63 lines |
| `state` | `ConversationState` | 54 lines |
| `chat` | `ChatService` response orchestration | 32 lines |
| `tests` | 10 test modules covering the above | 585 lines |

Architecturally a different lineage from the current backend: Pydantic models with in-memory services and YAML storage. SQLAlchemy is not used anywhere in it.

### Why it matters

None of these entities exist in the working repository — verified by symbol search: `WorkingHours`, `TimeSlot`, `Appointment`, `FAQEntry`, `BusinessInfo`, `ChannelIdentity`, `detect_intent`, `KnowledgeService` are all absent from `/root/colore-os`.

The modules cover exactly the gaps the current MVP fills with placeholders:

- Booking slots are three hardcoded strings; `schedule` models real working hours and availability.
- There is no service catalogue at all; `knowledge` has one, with masters and FAQ.
- Intent is classified by the LLM, but no entity extraction exists; `conversation` extracts service, master, date and time.
- A client reached on two channels cannot be recognised as one person; `identity` models that.

### Evidence of loss

- The code is in **no commit and no remote** — it exists in exactly one place on disk.
- The clone's Dockerfile sets `OPENHANDS_DISABLE_AUTOCOMMIT=1`: the agent's work was deliberately not auto-committed.
- The clone sits at `0bccaa9` (2026-07-28), one unpushed commit ahead of its own `origin/main`; the working repository has moved 60 commits beyond it.
- All 36 files share a modification window of 2026-07-29, 14:50–16:43 — a single ~2 hour agent session, never saved.
- The directory is bind-mounted into the running `colore-developer-service` container (`openhands-ai`) as `/workspace/colore-os`. Deleting it breaks that container.

### When to return

Before implementing **Altegio integration** and before building the **Production Booking Engine**. Reviewing it earlier than that is optional; reviewing it later than that means rebuilding work that already exists.

### Related Roadmap Phase

- Stage 1 — FIRST REVENUE: `Priority → Integrilla`, `Campaign Engine` (conversation entity extraction may apply)
- Stage 2 — Revenue Stability
- Stage 3 — Product Expansion: AI Administrator
- Epic — Altegio Write Back

See Research Dependencies in [`roadmap.md`](roadmap.md).

### Related ADR

- [`adr/ADR-001-runtime-first-development.md`](adr/ADR-001-runtime-first-development.md) — why findings must live in the Runtime rather than in a session
- `docs/adr/ADR-0002-Single-Source-of-Truth.md`
- No ADR yet governs adoption of this domain model. One is required before any of it is integrated.

### Recommendation

**Use as a source of ideas. Do not port the code directly.**

The two implementations do not share a storage model — the recovered modules are Pydantic and YAML with no database, the current backend is SQLAlchemy on PostgreSQL. Copying files across would import an incompatible architecture.

Three actions, in order:

1. **Preserve it.** Right now the only thing protecting 1700 lines is that nobody has run `git clean` in that directory.
2. **Review three modules first:** `knowledge`, `schedule`, `conversation`. They close the largest gaps.
3. **Address the cause:** `OPENHANDS_DISABLE_AUTOCOMMIT=1` means the next agent session will lose its work the same way.

### Constraint

**Deletion is forbidden until this research is complete.** The directory is also live infrastructure for a running container — see the evidence section.

---

## R-002 — Growth AI Integration Gaps

| Field | Value |
|---|---|
| **ID** | R-002 |
| **Title** | Growth AI integration gaps (4 unverified contracts) |
| **Status** | Pending Review |
| **Source** | `docs/research/GROWTH_AI_INTEGRATION_RESEARCH.md` (2026-08-08) |
| **Discovered** | 2026-08-08 (GROWTH-001) |
| **Deletion risk** | Low |

### Description

The 2026-08-08 integration research verified every contract needed for the `Meta → n8n → Coloré OS → Growth AI → Telegram` flow against official vendor documentation. Four contracts could **not** be verified and are recorded here rather than guessed.

| # | Gap | Why unverified | Blocks |
|---|---|---|---|
| G-1 | Altegio webhook payload schema and event list | `developer.alteg.io` webhook reference renders client-side; not readable by fetch | Altegio-triggered flows |
| G-2 | Altegio `book_record` / `book_dates` / `book_staff` / `book_services` exact contracts | same | Booking write-back (already deferred post-FIRST REVENUE) |
| G-3 | Instagram human-agent tag field name for replies outside the 24h window | documented as a capability, field name not stated on the page | Replying to an Instagram DM after 24h |
| G-4 | Meta System User token expiry semantics vs. user tokens | not stated on the System Users overview page | Token rotation policy |

### Why it matters

None of the four blocks today's flow — today is Meta-triggered and Telegram-out. Each blocks a specific, already-identified next step. Recording them prevents the next agent from either rebuilding the research or, worse, inventing a payload shape and writing code against fiction.

### When to return

- **G-1, G-2:** before any Altegio-triggered flow or booking write-back. Resolve by capturing a live payload from the salon account, or an authenticated docs session — not by guessing.
- **G-3:** before Instagram outbound messaging.
- **G-4:** before the first Meta token rotation, or on the first `190` auth error, whichever comes first.

### Related Roadmap Phase

Stage 1 — Growth AI Foundation; Epic — Altegio Write Back.

### Related ADR

[`adr/ADR-002-growth-ai-foundation.md`](adr/ADR-002-growth-ai-foundation.md)

### Recommendation

Close G-1 and G-2 together by capturing one real Altegio webhook delivery against a test endpoint. That single observation resolves more than reading the documentation would.

---

## R-003 — Meta Business Decisions Required From Product Owner

| Field | Value |
|---|---|
| **ID** | R-003 |
| **Title** | Meta Business decisions required from Product Owner (5) |
| **Status** | Pending Review |
| **Source** | `docs/research/META_BUSINESS_DECISIONS.md` (2026-08-08) |
| **Discovered** | 2026-08-08 (GROWTH-008) |
| **Deletion risk** | Low |

### Description

Meta cannot go live on engineering effort alone. Five decisions belong to the Product Owner:

1. Start Business Verification with the salon's legal entity.
2. Is ad-spend reporting wanted? If yes, connect Marketing API **Limited Access now**.
3. Approve the permission list for App Review.
4. Provide App ID, App Secret and a verify token; confirm n8n stays the subscription holder.
5. Is offline conversion reporting wanted? If yes, provide the Dataset ID and decide on the privacy notice for sending hashed client phones to Meta.

### Why it matters

Decision 2 has a timing trap that is easy to miss. Meta requires "at least 500 Marketing API calls in the last 15 days" with "an error rate of less than 15%" before Full Access can be requested. Full Access cannot be applied for on the day it is needed — the integration must already have been calling the API for a fortnight. Postponing the connection postpones ad reporting by two weeks beyond the decision.

Decision 5 depends on cross-channel identity: an Instagram-sourced visit cannot be reported back to Meta because `IGSID` is app-scoped and is not a phone. That is [[R-001]]'s `identity` module territory.

### When to return

Before any Meta credential is issued. Decisions 1 and 2 have external lead times and should start first.

### Related Roadmap Phase

Stage 1 — Growth AI Foundation; Stage 2 — Revenue Stability (ad attribution).

### Related ADR

`adr/ADR-002-growth-ai-foundation.md`

### Recommendation

Take decisions 1 and 2 immediately regardless of the rest — both are clocks that only start when the Product Owner acts, and neither blocks or is blocked by engineering.

---

## R-004 — Altegio `with_deleted=1` Is Undocumented And Required

| Field | Value |
|---|---|
| **ID** | R-004 |
| **Title** | Altegio `with_deleted=1` — undocumented, required for cancellations |
| **Status** | Pending Review |
| **Source** | Live account probe, 2026-08-08 (GROWTH-009) |
| **Discovered** | 2026-08-08 |
| **Deletion risk** | Low |

### Description

`GET /v1/records/{company_id}` does not return cancelled appointments by default, and it does not signal that anything was withheld. A cancelled appointment is indistinguishable from one that never existed.

Measured on the live account over 180 days:

| Call | `total_count` | deleted rows in page 1 |
|---|---|---|
| default | 341 | 0 |
| `deleted=1` | 341 | 0 |
| `include_deleted=1` | 341 | 0 |
| **`with_deleted=1`** | **383** | **13** |

Only `with_deleted=1` works. It is not in the published reference.

### Why it matters

The attribution loop reports `appointment_cancelled` to Meta. Without this parameter that state can never fire, and Meta would keep optimising toward appointments that were later cancelled. The flag currently carries a state that has real budget consequences.

### When to return

Before relying on cancellation events in production, and on any Altegio API version change. An undocumented parameter can be withdrawn without notice; if it stops working, cancellations silently stop being reported rather than erroring.

Worth confirming with Altegio support (api@alteg.io) that the parameter is supported and stable.

### Related Roadmap Phase

Stage 1 — Growth AI Foundation.

### Related ADR

`adr/ADR-002-growth-ai-foundation.md`

### Recommendation

Add a check that compares `total_count` with and without the flag. If they ever become equal, the parameter has stopped working and cancellation reporting is silently dead.

---

## Index

| ID | Title | Status | Deletion risk |
|---|---|---|---|
| R-001 | Recovered OpenHands Domain Model | Pending Review | **High** |
| R-002 | Growth AI Integration Gaps | Pending Review | Low |
| R-003 | Meta Business Decisions Required From Product Owner | Pending Review | Low |
| R-004 | Altegio `with_deleted=1` Undocumented | Pending Review | Low |

## Source of Truth

This file owns discovered-but-unfinished work only. Agreed work lives in [`roadmap.md`](roadmap.md). Decisions live in [`adr/`](adr/) and [`changelog.md`](changelog.md). Current state lives in [`state.md`](state.md).
