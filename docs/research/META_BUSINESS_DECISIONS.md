# Meta Business — decisions required from the Product Owner

**Date:** 2026-08-08
**Status:** nothing here is blocked on engineering. Every item is a decision or
an account action only the business owner can take.
**Sources:** official Meta documentation, fetched and quoted below.

Engineering state: the webhook handshake and signature verification are built
and tested (`app/integrations/connectors/meta_connector.py`), the ingest
endpoint runs, and the connector reports `не настроен — META_VERIFY_TOKEN`
until the values below exist. No code change is needed to go live.

---

## 1. Business Manager and verification

**Decision required: who owns the Business portfolio, and will it be verified?**

Meta's own guidance for server integrations:

> "An admin system user can create new users and access all assets belonging to the business."
> "A system user can only access the assets they have permission for."
> "Give system user access to assets and use system users for most API calls."

Rationale given: a compromised system user token "has limited scope and cannot
compromise more permissions."

**Business Verification** is required for Advanced Access to permissions:

> "Business Verification is required for all apps making requests for Advanced Access."

It requires legal documents for the entity that owns the salon. It takes days,
not minutes, and it blocks messaging non-test users. **It blocks nothing that is
already built** — start it in parallel.

**What we need from you:** the Business portfolio ID, and a decision to begin
verification with the salon's legal entity.

---

## 2. Marketing API access tier

**Decision required: do we need ad data, or only messages?**

Meta has two tiers:

| Tier | What it allows | Rate limit |
|---|---|---|
| **Limited Access** (default) | granted automatically with the Marketing API product; unlimited ad accounts; 1 system user + 1 admin system user | "Heavily rate-limited per ad account. For development only. Not for production apps running for live advertisers." |
| **Full Access** (after App Review) | all Business Manager and Catalog APIs; 10 system users + 1 admin | "Lightly rate limited per ad account." |

Upgrading is not just paperwork — it has a usage threshold:

> "Have successfully made at least 500 Marketing API calls in the last 15 days"
> "Have made Marketing API calls with an error rate of less than 15% in the last 500 calls"

**This is a sequencing consequence, and it is the important part of this
document:** Full Access cannot be requested until the integration has already
been calling the API for a fortnight. If ad-spend reporting matters, Limited
Access has to be connected *now* so the 500 calls accumulate, even though it is
"development only".

**What we need from you:** confirmation that ad performance (spend, cost per
lead, ROAS) is wanted. If yes, the ad account ID and the go-ahead to start
accumulating calls. If no, we skip the Marketing API entirely and Growth AI
reports leads and bookings without cost.

Relevant permissions: `ads_read` for reporting, `ads_management` to change
campaigns. **Recommendation: request `ads_read` only.** Nothing in the current
plan changes a campaign, and the smaller scope is easier to get approved.

---

## 3. Permissions to request in App Review

| Permission | Grants | Needed for |
|---|---|---|
| `instagram_business_basic` | "read an Instagram Business account profile's info and media" | identifying the account |
| `instagram_business_manage_messages` | "View, manage, and respond to messages" | Instagram DMs reaching Growth AI |
| `whatsapp_business_messaging` | "send WhatsApp messages … upload and retrieve media" | WhatsApp conversations |
| `whatsapp_business_management` | "read and/or manage WhatsApp business assets" — WABAs, phone numbers, message templates | registering the number and templates |
| `ads_read` | Marketing API reporting | ad spend, only if §2 is a yes |

**What we need from you:** approval of this list before App Review is
submitted. Each permission must be justified in the review with a screencast.

---

## 4. Webhook — built, waiting on values

Already implemented and tested:

- `GET /growth/webhook/meta` answers the handshake. Meta sends `hub.mode`,
  `hub.verify_token`, `hub.challenge`; we compare the token in constant time
  and echo the challenge.
- `POST /growth/webhook/meta` verifies `X-Hub-Signature-256` — HMAC-SHA256 over
  the **raw** body — and returns 401 otherwise. Without `META_APP_SECRET` it
  returns 503 rather than accepting unverified traffic.
- Deduplication is handled: Meta "will retry immediately, then try a few more
  times with decreasing frequency over the next 36 hours" and states "your
  server should handle deduplication in these cases."

**Decision required: n8n or direct?**

Today the recommendation stands (ADR-002 decision 4): n8n holds the
subscription. It already solves retries and credential storage, and it keeps
Meta's operational surface out of our codebase. The direct path exists so that
choice can be reversed without redesign.

