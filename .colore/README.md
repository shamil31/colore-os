# Colore Runtime Map

This folder contains the project Runtime.

Its purpose is to tell the AI agents how to understand the project, how to work, and where to record operating state.

## Source Of Truth

Project files inside this repository are the source of truth.

If Runtime notes, prompts, or AI memory conflict with repository files, use the repository files.

## Knowledge Layers

- Project Documentation: the repository files that describe the product, backend, infrastructure, and business logic.
- Runtime: the `.colore/` operating system that tells AI agents how to work with the project day to day.
- Verified History: the historical record of confirmed project events stored in `.colore/08_VERIFIED_HISTORY.md`.
- AI Instructions: the role and operating rules stored in `.colore/05_AI/` and `.github/copilot-instructions.md`.
- Prompt Library: the ready-to-use prompts stored in `.colore/PROMPTS/`.

## Top-Level Files

- `00_START.md` - workspace check, workday start rule, and core execution flow.
- `01_CONTRACT.md` - collaboration contract between the project owner and AI.
- `02_PROJECT.md` - project purpose, scope, users, modules, and success criteria.
- `03_ARCHITECTURE.md` - system architecture and layer responsibilities.
- `04_STACK.md` - current technology stack.
- `05_TASKS.md` - roadmap and backlog status at the project level.
- `06_SESSION.md` - session history.
- `07_DECISIONS.md` - historical architecture and operating decisions.
- `08_VERIFIED_HISTORY.md` - confirmed historical project events only.

## 00_Master

`00_Master/` is the current working control layer.

Use it before every task to understand the current state of the project without rewriting historical files.

- `PROJECT_STATE.md` - current project snapshot.
- `KNOWN_STATE.md` - verified facts only.
- `TODAY.md` - one active task for the current day.
- `BACKLOG.md` - idea intake and backlog staging.
- `DECISIONS.md` - currently active decisions used during execution.
- `WORKFLOW.md` - current execution workflow rules.

## 05_AI

`05_AI/` defines AI-specific operating guidance.

- `CHATGPT.md` - ChatGPT role and operating responsibilities.
- `COPILOT.md` - Copilot role and operating responsibilities.
- `PROMPT_TEMPLATES.md` - reusable prompt patterns and prompt-writing guidance.

## PROMPTS

`PROMPTS/` contains ready-to-use prompts for specific AI tools.

These files are for direct use or copy-paste.

They are not the same as `05_AI/`, which explains roles and guidance.

They are also not the same as project documentation or verified history.

## Workday Start

Every workday starts with:

`@GitHub Начинаем день`

Before every task, read:

- `.colore/00_Master/PROJECT_STATE.md`
- `.colore/00_Master/KNOWN_STATE.md`
- `.colore/00_Master/TODAY.md`
- `.colore/00_Master/DECISIONS.md`

## Workday Close

Close the day by updating the session log, recording any new decisions, and setting the first task for the next workday.