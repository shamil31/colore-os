# Colore OS Bootstrap

This file is the single entry point for the Colore OS project runtime. Read it first for context, status, and next actions.

## Project
- Name: Colore OS
- Product: AI Administrator for Beauty Salons
- Mission: Help salon operators manage clients, visits, revenue insights, and campaign operations with reliable automation.

## Current State
- Core backend service is in place under backend/.
- Revenue and client integration workflows are active.
- Export and reporting artifacts are generated in exports/ and backend/campaign.xlsx.
- Runtime guidance is maintained in .colore/.

## Active Sprint
- Focus: stabilize backend workflows, imports, and reporting outputs.
- Priority: keep generated artifacts out of version control and preserve repository clarity.
- Exit criteria: key workflows run without blocking issues and documentation stays current.

## Last Accepted Decisions
- Keep this bootstrap file as the primary daily entry point.
- Prefer repository files over runtime notes when they differ.
- Keep generated exports ignored by Git.
- Maintain architecture and runtime guidance in .colore/.

## Next Tasks
- [ ] Review current backend workflow status.
- [ ] Confirm any open blockers from integrations and exports.
- [ ] Update this file with the latest progress and next actions.

## Rules for the Architect
1. Read this file before starting work.
2. Prefer minimal, verified changes.
3. Keep implementation aligned with the repository structure.
4. Update this file at the start and end of each workday.
5. Preserve clarity for both humans and LLMs.

## Open Day
- Review status, blockers, and priorities.
- Confirm the task for the day.
- Record the expected outcome before work begins.

## Close Day
- Summarize completed work.
- Note unresolved issues and next steps.
- Update this file so the next session starts from a clear state.

## Main Project Directories
- [backend/](../backend)
- [docs/](../docs)
- [infrastructure/](../infrastructure)
- [.colore/](.)
- [exports/](../exports)

## Key Repository Documents
- [README.md](../README.md)
- [.colore/README.md](README.md)
- [.colore/00_START.md](00_START.md)
- [.colore/02_PROJECT.md](02_PROJECT.md)
- [.colore/03_ARCHITECTURE.md](03_ARCHITECTURE.md)
- [backend/app/main.py](../backend/app/main.py)
