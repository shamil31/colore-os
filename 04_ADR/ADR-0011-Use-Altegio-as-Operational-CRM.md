# ADR-0011: Use Altegio as Operational CRM

Status: Accepted
Date: 2026-08-01
Priority: P1 (Architecture)

## Decision

Coloré OS uses Altegio as the operational CRM.

Business decisions may be written back into Altegio through official API methods.

Preferred write-back priority:
1. Comments
2. Custom Fields
3. Importance
4. Labels / Tags
5. Discount

## Context

Official Altegio API audit (2026-08-01) confirmed that write-back can be performed through supported endpoints for:
- client profile updates
- client comments
- labels/tags
- custom field definitions and client custom field values
- loyalty and discount-related operations

## Rationale

Avoid duplicating operational data outside Altegio whenever official API supports storing it safely.

This keeps execution context close to front-desk operations, reduces drift between systems, and preserves a single operational CRM source of truth.

## Consequences

- Coloré OS remains decision and intelligence layer.
- Altegio remains operational CRM system of record.
- Write Back stream is intentionally postponed until AFTER Sprint FIRST REVENUE.
- Any write-back rollout must follow permissions, auditability, and idempotency controls.
