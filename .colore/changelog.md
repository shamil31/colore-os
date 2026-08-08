# Coloré OS — Changelog

Historical decisions and verified events only. Do not use this file for current status — see [`state.md`](state.md).

## Decision Log

### DEC-001 — VPS is the primary development environment
### DEC-002 — Workspace is `/root/colore-os`
### DEC-003 — Runtime is stored inside `.colore/`
### DEC-004 — Work cycle is `BACKLOG -> TODO -> DOING -> REVIEW -> DONE`
### DEC-005 — Finish Before Improve is mandatory

### DEC-006 — Revenue First becomes Product Strategy
Coloré develops in two parallel streams: Revenue and Product. Neither stream blocks the other. Product work must continuously increase business value.

### DEC-007 — AI Resource Policy
Always prefer the lowest-cost tool that can complete the task. Local role performers are the default choice. Coordinated operations support is reserved for larger repository-wide tasks. The Architecture role is responsible for architecture, product-strategy alignment, planning, review, and governance guidance. Optimize for long-term sustainability, not maximum AI usage.

### DEC-008 — AI Efficiency Standard adopted
Always achieve the required result using the minimum practical AI resources. Read Runtime before searching the repository. Never rediscover information that already exists in Runtime. Prefer updating existing documentation over creating duplicate files. Documentation is part of project memory — every verified discovery should be documented so it never needs rediscovery.

### DEC-009 — Phase Transition and Runtime Architecture Milestone
Phase 0 (Project Operating System) closed as DONE. Phase 1 (Revenue Engine MVP) opened as ACTIVE. Milestone includes UAOP adoption, finalized Runtime architecture, model-independent workflow, dual Revenue/Product operating model, and AI Efficiency Standard adoption.

### DEC-010 — FIRST REVENUE sprint declared active
Main goal: first real client booking initiated by Coloré OS. Main KPI: first revenue.

### DEC-011 — Revenue First and Reality First adopted as mandatory doctrine
Prioritize direct path to first revenue over product expansion. Planning and reporting must be evidence-based.

### DEC-012 — Role split fixed for operating stage
Architecture = architecture governance. Engineering = implementation. Reviewer = independent review.

### DEC-013 — Infrastructure continuity and scope boundary fixed
Use existing infrastructure. Coloré OS does not replace Altegio or Integrilla. AI Administrator development postponed until after first revenue.

### DEC-014 — Model Independence adopted
The project structure, architecture, documentation, processes, and ADRs do not depend on any specific AI model. When the executor of a role changes, project structure and governance remain unchanged. Superseded the model-named role convention (Claude / ChatGPT / Gemini) with role-based ownership (Architecture, Product, Engineering, Operations). See `docs/adr/ADR-0001` through `ADR-0003`.

### DEC-015 — Runtime First Development adopted
See [`adr/ADR-001-runtime-first-development.md`](adr/ADR-001-runtime-first-development.md).

## Verified History

### VH-001
- Date: 2026-08-01
- Event: Phase 0 (Project Operating System) closed.
- Status: DONE

### VH-002
- Date: 2026-08-01
- Event: Phase 1 (Revenue Engine MVP) opened.
- Status: ACTIVE

### VH-003
- Date: 2026-08-01
- Event: Runtime architecture milestone recorded (UAOP adopted, Runtime architecture finalized, AI-independent workflow, dual operating model, AI Efficiency Standard).
- Status: DONE

### VH-004
- Date: 2026-08-02
- Event: Campaign Pipeline (9/10 stages), Integrilla Export, Conversation Playbook, Project Knowledge Index shipped.
- Status: DONE

