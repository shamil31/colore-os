# Coloré OS — Runtime v1

**Runtime version:** 1.0
**Effective:** 2026-08-05

## Purpose

This file defines the mandatory operating order for any agent — human or AI — working in this repository. It replaces the fragmented runtime (`00_START.md`, `01_CONTRACT.md`, `09_UAOP.md`, `00_Master/WORKFLOW.md`) with a single authoritative execution contract.

## Mandatory Reading Order

Every agent MUST read these files in this exact order before doing any work:

1. `.colore/bootstrap.md` — Runtime Entry Procedure
2. `.colore/state.md` — Verified current project state
3. `.colore/research.md` — Open findings and unfinished investigations
4. `.colore/sprint.md` — Active sprint definition
5. `.colore/next.md` — Active task
6. `.colore/architecture.md` — System architecture

```
bootstrap -> state -> research -> PROJECT MEMORY REPORT -> sprint -> next -> architecture
```

No step may be skipped. No step may be reordered.

`research.md` is read **before** sprint and task on purpose: a finding that already solves the work about to start must be known before that work is planned, not after it has been rebuilt.

## Mandatory Project Memory Report

After reading `research.md`, the agent MUST emit a `=== PROJECT MEMORY REPORT ===` block in the fixed format defined in [`bootstrap.md`](bootstrap.md), and MUST explicitly acknowledge every open entry (`Acknowledged R-001.`).

**This step blocks everything after it.** No Sprint, no Next Task, no development, no code, no file changes may begin until the report has been emitted and every open entry acknowledged.

Without the acknowledgement line the Runtime Entry Procedure is **not complete**, regardless of what else the agent has read or done.

Any working session that has open research and does not open with `=== PROJECT MEMORY REPORT ===` has violated the Runtime.

If any file is missing or contradicts another, stop and escalate through the Architecture role — do not guess.

## Non-Negotiable Operating Principles

1. **Revenue First** — every decision optimizes for business outcome, never for code elegance or completeness.
2. **Reality First** — planning and reporting are based on verified facts only, never assumptions.
3. **Finish Before Improve** — complete the current task before refactoring or optimizing.
4. **Single Source of Truth** — when information conflicts, repository code wins over documentation, and `.colore/` wins over all other documentation.
5. **One Document = One Responsibility** — every runtime document owns exactly one concern.
6. **Model Independence** — the project structure does not depend on any specific AI model. Abstract roles are defined in `roles.md`; current tool assignment is in `agents.md`.
7. **Runtime First Development** — see [`adr/ADR-001-runtime-first-development.md`](adr/ADR-001-runtime-first-development.md).
8. **Project Memory Is Mandatory** — open research is reported and acknowledged before any work begins. Nothing the project has already discovered may be silently forgotten or rebuilt.

## Execution Lifecycle

Work moves through exactly these stages, in order, without skipping:

```
BACKLOG -> TODO -> DOING -> REVIEW -> DONE
```

- One active task at a time (see `next.md`).
- New ideas enter the backlog (see `roadmap.md`); they do not interrupt active work.
- A task is complete only after REVIEW.
- Never restart completed work.
- Never invent project facts.
- Never reopen a closed decision without explicit Architecture or Product approval.

## Day Boundaries

- **Start of day:** run [`playbooks/Open Day.md`](playbooks/Open%20Day.md).
- **End of day:** run [`playbooks/Close Day.md`](playbooks/Close%20Day.md).
- **Shipping a sprint result:** run [`playbooks/Release.md`](playbooks/Release.md).

## Document Map

| File | Owns |
|---|---|
| `bootstrap.md` | Runtime entry procedure |
| `state.md` | Verified current state |
| `sprint.md` | Active sprint |
| `next.md` | Active task |
| `research.md` | Project memory: findings and unfinished investigations |
| `roadmap.md` | Stages, backlog, long-term direction |
| `architecture.md` | System architecture and guardrails |
| `changelog.md` | Historical decisions and verified events |
| `roles.md` | Model-independent role responsibilities |
| `agents.md` | Current tool-to-role assignment |
| `adr/` | Architecture Decision Records |
| `playbooks/` | Operating procedures (Open Day, Close Day, Release) |
| `templates/` | Reusable document templates |

## Amendment Rule

This file can only be changed through an ADR, approved by the Architecture role.

**Supersedes:** `00_START.md`, `01_CONTRACT.md`, `09_UAOP.md`, `00_Master/WORKFLOW.md`, `00_Master/PROJECT_CONSTITUTION.md` (principles section)
