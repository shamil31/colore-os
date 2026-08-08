# Coloré OS — Next

Last updated: 2026-08-08

## Active Task

Growth AI Brain v0.1 — the Product Owner manages Coloré OS from Telegram.

- **Status:** REVIEW
- **Sub-sprint:** GROWTH AI FOUNDATION (see [`sprint.md`](sprint.md), [`adr/ADR-002-growth-ai-foundation.md`](adr/ADR-002-growth-ai-foundation.md))
- **Responsible role:** Engineering

## Delivered

1. Four Telegram commands: `Статус`, `Что нового?`, `Что требует моего решения?`, `Что делаем дальше?`
2. Host-side bot service `colore-growth-bot` (systemd, long polling, owner-only)
3. Live system status: doctor, deploy, git, docker, and all five integrations
4. Runtime documents read directly — no summarisation by inference

## Rule this task is built on

Every answer is a fact from the repository or a live check. When a source is
missing, the answer names the missing file instead of producing a plausible
reply. This is enforced by test, not by convention.

## What remains before this is DONE

Nothing is blocked. Product Owner review of the four answers in Telegram is the
remaining step — send `Статус` to `@Colore_Growth_bot`.

## Next After This

Growth AI Foundation is complete: the connector layer, the
`Meta → n8n → Coloré OS → Growth AI → Telegram` flow, and the Telegram
interface all run. The sub-sprint can close.

Then either:

- **Resume Priority → Integrilla** — the paused FIRST REVENUE critical path, or
- **Connect Meta for real** — n8n workflow plus Meta app, so live client
  messages enter the flow. Steps 2–3 of [`../docs/operations/GROWTH_AI_SETUP.md`](../docs/operations/GROWTH_AI_SETUP.md).

This is a Product decision. Ask the bot: `Что требует моего решения?`

## Do Not Work On

Altegio write-back (ADR-002 decision 6). Outbound messaging to clients on any
channel (ADR-002 decision 5). Identity resolution across channels — review
R-001 first, it already models this.

## Source of Truth

This file owns the single active task only. If it conflicts with the scope in [`sprint.md`](sprint.md), `sprint.md` wins.
