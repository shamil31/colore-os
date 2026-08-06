# Coloré OS — Runtime Bootstrap

## Runtime Header

This document is the Runtime Entry Contract.
Reading this document starts a new working session.
Any agent MUST execute the Runtime Entry Procedure before answering or acting on anything else.

## Runtime Entry Procedure

1. Confirm workspace: `/root/colore-os`, git repository present.
2. Read [`state.md`](state.md).
3. Read [`research.md`](research.md).
4. **Emit the Project Memory Report** (format below) and acknowledge every open entry.
   **This step is blocking.** Steps 5 onward may not begin until it is done.
5. Read [`sprint.md`](sprint.md), [`next.md`](next.md), [`architecture.md`](architecture.md).
6. Confirm current sprint and active task.
7. Confirm no unresolved contradiction between the five files above.
8. Report exactly: Current Goal, Current Sprint, Critical Path, Today's Task, Responsible, Expected Result.
9. Wait for the user before starting new work.

## Project Memory Report

After reading [`research.md`](research.md), and before anything else, emit this block. The format is fixed — do not reword, summarise or reorder it.

**When there are no open research entries:**

```
=== PROJECT MEMORY REPORT ===

Project Memory:
No open research.
```

**When open entries exist**, emit the header once, then one block per open entry:

```
=== PROJECT MEMORY REPORT ===

Project Memory

Open Research

R-001
Recovered OpenHands Domain Model

When to revisit:
Before Altegio integration
and Production Booking Engine.

Status:
Pending Review.

Required action:
Acknowledge.
```

Then write the acknowledgement explicitly, one line per entry:

```
Acknowledged R-001.
```

**Without that line the Runtime Entry Procedure is not complete.**

An entry is open when its Status is `Pending Review`, `Under Review` or `Adopted`. Entries marked `Rejected` or `Closed` are not reported.

## Blocking Rule

No Sprint, no Next Task, no development, no code, no file changes — nothing — may begin until the Project Memory Report has been emitted and every open entry acknowledged.

An agent that starts work without it has not entered the Runtime. Stop and emit the report.

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

Your first output of the session must contain `=== PROJECT MEMORY REPORT ===`.
