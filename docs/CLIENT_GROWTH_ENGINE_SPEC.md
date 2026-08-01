# Client Growth Engine Spec

## Product Intent

Client Growth Engine is the first commercial module of Coloré OS.

Its purpose is to increase salon revenue quickly by reactivating existing customers from Altegio data and converting them into bookings.

This is a business specification only.

## 1. Available Customer Data Required

Minimum customer data for the first MVP cycle:

- client identifier
- full name
- contact phone (for WhatsApp)
- last visit date
- basic service history
- current booking status
- preferred or recent service category
- message outcome status (responded, booked, postponed, no response)

Operational rules to confirm with business owner:

- reactivation messaging window: TODO
- maximum follow-up frequency: TODO
- approved offer types: TODO

## 2. Customer Segmentation Strategy

MVP uses one simple segmentation model based on recency:

- Regular: client is active and close to expected next visit window
- Delayed: client is overdue compared to expected return window
- Lost: client is significantly overdue and considered at churn risk

Segmentation principle:

- start from visit recency only
- keep segments easy to explain for operators
- avoid advanced scoring in MVP

Threshold values for each segment:

- TODO (set by Product Owner and business owner)

## 3. Visit Frequency Analysis

MVP frequency analysis should answer one question:

- when is this client most likely due to return?

Minimal method:

- use recent visit dates to estimate a basic return interval
- classify each client into Regular, Delayed, or Lost by interval deviation
- update classification after each campaign cycle

MVP output:

- segment label
- due/overdue status
- priority for outreach

## 4. Service History Analysis

MVP service-history analysis should stay minimal:

- identify most recent service category
- identify top repeated service category
- identify whether prior interest should drive the return message

Use in campaign:

- message relevance (service mention)
- booking suggestion relevance
- faster conversion to a concrete appointment option

Not required in MVP:

- deep multi-service recommendation models
- advanced personalization scoring

## 5. Three Client Return Strategies

### Regular

Objective:

- maintain normal return rhythm and prevent drop-off.

Offer style:

- light reminder with easy booking CTA.

Message angle:

- convenience and continuity.

Expected impact:

- steady baseline bookings and reduced passive churn.

### Delayed

Objective:

- recover clients who missed their expected return window.

Offer style:

- stronger reason to come back (time-limited or value-driven prompt).

Message angle:

- “you are due” + clear next step.

Expected impact:

- higher incremental bookings than Regular segment.

### Lost

Objective:

- recover high-risk churned clients at lowest possible cost.

Offer style:

- re-entry offer and low-friction restart.

Message angle:

- win-back with simple commitment path.

Expected impact:

- smaller conversion rate but high incremental value from otherwise lost demand.

## 6. WhatsApp Campaign Flow Through Integrilla

MVP campaign flow:

1. Select one target segment for the day.
2. Build recipient list from Altegio customer data.
3. Prepare one segment-specific WhatsApp template.
4. Send messages through Integrilla.
5. Capture responses and classify outcomes:
   - booking intent
   - question/clarification
   - postpone
   - no response
6. Route booking-intent responses to booking completion path.
7. Log outcome per client for the next cycle.

MVP constraints:

- one outbound message per cycle per client
- no complex multi-step drip in first release
- keep manual override available for edge cases

## 7. KPIs

Primary KPIs:

- Reactivation rate
- Bookings
- Revenue

Supporting KPIs:

- segment response rate
- booking conversion by segment (Regular/Delayed/Lost)
- no-response share
- time-to-booking after first message

First-cycle target values:

- TODO (set jointly by Product Owner and business owner)

## 8. MVP Scope

Included:

- one recency-based segmentation model (Regular/Delayed/Lost)
- one WhatsApp campaign channel (Integrilla)
- one campaign cycle workflow
- one booking conversion handoff path
- one KPI reporting view focused on reactivation, bookings, and revenue

Commercial value target:

- generate measurable new paid bookings from existing client base with minimal operational complexity.

## 9. Future AI Enhancements

After MVP proves revenue impact, add:

- dynamic segment thresholds by service category
- send-time optimization
- message variant optimization by segment
- churn-risk prediction model
- next-best-offer recommendation
- multi-channel orchestration beyond WhatsApp
- automated campaign pacing by client response behavior

Enhancement rule:

- introduce only features that improve KPI outcomes without increasing operating complexity disproportionately.
