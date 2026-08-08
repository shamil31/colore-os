# Growth AI — Integration Research

**Date:** 2026-08-08
**Scope:** Only what is required to connect Meta Business, Instagram Graph, WhatsApp Business, Altegio, Telegram Bot API and n8n.
**Sources:** Official vendor documentation only. Every claim below is traceable to a URL listed in the section.
**Status:** Verified 2026-08-08. Unverified items are marked **NOT VERIFIED** — they are gaps, not assumptions.

Target flow this research must enable:

```
Meta → n8n → Coloré OS → Growth AI → Telegram
```

---

## 1. Meta Business Platform (Graph API foundation)

**Sources**
- https://developers.facebook.com/docs/graph-api/overview
- https://developers.facebook.com/docs/graph-api/webhooks/getting-started
- https://developers.facebook.com/docs/marketing-api/system-users/overview
- https://developers.facebook.com/docs/permissions

### Request model

Host: `graph.facebook.com`. Calls are version-prefixed:

```
https://graph.facebook.com/v23.0/{node-id}/{edge}?access_token=ACCESS-TOKEN
```

> "If you do not include a version number we will default to the oldest available version, so it's recommended to include the version number in your requests."

The data model is **nodes** (an object with a unique ID), **edges** (a connection between two nodes), **fields** (node properties, selectable with the `fields` parameter).

Tokens are documented as the `access_token` query parameter. WhatsApp Cloud API and Instagram messaging both additionally accept `Authorization: Bearer <TOKEN>` — see sections 2 and 3.

### System Users — the only correct token type for a server

> "An admin system user can create new users and access all assets belonging to the business."
> "A system user can only access the assets they have permission for."
> "Give system user access to assets and use system users for most API calls."

Rationale given: if a system user token is compromised, "it has limited scope and cannot compromise more permissions."

**NOT VERIFIED:** exact expiry semantics of system user tokens vs. user tokens were not stated on the pages fetched. Treat every token as expirable and store an issued-at timestamp.

### Webhooks — verification handshake

Meta sends a `GET` to the callback URL with three query parameters:

| Parameter | Value |
|---|---|
| `hub.mode` | always `subscribe` |
| `hub.challenge` | integer to echo back |
| `hub.verify_token` | the string configured in the App Dashboard |

> "Verify that the hub.verify_token value matches the string you set in the Verify Token field."
> "Respond with the hub.challenge value."

### Webhooks — payload signature

Header: `X-Hub-Signature-256`, format `sha256={signature}`.

> "Generate a SHA256 signature using the payload and your app's App Secret. Compare your signature to the signature in the X-Hub-Signature-256 header (everything after sha256=)."

The signature covers the **raw request body**. Any framework that re-serialises JSON before signing will produce a mismatch.

### Webhooks — delivery guarantees

> "Your server must have a valid TLS or SSL certificate correctly configured and installed. Self-signed certificates are not supported."
> "Your endpoint should respond to all Event Notifications with 200 OK HTTPS."
> "If any update sent to your server fails, we will retry immediately, then try a few more times with decreasing frequency over the next 36 hours. Your server should handle deduplication in these cases. Unacknowledged responses will be dropped after 36 hours."

**Deduplication is our responsibility, explicitly.** Retries continue for 36 hours.

### Permissions and access levels

> "Business Verification is required for all apps making requests for Advanced Access."

Relevant permission strings, exact:

| Permission | Grants |
|---|---|
| `instagram_business_basic` | "read an Instagram Business account profile's info and media" |
| `instagram_business_manage_messages` | "access messages on an Instagram professional account" — "View, manage, and respond to messages" |
| `whatsapp_business_messaging` | "send WhatsApp messages … upload and retrieve media from messages, manage and get WhatsApp business profile information" |
| `whatsapp_business_management` | "read and/or manage WhatsApp business assets" — WABAs, phone numbers, message templates |
| `pages_messaging` | "manage and access Page conversations and calling in Messenger" |
| `business_management` | "read and write with the Business Manager API" |