### VH-005
- Date: 2026-08-05
- Event: Lead Intelligence MVP shipped — Lead State Machine v1, Lead Intelligence Model v1, SOP Document Lifecycle, SOP Task Lifecycle (Sprint #1).
- Status: DONE

### VH-006
- Date: 2026-08-05
- Event: Next Best Action Engine v1 shipped (Sprint #2).
- Status: DONE

### VH-007
- Date: 2026-08-05
- Event: Conversation Engine v1 shipped (Sprint #3).
- Status: DONE

### VH-008
- Date: 2026-08-05
- Event: Runtime Architecture v1 shipped (Sprint #4); relocated from domain-specific to system-level `docs/architecture/`.
- Status: DONE

### VH-009
- Date: 2026-08-05
- Event: Project knowledge architecture established — `docs/architecture/`, `docs/adr/`, `docs/domain/`, `docs/operations/`, `docs/research/`; model-specific ownership replaced with role-based ownership across all documents.
- Status: DONE

### VH-010
- Date: 2026-08-05
- Event: Runtime v1 migration — `.colore/` restructured into flat authoritative document set (`bootstrap.md`, `state.md`, `sprint.md`, `next.md`, `roadmap.md`, `architecture.md`, `changelog.md`, `runtime.md`, `roles.md`, `agents.md`) plus `adr/`, `playbooks/`, `templates/`.
- Status: DONE

### VH-011
- Date: 2026-08-08
- Event: GROWTH-001 — Growth AI integration research completed against official vendor documentation for Meta Business, Instagram Graph, WhatsApp Business, Altegio, Telegram Bot API and n8n. ADR-002 accepted: Growth AI enters as a sub-sprint inside FIRST REVENUE, structured as a connector layer rather than per-channel work.
- Status: DONE
- Evidence: `docs/research/GROWTH_AI_INTEGRATION_RESEARCH.md`, `.colore/adr/ADR-002-growth-ai-foundation.md`, R-002 in `research.md` (4 unverified contracts recorded as gaps).

### VH-012
- Date: 2026-08-08
- Event: GROWTH-002..005 — Growth AI Foundation delivered. A connector layer found uncommitted in the working tree was adopted rather than duplicated, then extended with capability dispatch, dry-run state and published rate limits; Telegram, Meta and n8n connectors added; the `Meta → n8n → Coloré OS → Growth AI → Telegram` flow wired end to end with a persisted, queryable trace.
- Status: DONE
- Evidence: commits `4fb21d5`, `25d6e66`, `6343318`, `61f70e7`. 116 tests passing. Live verification against the deployed container: WhatsApp payload classified BOOKING (0.98) at high priority, Instagram DM classified PRICE, Meta retry deduplicated, Instagram echo skipped, delivery receipt skipped, unauthenticated ingest rejected 401, unconfigured Meta paths closed 403/503. `scripts/doctor.sh` reports SYSTEM HEALTHY.
- Note: `requests` was imported by `altegio/client.py` and `n8n_adapter.py` but never declared in `requirements.txt`. Present in the dev virtualenv, absent from the image — the tests passed while the container could not import the module at all. Declared in `6343318`'s predecessor `4fb21d5`.

### VH-013
- Date: 2026-08-08
- Event: GROWTH-007 — Growth AI Brain v0.1. Telegram became the Product Owner's interface: `Статус`, `Что нового?`, `Что требует моего решения?`, `Что делаем дальше?`. Telegram credentials configured in the deployment, first live message delivered to the owner.
- Status: DONE
- Evidence: `backend/app/growth/{commands,system_status,runtime_reader,bot}.py`, `infrastructure/colore-growth-bot.service`. 142 tests passing. Bot `@Colore_Growth_bot` active under systemd, first owner command answered 10:02.
- Note: the bot runs on the host rather than in the backend container. Every question it answers needs the git tree, `.colore/`, `scripts/doctor.sh` or the sibling containers — none of which the image contains. `deploy.sh` now restarts it, so a deploy cannot leave the bot on an older commit.

### VH-014
- Date: 2026-08-08
- Event: GROWTH-008 — Growth AI connected to real business data. Altegio verified live and reporting: Colore beauty lab (id 1316083), 334 clients, 90 services, 4 specialists, 47 appointments in 30 days. New `Аналитика` command returns leads, bookings, conversion, missing data and recommendations. Meta Business decisions documented as R-003.
- Status: DONE
- Evidence: `backend/app/growth/{business_data,analytics}.py`, `docs/research/META_BUSINESS_DECISIONS.md`, R-003 in `research.md`. 166 tests passing.
- Note: `ALTEGIO_COMPANY_ID=2403` in the environment is stale — Altegio answers "No location with identifier 2403 found". The real id is 1316083. Company id is now resolved from the API at runtime and the mismatch is reported rather than silently preferred.
- Note: conversion is reported only over leads that can be attributed to a booking by phone. Bookings divided by leads was rejected as a metric: most of the salon's 47 appointments have no connection to Growth AI, so that ratio would look like an answer and mean nothing.

### VH-015
- Date: 2026-08-08
- Event: GROWTH-009 — attribution loop closed. Five confirmed business outcomes (lead created, appointment booked, appointment cancelled, client arrived, no-show) are built into Conversions API events with unique event_id, event_time, action_source and hashed matching fields, queued in `meta_conversions`, and reported by the new Telegram command `Meta`. 235 real events queued from live Altegio data.
- Status: DONE
- Evidence: `backend/app/growth/{attribution,meta_sync,meta_renderer}.py`, `backend/app/models/meta_conversion.py`, migration `b2c3d4e5f6a7`, `docs/research/META_ATTRIBUTION_FLOW.md`. 195 tests passing. Idempotency verified live: two consecutive builds over 235 events inserted 0 rows on the second, 235 distinct event ids. No raw phone, email or name is stored — checked against the live table.
- Note: cancellations are invisible without `with_deleted=1` on the Altegio records endpoint — an undocumented parameter found by probing. Default call returned 341 records over 180 days with `deleted` false for all of them; with the flag, 383 of which 13 deleted. Recorded as R-004.
- Note: events are built only when a strong identifier (phone or email) exists. A name is not an identifier, so name-only records are skipped rather than sent unattributable. Instagram leads produce no event: IGSID is app-scoped and is not a phone.
- Blocker: nothing is sent. `META_ACCESS_TOKEN` and `META_DATASET_ID` do not exist on this server, so the queue accumulates instead of transmitting.

### VH-016
- Date: 2026-08-08
- Event: P0-001 — Meta delivery queue made recoverable. Delivery states are now queued, sending, sent, retry, permanent_failure. Failures are classified: network, timeout, 5xx, rate limit and configuration faults become retry with exponential backoff; only faults in the event itself (invalid payload, duplicate, past Metas 7-day window) become permanent_failure, and only per event.
- Status: DONE
- Evidence: `backend/app/growth/meta_delivery.py`, rewritten `send_pending` in `meta_sync.py`, migration `c3d4e5f6a7b8`. 27 new tests, 222 passing. Live queue migrated: 235 rows pending -> queued, then 229 expired as past the 7-day window, 6 remain sendable.
- Note: a batch that Meta refuses permanently is now halved and re-sent to isolate the offending event, instead of condemning its neighbours. Cost is at most 2·log2(n) extra requests; the alternative was losing up to 100 confirmed outcomes per bad event.
- Note: an expired token and an unknown dataset are classified temporary, not permanent, although the P0 brief lists invalid dataset as a candidate for permanent_failure. The event is valid in both cases and only the configuration is wrong; marking them permanent would recreate the exact defect being fixed. Deviation is deliberate and reversible.

### VH-017
- Date: 2026-08-08
- Event: P0-003 — universal integration scheduler. Generic job registry, interval/manual/dry-run/test execution, persisted run history, and per-job isolation. Meta conversions became the first job. Currency moved to configuration. Meta test events supported. Doctor verifies scheduler state; Telegram `Meta` reports Scheduler, Last Run, Next Run, Queue, Last Success, Last Error.
- Status: DONE
- Evidence: `backend/app/scheduler/`, `backend/app/growth/meta_job.py`, migration `d4e5f6a7b8c9`, `infrastructure/colore-scheduler.service`. 32 new tests, 254 passing. Service active on the host; doctor reports registered jobs, last and next execution, and failed jobs.
- Note: this closed the gap found in P0-002 — `send_pending` was reachable only through `synchronise`, which nothing called. With a valid token and dataset, zero events would ever have been transmitted.
- Note: `BUSINESS_CURRENCY` defaults to empty and an unset currency means events carry no value at all. The salon prices in RSD while its ad account bills in EUR; a wrong guess misstates every Purchase by roughly 100x, and no value is safer than an unverified one.
- Note: SQLAlchemy `echo` was hardcoded True. Harmless before, but a service ticking every 60s floods the journal and eventually the disk. Now `SQL_ECHO`, default False.

## Entry Template

### VH-XXX
- Date: TODO
- Event: TODO
- Status: TODO
- Evidence: TODO

## Source of Truth

This file owns historical decisions and verified past events only. Current state lives in [`state.md`](state.md).
