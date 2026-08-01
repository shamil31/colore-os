# Revenue Engine MVP

## Purpose

This document defines the first revenue modules that can generate money quickly for Coloré OS.

It is a business design document only.

It does not define implementation details, technical architecture changes, or new code.

## Scope

The MVP starts from the current project context already verified in the repository:

- current active package: `Package 03 - Client Retention & Reactivation`
- existing local client CRUD in backend
- documented CRM-based flows for follow-up, lead qualification, booking, schedule, services, promotions, and handoff

Where the repository does not verify a data source, this document keeps that requirement as `TODO`.

## Revenue Principles

The first revenue modules should:

1. reactivate existing demand faster than creating new demand
2. move clients toward booking with minimal friction
3. use the smallest possible set of business data
4. recover revenue from paused, lost, or undecided conversations
5. prioritize short time-to-value over feature breadth

## Priority Order

1. Client Reactivation
2. Repeat Booking Reminder
3. Lost Lead Recovery
4. VIP Retention
5. Birthday Campaign

This order is based on expected revenue speed and current repository readiness.

## 1. Client Reactivation

### Goal

Bring inactive or paused clients back into conversation and convert them into the next booking.

### Required Data

- client identity
- contact channel
- previous interaction context
- current client status
- relevant service interest
- preferred or possible booking time
- reactivation trigger logic: TODO
- inactivity threshold definition: TODO

### User Flow

1. Business selects a reactivation segment.
2. Client receives a short, relevant reactivation message.
3. Client shows interest, declines, or ignores.
4. Interested clients move to service clarification or direct booking.
5. Result is recorded as reactivated, postponed, not interested, or no response.

### Automation Flow

1. Find client and retrieve previous context.
2. Select one relevant reactivation reason.
3. Send one follow-up message.
4. If client responds positively, propose the next step.
5. If ready, move directly to booking flow.
6. If not ready, update status for later follow-up.

### Business Value

- converts warm demand faster than acquisition
- monetizes existing CRM base
- reduces lost revenue from unfinished conversations
- increases booking volume without increasing admin load

### Estimated Implementation Effort

Medium

### Priority

P1

## 2. Repeat Booking Reminder

### Goal

Increase repeat visits by reminding existing clients to rebook at the right moment.

### Required Data

- client identity
- prior booking or visit history: TODO
- service category or last service: TODO
- expected repeat interval: TODO
- booking availability
- contact channel

### User Flow

1. System identifies clients who are likely due for another visit.
2. Client receives a reminder tied to their likely next need.
3. Client chooses to book, postpone, or ignore.
4. Interested clients move directly into booking options.
5. Outcome is recorded for future timing.

### Automation Flow

1. Detect clients approaching their next likely booking window.
2. Generate a reminder based on previous service context.
3. Offer a simple next action.
4. If client agrees, move into schedule selection and booking.
5. If client delays, assign a later reminder state.

### Business Value

- increases visit frequency
- improves revenue predictability
- fills calendar demand from known customers
- reduces churn caused by simple forgetfulness

### Estimated Implementation Effort

Medium

### Priority

P1

## 3. Lost Lead Recovery

### Goal

Recover leads who showed intent but did not convert to booking.

### Required Data

- client or lead identity
- previous conversation status
- last known interest or requested service
- lead qualification result
- reason for drop-off: TODO
- follow-up timing rule: TODO
- contact channel

### User Flow

1. Business identifies leads that stopped before booking.
2. Lead receives a short recovery message based on prior context.
3. Lead resumes conversation, declines, or stays silent.
4. Resumed leads move to qualification, objection handling, or booking.
5. Result is stored for next follow-up or closure.

### Automation Flow

1. Identify leads with unfinished next step.
2. Retrieve prior conversation context.
3. Send one recovery message focused on the next decision.
4. Route reply to booking, service selection, objection handling, or human handoff.
5. Update lead status after response or non-response.

### Business Value

- captures revenue that is already partially acquired
- improves conversion from existing inbound demand
- reduces waste in lead generation and admin effort
- gives the owner a direct lever on booking conversion

### Estimated Implementation Effort

Low to Medium

### Priority

P1

## 4. VIP Retention

### Goal

Protect high-value clients from churn and increase repeat high-margin bookings.

### Required Data

- client identity
- VIP definition or segmentation rule: TODO
- visit frequency: TODO
- spend history: TODO
- preferred services or masters: TODO
- priority contact channel
- retention offer policy: TODO

### User Flow

1. Business identifies VIP clients.
2. VIP client receives a personal retention or appreciation message.
3. Client is offered a relevant next step such as priority booking or tailored offer.
4. Interested clients move to booking or staff selection.
5. Outcome is tracked separately from standard retention.

### Automation Flow

1. Select VIP segment by defined business rule.
2. Build a high-context message based on known preferences.
3. Offer a premium next step.
4. If client responds, route directly to booking or human support.
5. Record VIP engagement outcome.

### Business Value

- protects the most valuable revenue base
- increases retention of high-margin customers
- supports premium positioning and loyalty
- reduces churn cost where business impact is highest

### Estimated Implementation Effort

High

### Priority

P2

## 5. Birthday Campaign

### Goal

Generate timely repeat bookings and goodwill through birthday-triggered outreach.

### Required Data

- client identity
- birthday date: TODO
- contact channel
- campaign rule or offer definition: TODO
- marketing permission status: TODO
- offer redemption tracking: TODO

### User Flow

1. Eligible clients enter a birthday campaign window.
2. Client receives a birthday message with a simple next action.
3. Client asks a question, books, postpones, or ignores.
4. Interested clients move to service selection or booking.
5. Campaign outcome is recorded for later analysis.

### Automation Flow

1. Identify clients in the birthday period.
2. Send one birthday-triggered message.
3. Route interested replies into booking flow.
4. Track response and booking outcome.
5. Stop campaign when window expires.

### Business Value

- creates a predictable campaign moment
- reactivates dormant clients with low friction
- strengthens emotional retention and brand loyalty
- can produce quick short-term bookings when data exists

### Estimated Implementation Effort

Medium

### Priority

P3

## Recommended MVP Sequence

### Wave 1

- Client Reactivation
- Repeat Booking Reminder
- Lost Lead Recovery

Reason:

These modules target already-warm demand and are the most direct path to near-term revenue.

### Wave 2

- VIP Retention
- Birthday Campaign

Reason:

These modules can be valuable, but they depend more heavily on segmentation and customer-history data that is not yet verified in the repository.

## Core Business Dependencies

To make the MVP commercially useful, the business side needs clear rules for:

- who counts as inactive
- who counts as repeat-due
- who counts as lost lead
- who counts as VIP
- what message timing is acceptable
- what promotional or retention offers are allowed

Current repository status for these rules:

- inactive definition: TODO
- repeat interval logic: TODO
- lost lead definition: TODO
- VIP segmentation rule: TODO
- birthday campaign rule: TODO
- approved offer policy: TODO

## Expected Fastest Revenue Effect

The fastest money should come from:

1. unfinished conversations
2. clients already known to the salon
3. clients close to a booking decision
4. reminders tied to a specific next action

Therefore the commercial center of the MVP is:

- reactivation
- repeat reminder
- lead recovery

Those three modules should define the first revenue engine before broader lifecycle marketing is added.