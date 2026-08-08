# Coloré OS — Next

Last updated: 2026-08-08

## Active Task

Growth AI Foundation — build the connector layer and prove one end-to-end trace.

- **Status:** DOING
- **Sub-sprint:** GROWTH AI FOUNDATION (see [`sprint.md`](sprint.md), [`adr/ADR-002-growth-ai-foundation.md`](adr/ADR-002-growth-ai-foundation.md))
- **Rule:** Finish Before Improve — no other task starts until this reaches REVIEW → DONE.
- **Responsible role:** Engineering (see [`agents.md`](agents.md) for current tool assignment)

## Target Flow

```
Meta → n8n → Coloré OS → Growth AI → Telegram
```

## Steps

1. Integration research from official documentation — **DONE** (`docs/research/GROWTH_AI_INTEGRATION_RESEARCH.md`)
2. Connector Gateway, Integration Registry, Capability Registry
3. Connectors: n8n Adapter, Telegram, Altegio, Meta (minimal)
4. Inbound event endpoint, Growth AI decision service, outbound dispatch
5. End-to-end trace through the full chain

## Definition of Done

1. A Meta-shaped event posted to the Coloré OS inbound endpoint is normalised, deduplicated and routed.
2. Growth AI produces a decision from it.
3. The decision is dispatched through the Telegram connector — live if a bot token is configured, recorded as a dry-run trace if not.
4. Every step is visible in one queryable trace.
5. `scripts/doctor.sh` reports `SYSTEM HEALTHY` on the deployed container.

## Deferred — resumes after this task

- Priority → Integrilla manual transport loop (previous active task, unchanged in scope)

## Do Not Work On

Recovery Engine v2, AI Scoring improvements, Analytics Dashboard, Multi-tenant support, Advanced Reporting.
Altegio write-back (still deferred — ADR-002 decision 6).
Outbound messaging to clients on any channel (ADR-002 decision 5).

## Source of Truth

This file owns the single active task only. If it conflicts with the scope in [`sprint.md`](sprint.md), `sprint.md` wins.
