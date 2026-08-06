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
| [`roadmap.md`](roadmap.md) | Stages, backlog, long-term direction |
| [`architecture.md`](architecture.md) | System architecture and guardrails |
| [`changelog.md`](changelog.md) | Historical decisions and verified events |
| [`roles.md`](roles.md) | Model-independent role responsibilities |
| [`agents.md`](agents.md) | Current tool-to-role assignment |
| [`runtime.md`](runtime.md) | Mandatory reading order and operating contract |
| [`adr/`](adr/) | Architecture Decision Records |
| [`playbooks/`](playbooks/) | Operating procedures: Open Day, Close Day, Release |
| [`templates/`](templates/) | Reusable document templates |

## Source of Truth

Repository code always wins over documentation. Within documentation, `.colore/` outranks everything else — see [`runtime.md`](runtime.md) for the full hierarchy.

## Version

**Runtime v1.0** — effective 2026-08-05. See [`adr/ADR-001-runtime-first-development.md`](adr/ADR-001-runtime-first-development.md).
