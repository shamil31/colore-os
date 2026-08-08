# Coloré OS — Roadmap

Last updated: 2026-08-05

## Stage 1 — FIRST REVENUE (ACTIVE)

Goal: first real client booking initiated by Coloré OS and recorded in Altegio.

Execution order:
0. Growth AI Foundation — connector layer (ADR-002, added 2026-08-08)
1. Priority → Integrilla
2. Campaign Engine
3. Segmentation
4. Message Selection
5. Campaign Results
6. Learning loop from real outcomes

Exit criteria: first confirmed revenue event.

## Stage 2 — Revenue Stability

- Improve campaign targeting and delivery reliability.
- Expand learning datasets.
- Improve conversion quality with validated evidence.

## Stage 3 — Product Expansion (Post-Revenue)

Unlocked only after Stage 1 exit criteria is met.

- AI Administrator
- Dashboard
- Marketplace
- SaaS packaging
- Messenger extensions
- Event sourcing

## Research Dependencies

Some roadmap items are blocked on an open finding in [`research.md`](research.md). Check the listed entry **before** implementing the item — not after.

| Before implementing | Check | Why |
|---|---|---|
| Production Booking | **R-001** | `schedule` module already models working hours, slots and appointments; current slots are hardcoded |
| Altegio integration | **R-001** | `identity` and `client` modules already model cross-channel identity and client state |
| Knowledge Base | **R-001** | `knowledge` module already holds the service catalogue, masters and FAQ |
| Conversation Engine | **R-001** | `conversation` module already extracts service, master, date and time from a message |

Skipping this check means rebuilding work the project has already produced once.

## Backlog

### P0 — Execute First
- Priority → Integrilla
- Campaign Engine
- Segmentation
- Message Selection
- Campaign Results
- Learning

### Deferred Until First Revenue
- AI Administrator
- Dashboard
- Marketplace
- SaaS
- Event Sourcing
- Messenger — **partially unblocked 2026-08-08 by ADR-002.** The connector layer is in scope now; building out individual channels beyond one end-to-end trace is not.

### Architecture Backlog
- Rename `docs/domain/customer_intelligence/` to `docs/domain/decision_intelligence/` (future consolidation)
  - Status: deferred pending Active/Lost/VIP Intelligence models
  - Reason: "Decision Intelligence" more accurately covers all client types, not only leads
  - Timing: after at least 2 additional Customer Intelligence subtypes exist

### Epic — Altegio Write Back
- Status: Future (postponed until after FIRST REVENUE)
- Candidate capabilities: AI Priority, AI Segment, VIP Level, Campaign History, Last Campaign, Reactivation Status, Internal Notes, Personal Discount, AI Recommendations

## Intake Rule

New ideas enter this file first. They do not interrupt an active DOING task (see [`next.md`](next.md)).

## Backlog Hygiene

Remove or rewrite any item that conflicts with the FIRST REVENUE doctrine (see [`sprint.md`](sprint.md)). If an item does not move toward first revenue now, keep it deferred here.

## Source of Truth

This file owns roadmap stages and backlog only.
