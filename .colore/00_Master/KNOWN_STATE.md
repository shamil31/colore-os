# Colore Runtime - Known State

Last verified: 2026-08-01

This file contains only the current verified project state.

Historical verified events belong only in `.colore/08_VERIFIED_HISTORY.md`.

## Verified Facts
- Workspace path is /root/colore-os.
- Runtime is stored under .colore.
- Git repository exists in this workspace.
- Git `origin` remote points to `https://github.com/shamil31/colore-os.git`.
- Runtime core docs currently exist:
  - 00_START.md
  - 01_CONTRACT.md
  - 02_PROJECT.md
  - 03_ARCHITECTURE.md
  - 04_STACK.md
  - 05_TASKS.md
  - 06_SESSION.md
  - 07_DECISIONS.md
- Stack documented in .colore/04_STACK.md includes:
  - Python, FastAPI, PostgreSQL, SQLAlchemy, Alembic, Redis, Docker, Nginx, Git, GitHub, VS Code, OpenAI API
- DEC-001 states that VPS is the primary development environment.
- DEC-002 states that the project workspace path is /root/colore-os.
- DEC-003 states that the Runtime is stored inside .colore.
- `Runtime v1.0` is listed as DONE in `.colore/05_TASKS.md`.
- Current project phase is `Phase 4 - Conversation Flows`.
- Current next task in the project roadmap is `Package 03 - Client Retention & Reactivation`.
- `backend/app/main.py` defines a FastAPI app with `/`, `/db`, and `/clients` routes.
- `backend/app/api/clients.py` implements CRUD endpoints for clients.
- `backend/app/db/database.py` implements SQLAlchemy engine and PostgreSQL connection testing.
- `infrastructure/docker-compose.yml` defines `postgres`, `n8n`, and `backend` services.
- docs/ contains core product and AI framework documents plus 13 scenario files.
- .colore/PROMPTS/chatgpt.md has runtime instructions.
- .colore/PROMPTS/copilot.md contains ready-to-use GitHub Copilot prompts.
- .colore/PROMPTS/claude.md contains ready-to-use Claude prompts.

## Unknowns
- Current sprint name or identifier: TODO
- Coloré Development OS v1.0 implemented: TODO
- Git workflow operational: TODO
- Copilot Chat workflow operational: TODO
- Copilot Cloud Agent tested: TODO
- Verified external API integrations beyond PostgreSQL connectivity and local backend routes: TODO
- Formal owner-approved priorities beyond current TODO list: TODO
- Target deadline for Phase 4 completion: TODO
- Definition of done for Package 03 in runtime docs: TODO
