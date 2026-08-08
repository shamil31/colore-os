# Growth AI — Setup

**Status:** the flow runs today with no credentials. Every channel without a
token records a dry run instead of failing. This document is how to turn each
one live, in the order that gives the most value first.

Flow:

```
Meta (WhatsApp / Instagram)
  → n8n workflow            (holds the subscription, the retries, the secrets)
  → POST /growth/events     (Coloré OS, shared-secret header)
  → Growth AI               (intent, priority, reason)
  → Telegram                (alert to the salon operator)
```

Research basis: `docs/research/GROWTH_AI_INTEGRATION_RESEARCH.md`.
Decision basis: `.colore/adr/ADR-002-growth-ai-foundation.md`.

---

## What is already configured on this server

| | |
|---|---|
| `GROWTH_INBOUND_SECRET` | set in `/opt/colore-os/docker/.env` (2026-08-08) |
| `COLORE_API_TOKEN` | set in both env files (2026-08-08) — see [Security](#security) below |
| n8n | `https://n8n.colorebl.com`, container `colore-n8n` |
| Database | `growth_events`, `growth_actions` created by migration `a1b2c3d4e5f6` |

Everything else is unset, deliberately.

## Security

Every route that returns business data — `/growth/events`, `/growth/events/{id}`,
`/growth/integrations`, `/conversations`, `/clients`, `/ai/*`, `/booking/*`, `/db`
— requires `X-Colore-Api-Key: <COLORE_API_TOKEN>`. This is deny-by-default
(`backend/app/core/security.py`): a route not explicitly listed as public is
protected automatically, including ones written after this note.

Public without a key: `/`, `/docs`, `/openapi.json`, `/ui` (the static page
itself; it prompts for the key in-browser and attaches it to its own calls).

Self-authenticated with their own secret, not this key: `POST /growth/events`
(n8n's `X-Colore-Token`) and `/growth/webhook/meta` (Meta's own verification).

An unset `COLORE_API_TOKEN` returns `503` on every protected route rather than
opening it — the same fail-closed rule as `GROWTH_INBOUND_SECRET`.

## Check what is live right now

```bash
curl -s -H "X-Colore-Api-Key: $COLORE_API_TOKEN" http://localhost:8000/growth/integrations | python3 -m json.tool
```

`configured: false` plus a `missing_configuration` list is the answer to
"why did nothing arrive". No secret value is ever returned.

---

## Step 1 — Telegram (highest value, 5 minutes)

This is the only step that changes a dry run into a person being told.

1. Talk to [@BotFather](https://t.me/botfather), `/newbot`, keep the token.
2. Add the bot to the operator group, or message it directly.
3. Get the chat id:
   ```bash
   curl -s "https://api.telegram.org/bot<TOKEN>/getUpdates" | python3 -m json.tool
   ```
   Read `result[].message.chat.id`. A group id is negative.
4. Append to `/opt/colore-os/docker/.env`:
   ```
   TELEGRAM_BOT_TOKEN=<token>
   TELEGRAM_OPERATOR_CHAT_ID=<chat id>
   ```
5. `./deploy.sh`

Verify — this sends a real message:

```bash
curl -s -X POST http://localhost:8000/growth/events \
  -H "X-Colore-Token: $GROWTH_INBOUND_SECRET" \
  -H 'Content-Type: application/json' \
  -d '{"object":"whatsapp_business_account","entry":[{"id":"W","changes":[{"field":"messages","value":{"messaging_product":"whatsapp","metadata":{"phone_number_id":"P"},"contacts":[{"profile":{"name":"Test"},"wa_id":"381600000000"}],"messages":[{"from":"381600000000","id":"wamid.SETUP1","type":"text","timestamp":"1","text":{"body":"Хочу записаться"}}]}}]}]}'
```

`"status":"ok"` in `dispatch` means it was delivered. `dry_run` means the
settings did not reach the container — check `/growth/integrations`.

Note: `getUpdates` stops working if a webhook is ever set on the bot. Coloré OS
does not set one.

---

## Step 2 — n8n workflow

One workflow, three nodes.

**Webhook node**
- Method `POST`
- Path: something unguessable, e.g. `colore-growth-<random>`
- Authentication: `Header auth` (a credential only Meta's caller will have) or
  `None` if only Meta reaches it
- Respond: **Immediately**

  Meta wants a fast `200`. Waiting for the last node couples Meta's 36-hour
  retry machinery to our LLM latency.

**HTTP Request node**
- Method `POST`
- URL `http://colore-backend:8000/growth/events` (both containers are on
  `colore-net`, so the container name resolves)
- Authentication: `Generic` → `Header Auth`
  - Name: `X-Colore-Token`
  - Value: the `GROWTH_INBOUND_SECRET` from `/opt/colore-os/docker/.env`
- Body: JSON, pass the incoming payload through

  Coloré OS unwraps a body nested under `body` or `payload`, so an approximate
  mapping still works.

**Publish the workflow.** An unpublished workflow answers 404 on its production
URL, and that is the most common cause of "the flow stopped working".

Then point Meta at the n8n **production** webhook URL.

---

## Step 3 — Meta app

1. Create a Meta app, add the WhatsApp and/or Instagram product.
2. Add a **System User** in the Business portfolio and generate its token —
   not a personal user token.
3. Webhooks → Callback URL = the n8n production URL. Verify token = whatever
   n8n expects.
4. Subscribe to the `messages` field only. `comments` and `mentions` are a
   different product decision and are not on this path.
5. Business Verification + Advanced Access are required before non-test users
   can message you. Start this early — it is measured in days, and it blocks
   nothing that is built.

---

## Optional — point Meta straight at Coloré OS

Only worth doing to remove n8n from the path. The endpoint already exists.

```
META_VERIFY_TOKEN=<the same string given to Meta>
META_APP_SECRET=<app secret from the Meta dashboard>
```

- `GET /growth/webhook/meta` answers the `hub.challenge` handshake.
- `POST /growth/webhook/meta` requires a valid `X-Hub-Signature-256` over the
  raw body and returns 401 otherwise. Without `META_APP_SECRET` it returns 503
  rather than accepting unverified traffic.

Coloré OS must be reachable over HTTPS with a real certificate — Meta does not
accept self-signed ones.

---

## Reading the trace

```bash
curl -s -H "X-Colore-Api-Key: $COLORE_API_TOKEN" http://localhost:8000/growth/events | python3 -m json.tool
curl -s -H "X-Colore-Api-Key: $COLORE_API_TOKEN" http://localhost:8000/growth/events/1 | python3 -m json.tool
```

Skips are recorded, not silent. `skip_reason` will be one of:

| Reason | Meaning |
|---|---|
| `echo` | our own message reflected back by Instagram — dropping it is what stops the assistant answering itself |
| `status_only` | a delivery or read receipt, not a conversation |
| `unsupported_type` | an image, audio or sticker; readable, not yet actionable |
| `unknown_shape` | not a payload shape the normaliser knows |

`result: duplicate` is normal traffic, not an error: Meta retries a failed
delivery for 36 hours.

---

## Managing Coloré OS from Telegram

The bot `@Colore_Growth_bot` answers the Product Owner. Four commands:

| Command | Answers with |
|---|---|
| `Статус` | doctor, deploy, git, docker and every integration — all live checks |
| `Что нового?` | today's `.colore/changelog.md` entries and today's commits |
| `Что требует моего решения?` | open Review Queue entries, project Unknowns, blockers on the active task |
| `Что делаем дальше?` | current sprint and active task from `sprint.md` and `next.md` |
| `Аналитика` | leads, bookings, conversion, missing data and recommendations — live from Altegio and `growth_events` |

Anything else gets the command list back. Messages from anyone other than
`TELEGRAM_OWNER_ID` are logged and ignored without a reply.

**Every answer is a fact from the repository or a live check.** When a source is
missing, the answer names the missing file rather than inventing a plausible
reply — there is a test for exactly that.

### The service

The bot runs on the **host**, as systemd unit `colore-growth-bot`, not in the
backend container. That is not a preference: the image contains no repository,
no `.colore/`, and no docker socket, so a bot inside it could not answer a
single status question truthfully.

```bash
systemctl status colore-growth-bot
journalctl -u colore-growth-bot -f
```

Install (already done on this server):

```bash
cp infrastructure/colore-growth-bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now colore-growth-bot
```

Credentials come from `/root/colore-os/backend/.env`, which is gitignored.
`./deploy.sh` restarts the service, so a deploy cannot leave the bot running an
older commit.

It uses long polling, not a webhook. `setWebhook` would irreversibly disable
`getUpdates` for this bot, and polling needs no inbound port.

### How `Аналитика` counts

| Figure | Source | Basis |
|---|---|---|
| Leads | `growth_events` in Coloré OS | inbound client messages Growth AI processed |
| Bookings | Altegio `/records` | appointments in the period, `deleted` excluded, split by the official attendance codes (`-1` no-show, `0` pending, `1` arrived, `2` confirmed) |
| Conversion | both | **only** leads attributable to a booking |

Conversion is never bookings ÷ leads. Most of the salon's appointments have
nothing to do with Growth AI, so that ratio would look like an answer and mean
nothing. A lead counts as converted when its phone matches an Altegio client
*and* that client has a booking created **after** the lead arrived — a client
who already had an appointment did not convert because of a message.

Leads that cannot be attributed are reported with the reason. Instagram is the
common case: an `IGSID` is app-scoped and is not a phone number.

The company id is resolved from Altegio at runtime, not from
`ALTEGIO_COMPANY_ID`. That setting is stale on this server (`2403`, which
Altegio does not recognise) and the mismatch is reported in the answer.

## What this does not do yet

- **Nothing is sent to a client automatically.** Telegram alerts the operator,
  who replies in the original channel by hand (ADR-002 decision 5).
- **No identity resolution.** A WhatsApp `wa_id` is a phone number and joins
  directly to Altegio; an Instagram `IGSID` does not. R-001 in
  `.colore/research.md` holds a domain model for this — review it before
  building one.
- **No Altegio write-back.** Altegio stays the system of record.
