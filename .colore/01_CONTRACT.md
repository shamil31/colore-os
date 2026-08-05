# Coloré OS - Universal Operating Contract

Last updated: 2026-08-05

This is a mandatory behavior contract for any actor entering the project.
It is not a project description.

## 1) Start Of Work (Mandatory)

Before any task, the LLM must:
1. Confirm workspace path: /root/colore-os.
2. Confirm repository is valid (git present).
3. Read Source Of Truth documents in this exact order:
	 - .colore/09_UAOP.md
	 - .colore/01_CONTRACT.md
	 - .colore/00_Master/PROJECT_STATE.md
	 - .colore/00_Master/CURRENT_SPRINT.md
	 - .colore/00_Master/DECISIONS.md
	 - .colore/00_Master/KNOWN_STATE.md
	 - .colore/00_Master/BACKLOG.md
	 - .colore/00_Master/ROADMAP.md
	 - .colore/00_Master/TODAY.md

If any step fails, execution must stop and be fixed first.

## 2) Source Of Truth Priority

When information conflicts, use this precedence:
1. .colore/00_Master/*.md
2. .colore/01_CONTRACT.md, .colore/02_PROJECT.md, .colore/03_ARCHITECTURE.md, .colore/05_TASKS.md
3. Historical files (.colore/06_SESSION.md, .colore/07_DECISIONS.md, .colore/08_VERIFIED_HISTORY.md)
4. All other project docs

Chat history is never a source of truth.

## 3) Non-Revisable Decisions (Unless Role Owner Explicitly Reopens)

- Revenue First.
- Reality First.
- Finish Before Improve.
- Main KPI: first revenue.
- Coloré OS does not replace Altegio.
- Coloré OS does not replace Integrilla.
- Use existing infrastructure.
- AI Administrator development is postponed.
- Role split:
	- Reviewer = Independent Review
	- Engineering = Implementation
	- Architect = Architecture Governance

## 4) Execution Model

- One active task at a time.
- Every task follows: BACKLOG -> TODO -> DOING -> REVIEW -> DONE.
- New ideas enter BACKLOG first.
- Closed questions are not reopened without explicit owner decision.
- No optimization work before completion of active P0 task.

## 5) Sync Project Procedure

When running Sync Project, LLM must:
1. Update all Source Of Truth docs.
2. Record all decisions made today.
3. Remove obsolete priorities and contradictions.
4. Ensure architecture and vision are aligned to current sprint.
5. Run consistency check across Source Of Truth.
6. Commit with meaningful message.

## 6) Open Day Procedure

1. Read .colore/bootstrap.md as the authoritative runtime contract.
2. Restore runtime context before answering.
3. Execute the Open Day protocol defined in bootstrap.
4. Confirm current sprint, current KPI, and one active product task.
5. Continue work from the restored state.

## 7) Close Day Procedure

1. Review the session and record only verified outcomes.
2. Update .colore/bootstrap.md with current phase, sprint, completed work, risks, next decision, and first task.
3. Update the current phase, sprint, completed work, and next task in the runtime state.
4. Update any blocked items and open questions.
5. Commit the day-close state with a meaningful message.

## 8) Failure Prevention Rules

- Never infer completion from assumptions.
- Never claim work done without repository evidence.
- Never shift priority from P0 revenue tasks to deferred tracks.
- Never replace systems that are declared foundational in decisions.

## 9) Amendment Rule

This contract can be changed only by explicit role-based decision recorded in the decisions log.
