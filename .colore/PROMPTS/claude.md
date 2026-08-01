## Claude Ready Prompts

This file contains ready-to-use prompts for Claude work inside this repository.

## Start Of Day

Начинаем день.

Read the Runtime, confirm the workspace, and report the current active task from project files only.

## Before Task

Read:

- `.colore/00_Master/PROJECT_STATE.md`
- `.colore/00_Master/KNOWN_STATE.md`
- `.colore/00_Master/TODAY.md`
- `.colore/00_Master/DECISIONS.md`

Then continue only the active task.

## Guardrails

- Runtime overrides AI memory.
- Never restart completed work.
- Never invent project facts.

## Close Day

Summarize completed work, identify any decision updates, and point to the first task for the next workday.
