# Engineering Runtime Instructions

## Scope
- Applies to this repository only.

## First Instruction
- Read 09_UAOP.md before reading any other Runtime document.

## Mandatory Read Before Work
- .colore/09_UAOP.md
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
- Engineering is responsible for implementation.
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

## Backend Runtime Commands
- All backend Python commands must run inside the project virtual environment.
- Required command pattern:
  1. `source .venv/bin/activate`
  2. `python ...`
- Do not use direct system interpreter commands in backend runtime instructions.

## Resource Efficiency
- Minimize unnecessary repository scans.
- Read only the files required for the current task.
- Reuse Runtime knowledge instead of rediscovering information.
- Keep prompts concise.
- Avoid repeating completed analysis.

# AI Efficiency Standard

## Core Principle
- Always achieve the required result using the minimum practical AI resources.

## Rules
1. Read Runtime before searching the repository.
2. Never rediscover information that already exists in Runtime.
3. Search only the files required for the current task.
4. Prefer updating existing documentation over creating duplicate files.
5. Keep prompts concise.
6. When the task changes significantly, prefer starting a new session instead of carrying unnecessary context.
7. Use the lowest-cost capable tool.

Priority:

Local tools
↓

Assigned engineering support
↓

Coordinated operations support
↓

External services

8. Avoid repeated repository-wide scans unless Runtime indicates repository structure has changed.
9. Reuse previous verified knowledge whenever possible.
10. Documentation is part of the project memory.
Every verified discovery should be documented so it never needs to be rediscovered.
