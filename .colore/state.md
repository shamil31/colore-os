# Coloré OS — State

Last verified: 2026-08-05
Maintained manually. Never infer state from code structure alone.

## Verified Facts

- Workspace path: `/root/colore-os`
- Runtime stored under `.colore/` (Runtime v1)
- Git repository present; origin: `https://github.com/shamil31/colore-os.git`
- Current sprint: FIRST REVENUE (see [`sprint.md`](sprint.md))
- Main KPI: first revenue (первая выручка)

## Project Identity

- **Purpose:** Coloré OS is a revenue operating system built above existing salon infrastructure (Altegio CRM, Integrilla messaging).
- **Mission:** Measurable revenue growth through client prioritization, campaign execution, and a closed learning loop on real outcomes.
- **Users:** Salon owner, revenue/operator team, clients (via external channels).
- **Core modules:** Revenue Engine, Priority Engine, Decision Engine, Business Intelligence, Campaign Engine, Learning Loop.
- **Long-term vision:** After repeatable revenue is confirmed, Coloré OS becomes a commercial product for independent salons.
- **Success criteria:** First revenue booking initiated by Coloré OS is confirmed; a verified trace exists from priority to booking; data exists to drive the next conversion-improvement iteration.

## Verified Completed Work

- Altegio Authentication
- Company Discovery
- Client Import
- Visit Import
- Revenue Engine
- Revenue Report
- Priority Report
- Business Priority Report
- Visit cost import fixed
- Revenue correctness verified
- Priority Formula verified
- Campaign Pipeline (9/10 stages) — 2026-08-02
- Integrilla Export (XLSX generation) — 2026-08-02
- Conversation Playbook (7 rules, 7 scenarios) — 2026-08-02
- Project Knowledge Index — 2026-08-02
- Altegio API Capabilities Audit — 2026-08-01
- Lead Intelligence MVP (Sprint #1): Lead State Machine v1, Lead Intelligence Model v1, SOP Document Lifecycle, SOP Task Lifecycle — 2026-08-05
- Next Best Action Engine v1 (Sprint #2) — 2026-08-05
- Conversation Engine v1 (Sprint #3) — 2026-08-05
- Runtime Architecture v1 (Sprint #4) — 2026-08-05
- Project knowledge architecture: `docs/architecture/`, `docs/adr/`, `docs/domain/`, `docs/operations/`, `docs/research/` — 2026-08-05
- Runtime v1 migration (this document set) — 2026-08-05
- Conversation Flows: Scenarios 001–013 (Book Appointment, Reschedule, Cancel, Consultation, Price Inquiry, Service Selection, Lead Qualification, Objection Handling, Human Handoff, Promotion Inquiry, Master Selection, First Contact, Follow Up) — see `docs/domain/scenarios/`
- Product Vision v1.0, AI Constitution v1.0, AI Employee Framework v1.0, Conversation Principles v1.0, Intent Map v1.0, Decision Model v1.0 — see `docs/research/`

## Architecture Guardrails

See [`architecture.md`](architecture.md) for full detail.

- Coloré OS does not replace Altegio.
- Coloré OS does not replace Integrilla.
- Altegio remains system of record for CRM clients, appointments, and history.
- Integrilla remains message transport.

## Backend & Infrastructure Present

- `backend/app/main.py` — `/`, `/db`, `/clients` routes
- `backend/app/api/clients.py` — CRUD for clients
- `backend/app/db/database.py` — SQLAlchemy engine and DB connectivity
- `infrastructure/docker-compose.yml` — postgres, n8n, backend

## Unknowns

- Timestamp/identifier of the first live booking initiated by Coloré OS: TODO
- Campaign baseline values for conversion and uplift: TODO
- SLA for Integrilla delivery and retry guarantees: TODO

## Source of Truth

This file owns current verified state only. Historical events live in [`changelog.md`](changelog.md). Active sprint lives in [`sprint.md`](sprint.md). Active task lives in [`next.md`](next.md).
