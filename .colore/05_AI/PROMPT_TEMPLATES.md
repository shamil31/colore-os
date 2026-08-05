# Colore Runtime - Prompt Templates

## Purpose
- Provide reusable templates for AI runtime prompts.
- This file explains reusable prompt patterns and prompt-writing guidance.
- Ready-to-use prompts belong in `.colore/PROMPTS/`.

## Template: Runtime Start
1. Confirm workspace path.
2. Read runtime core files.
3. Read `.colore/00_Master/PROJECT_STATE.md`, `.colore/00_Master/KNOWN_STATE.md`, `.colore/00_Master/TODAY.md`, and `.colore/00_Master/DECISIONS.md` before the task.
4. Check git status and current task state.
5. Report current phase and next actionable task.

## Template: Runtime Task Execution
1. Restate active task.
2. Define acceptance criteria.
3. Execute only current task scope.
4. Move task state through REVIEW before DONE.

## Prompt Writing Guidance
- Use project files as the source of truth.
- Keep unknown values explicitly marked as TODO.
- Do not restart completed work.
- Keep prompts aligned with the Runtime role split between Architect and Engineering.

## Template: Runtime Day Close
1. Summarize completed work.
2. Update session and decision logs.
3. Set first task for next day.

## Unknowns
- Unified template variables set: TODO
- Prompt versioning convention: TODO