**What we need from you:** the Meta App ID and App Secret, and a verify token
string of your choosing. Subscribe to the `messages` field only — `comments`
and `mentions` are a separate product decision about replying in public.

---

## 5. Conversions API / offline conversions — architecture

**Decision required: do we send confirmed salon visits back to Meta?**

### Why it matters

Meta optimises ad delivery on the outcomes it can see. Today it sees a message
being started. It cannot see that the person then came to the salon and paid,
because that happens in Altegio. Sending that back is what makes the ad
budget optimise for revenue rather than for conversations.

### What the API requires

Required server event fields:

| Field | Note |
|---|---|
| `event_name` | "A standard event or custom event name" |
| `event_time` | "A Unix timestamp in seconds indicating when the actual event occurred" |
| `user_data` | "A map that contains customer information data" |
| `action_source` | where the conversion happened |

`action_source` allowed values: `email`, `website`, `app`, `phone_call`, `chat`,
`physical_store`, `system_generated`, `business_messaging`, `other`.

**For a salon visit, `action_source` is `physical_store`.** For a booking taken
in a WhatsApp or Instagram conversation, it is `business_messaging`.

Customer data must be hashed with SHA256, after normalisation:

| Parameter | Normalisation before hashing |
|---|---|
| `ph` (phone) | "Remove symbols, letters, and any leading zeros… Always include the country code" |
| `em` (email) | "Trim any leading and trailing spaces. Convert all characters to lowercase." |
| `fn`, `ln` | "Lowercase only with no punctuation" |
| `external_id` | "Hashing recommended" |

Sent unhashed: `client_ip_address`, `client_user_agent`, `fbc`, `fbp`.

Deduplication against the Pixel uses `event_id` + `event_name`:

> "the `eventID` from a browser or app event must match the `event_id` in the corresponding server event."

Within 5 minutes the browser event wins; within 48 hours only the first counts.

### Proposed architecture

```
Altegio record, attendance = 1 (пришёл)
    → Coloré OS reads it (already implemented — analytics reads this today)
    → normalise + SHA256 the client phone
    → POST /{dataset_id}/events   action_source: physical_store
                                  event_name:    Purchase
                                  event_time:    visit time
                                  event_id:      altegio record id
    → Meta attributes the visit to the ad that started the conversation
```

`event_id = Altegio record id` gives idempotency for free: re-sending the same
visit cannot double-count it.

### What this depends on

The link from a Meta lead to an Altegio client. Today that exists only for
WhatsApp, where `wa_id` is a phone number. **Instagram `IGSID` is app-scoped and
is not a phone**, so an Instagram-sourced visit cannot currently be reported
back. This is the same gap the `Аналитика` command reports, and R-001 in
`.colore/research.md` holds a domain model for it.

**What we need from you:**
1. Whether offline conversion reporting is wanted at all.
2. If yes: the Dataset ID (offline event set) from Events Manager.
3. A decision on the privacy notice — sending hashed customer phone numbers to
   Meta is a data-processing choice the salon owner makes, not engineering.

---

## Summary — the five decisions

| # | Decision | Blocks |
|---|---|---|
| 1 | Start Business Verification with the salon's legal entity | messaging non-test users |
| 2 | Is ad-spend reporting wanted? If yes, connect Limited Access **now** | cost per lead, ROAS — and the 15-day clock for Full Access |
| 3 | Approve the permission list for App Review | everything live |
| 4 | Provide App ID, App Secret, verify token; keep n8n as the subscription holder | inbound client messages |
| 5 | Is offline conversion reporting wanted? If yes, Dataset ID + privacy decision | ad budget optimising for revenue |

None of these blocks engineering. Altegio is connected and reporting real data
today; `Аналитика` works now and will report ad metrics the moment §2 exists.

---

## Open gaps

Recorded rather than guessed:

| # | Gap | Effect |
|---|---|---|
| G-5 | The offline-event-management doc page returned 404 on 2026-08-08 | dataset creation steps unverified; the event contract above is verified |
| G-6 | Altegio `start_date`/`end_date` on `/records` filter by appointment date, observed not documented | analytics states the basis explicitly |

## Source of truth

This file owns Meta business decisions only. Integration contracts live in
`GROWTH_AI_INTEGRATION_RESEARCH.md`. Decisions live in `.colore/adr/`.
