# Copilot Runtime Instructions

## Scope
- Applies to this repository only.

## Mandatory Read Before Work
- .colore/00_START.md
- .colore/01_CONTRACT.md
- .colore/02_PROJECT.md
- .colore/03_ARCHITECTURE.md
- .colore/04_STACK.md
- .colore/05_TASKS.md
- .colore/06_SESSION.md
- .colore/07_DECISIONS.md

## Every Workday Starts
- Start the workday with: @GitHub Начинаем день

## Read Before Every Task
- .colore/00_Master/PROJECT_STATE.md
- .colore/00_Master/KNOWN_STATE.md
- .colore/00_Master/TODAY.md
- .colore/00_Master/DECISIONS.md

## Runtime Rules
- Work on one task at a time.
- Do not interrupt active work with new ideas.
- Put new ideas into BACKLOG first.
- Follow task lifecycle exactly:
  - BACKLOG -> TODO -> DOING -> REVIEW -> DONE
- Main rule: Finish before Improve.
- Runtime always overrides AI memory.
- Runtime overrides AI assumptions.
- Copilot is responsible only for implementation.
- Never restart completed work.
- Never invent project facts.
- Never infer project phase automatically.
- Never convert historical events into current state.
- VERIFIED_HISTORY contains historical facts only.
- KNOWN_STATE contains current facts only.

## Guardrails
- Confirm workspace is /root/colore-os before changes.
- Prefer repository files as source of truth when information conflicts.
- Use `.colore/05_AI/` for AI role guidance and `.colore/PROMPTS/` for ready-to-use prompts.
- Keep unknown values explicitly marked as TODO.
