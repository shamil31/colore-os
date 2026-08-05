# ADR-0002: Single Source of Truth

**Status:** Accepted  
**Date:** 2026-08-05  
**Decision Owner:** Architecture  
**Stakeholders:** Engineering, Product

---

## Context

Knowledge about the project exists in multiple forms: committed code, documentation, chat history, ADRs, git logs, configuration. Without a strict hierarchy, teams waste time resolving conflicts between these sources and making decisions based on stale information.

## Decision

**When information conflicts, apply this hierarchy (highest to lowest authority):**

```
1. Repository Code & Commits (Git is the permanent record)
        ↓
2. .colore/ Runtime Documentation (current project state)
        ↓
3. docs/architecture/ (approved system design)
        ↓
4. docs/adr/ (historical decisions)
        ↓
5. docs/ (all other documentation)
        ↓
6. Chat History & Memory (lowest authority)
```

**Corollary:** Repository code always wins over documentation. If documentation contradicts code, the code is correct and documentation is stale.

## Consequences

**Positive:**
- Clear conflict resolution: check hierarchy, apply rule
- Prevents analysis paralysis ("which source is right?")
- Forces team to keep code documentation in sync
- Single place to look for current state (.colore/)

**Negative:**
- Requires discipline to keep .colore/ updated
- Documentation can lag behind code
- Team must actively maintain hierarchy

## Rationale

The repository is the permanent record of what was built and decided. Everything else is interpretation or scaffolding. Making code authoritative prevents the false belief that documentation is more true than what actually runs.

## Implementation

- Every new document specifies its SSOT status (is it authoritative or reference?)
- When documentation becomes stale, it's marked Deprecated, not deleted
- .colore/ is updated daily before new work begins
- Conflicts resolved by reading code, not debating docs

## Related Decisions

- ADR-0001: Business First (decisions made quickly using SSOT)
- ADR-0003: One Document = One Responsibility (reduces conflicts through clear ownership)
- SOP_DOCUMENT_LIFECYCLE: Reviews and approval ensure SSOT status is maintained

---

**Approval Authority:** Architecture  
**Approval Date:** 2026-08-05
