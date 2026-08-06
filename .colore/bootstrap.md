# Coloré OS — Runtime Bootstrap

## Runtime Header

This document is the Runtime Entry Contract.
Reading this document starts a new working session.
Any agent MUST execute the Runtime Entry Procedure before answering or acting on anything else.

## Runtime Entry Procedure

1. Confirm workspace: `/root/colore-os`, git repository present.
2. Read, in order, per [`runtime.md`](runtime.md):
   - [`state.md`](state.md)
   - [`sprint.md`](sprint.md)
   - [`next.md`](next.md)
   - [`architecture.md`](architecture.md)
3. Confirm current sprint and active task.
4. Confirm no unresolved contradiction between the four files above.
5. Report exactly: Current Goal, Current Sprint, Critical Path, Today's Task, Responsible, Expected Result.
6. Wait for the user before starting new work.

## Commands

- **Open Day** = execute this Runtime Entry Procedure. Full checklist: [`playbooks/Open Day.md`](playbooks/Open%20Day.md).
- **Close Day** = review completed work, update `state.md`, `sprint.md`, `next.md`, `changelog.md`. Full checklist: [`playbooks/Close Day.md`](playbooks/Close%20Day.md).
- **Release** = ship a sprint result. Full checklist: [`playbooks/Release.md`](playbooks/Release.md).

## Authoritative State

This file defines the entry procedure only. It does not contain project state.

Project state lives in `state.md`. Sprint lives in `sprint.md`. Active task lives in `next.md`. None of these may contradict `runtime.md`.

## Do Not Include In This File

- Project snapshot or status
- Long explanations or README-like content
- Marketing text
- Technology stack details
- Implementation details

END OF RUNTIME CONTRACT

If you are reading this document: execute the Runtime Entry Procedure immediately. Do not ask whether to start. Runtime has already started.
