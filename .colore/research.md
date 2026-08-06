# Research Registry

Last updated: 2026-08-06

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

## Index

| ID | Title | Status | Deletion risk |
|---|---|---|---|
| R-001 | Recovered OpenHands Domain Model | Pending Review | **High** |

## Source of Truth

This file owns discovered-but-unfinished work only. Agreed work lives in [`roadmap.md`](roadmap.md). Decisions live in [`adr/`](adr/) and [`changelog.md`](changelog.md). Current state lives in [`state.md`](state.md).
