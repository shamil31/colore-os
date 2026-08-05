# ADR-0003: One Document = One Responsibility

**Status:** Accepted  
**Date:** 2026-08-05  
**Decision Owner:** Architecture  
**Stakeholders:** Engineering, Product

---

## Context

Projects with diffuse documentation responsibility suffer from:
- Duplicate knowledge in multiple files (inconsistency when one changes)
- Unclear ownership (who updates this when it's wrong?)
- Bloated documents that try to cover too much
- Teams re-reading documents searching for specific facts

## Decision

**Every document has exactly one clear responsibility and one owner.**

A document can be:
- **Architecture** — describes system design (owns that description)
- **Decision Record** — captures a decision and its rationale (owns that decision)
- **Process/SOP** — describes how we do recurring work (owns that procedure)
- **Domain Model** — describes one business concept (owns that concept)
- **Navigation/Index** — references other documents (owns the navigation structure)

**A document must NOT:**
- Summarize other documents (link, don't copy)
- Own multiple concepts (split into separate documents)
- Duplicate knowledge from SSOT (reference the SSOT instead)
- Serve multiple purposes (pick one, create new docs for others)

## Consequences

**Positive:**
- Clear ownership: "This document is stale? Talk to [owner]"
- Single update path: changes in one place only
- Lean documents: no bloat from copied content
- Fast navigation: each doc is focused

**Negative:**
- More documents (required to maintain separation)
- Requires discipline in review (catch violations at document level)
- Teams must use index/navigation to find things

## Implementation

Every document must specify:
```
Owner: [name]
Responsibility: [one clear sentence]
SSOT Status: [Yes/No]
Used By: [what consumes this]
Depends On: [what this needs]
```

Violations are caught in document review (SOP_DOCUMENT_LIFECYCLE).

## Examples

**Good single-responsibility documents:**
- LEAD_STATE_MACHINE.md: owns the 10-state lifecycle model
- NEXT_BEST_ACTION_ENGINE.md: owns the action selection logic
- CONVERSATION_ENGINE.md: owns message generation rules

**Bad multi-responsibility documents (should split):**
- "Lead Intelligence Complete Guide" (should split into Model, State Machine, Action Engine, Conversation Engine)
- "Everything You Need to Know About Campaigns" (should split into Pipeline, Playbook, Scenarios)

## Related Decisions

- ADR-0002: Single Source of Truth (combined with this, prevents duplication)
- ADR-0001: Business First (clear responsibility = faster decisions)
- ARCHITECTURE_INDEX.md: enforces this at system level

---

**Approval Authority:** Architecture  
**Approval Date:** 2026-08-05
