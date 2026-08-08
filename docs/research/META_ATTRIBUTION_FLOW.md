# Meta Attribution Flow

**Date:** 2026-08-08
**Scope:** how a business outcome travels from a client's first message to a
confirmed conversion in Meta, and what guarantees hold at each step.

This document describes mechanism only. No marketing advice, no
recommendations, no forecasting.

---

## The flow

```
Lead
  │   inbound message on WhatsApp or Instagram
  │   arrives via n8n → POST /growth/events
  ▼
Conversation
  │   normalised, deduplicated, persisted as growth_events
  │   Growth AI classifies intent and alerts the operator over Telegram
  ▼
Booking
  │   a human books the client — in Altegio, by hand
  ▼
Altegio
  │   system of record: the appointment, and later its outcome
  │   attendance -1 no-show · 0 pending · 1 arrived · 2 confirmed
  ▼
Meta Conversion API
  │   only outcomes Altegio has already confirmed
  │   POST /{dataset_id}/events
  ▼
Confirmation
      accepted or rejected, recorded per event in meta_conversions
```

---

## The five states

| State | Built from | Meta `event_name` | `action_source` | `event_id` |
|---|---|---|---|---|
| Lead created | `growth_events` row, status `processed` | `Lead` | `business_messaging` | `lead-{event.id}` |
| Appointment booked | Altegio record exists | `Schedule` | `business_messaging` | `booked-{record.id}` |
| Appointment cancelled | Altegio record `deleted` | `AppointmentCancelled` | `business_messaging` | `cancelled-{record.id}` |
| Client arrived | Altegio `attendance = 1` | `Purchase` | `physical_store` | `arrived-{record.id}` |
| No-show | Altegio `attendance = -1` | `NoShow` | `physical_store` | `noshow-{record.id}` |

`Lead`, `Schedule` and `Purchase` are Meta standard events. `AppointmentCancelled`
and `NoShow` are custom event names, which the Conversions API permits.

`action_source` values are constrained by Meta to: `email`, `website`, `app`,
`phone_call`, `chat`, `physical_store`, `system_generated`,
`business_messaging`, `other`. A visit to the salon is `physical_store` — that
is the event Meta cannot observe by any other means, and the reason this flow
exists.

---

## What guarantees "never fabricate a conversion"

**An event is built only from a record that already exists.** There is no code
path from an estimate, a ratio, or an expectation to a row in
`meta_conversions`.

Three rules do the work, each with a test that fails if it is removed:

1. **A lead never produces a booking event.** A conversation is not a
   conversion. `build_events` emits `lead_created` and stops.
2. **A booking never produces an arrival event.** Attendance is Altegio's to
   confirm. An appointment with `attendance = 0` (pending) yields
   `appointment_booked` and nothing else, because nothing else has happened.
3. **A cancelled appointment never produces an arrival.** The cancellation is
   terminal for that record.

Cancellations are only visible with `with_deleted=1` on the records endpoint.
Verified on the live account 2026-08-08: the default call returned 341 records
over 180 days with `deleted` false for every one; the same call with the flag
returned 383, of which 13 were deleted. Without the flag a cancelled
appointment is indistinguishable from one that never existed — the record
simply stops being returned. See R-004.

---

## What every event carries

Required by Meta, present on every row:

| Field | Value |
|---|---|
| `event_name` | from the table above |
| `event_time` | Unix seconds — booking uses `create_date`, outcome uses the appointment `date`, lead uses `received_at` |
| `event_id` | derived from the source record's identity |
| `action_source` | from the table above |
| `user_data` | matching fields, hashed |

### Matching fields

An event is only built when a **strong identifier** is present — `ph` (phone)
or `em` (email). A name is not an identifier: Meta cannot attribute an offline
event to "Ана", and `external_id` is inert here because nothing sends a
matching id from the ad side. Records with neither phone nor email are skipped
rather than sent unattributable.

All customer parameters are SHA256-hashed after the normalisation Meta
specifies:

| Parameter | Normalisation |
|---|---|
| `ph` | digits only, leading zeros stripped, country code included |
| `em` | trimmed, lowercased |
| `fn`, `ln` | lowercased, punctuation removed |
| `external_id` | Altegio client id, hashed |

Raw phone numbers, emails and names are never written to `meta_conversions`
and never leave the hashing functions. Verified by test and by inspecting the
live table: no 11–13 digit sequence appears in any stored `user_data`.

An Instagram lead produces no event at all. `IGSID` is app-scoped and is not a
phone number, so there is no strong identifier to match on. This is a stated
absence, not a silent zero.

---

## Deduplication

Two layers, both keyed on the same value.

**Locally.** `event_id` is derived from the source record — `arrived-661257546`,
not a random UUID or a row counter. A unique constraint on `event_id` means
rebuilding the queue over the same Altegio data inserts nothing. Verified:
two consecutive builds over 235 events inserted 0 rows the second time, and all
235 ids are distinct.

**At Meta.** The same `event_id` is what Meta deduplicates on:

> "The `event_id` and `event_name` parameters are used to deduplicate events
> sent by both web (via the Meta Pixel) or app (via SDK or App Events API) and
> the Conversions API."

Within 5 minutes a browser event is favoured; within 48 hours only the first
event counts. A re-sent visit therefore cannot double-count, whether the repeat
comes from our queue or from a Pixel.

---

## The queue

`meta_conversions` holds one row per outcome, with a status:

```
pending  → built from a confirmed outcome, not yet sent
sent     → handed to Meta
accepted → Meta acknowledged it
rejected → Meta refused it; `error` holds the reason verbatim
```

Build, send and record are three separate steps. Build never sends. Send never
invents. When Meta is not configured, build still runs and the queue
accumulates, so the history is already present the moment credentials exist
rather than lost to the gap.

A send that fails marks every event in the batch `rejected` with Meta's own
message. It is never silently dropped, and the queue is never reported drained
when Meta received nothing.

---

## Reading it

Telegram command `Meta`:

```
Connected: YES/NO
Events waiting: n
Events sent: n
Accepted: n
Rejected: n
Last synchronization: Today 14:35
```

When Meta is not connected the answer names each missing setting and where it
comes from. Secret values are never shown.

---

## Current state — 2026-08-08

Built from live Altegio data, 90-day window:

| State | Queued |
|---|---|
| Appointment booked | 118 |
| Client arrived | 99 |
| Appointment cancelled | 9 |
| No-show | 8 |
| Lead created | 1 |
| **Total** | **235** |

Sent: 0. `Connected: NO` — `META_ACCESS_TOKEN` and `META_DATASET_ID` do not
exist on this server. The events are queued, not lost.

---

## Open gaps

| # | Gap | Effect |
|---|---|---|
| G-7 | `with_deleted=1` is not in the published Altegio reference; behaviour verified empirically | cancellation detection rests on an observed, undocumented parameter |
| G-8 | Currency is assumed RSD from the salon's location | `custom_data.value` on arrival events would be mislabelled if the account bills in another currency |
| G-9 | Instagram leads carry no strong identifier | Instagram-sourced outcomes cannot be attributed until cross-channel identity exists (R-001) |

## Source of truth

This file owns the attribution mechanism only. Meta business decisions live in
`META_BUSINESS_DECISIONS.md`. Integration contracts live in
`GROWTH_AI_INTEGRATION_RESEARCH.md`.
