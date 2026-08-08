# Coloré OS — Next

Last updated: 2026-08-08

## Active Task

Growth AI Foundation — connector layer and one end-to-end trace.

- **Status:** REVIEW
- **Sub-sprint:** GROWTH AI FOUNDATION (see [`sprint.md`](sprint.md), [`adr/ADR-002-growth-ai-foundation.md`](adr/ADR-002-growth-ai-foundation.md))
- **Responsible role:** Engineering

## Delivered

1. Integration research from official documentation — `docs/research/GROWTH_AI_INTEGRATION_RESEARCH.md`
2. Connector Gateway, Integration Registry, Capability Registry, Event Bus
3. Connectors: Telegram, Meta, n8n, Altegio (read-only), OpenAI
4. Inbound event endpoint, Growth AI decision service, outbound dispatch
5. End-to-end trace, verified live against the deployed container

## Definition of Done — status

| # | Criterion | Status |
|---|---|---|
| 1 | Meta-shaped event normalised, deduplicated, routed | DONE — verified live |
| 2 | Growth AI produces a decision | DONE — BOOKING 0.98 / high, with a written reason |
| 3 | Decision dispatched through Telegram | DONE as dry run — no bot token exists yet |
| 4 | Every step visible in one queryable trace | DONE — `GET /growth/events/{id}` |
| 5 | `scripts/doctor.sh` reports SYSTEM HEALTHY | DONE |

## What remains before this is DONE

**One thing, and it is not code:** a Telegram bot token and operator chat id.
Until they exist, criterion 3 is a recorded dry run rather than a person being
told. Steps: [`../docs/operations/GROWTH_AI_SETUP.md`](../docs/operations/GROWTH_AI_SETUP.md), Step 1, about five minutes.

Meta credentials and the n8n workflow are Steps 2–3 of the same document. They
are not blockers for closing this task — the n8n hop is proven by the endpoint
it calls.

## Next After This

Priority → Integrilla manual transport loop resumes (previous active task,
unchanged in scope), unless Product redirects.

## Do Not Work On

Altegio write-back (ADR-002 decision 6). Outbound messaging to clients on any
channel (ADR-002 decision 5). Identity resolution across channels — review
R-001 first, it already models this.

## Source of Truth

This file owns the single active task only. If it conflicts with the scope in [`sprint.md`](sprint.md), `sprint.md` wins.
