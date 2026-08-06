# Coloré OS — Next

Last updated: 2026-08-05

## Active Task

Build and validate the Priority → Integrilla message transport loop.

- **Status:** TODO
- **Rule:** Finish Before Improve — no other task starts until this reaches DOING → REVIEW → DONE.
- **Responsible role:** Engineering (see [`agents.md`](agents.md) for current tool assignment)

## Steps

1. Run: `python -m app.scripts.export_integrilla`
2. Review `campaign.xlsx` output
3. Import to Integrilla manually
4. Execute conversation playbook (`docs/operations/`)
5. Track metrics: replies → dialogs → bookings

## Definition of Done

One real client from the "Long Absence" segment:
1. Responds to the first message
2. Has a dialog (2+ exchanges)
3. Books an appointment in Altegio
4. Shows up for the appointment

When this happens, the FIRST REVENUE sprint (see [`sprint.md`](sprint.md)) is DONE.

## Do Not Work On

Recovery Engine v2, AI Scoring improvements, Analytics Dashboard, Multi-tenant support, automatic Integrilla API integration, Advanced Reporting — all deferred. See [`roadmap.md`](roadmap.md).

## Source of Truth

This file owns the single active task only. If it conflicts with the scope in [`sprint.md`](sprint.md), `sprint.md` wins.
