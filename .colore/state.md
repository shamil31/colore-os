# Coloré OS — State

Last verified: 2026-08-08
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
- Growth AI Foundation (2026-08-08, ADR-002):
  - Integration research against official documentation for Meta Business, Instagram Graph, WhatsApp Business, Altegio, Telegram Bot API, n8n — `docs/research/GROWTH_AI_INTEGRATION_RESEARCH.md`
  - Connector layer: Integration Registry, Capability Registry, Connector Gateway (capability dispatch, dry run, rate limits), Event Bus — `backend/app/integrations/gateway/`
  - Connectors: Telegram, Meta (webhook verification), n8n (workflow trigger), Altegio (read-only), OpenAI — `backend/app/integrations/connectors/`
  - Growth AI flow `Meta → n8n → Coloré OS → Growth AI → Telegram`, verified live against the deployed container 2026-08-08
  - Telegram live: bot `@Colore_Growth_bot`, first real message delivered to the owner 2026-08-08
  - Growth AI Brain v0.1 — four Product Owner commands over Telegram (`Статус`, `Что нового?`, `Что требует моего решения?`, `Что делаем дальше?`)
  - 142 tests passing

## Deployment Source of Truth

| | |
|---|---|
| **Working repository** | `/root/colore-os` |
| **Working compose** | `/opt/colore-os/docker/docker-compose.yml` |
| **Build context** | `/root/colore-os/backend` |
| **Container env file** | `/opt/colore-os/docker/.env` |

`/opt/colore-os/app` is an **archived** second clone of this repository, pinned to a July commit. It is not the source of truth and must never be used as a build context. It still holds ~1700 lines of uncommitted parallel work that exists nowhere else — do not delete it without reviewing that work first.

Rebuild and restart:

```bash
cd /opt/colore-os/docker
GIT_COMMIT=$(git -C /root/colore-os rev-parse --short HEAD) docker compose build backend
docker compose up -d backend
```

The container logs its version, git commit, build context and whether `OPENAI_API_KEY` is present on every start — check those lines first if the running code looks wrong.

## Architecture Guardrails

See [`architecture.md`](architecture.md) for full detail.

- Coloré OS does not replace Altegio.
- Coloré OS does not replace Integrilla.
- Altegio remains system of record for CRM clients, appointments, and history.
- Integrilla remains message transport.

## Backend & Infrastructure Present

- `backend/app/main.py` — `/`, `/db`, `/clients` routes
- `backend/app/api/clients.py` — CRUD for clients
- `backend/app/api/growth.py` — `/growth/events`, `/growth/webhook/meta`, `/growth/integrations`, trace endpoints
- `backend/app/db/database.py` — SQLAlchemy engine and DB connectivity
- `infrastructure/docker-compose.yml` — postgres, n8n, backend
- Tables `growth_events`, `growth_actions` (migration `a1b2c3d4e5f6`, applied 2026-08-08)
- `colore-growth-bot` — host-side systemd service (`infrastructure/colore-growth-bot.service`). Runs on the host, not in a container: the backend image contains no repository, no `.colore/`, no docker socket, so it could not answer status questions truthfully from inside. Restarted by `deploy.sh`. Logs: `journalctl -u colore-growth-bot -f`.
- `GROWTH_INBOUND_SECRET` added to `/opt/colore-os/docker/.env` 2026-08-08 (backup taken alongside it). No channel credentials are set: Telegram, Meta and n8n all run as dry runs until tokens exist. Setup steps: [`docs/operations/GROWTH_AI_SETUP.md`](../docs/operations/GROWTH_AI_SETUP.md).

## Unknowns

- Timestamp/identifier of the first live booking initiated by Coloré OS: TODO
- Campaign baseline values for conversion and uplift: TODO
- SLA for Integrilla delivery and retry guarantees: TODO

## Source of Truth

This file owns current verified state only. Historical events live in [`changelog.md`](changelog.md). Active sprint lives in [`sprint.md`](sprint.md). Active task lives in [`next.md`](next.md).
