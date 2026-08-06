# Coloré OS — Runtime Bootstrap

## Runtime Header

This document is the Runtime Entry Contract.
Reading this document starts a new working session.
Any agent MUST execute the Runtime Entry Procedure before answering or acting on anything else.

## Runtime Entry Procedure

1. Confirm workspace: `/root/colore-os`, git repository present.
2. Read, in order, per [`runtime.md`](runtime.md):
   - [`state.md`](state.md)
   - [`research.md`](research.md)
   - [`sprint.md`](sprint.md)
   - [`next.md`](next.md)
   - [`architecture.md`](architecture.md)
3. Confirm current sprint and active task.
4. Confirm no unresolved contradiction between the five files above.
5. Report exactly: Current Goal, Current Sprint, Critical Path, Today's Task, Responsible, Expected Result.
6. Wait for the user before starting new work.

## Project Memory Rule

Check the Review Queue in [`research.md`](research.md) before starting work.

Every agent — ChatGPT, Claude Code, GitHub Copilot, any future one, human included — **must read [`research.md`](research.md) before starting new development.**

Before building anything, check whether an open entry already covers it. If one does, say so and raise it before writing code: the project has already paid for that work once.

Entries marked **Deletion risk: High** must not be deleted, moved or cleaned up while their research is open.

## Commands

- **Open Day** = execute this Runtime Entry Procedure. Full checklist: [`playbooks/Open Day.md`](playbooks/Open%20Day.md).
- **Close Day** = review completed work, update `state.md`, `sprint.md`, `next.md`, `changelog.md`. Full checklist: [`playbooks/Close Day.md`](playbooks/Close%20Day.md).
- **Release** = ship a sprint result. Full checklist: [`playbooks/Release.md`](playbooks/Release.md).

## Authoritative State

This file defines the entry procedure only. It does not contain project state.

Project state lives in `state.md`. Open findings live in `research.md`. Sprint lives in `sprint.md`. Active task lives in `next.md`. None of these may contradict `runtime.md`.

## Do Not Include In This File

- Project snapshot or status
- Long explanations or README-like content
- Marketing text
- Technology stack details
- Implementation details

END OF RUNTIME CONTRACT

If you are reading this document: execute the Runtime Entry Procedure immediately. Do not ask whether to start. Runtime has already started.