### How Coloré OS should use this today

1. **Do not call Graph API from Coloré OS for inbound.** Meta's retry-for-36-hours contract plus raw-body signature verification is exactly the class of work n8n already solves. n8n owns the Meta webhook subscription; Coloré OS receives a normalised event from n8n. See section 6.
2. **Signature verification must still exist in Coloré OS**, because the day we point Meta directly at us it must already work. Implement `X-Hub-Signature-256` HMAC-SHA256 over the raw body in the Meta Connector, behind a config flag, and keep it off the n8n path.
3. **Build the `GET` verification handshake now.** It is 10 lines, it is required before Meta will accept the callback URL at all, and it cannot be tested later without it. Echo `hub.challenge` only when `hub.verify_token` matches `META_VERIFY_TOKEN`.
4. **Deduplicate by provider message id**, not by our own receipt time. 36 hours of retries means a duplicate is normal traffic, not an anomaly.
5. **Assume a System User token**, not a personal token. Configure `META_ACCESS_TOKEN` as a single opaque secret and never log it. Do not build a user OAuth flow — nothing today needs one.
6. **Pin the API version in one constant** (`v23.0`), never per call site. An unversioned call silently gets the oldest version.
7. **Advanced Access + Business Verification is a business blocker, not an engineering one.** It gates production Instagram/WhatsApp messaging to non-test users. Start it in parallel; it does not block anything built today.

---

## 2. Instagram Graph / Instagram Platform messaging

**Sources**
- https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/messaging-api
- https://developers.facebook.com/docs/instagram-platform/webhooks

### Sending a direct message

Host `graph.instagram.com`, endpoint `/{IG_ID}/messages` (or `/me/messages`).

```json
{
  "recipient": { "id": "<IGSID>" },
  "message":   { "text": "<TEXT_OR_LINK>" }
}
```

Auth: `Authorization: Bearer <INSTAGRAM_USER_ACCESS_TOKEN>`.

Required permissions: `instagram_business_basic`, `instagram_business_manage_messages`.

### Messaging window

> "Your app has 24 hours to respond to any message sent from an Instagram user to your app user."

Outside the window a response must be tagged (human agent case) to be delivered.

**NOT VERIFIED:** the exact tag field name for the human-agent case was not stated on the page fetched.

### Webhooks

Subscribable fields include `messages`, `message_echoes`, `message_reactions`, `messaging_postbacks`, `messaging_seen`, `messaging_referral`, `messaging_optins`, `messaging_handover`, plus `comments`, `live_comments`, `mentions`, `story_insights`.

Envelope: `object`, `entry[]`, and within each entry `id`, `time`, and either `changes` / `changed_fields` or — for messaging — a `messaging` array containing `recipient.id`, `is_echo`, `is_self`.

Verification and signing are the standard Meta mechanism from section 1 (`hub.challenge`, `X-Hub-Signature-256: sha256=`, respond `200 OK`).

### How Coloré OS should use this today

1. **`is_echo` is the first thing the normaliser must check.** Instagram echoes back messages *we* sent. Without an echo filter, Growth AI answers itself in a loop on the very first live message. This is the single highest-risk detail in this document.
2. **Subscribe to `messages` only, today.** `comments` and `mentions` are a different product decision (public reply vs. private reply) and are not on the Meta → Telegram path.
3. **The 24-hour window makes latency a revenue property, not a nicety.** Growth AI's job today is to get a human to answer inside the window — which is precisely why the outbound leg is Telegram (to the salon operator), not Instagram (to the client). No message is sent to a client automatically today.
4. **`IGSID` is the identity key for Instagram**, and it is per-app-scoped — it is not the Instagram username and cannot be matched against Altegio by name. Store it as `(channel='instagram', external_id=IGSID)` and resolve to a Coloré client later. R-001's `identity` module models exactly this; review it before that resolution is built.
5. **Do not build outbound Instagram sending today.** The connector exposes `receive` capability only. Adding `send` is a one-method change once Advanced Access is granted.

