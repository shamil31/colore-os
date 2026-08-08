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

## Entry Template

### VH-XXX
- Date: TODO
- Event: TODO
- Status: TODO
- Evidence: TODO

## Source of Truth

This file owns historical decisions and verified past events only. Current state lives in [`state.md`](state.md).
