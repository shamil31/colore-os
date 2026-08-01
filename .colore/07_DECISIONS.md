# Coloré OS — DECISIONS

## Журнал архитектурных решений

Этот файл является историческим журналом решений.

Он хранит подтвержденные архитектурные и операционные решения проекта.

Текущий рабочий набор решений для ежедневного исполнения ведется отдельно в `.colore/00_Master/DECISIONS.md`.

Исторические записи не должны заменяться ежедневными рабочими заметками.

### DEC-001

VPS является основной средой разработки.

### DEC-002

Workspace проекта — /root/colore-os.

### DEC-003

Runtime хранится внутри .colore.

### DEC-004

Работа ведется по циклу:

BACKLOG → TODO → DOING → REVIEW → DONE.

### DEC-005

Главное правило:

Finish before Improve.

### DEC-006

Revenue First becomes Product Strategy.

Описание:

Coloré развивается в двух параллельных потоках:

1. Revenue
2. Product

Ни один поток не должен блокировать другой.

Разработка продукта должна непрерывно увеличивать бизнес-ценность.

### DEC-007

AI Resource Policy

Правила:

- Always prefer the lowest-cost tool that can complete the task.
- Local models (Ollama and future local LLMs) are the default choice whenever practical.
- GitHub Copilot Chat is used for everyday development assistance.
- GitHub Cloud Agent is reserved for large autonomous tasks, repository-wide analysis, documentation generation, and long-running work.
- ChatGPT is responsible for architecture, product strategy, business design, planning, reviews, and project management.
- Before using a cloud AI service, evaluate whether the expected time savings justify the credit cost.
- Optimize for long-term sustainability, not maximum AI usage.

### DEC-008

AI Efficiency Standard adopted as permanent project policy.

Правила:

- Always achieve the required result using the minimum practical AI resources.
- Read Runtime before searching the repository.
- Never rediscover information that already exists in Runtime.
- Search only the files required for the current task.
- Prefer updating existing documentation over creating duplicate files.
- Keep prompts concise.
- When the task changes significantly, prefer starting a new session instead of carrying unnecessary context.
- Use the lowest-cost capable tool.

Priority:

Local tools
↓

GitHub Copilot Chat
↓

GitHub Cloud Agent
↓

External cloud models

- Avoid repeated repository-wide scans unless Runtime indicates repository structure has changed.
- Reuse previous verified knowledge whenever possible.
- Documentation is part of the project memory.
- Every verified discovery should be documented so it never needs to be rediscovered.

### DEC-009

Phase Transition and Runtime Architecture Milestone

Решение:

- Phase 0 (Project Operating System) признана завершенной (DONE).
- Phase 1 (Revenue Engine MVP) признана активной (ACTIVE).
- Архитектурный milestone проекта зафиксирован:
	- UAOP adopted.
	- Runtime architecture finalized.
	- AI-independent workflow established.
	- Revenue/Product dual operating model adopted.
	- AI Efficiency Standard adopted.

### DEC-010

FIRST REVENUE sprint declared as active operating mode.

Решение:

- Current sprint: FIRST REVENUE.
- Main goal: первая реальная запись клиента, инициированная Coloré OS.
- Main KPI: первая выручка.

### DEC-011

Revenue First and Reality First adopted as mandatory execution doctrine.

Решение:

- Prioritize direct path to first revenue over product expansion.
- Planning and reporting must be evidence-based.

### DEC-012

Role split fixed for current operating stage.

Решение:

- Claude = Independent Reviewer.
- Copilot = Implementation.
- GPT = CTO.

### DEC-013

Infrastructure continuity and scope boundary fixed.

Решение:

- Use existing infrastructure.
- Coloré OS does not replace Altegio.
- Coloré OS does not replace Integrilla.
- AI Administrator development is postponed until after first revenue.
