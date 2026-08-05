# Colore Runtime - Workflow

## Execution Rules
- Work on one task at a time.
- Revenue First is the default operating mode.
- Reality First is mandatory for plans, status, and reports.
- Product work must support first revenue until KPI is reached.
- Follow lifecycle order without skipping stages:
  - BACKLOG -> TODO -> DOING -> REVIEW -> DONE
- A task is complete only after REVIEW.
- New ideas go to BACKLOG first.
- Main rule: Finish Before Improve.
- Runtime always overrides AI memory.
- Never restart completed work.
- Never invent project facts.
- Never reopen closed decisions without explicit owner approval.

## Day Start
- Every workday starts with the Runtime Entry Procedure.
- Open repository at /root/colore-os.
- Read .colore/bootstrap.md first to restore runtime context.
- Read runtime docs in strict order:
  - .colore/09_UAOP.md
  - .colore/01_CONTRACT.md
  - .colore/00_Master/PROJECT_STATE.md
  - .colore/00_Master/CURRENT_SPRINT.md
  - .colore/00_Master/DECISIONS.md
  - .colore/00_Master/KNOWN_STATE.md
  - .colore/00_Master/BACKLOG.md
  - .colore/00_Master/ROADMAP.md
- Read before every task:
  - .colore/00_Master/TODAY.md
- Verify workspace and git state.
- Identify current active task.

## Runtime Entry Procedure
1. Verify workspace and git state.
2. Read .colore/bootstrap.md as the authoritative runtime contract.
3. Restore runtime context and execute the Runtime Entry Procedure from bootstrap.
4. Confirm current sprint and P0 task.
5. Move only one task to DOING.
6. Record start context in TODAY.md.

## Sync Project Procedure
1. Update all Source Of Truth docs.
2. Record all decisions taken today.
3. Remove outdated priorities and contradictions.
4. Validate architecture and vision alignment.
5. Commit synchronized state.

## Day Close
- Summarize completed work.
- Record updates in session log.
- Record any new decisions.
- Set first task for next working day.

## Close Day Procedure
1. Check status of current DOING task.
2. Record verified outcomes only.
3. Update .colore/bootstrap.md with current phase, sprint, completed work, risks, next decision, and first task.
4. Update next-day first task.
5. Ensure no open contradiction in Source Of Truth.
6. Commit day-close documentation.

## Unknown Process Details
- Automation steps for status transitions: TODO
- Mandatory review checklist format: TODO
