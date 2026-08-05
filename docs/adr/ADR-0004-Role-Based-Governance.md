# ADR-0004: Role-Based Governance

**Status:** Accepted  
**Date:** 2026-08-05  
**Decision Owner:** Architecture  
**Stakeholders:** Product Owner, Architect, Engineering, Documentation, QA, Operations, Reviewer

---

## Context

The project needs a governance model that remains stable even as the assigned executors change. A system that depends on a specific model, vendor, or assistant creates avoidable coupling and makes the architecture fragile.

## Decision

The project will depend on roles rather than on specific AI systems or individuals.

This principle means:
- The architecture is governed by roles.
- The executor of a role may be a human, an LLM, a local model, or a future system.
- Replacing or changing the assignee of a role does not require changing the architecture.
- Governance, responsibilities, and decision authority remain defined in role-based documentation.

## Consequences

**Positive:**
- The project remains portable across tools and executors.
- Governance is more durable and future-proof.
- Roles can be reassigned without architectural churn.

**Negative:**
- Role definitions must be maintained carefully.
- Assignment changes must be documented explicitly.

## Implementation

The project will use the role definitions in [docs/organization/ROLES.md](../organization/ROLES.md) as the governing model for responsibilities and coordination.

## Related Decisions

- ADR-0003: One Document = One Responsibility
- ADR-0002: Single Source of Truth
- ADR-0001: Business First
