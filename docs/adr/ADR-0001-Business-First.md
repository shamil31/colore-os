# ADR-0001: Business First

**Status:** Accepted  
**Date:** 2026-08-05  
**Deciders:** Claude (Lead Engineer), ChatGPT (CTO), Shamil (CEO)

---

## Context

Coloré OS operates in a resource-constrained environment where every engineering decision carries opportunity cost. Without a clear priority hierarchy, the team risks investing in technical elegance, architectural purity, or feature completeness at the expense of revenue generation.

## Decision

**Every engineering decision optimizes for business outcome, never for code elegance, architectural purity, or feature completeness.**

The priority hierarchy is:
```
1. Business Result
     ↓
2. Revenue
     ↓
3. Sprint Goal
     ↓
4. Architecture
     ↓
5. Implementation
     ↓
6. Optimization
```

## Consequences

**Positive:**
- Clear decision-making filter: "Does this advance revenue?"
- Fast validation of business hypothesis
- Technical debt accepted where it generates revenue
- No scope creep for perfection

**Negative:**
- Technical shortcuts accumulate over time
- May require refactoring for scale (after revenue validation)
- Pressures towards pragmatism over sustainability
- Requires discipline to not abandon architecture entirely

## Rationale

The company mission is to increase salon revenue. Engineering exists to serve business goals, not the reverse. Until first revenue is verified, business outcome trumps all other considerations.

## Related Decisions

- ADR-0002: Single Source of Truth (enables business decision-making)
- ADR-0003: One Document = One Responsibility (reduces overhead, speeds decisions)
- PROJECT_CONSTITUTION: Principle #1 (codifies this decision)

---

**Reviewer:** ChatGPT (CTO) ✓  
**Approval Date:** 2026-08-05
