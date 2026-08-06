# Playbook: Close Day

Trigger: end of a working session, or the command "Close Day" / "Закрываем день".

## Procedure

1. Check status of the current DOING task in [`../next.md`](../next.md).
2. Record only verified outcomes — nothing inferred, nothing assumed.
3. Update [`../state.md`](../state.md) with newly verified facts and completed work.
4. Update [`../sprint.md`](../sprint.md) if scope or status changed.
5. Update [`../next.md`](../next.md) with the first task for the next session.
6. Append new decisions and verified events to [`../changelog.md`](../changelog.md).
7. Confirm no contradiction exists between `state.md`, `sprint.md`, `next.md`, and `architecture.md`.
8. Stage and commit: `git add .colore/` plus any other changed files, with a clear commit message.

## Forbidden During Close Day

- Recording unverified or assumed progress as done.
- Leaving two files with conflicting claims about the same fact.
- Silently dropping an open decision without recording it in `changelog.md`.

## Required Output

A short summary:

```
Completed:
Updated files:
Next task:
Open questions:
```

## Source

Governed by [`../runtime.md`](../runtime.md).
