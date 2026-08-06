# Coloré OS — Architecture

Last updated: 2026-08-05

## Revenue Architecture Chain

```
Altegio (CRM: clients, records, history)
   -> Coloré OS (Revenue Engine, Priority Engine, Decision Engine, Business Intelligence)
   -> Integrilla (message transport)
   -> Client
   -> Altegio (write-back)
   -> Revenue
   -> Learning
```

## Architectural Principles

- Coloré OS does not replace Altegio.
- Coloré OS does not replace Integrilla.
- Altegio remains CRM and appointment system of record.
- Integrilla remains message transport.
- Coloré OS acts as the revenue intelligence and decision layer above both.
- No platform replacement work — build within existing infrastructure.

## Core Components

### Revenue Engine
Determines revenue opportunities from CRM data.

### Priority Engine
Ranks clients and opportunities for action.

### Decision Engine
Selects action strategy and campaign intent. Implemented as the Lead Intelligence chain:
Lead Intelligence Model → Lead State Machine → Next Best Action Engine → Conversation Engine.
Full specification: [`docs/architecture/ARCHITECTURE_INDEX.md`](../docs/architecture/ARCHITECTURE_INDEX.md) and [`docs/architecture/RUNTIME_ARCHITECTURE.md`](../docs/architecture/RUNTIME_ARCHITECTURE.md).

### Business Intelligence
Measures outcomes and generates learning signals (Learning Loop).

## Data and Feedback Loop

1. Read state from Altegio.
2. Generate priorities and decisions in Coloré OS.
3. Deliver messages through Integrilla.
4. Capture client response and booking result in Altegio.
5. Update revenue reports and learning loop.

## Technology Stack

Python, FastAPI, PostgreSQL, SQLAlchemy, Alembic, Redis, Docker, Nginx, Git, GitHub, VS Code, external API integrations (Altegio, Integrilla).

## Current Boundary

AI Administrator is explicitly out of scope until the first revenue KPI is reached (see [`roadmap.md`](roadmap.md), Stage 3).

## Detailed System Design

Full end-to-end architecture, ADRs, and domain models live under `docs/`:

- [`docs/architecture/ARCHITECTURE_INDEX.md`](../docs/architecture/ARCHITECTURE_INDEX.md) — navigation and dependency graph
- [`docs/architecture/RUNTIME_ARCHITECTURE.md`](../docs/architecture/RUNTIME_ARCHITECTURE.md) — complete data flow
- [`docs/adr/`](../docs/adr/) — permanent architecture decisions
- [`docs/domain/customer_intelligence/`](../docs/domain/customer_intelligence/) — Lead Intelligence domain model

## Source of Truth

This file owns the top-level system architecture and non-negotiable guardrails only. Detailed component design lives in `docs/architecture/`. Decisions live in `docs/adr/` and [`changelog.md`](changelog.md).
