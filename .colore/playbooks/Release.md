# Playbook: Release

Trigger: a sprint, sub-sprint, or approved artifact is ready to ship.

## Procedure

1. Confirm the artifact completed the full document or task lifecycle (see `docs/operations/SOP_DOCUMENT_LIFECYCLE.md` or `SOP_TASK_LIFECYCLE.md`): IDEA → DESIGN → REVIEW → APPROVED before integration, or IDEA → RESEARCH → DESIGN → REVIEW → BUILD → VERIFY before deploy.
2. Verify no contradiction with [`../architecture.md`](../architecture.md) or any file in `docs/adr/`.
3. Verify [`../state.md`](../state.md) reflects the artifact as completed work.
4. Verify [`../sprint.md`](../sprint.md) sub-sprint log is updated if applicable.
5. Update [`../roadmap.md`](../roadmap.md) if the release changes backlog priority.
6. Append the release event to [`../changelog.md`](../changelog.md) as a new `VH-XXX` entry.
7. Commit with a message describing exactly what was integrated — one commit per release unless explicitly instructed otherwise.
8. Confirm no broken internal links were introduced (check references to moved or renamed files).

## Forbidden During Release

- Releasing an artifact that skipped REVIEW or VERIFY.
- Releasing architecture changes without Architecture role sign-off.
- Bundling unrelated changes into a release commit.

## Required Output

```
Released:
Sprint:
Files changed:
Commit:
Sprint Status: OPEN | READY FOR NEXT REVIEW | CLOSED
```

## Source

Governed by [`../runtime.md`](../runtime.md).
