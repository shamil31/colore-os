# Architecture Index

Navigation guide for system architecture documents.

---

## Document Map

### RUNTIME_ARCHITECTURE.md
- **Purpose:** Complete data flow through system (sources → layers → delivery → learning)
- **Single Source of Truth:** Yes — only place that describes full pipeline
- **Depends On:** All layer designs (Intelligence Model, State Machine, NBA Engine, Conversation Engine)
- **Used By:** Implementation teams (Sprint #5+), API design, database schema design
- **Owner:** Architect
- **Status:** Sprint #4 (Research & Design complete)

---

## Domain Architecture

### docs/domain/customer_intelligence/

#### LEAD_INTELLIGENCE_MODEL.md
- **Purpose:** How system understands leads (Intent, Emotion, Readiness, Trust)
- **Single Source of Truth:** Yes — only definition of intelligence layer
- **Depends On:** None (foundational)
- **Used By:** Lead State Machine, NBA Engine, Conversation Engine
- **Owner:** Engineering
- **Status:** Sprint #1 (Integrated)

#### LEAD_STATE_MACHINE.md
- **Purpose:** 10-state lifecycle of a lead from contact to booking/closure
- **Single Source of Truth:** Yes — only definition of state transitions
- **Depends On:** Lead Intelligence Model (input)
- **Used By:** NBA Engine, Conversation Engine
- **Owner:** Engineering
- **Status:** Sprint #1 (Integrated)

#### NEXT_BEST_ACTION_ENGINE.md
- **Purpose:** Selects one optimal action based on lead understanding
- **Single Source of Truth:** Yes — only definition of decision logic
- **Depends On:** Lead Intelligence Model, Lead State Machine, Business Context
- **Used By:** Conversation Engine, Implementation
- **Owner:** Engineering
- **Status:** Sprint #2 (Integrated)

#### CONVERSATION_ENGINE.md
- **Purpose:** Transforms action into message respecting brand voice
- **Single Source of Truth:** Yes — only definition of message layer
- **Depends On:** Next Best Action Engine (input)
- **Used By:** Integrilla (delivery), Learning Loop
- **Owner:** Engineering
- **Status:** Sprint #3 (Integrated)

---

## Operations & Procedures

### docs/operations/

#### SOP_DOCUMENT_LIFECYCLE.md
- **Purpose:** 5-stage lifecycle: IDEA → DESIGN → REVIEW → APPROVED → INTEGRATED
- **Single Source of Truth:** Yes — only definition of document workflow
- **Depends On:** None (process document)
- **Used By:** All documentation creation (Architecture Index, ADRs, etc.)
- **Owner:** Engineering
- **Status:** Sprint #1 (Integrated)

#### SOP_TASK_LIFECYCLE.md
- **Purpose:** 8-stage lifecycle: IDEA → RESEARCH → DESIGN → REVIEW → BUILD → VERIFY → DEPLOY → LEARN
- **Single Source of Truth:** Yes — only definition of task workflow
- **Depends On:** None (process document)
- **Used By:** All task execution
- **Owner:** Engineering
- **Status:** Sprint #1 (Integrated)

### docs/operations/governance/
*Reserved for governance procedures and project rules*

### docs/operations/infrastructure/
*Reserved for external system integrations (Altegio, Integrilla, etc.)*

---

## Decision Records

### docs/adr/
*Architecture Decision Records — permanent decisions that shape the system*

---

## Research & Exploration

### docs/research/
*Specifications, explorations, and research documents*

---

## Dependencies Graph

```
RUNTIME_ARCHITECTURE (System Overview)
    ├─ Depends on all layers
    
LEAD_INTELLIGENCE_MODEL (Foundation)
    ├─ Input: Raw message from client
    ├─ Output: Intent, Emotion, Readiness, Trust
    │
    └─→ LEAD_STATE_MACHINE
        ├─ Input: Intelligence outputs
        ├─ Output: Lead State, Allowed Actions
        │
        └─→ NEXT_BEST_ACTION_ENGINE
            ├─ Input: State + Intelligence + Business Context
            ├─ Output: Action + Reason
            │
            └─→ CONVERSATION_ENGINE
                ├─ Input: Action + Brand Voice
                ├─ Output: Message
                │
                └─→ Integrilla (Delivery)
                    │
                    └─→ Learning Loop (Feedback)

SOP_DOCUMENT_LIFECYCLE (Governs)
    └─→ All documentation creation

SOP_TASK_LIFECYCLE (Governs)
    └─→ All task execution
```

---

## Ownership Matrix

| Document | Owner | Type | Status |
|----------|-------|------|--------|
| RUNTIME_ARCHITECTURE.md | Engineering | Architecture | Sprint #4 |
| LEAD_INTELLIGENCE_MODEL.md | Engineering | Domain | Sprint #1 |
| LEAD_STATE_MACHINE.md | Engineering | Domain | Sprint #1 |
| NEXT_BEST_ACTION_ENGINE.md | Engineering | Domain | Sprint #2 |
| CONVERSATION_ENGINE.md | Engineering | Domain | Sprint #3 |
| SOP_DOCUMENT_LIFECYCLE.md | Engineering | Process | Sprint #1 |
| SOP_TASK_LIFECYCLE.md | Engineering | Process | Sprint #1 |

---

## Usage Rules

1. **Never duplicate knowledge** — Each document has one owner, one purpose
2. **Follow SSOT** — If SSOT document exists, reference it, don't rewrite
3. **Navigate via dependencies** — Use this index to understand what feeds into what
4. **Update ownership** — If you become owner of a document, update this index

---

## How to Use This Index

- **New to the project?** Start with RUNTIME_ARCHITECTURE.md to see the full pipeline
- **Understanding lead handling?** Follow: Intelligence Model → State Machine → NBA Engine → Conversation Engine
- **Creating new documents?** Check SOP_DOCUMENT_LIFECYCLE.md and ADRs for precedent
- **Uncertain about ownership?** Check this index's Ownership Matrix

---

**Last Updated:** 2026-08-05  
**Version:** 1.0