---

## 3. WhatsApp Business (Cloud API)

**Sources**
- https://developers.facebook.com/docs/whatsapp/cloud-api/get-started
- https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/payload-examples

### Sending

```
POST https://graph.facebook.com/v23.0/{phone-number-id}/messages
Authorization: Bearer <SYSTEM_USER_ACCESS_TOKEN>
```

Body fields: `messaging_product` (must be `"whatsapp"`), `recipient_type` (`"individual"`), `to`, `type`, then `text` (`{"body": "…"}`) or `template`.

### 24-hour customer service window

> "This 24-hour window allows you to send non-template messages to users on WhatsApp."

The window opens when the customer replies. **First contact requires an approved template.** Free-form text to a cold number will be rejected.

### Inbound webhook payload

```json
{
  "object": "whatsapp_business_account",
  "entry": [{
    "id": "…",
    "changes": [{
      "field": "messages",
      "value": {
        "messaging_product": "whatsapp",
        "metadata":  { "display_phone_number": "…", "phone_number_id": "…" },
        "contacts":  [{ "profile": { "name": "…" }, "wa_id": "…" }],
        "messages":  [{ "from": "…", "id": "…", "timestamp": "…",
                        "type": "text", "text": { "body": "…" } }]
      }
    }]
  }]
}
```

Note the nesting difference from Instagram: WhatsApp uses `entry[].changes[].value.messages[]`; Instagram messaging uses `entry[].messaging[]`. **A single "Meta webhook parser" that assumes one shape will drop the other silently.**

Delivery receipts arrive as a `statuses[]` array in the same `value` object rather than `messages[]`.

### How Coloré OS should use this today

1. **Branch the normaliser on `object`**, not on guesswork: `whatsapp_business_account` → `changes[].value`, Instagram → `messaging[]`. One function, two explicit branches, each tested.
2. **An event whose `value` has `statuses` but no `messages` is a delivery receipt, not a conversation.** It must be accepted with `200` and dropped, not passed to Growth AI.
3. **`wa_id` is the identity key**, and unlike IGSID it *is* a phone number — which means it is directly joinable against Altegio clients. This is the cheapest identity resolution the project will ever get; the WhatsApp path is therefore the highest-value one to finish after today.
4. **Template approval is the real lead time.** Nothing today sends a WhatsApp message, so this is not on the critical path — but any future outbound reactivation campaign on WhatsApp starts with a template submitted for approval, and that is measured in days, not minutes.
5. `phone_number_id` (not the display number) is the send-endpoint path segment. Store both; log only the display number.

---

## 4. Altegio

**Sources**
- https://developer.alteg.io/ (redirect target of developers.alteg.io)
- https://developer.alteg.io/api
- Repository, verified in code: `backend/app/integrations/altegio/`
- Prior project audit: `docs/ALTEGIO_API_CAPABILITIES.md` (2026-08-02)

### Connection

Base URL: `https://api.alteg.io/api`

Authentication, two modes:

```
Authorization: Bearer <partner_token>
Authorization: Bearer <partner_token>, User <user_token>
```

Required: `Accept: application/vnd.api.v2+json`

Rate limit, stated: **200 requests/min or 5 requests/sec per IP.**

Both `/v1/…` and `/v2/…` are production-ready.

Endpoint groups: Online Booking (public, no user auth), Business Management v1, Business Management v2, Developer Tools (webhooks, dictionaries).

### Already implemented and working in this repository

`backend/app/integrations/altegio/` implements auth, and read access to companies, staff, services, clients and records, with pagination. This is verified working code, not a plan.

Known slot endpoint: `GET /api/v1/book_times/{company_id}/{staff_id}/{date}`.

### Gaps

