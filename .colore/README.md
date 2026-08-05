# Colore Runtime Map

This folder contains the project Runtime.

Its purpose is to tell the AI agents how to understand the project, how to work, and where to record operating state.

## Source Of Truth

Project files inside this repository are the source of truth.

If Runtime notes, prompts, or AI memory conflict with repository files, use the repository files.

## Knowledge Layers

- Project Documentation: the repository files that describe the product, backend, infrastructure, and business logic.
- Runtime: the `.colore/` operating system that tells AI agents how to work with the project day to day.
- UAOP: the highest-level AI operating standard in `.colore/09_UAOP.md`.
- Verified History: the historical record of confirmed project events stored in `.colore/08_VERIFIED_HISTORY.md`.
- AI Instructions: the role and operating rules stored in `.colore/05_AI/` and `.github/copilot-instructions.md`.
- Prompt Library: the ready-to-use prompts stored in `.colore/PROMPTS/`.

## Top-Level Files

- `00_START.md` - workspace check, workday start rule, and core execution flow.
- `01_CONTRACT.md` - mandatory universal operating contract for any LLM.
- `02_PROJECT.md` - project purpose, scope, users, modules, and success criteria.
- `03_ARCHITECTURE.md` - system architecture and layer responsibilities.
- `04_STACK.md` - current technology stack.
- `05_TASKS.md` - roadmap and backlog status at the project level.
- `06_SESSION.md` - session history.
- `07_DECISIONS.md` - historical architecture and operating decisions.
- `08_VERIFIED_HISTORY.md` - confirmed historical project events only.
- `09_UAOP.md` - Universal AI Operating Protocol (highest-level model-independent AI standard).

## 00_Master

`00_Master/` is the current working control layer.

**⭐ BEFORE ANY SERIOUS WORK: Read `PROJECT_CONSTITUTION.md` first.**

Use it before every task to understand the current state of the project without rewriting historical files.

- **`PROJECT_CONSTITUTION.md`** - immutable project identity, principles, and strategic decisions. Read this before starting any task.
- `PROJECT_STATE.md` - current project snapshot.
- `CURRENT_SPRINT.md` - active sprint scope, KPI, and exit condition.
- `KNOWN_STATE.md` - verified facts only.
- `TODAY.md` - one active task for the current day.
- `BACKLOG.md` - idea intake and backlog staging.
- `ROADMAP.md` - synchronized execution stages.
- `DECISIONS.md` - currently active decisions used during execution.
- `WORKFLOW.md` - current execution workflow rules.
- `NEXT.md` - session entry point for any new LLM session.

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

**For any new work session, start here:**

1. Read `.colore/00_Master/PROJECT_CONSTITUTION.md` — understand immutable principles and current strategic focus
2. Read `.colore/09_UAOP.md` — understand universal AI operating protocol
3. Read `.colore/01_CONTRACT.md` — follow LLM operating contract

**Before every task, read:**

- `.colore/00_Master/PROJECT_CONSTITUTION.md` — project identity
- `.colore/00_Master/NEXT.md` — session entry point
- `.colore/00_Master/PROJECT_STATE.md` — current state
- `.colore/00_Master/TODAY.md` — today's focus
- `.colore/00_Master/DECISIONS.md` — active decisions
- `.colore/00_Master/KNOWN_STATE.md` — verified facts

## Workday Close

Close the day with Close Day procedure from .colore/01_CONTRACT.md.