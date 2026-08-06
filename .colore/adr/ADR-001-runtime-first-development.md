# ADR-001: Runtime First Development

**Decision Owner:** Architecture
**Status:** Accepted
**Date:** 2026-08-05

---

## Context

Before this decision, project state was scattered across a numbered file sequence (`00_START.md` … `09_UAOP.md`), a separate `00_Master/` sync layer, role prompt files, and a bootstrap file that mixed entry procedure with project snapshot. Every new session had to reconcile multiple partially-overlapping sources before any real work could start, and updates frequently landed in only one of several places holding the same fact.

## Decision

**No engineering, research, or product work begins until the Runtime has been read, in the order defined in `runtime.md`, and the agent has reported current goal, sprint, critical path, task, responsible role, and expected result.**

Runtime is not documentation about the project — it is the operating precondition for working on the project. An agent that has not completed the Runtime Entry Procedure is not authorized to act, regardless of how well it can infer context from the repository or from memory.

This principle governs the shape of `.colore/`:
- One flat set of authoritative files, each with exactly one responsibility (`state.md`, `sprint.md`, `next.md`, `roadmap.md`, `architecture.md`, `changelog.md`, `roles.md`, `agents.md`)
- One entry contract (`bootstrap.md`) that contains procedure only, never state
- One master order document (`runtime.md`) that no other file may contradict
- Operating procedures externalized as playbooks (`Open Day`, `Close Day`, `Release`) rather than re-described inline wherever needed

## Consequences

**Positive:**
- A new agent becomes productive within minutes, not by re-deriving project history.
- Facts have exactly one home; there is no second copy to fall out of sync.
- Runtime failures are detectable: if the entry procedure cannot be completed, work correctly stops.

**Negative:**
- Every fact change requires updating the one correct file, not just "somewhere convenient" — this is intentional friction, not a bug.
- Runtime discipline must be actively maintained during Close Day; skipping it degrades the guarantee for the next session.

## Rationale

A project that can be picked up correctly by any capable agent, at any time, without a live human walkthrough, requires that "where do I start" and "what is true right now" have single, unambiguous answers. Runtime First Development makes the Runtime itself the dependency every unit of work is built on, not an afterthought maintained around the work.

## Related Decisions

- `changelog.md` DEC-014 — Model Independence
- `docs/adr/ADR-0002-Single-Source-of-Truth.md`
- `docs/adr/ADR-0003-One-Document-One-Responsibility.md`

---

**Approval Authority:** Architecture
**Approval Date:** 2026-08-05
