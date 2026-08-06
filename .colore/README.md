# Coloré OS — Runtime

This folder is the Runtime: the authoritative operating system that tells any agent how to understand the project, how to work, and where state lives.

**Do not read files in this folder in arbitrary order.** The mandatory reading order, the operating principles, and the execution lifecycle are all defined in [`runtime.md`](runtime.md) — start there, or start at [`bootstrap.md`](bootstrap.md), which triggers the same procedure.

## Structure

| File / Folder | Owns |
|---|---|
| [`bootstrap.md`](bootstrap.md) | Runtime entry procedure |
| [`state.md`](state.md) | Verified current project state |
| [`sprint.md`](sprint.md) | Active sprint |
| [`next.md`](next.md) | Active task |
| [`research.md`](research.md) | Project memory: findings and unfinished investigations |
| [`roadmap.md`](roadmap.md) | Stages, backlog, long-term direction |
| [`architecture.md`](architecture.md) | System architecture and guardrails |
| [`changelog.md`](changelog.md) | Historical decisions and verified events |
| [`roles.md`](roles.md) | Model-independent role responsibilities |
| [`agents.md`](agents.md) | Current tool-to-role assignment |
| [`runtime.md`](runtime.md) | Mandatory reading order and operating contract |
| [`adr/`](adr/) | Architecture Decision Records |
| [`playbooks/`](playbooks/) | Operating procedures: Open Day, Close Day, Release |
| [`templates/`](templates/) | Reusable document templates |

## Project Memory

Four documents hold forward-looking information, and they are routinely confused. They are not interchangeable.

| Document | Holds | Question it answers | Who decides what goes in |
|---|---|---|---|
| [`roadmap.md`](roadmap.md) | Sequenced delivery stages and the backlog | *What are we going to build, and in what order?* | Product |
| Backlog (inside `roadmap.md`) | Agreed work waiting its turn | *What is queued?* | Product |
| [`research.md`](research.md) | Findings, unfinished investigations, recovered work | *What did we discover but not finish?* | Whoever found it |
| [`adr/`](adr/) | Decisions already taken and binding | *What did we settle, and why?* | Architecture |

The distinctions that matter:

- **Roadmap is commitment. Research is not.** An entry in `research.md` is not scheduled, not approved and not owed to anyone. It is a fact the project must not forget.
- **Backlog is agreed work. Research is unevaluated.** A backlog item is understood well enough to be built. A research entry may turn out to be worthless — that outcome is recorded, not deleted.
- **ADR is closed. Research is open.** An ADR ends a question. A research entry keeps one alive so it is answered deliberately instead of by accident.
- **Research is memory, not intent.** It exists because the alternative is rediscovering — or destroying — work that was already paid for.

An entry is never deleted. When resolved it is marked `Closed` with the outcome, so the reasoning survives even when the finding is rejected.

Entries marked **Deletion risk: High** must not be deleted, moved or cleaned up while their research is open.

## Source of Truth

Repository code always wins over documentation. Within documentation, `.colore/` outranks everything else — see [`runtime.md`](runtime.md) for the full hierarchy.

## Version

**Runtime v1.0** — effective 2026-08-05. See [`adr/ADR-001-runtime-first-development.md`](adr/ADR-001-runtime-first-development.md).