**NOT VERIFIED today:** exact paths and bodies for `book_record`, `book_dates`, `book_staff`, `book_services`, and the webhook payload schema. The Developer Tools / Webhooks section exists and is documented as supporting record and client events, but the reference page renders client-side and could not be read by fetch. Resolving this needs either an authenticated docs session or a captured live payload.

Prior audit finding, still standing: Coloré OS is **read-only** against Altegio; write-back is deferred by architecture decision until after FIRST REVENUE.

### How Coloré OS should use this today

1. **Wrap what already exists — do not rewrite it.** The Altegio Connector's job today is to expose the existing `AltegioDataClient` through the Capability Registry so Growth AI can ask "who is this client?" without knowing that Altegio exists. Zero new HTTP code.
2. **Declare read capabilities only** (`clients.read`, `records.read`). Declaring a write capability the architecture forbids would let a future agent call it.
3. **Respect 5 req/sec at the gateway, not at the call site.** One shared limiter in the connector; Growth AI must not be able to exhaust the salon's whole API quota answering one message.
4. **Altegio stays the system of record.** Growth AI reads context from it and writes nothing — this is `architecture.md`'s guardrail and today's work must not weaken it.
5. **The unverified webhook schema is a real dependency for later, not today.** Today's flow is Meta-triggered, not Altegio-triggered. Record it as an open research gap rather than guessing a payload shape and building against fiction.

---

## 5. Telegram Bot API

**Sources**
- https://core.telegram.org/bots/api
- https://core.telegram.org/bots/faq

### Request model

```
https://api.telegram.org/bot<token>/METHOD_NAME
```

Response envelope, always:

```json
{ "ok": true, "result": … }
{ "ok": false, "error_code": 400, "description": "…" }
```

> "If 'ok' equals True, the request was successful … In case of an unsuccessful request, 'ok' equals False and the error is explained in the 'description'."

**An HTTP 200 with `ok: false` is a failure.** Checking the status code alone is wrong.

### sendMessage

Required: `chat_id` (Integer or String), `text` (String).
Key optional: `parse_mode`, `reply_markup` (`InlineKeyboardMarkup`), `link_preview_options`, `disable_notification`, `reply_parameters`.

### Receiving updates

`setWebhook` parameters: `url`, `certificate`, `ip_address`, `max_connections` (1–100, default 40), `allowed_updates`, `drop_pending_updates`, `secret_token` (1–256 chars, `A-Z a-z 0-9 _ -`).

> When `secret_token` is set, every request carries the header `X-Telegram-Bot-Api-Secret-Token` containing that token.

> "Ports currently supported for webhooks: 443, 80, 88, 8443."

> "You will not be able to receive updates using getUpdates for as long as an outgoing webhook is set up."

`Update` always carries `update_id` (unique, sequential) plus exactly one of `message`, `edited_message`, `callback_query`, `channel_post`, `my_chat_member`, and others.

### Rate limits (official)

> "In a single chat, avoid sending more than one message per second."
> "In a group, bots are not be able to send more than 20 messages per minute."
> "For bulk notifications, bots are not able to broadcast more than about 30 messages per second."

### How Coloré OS should use this today

1. **Telegram is the outbound leg of today's flow — to the salon operator, not to the client.** That choice is deliberate: it makes the first live Growth AI run observable and reversible. Nothing reaches a paying client without a human seeing it first.
2. **`ok: false` must raise.** The connector treats `{"ok": false}` as an error carrying `description`, regardless of HTTP status. This is the most common way a Telegram integration silently stops working.
3. **Use `secret_token` from day one** and reject any inbound webhook whose `X-Telegram-Bot-Api-Secret-Token` header does not match. It is one config value and one string comparison — there is no reason to ship without it.
4. **Do not call `setWebhook` today.** Today's Telegram capability is `send` only. Setting a webhook irreversibly disables `getUpdates` for this bot, and inbound Telegram is not on today's path.
5. **1 message/sec per chat is the binding limit** for an operator-alert channel, not the 30/sec bulk figure. Rate-limit per `chat_id`.
6. **Send with `parse_mode` unset by default.** A client's message containing `_` or `*` will make a Markdown-parsed alert fail to send — and the failure would be on the alert, i.e. exactly when we are least watching.

