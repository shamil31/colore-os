# Business Intelligence Model for Revenue Engine

## 1. Purpose

Define a practical Business Intelligence scoring model for Coloré OS that supports Package 03 - Client Retention & Reactivation and follows the principle Revenue First.

This document is business specification only.

## 2. Scope

Model scope uses existing Revenue Engine entities and fields:
- RevenueClient
- RevenueClientVisit
- last_visit_date / last_visit_at
- visit_count / total_visits
- total_spent
- visit amount from RevenueClientVisit.amount
- service context from RevenueClientVisit.services and RevenueClient.last_service_name

Primary use case:
- Prioritize which clients should be contacted first for reactivation campaigns.

Out of scope:
- Campaign automation logic
- Message templates
- Channel orchestration
- Code implementation details

## 3. Core Business Definitions

### 3.1 Who is a valuable client?

A valuable client is a client who combines:
- High Monetary Value: strong total spend over observed visits
- Healthy Frequency: repeat visits, not one-time transactions
- Service Quality Mix: services with premium ticket or high margin
- Reactivation Potential: enough delay to justify outreach without being permanently lost

Business interpretation:
- Value is not only spend.
- Value is spend plus repeat behavior plus realistic return potential.

### 3.2 Who should never be disturbed?

Do not proactively disturb clients in these states:
- Recent and Regular: client is still inside expected revisit window
- Just Served: client had a recent visit and no delay signal
- Cooling Window Active: minimum contact gap is not passed
- Explicit No-Contact: business policy or channel rule marks client as no outreach
- Highly Engaged Active: frequent returning clients with no overdue signal

Business rule:
- If client is Regular and not delayed, exclude from reactivation list.

### 3.3 When is a client truly overdue?

A client is truly overdue only when actual delay exceeds service-appropriate revisit expectation.

Overdue logic:
- Expected Visit Date = Last Visit Date + Expected Revisit Interval
- Delay Days = max(0, Today - Expected Visit Date)
- Truly Overdue when Delay Days >= Overdue Threshold for that service cycle

This avoids false overdue labels for naturally long-cycle services.

## 4. Service Revisit Cycles

Different services require different return timing.

### 4.1 Service Cycle Groups (business baseline)

- Fast Cycle (2-4 weeks): bangs trim, root touch-up, maintenance services
- Medium Cycle (4-8 weeks): haircut maintenance, standard color refresh
- Slow Cycle (8-14 weeks): full color transformation, major correction, premium long-session services

### 4.2 Priority of service-cycle selection

For each client, use in order:
1. Last Service Name classification (if available)
2. Most frequent recent service family from visit history
3. Default salon cycle if service is unknown

### 4.3 Business thresholds per cycle

For each cycle group define:
- Delayed threshold
- Lost threshold

Example business defaults (to be owner-approved):
- Fast: delayed 21 days, lost 45 days
- Medium: delayed 45 days, lost 90 days
- Slow: delayed 75 days, lost 140 days

## 5. Client Value Calculation

Client Value should combine three dimensions:

1. Monetary Component
- Total Revenue from visit history
- Optional weighted recent revenue (higher weight on recent spend)

2. Frequency Component
- Total Visits
- Consistency of repeat visits

3. Margin Proxy Component (when direct margin is unavailable)
- Service mix proxy from premium service categories

Proposed business formula:

Client Value Index = 0.55 * Monetary Score + 0.30 * Frequency Score + 0.15 * Service Mix Score

All component scores are normalized to 0-100.

## 6. Probability of Return Estimation

Return probability should reflect timing fit, not only spend.

Use a simple business probability model:

Return Probability Score =
- + Timing Fit Score (how close client is to best reactivation window)
- + Historical Response Proxy (if known from past outcomes)
- + Habit Score (visit regularity)
- - Churn Friction Score (long silence, repeated no-response, inconsistent cadence)

If response history is missing, use timing + habit only.

Business interpretation:
- Highest reactivation chance is usually in delayed window, before deep lost state.

## 7. Churn Risk Signals

A client should be marked at churn risk when multiple signals appear:
- Delay grows beyond cycle-specific lost threshold
- Visit intervals become unstable or expand sharply
- Revenue drops across recent visits
- Visits count trend declines
- No successful reactivation outcome over repeated attempts

Risk tiers:
- Low Risk: regular/near due
- Medium Risk: delayed with moderate drift
- High Risk: lost or chronically non-returning

## 8. Priority Score Model

Priority Score must rank reactivation candidates by business impact, not only delay.

### 8.1 Required normalized inputs (0-1)

- Delay Weight (DW): normalized delay severity by service cycle
- Monetary Weight (MW): normalized client monetary value
- Frequency Weight (FW): normalized repeat behavior
- Return Probability Weight (RPW): normalized likelihood to return now
- Churn Risk Weight (CRW): normalized risk severity

### 8.2 Core Priority formula

Base Priority = DW * MW * FW

Final Priority Score = 100 * Base Priority * RPW * (1 + 0.35 * CRW)

Design intent:
- Delay, value, and frequency remain core.
- Return probability prevents wasting effort on very unlikely cases.
- Churn risk boosts urgency where revenue loss risk is real.

### 8.3 Guardrails

- If client is in Do Not Disturb state: Priority = 0
- If client has no valid contact channel: Priority moves to operational hold list
- If client is Regular and inside cycle window: exclude from campaign ranking

## 9. Practical Segment Output for Operations

Every ranked client should have:
- Segment: Regular / Delayed / Lost
- Value Tier: High / Medium / Low
- Priority Score (0-100)
- Reason string (example):
  - "High value, medium delay, high return probability"

Operational goal:
- Produce a daily TOP reactivation list that business can execute immediately.

## 10. Business Answers to the 8 Required Questions

1. Who is valuable?
- High spend + repeat visits + premium service mix + realistic return potential.

2. Who should never be disturbed?
- Regular clients inside revisit window, clients in cooling window, explicit no-contact clients, and active clients without delay.

3. When truly overdue?
- When delay exceeds cycle-specific threshold, not just generic days-since-last-visit.

4. Which services have different revisit cycles?
- Fast, medium, and slow cycle service groups; classify by last service and recent history.

5. How to calculate client value?
- Weighted index of monetary, frequency, and service mix, normalized to 0-100.

6. How to estimate return probability?
- Timing fit + habit regularity + response proxy minus churn friction.

7. Which signals indicate churn risk?
- Long delay beyond lost threshold, interval expansion, spend decline, lower visit trend, repeated no-response.

8. How to calculate Priority Score?
- Final Priority = 100 * (DW * MW * FW) * RPW * (1 + 0.35 * CRW), with do-not-disturb and data guardrails.

## 11. Decision Notes for Product Owner

Items requiring owner approval before operational rollout:
- Service-to-cycle mapping table
- Delayed/lost thresholds by cycle
- Cooling window duration
- Weights for value index and final priority formula
- Contact policy exclusions

This keeps the model explainable, commercially grounded, and aligned with Revenue First and Finish before Improve.