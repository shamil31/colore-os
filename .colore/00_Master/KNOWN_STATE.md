# Colore Runtime - Known State

Last verified: 2026-08-01

This file contains only the current verified project state.

Historical verified events belong only in .colore/08_VERIFIED_HISTORY.md.

## Verified Facts
- Workspace path is /root/colore-os.
- Runtime is stored under .colore.
- Git repository exists in this workspace.
- Git origin remote points to https://github.com/shamil31/colore-os.git.
- Runtime core docs currently exist:
  - 00_START.md
  - 01_CONTRACT.md
  - 02_PROJECT.md
  - 03_ARCHITECTURE.md
  - 04_STACK.md
  - 05_TASKS.md
  - 06_SESSION.md
  - 07_DECISIONS.md
- Master synchronization docs currently exist:
  - 00_Master/PROJECT_STATE.md
  - 00_Master/CURRENT_SPRINT.md
  - 00_Master/DECISIONS.md
  - 00_Master/KNOWN_STATE.md
  - 00_Master/BACKLOG.md
  - 00_Master/ROADMAP.md
  - 00_Master/WORKFLOW.md
- Current sprint is FIRST REVENUE.
- Main KPI is first revenue.
- Verified completed work:
  - Altegio Authentication
  - Company Discovery
  - Client Import
  - Visit Import
  - Revenue Engine
  - Revenue Report
  - Priority Report
  - Business Priority Report
  - Исправлен импорт стоимости визитов
  - Проверена корректность Revenue
  - Проверена Priority Formula
- Architecture operating chain is fixed:
  - Altegio -> Coloré OS -> Integrilla -> Client -> Altegio -> Revenue -> Learning
- Coloré OS does not replace Altegio.
- Coloré OS does not replace Integrilla.
- Backend and infra exist and are active in repository:
  - backend/app/main.py with /, /db, /clients routes
  - backend/app/api/clients.py CRUD for clients
  - backend/app/db/database.py SQLAlchemy engine and DB connectivity
  - infrastructure/docker-compose.yml with postgres, n8n, backend

## Unknowns
- Timestamp and identifier of the first live booking initiated by Coloré OS: TODO
- Campaign baseline values for conversion and uplift: TODO
- SLA for Integrilla delivery and retry guarantees: TODO