---

## 6. n8n

**Sources**
- https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/
- https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/
- https://docs.n8n.io/connect/n8n-api/authentication
- Verified on this server: `colore-n8n` container, image `n8nio/n8n:2.31.7`, `WEBHOOK_URL=https://n8n.colorebl.com`

### Webhook node

Test vs production are two distinct registrations:

> "n8n registers a test webhook when you select **Listen for Test Event** or **Execute workflow**, if the workflow isn't active."
> "n8n registers a production webhook when you publish the workflow. When using the production URL, n8n doesn't display the data in the workflow."

Methods: `DELETE, GET, HEAD, PATCH, POST, PUT`.

Authentication options: `Basic auth`, `Header auth`, `JWT auth`, `None`.

Respond options: immediately ("Workflow got started"), when last node finishes, or via the `Respond to Webhook` node (plus a streaming mode).

### HTTP Request node

Generic credential types: `Basic auth`, `Custom auth`, `Digest auth`, `Header auth`, `OAuth1 API`, `OAuth2 API`, `Query auth`, `Simplified Custom Auth`.

Options include `Batching`, `Timeout`, `Redirects`, `Pagination`, `Response` → `Response Format` (Autodetect, File, JSON, Text), `Ignore SSL Issues`.

### Public REST API

> Header: `X-N8N-API-KEY`
> Self-hosted base URL: `https://<your-instance-url>/api/v1`
> Key creation: "Settings > n8n API > Create an API key", with a Label and an Expiration.

### How Coloré OS should use this today

1. **n8n owns the Meta edge; Coloré OS owns the decision.** n8n holds the Meta subscription, the `hub.challenge` handshake, retries and credential storage. Coloré OS exposes exactly one inbound endpoint and does the thinking. This keeps Meta's operational surface out of our codebase.
2. **Secure the n8n → Coloré OS hop with `Header auth`**, not IP trust. n8n sends `X-Colore-Signature`/shared secret on the HTTP Request node; Coloré OS rejects anything else. Both containers are on `colore-net`, but the backend also publishes `:8000` publicly — network position is not authentication here.
3. **Use the production webhook URL, and know that a deactivated workflow returns 404.** The most likely cause of "the flow stopped working" is an unpublished workflow, not a code bug. The n8n Adapter must surface that distinctly.
4. **Respond "immediately" on the Meta-facing webhook.** Meta wants a fast `200`; the workflow should acknowledge first and call Coloré OS after. Waiting for the last node couples Meta's 36-hour retry machinery to our LLM latency.
5. **The n8n Adapter in Coloré OS is for the outbound direction** — Coloré OS triggering an n8n workflow by URL, with `Header auth`. The public REST API (`X-N8N-API-KEY`) is for managing workflows, which nothing today needs; do not wire it yet.
6. **`WEBHOOK_URL=https://n8n.colorebl.com` is already correct on this server.** No infrastructure change is required to start.

---

## Open gaps (carry into `research.md` if not closed)

| # | Gap | Blocks |
|---|---|---|
| G-1 | Altegio webhook payload schema and event list — docs page is client-rendered | Altegio-triggered flows (not today's path) |
| G-2 | Altegio `book_record` / `book_dates` exact contracts | Booking write-back (deferred post-FIRST REVENUE) |
| G-3 | Instagram human-agent tag field name | Replying outside the 24h window |
| G-4 | Meta system user token expiry semantics | Long-run token rotation policy |

---

## Source of truth

This file owns integration research findings only. Architecture decisions live in `docs/adr/` and `.colore/adr/`. Implementation lives in `backend/app/connectors/`. Current state lives in `.colore/state.md`.
