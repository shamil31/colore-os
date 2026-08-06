# Playbook: Open Day

Trigger: start of a working session, or the command "Open Day" / "Начинаем день".

## Procedure

1. Confirm workspace: `/root/colore-os`, `.git` present.
2. Run `git status` and `git log --oneline -5`.
3. Read, in this exact order (per [`../runtime.md`](../runtime.md)):
   1. [`../bootstrap.md`](../bootstrap.md)
   2. [`../state.md`](../state.md)
   3. [`../sprint.md`](../sprint.md)
   4. [`../next.md`](../next.md)
   5. [`../architecture.md`](../architecture.md)
4. Determine the last fully closed sprint. **If the previous sprint is not closed, new task selection is forbidden** — resolve or explicitly re-scope the open sprint first.
5. Determine the critical path: the single next objective that most directly advances FIRST REVENUE. Not a list of ideas, not options — one target.
6. Check whether that target is revenue-relevant. If it does not advance FIRST REVENUE, move it to [`../roadmap.md`](../roadmap.md) backlog automatically and select the next candidate.
7. Assign the task by type, per [`../agents.md`](../agents.md):
   - Research → Engineering (Claude)
   - Integration/Build → Engineering + Operations (Claude Code)
   - Architecture decision → Architecture (ChatGPT)
   - Business decision → Product (Shamil)
8. Move exactly one task to DOING.

## Forbidden During Open Day

- Presenting multiple options and asking "what should we do?"
- Reopening a closed sprint.
- Revisiting an already-approved document.
- Starting a new architecture document without demonstrated necessity.

## Required Output

At the end of every Open Day, report exactly these six fields, nothing more:

```
Current Goal:
Current Sprint:
Critical Path:
Today's Task:
Responsible:
Expected Result:
```

## Source

Governed by [`../runtime.md`](../runtime.md) and [`ADR-001-runtime-first-development`](../adr/ADR-001-runtime-first-development.md).
