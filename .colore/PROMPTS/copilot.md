## Copilot Ready Prompts

This file contains ready-to-use prompts for GitHub Copilot work inside this repository.

## Start Of Day

@GitHub Начинаем день

Read the Runtime, confirm the workspace, and identify the current active task without inventing project facts.

## Before Task

Read:

- `.colore/00_Master/PROJECT_STATE.md`
- `.colore/00_Master/KNOWN_STATE.md`
- `.colore/00_Master/TODAY.md`
- `.colore/00_Master/DECISIONS.md`

Then implement only the active task.

## Implementation Guardrails

- Runtime overrides AI memory.
- Copilot is responsible only for implementation.
- Never restart completed work.
- Never invent project facts.

## Close Day

Summarize completed implementation work and list any runtime updates that still need owner confirmation.
