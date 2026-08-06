# Coloré OS Project Knowledge Index

**Date:** 2026-08-02  
**Purpose:** Single entry point for all project documentation  
**Scope:** Navigation and categorization of all project knowledge

---

## Source of Truth Hierarchy

When information conflicts, apply this priority:

```
Repository Code & Commits (HIGHEST AUTHORITY)
           ↓
     Project OS (.colore/)
           ↓
    Architecture Decision Records
           ↓
    Standard Operating Procedures
           ↓
    Playbooks & SOP
           ↓
    Research & Specs
           ↓
    Chat History & Notes
(LOWEST AUTHORITY)
```

**Rule:** Always check higher levels before lower levels. Repository code is authoritative.

---

## 0. System Architecture

Foundation of how Coloré OS processes data end-to-end.

| Document | Purpose | Status | Sprint |
|----------|---------|--------|--------|
| [docs/architecture/RUNTIME_ARCHITECTURE.md](architecture/RUNTIME_ARCHITECTURE.md) | Complete data flow through system: sources → processing layers → delivery → learning | Integrated | #4 |

**Foundation for:** All technical implementation decisions, service architecture, database schema design.

---

## 1. Active Sprint

Current business focus and execution state.

| Document | Purpose | Status | Commit |
|----------|---------|--------|--------|
| [.colore/next.md](./../.colore/next.md) | Daily revenue focus and active product task | Active | — |
| [.colore/state.md](./../.colore/state.md) | Current sprint name, KPI, priorities, execution queue | Active | — |
| [.colore/sprint.md](./../.colore/sprint.md) | Sprint details and status | Active | — |

**Entry point:** Start here each session. Read TODAY.md first for daily focus.

---

## 2. Architecture

System design, technology decisions, and operating principles.

| Document | Purpose | Status | Commit |
|----------|---------|--------|--------|
| [REVIEWER.md](REVIEWER.md) | Engineering operating manual; roles, rules, execution discipline | Active | 1.1 (2026-08-02) |
| [.colore/architecture.md](./../.colore/architecture.md) | Revenue architecture chain, system components, non-negotiable constraints | Active | — |
| [.colore/architecture.md](./../.colore/architecture.md) | Technology stack (FastAPI, SQLAlchemy, PostgreSQL, Docker) | Active | — |
| [.colore/runtime.md](./../.colore/runtime.md) | Universal AI Operating Protocol for all AI systems | Active | — |

**Non-negotiable this sprint:** Coloré OS does not replace Altegio or Integrilla. Operating chain: Altegio → Coloré OS → Integrilla → Client → Altegio.

---

## 3. ADR (Architecture Decision Records)

Permanent decisions that shape the system and cannot be revised mid-sprint.

| Document | Purpose | Status | Commit |
|----------|---------|--------|--------|
| [.colore/changelog.md](./../.colore/changelog.md) | Active working decisions and decision history | Active | — |
| [04_ADR/ADR-0011-Use-Altegio-as-Operational-CRM.md](04_ADR/ADR-0011-Use-Altegio-as-Operational-CRM.md) | Decision to use Altegio as operational CRM; no replacement | Active | 3d22c5c |

**Rule:** Architecture changes require ADR. No implementation without CTO sign-off.

---

## 4. SOP (Standard Operating Procedures)

How we execute recurring operations and workflows.

| Document | Purpose | Status | Commit |
|----------|---------|--------|--------|
| [.colore/runtime.md](./../.colore/runtime.md) | AI engagement contract and working agreements | Active | — |
| [.colore/state.md](./../.colore/state.md) | Project governance, workflow, and approval process | Active | — |
| [docs/FIRST_CAMPAIGN_CHECKLIST.md](FIRST_CAMPAIGN_CHECKLIST.md) | Step-by-step execution checklist for first campaign launch | Active | 7b3ca59 |
| [docs/CAMPAIGN_PIPELINE.md](CAMPAIGN_PIPELINE.md) | End-to-end campaign generation pipeline; all 10 stages documented | Active | b0d1eed |

**Daily use:** FIRST_CAMPAIGN_CHECKLIST for launch execution. CAMPAIGN_PIPELINE for understanding data flow.

---

## 5. Playbooks

Step-by-step guides for recurring problems and tasks.

| Document | Purpose | Status | Commit |
|----------|---------|--------|--------|
| [docs/INTEGRATION_STATUS.md](INTEGRATION_STATUS.md) | Current integration status across all systems | Active | — |
| [docs/ALTEGIO_API_CAPABILITIES.md](ALTEGIO_API_CAPABILITIES.md) | Altegio API audit: read vs write capabilities, deferred items | Active | d55f516 |

---

## 6. API Documentation

External integration and system interfaces.

| Document | Purpose | Status | Commit |
|----------|---------|--------|--------|
| [docs/ALTEGIO_API_CAPABILITIES.md](ALTEGIO_API_CAPABILITIES.md) | Altegio API read-only status, write-back deferred until post-FIRST REVENUE | Active | d55f516 |
| [.colore/roles.md](./../.colore/roles.md) | Architect role responsibilities and operating principles | Active | — |
| [.colore/roles.md](./../.colore/roles.md) | Engineering role policy and constraints | Active | — |

---

## 7. Research & Specs

Exploratory work, specifications, and business intelligence models.

| Document | Purpose | Status | Commit |
|----------|---------|--------|--------|
| [01_Research/Business_Intelligence_Model.md](./../01_Research/Business_Intelligence_Model.md) | Client value calculation, priority scoring, churn risk signals; business rules | Active | — |
| [01_Research/Altegio_API_Capabilities.md](./../01_Research/Altegio_API_Capabilities.md) | Altegio API research and capability exploration | Active | — |
| [docs/REACTIVATION_ENGINE_SPEC.md](REACTIVATION_ENGINE_SPEC.md) | Client reactivation strategy and candidate ranking | Draft | — |
| [docs/CLIENT_GROWTH_ENGINE_SPEC.md](CLIENT_GROWTH_ENGINE_SPEC.md) | Client growth and acquisition strategy | Draft | — |
| [docs/REVENUE_ENGINE_MVP.md](REVENUE_ENGINE_MVP.md) | Minimum viable revenue engine specification | Draft | — |
| [docs/AI_ADMINISTRATOR_SPEC.md](AI_ADMINISTRATOR_SPEC.md) | Specification for autonomous AI administrator system (deferred) | Draft | — |
| [docs/AI_CONSTITUTION.md](AI_CONSTITUTION.md) | Operating principles and constraints for AI systems | Active | — |
| [docs/AI_EMPLOYEE_FRAMEWORK.md](AI_EMPLOYEE_FRAMEWORK.md) | Framework for treating AI systems as team members | Active | — |

---

## 8. Reports & Status

Current state, progress tracking, and verified facts.

| Document | Purpose | Status | Commit |
|----------|---------|--------|--------|
| [.colore/state.md](./../.colore/state.md) | Verified facts only; last verified 2026-08-01 | Active | — |
| [.colore/roadmap.md](./../.colore/roadmap.md) | Future work not in current sprint | Active | — |
| [.colore/roadmap.md](./../.colore/roadmap.md) | Strategic direction and long-term vision | Active | — |
| [.colore/changelog.md](./../.colore/changelog.md) | Historical log of verified events and decisions | Active | — |
| [docs/INTEGRATION_STATUS.md](INTEGRATION_STATUS.md) | Current status of all system integrations | Active | — |

---

## 9. AI & Team

AI team structure, roles, and collaboration framework.

| Document | Purpose | Status | Commit |
|----------|---------|--------|--------|
| [REVIEWER.md](REVIEWER.md) | Engineering role responsibilities, authority, and constraints | Active | 1.1 |
| [.colore/roles.md](./../.colore/roles.md) | Architect role (architecture, strategy, approvals) | Active | — |
| [.colore/roles.md](./../.colore/roles.md) | Engineering role policy and implementation constraints | Active | — |
| [docs/AI_CONSTITUTION.md](AI_CONSTITUTION.md) | AI operating principles (no hallucination, reality first, revenue first) | Active | — |
| [docs/AI_EMPLOYEE_FRAMEWORK.md](AI_EMPLOYEE_FRAMEWORK.md) | Treating AI as team member with clear role and accountability | Active | — |

---

## 10. Customer Intelligence

Decision models and lead handling frameworks. How Coloré OS understands clients and makes decisions.

### Lead Intelligence (Sprint #1 + Sprint #2 + Sprint #3)

| Document | Purpose | Status | Sprint |
|----------|---------|--------|--------|
| [docs/domain/customer_intelligence/LEAD_INTELLIGENCE_MODEL.md](domain/customer_intelligence/LEAD_INTELLIGENCE_MODEL.md) | How Coloré OS understands leads: intent → emotion → readiness → trust | Integrated | #1 |
| [docs/domain/customer_intelligence/LEAD_STATE_MACHINE.md](domain/customer_intelligence/LEAD_STATE_MACHINE.md) | Lead lifecycle: 10 states from initial contact to booking or closure | Integrated | #1 |
| [docs/domain/customer_intelligence/NEXT_BEST_ACTION_ENGINE.md](domain/customer_intelligence/NEXT_BEST_ACTION_ENGINE.md) | Decision layer: selects one next action based on lead understanding and business context | Integrated | #2 |
| [docs/domain/customer_intelligence/CONVERSATION_ENGINE.md](domain/customer_intelligence/CONVERSATION_ENGINE.md) | Communication layer: transforms action into message respecting brand voice | Integrated | #3 |

**Complete Architecture Chain:** 
```
Lead Intelligence Model (understand: Intent, Emotion, Readiness, Trust)
    ↓
Lead State Machine (position: 10 states)
    ↓
Next Best Action Engine (decide: action + reason)
    ↓
Conversation Engine (speak: message + tone)
```

---

## 11. Execution SOPs

Standard Operating Procedures for recurring operations.

| Document | Purpose | Status | Commit |
|----------|---------|--------|--------|
| [docs/operations/SOP_DOCUMENT_LIFECYCLE.md](operations/SOP_DOCUMENT_LIFECYCLE.md) | How documents move from IDEA → DESIGN → REVIEW → APPROVED → INTEGRATED | Integrated | Sprint #1 |
| [docs/operations/SOP_TASK_LIFECYCLE.md](operations/SOP_TASK_LIFECYCLE.md) | How tasks move from IDEA → RESEARCH → DESIGN → REVIEW → BUILD → VERIFY → DEPLOY → LEARN | Integrated | Sprint #1 |
| [docs/FIRST_CAMPAIGN_CHECKLIST.md](FIRST_CAMPAIGN_CHECKLIST.md) | Step-by-step execution checklist for first campaign launch | Active | 7b3ca59 |
| [docs/CAMPAIGN_PIPELINE.md](CAMPAIGN_PIPELINE.md) | End-to-end campaign generation pipeline; all 10 stages documented | Active | b0d1eed |

**Usage:** Use SOP_TASK_LIFECYCLE to manage any task. Use SOP_DOCUMENT_LIFECYCLE to manage document creation. Use CAMPAIGN_PIPELINE and FIRST_CAMPAIGN_CHECKLIST for campaign-specific execution.

---

## 12. Project State & Governance

Project-level state, decisions, and verification.

| Document | Purpose | Status | Commit |
|----------|---------|--------|--------|
| [.colore/state.md](./../.colore/state.md) | Verified facts; source of truth for project state | Active | — |
| [.colore/state.md](./../.colore/state.md) | Current sprint, priorities, completed work | Active | — |
| [.colore/changelog.md](./../.colore/changelog.md) | Active decisions driving execution | Active | — |
| [.colore/changelog.md](./../.colore/changelog.md) | Full decision history and ADR records | Active | — |
| [.colore/runtime.md](./../.colore/runtime.md) | Work workflow: BACKLOG → TODO → DOING → REVIEW → DONE | Active | — |

---

## Additional Resources

| Document | Purpose | Status | Commit |
|----------|---------|--------|--------|
| [README.md](../README.md) | Project overview and getting started | Active | — |
| [.colore/README.md](./../.colore/README.md) | Runtime documentation overview | Active | — |
| [.colore/changelog.md](./../.colore/changelog.md) | Session management and logging | Active | — |
| [docs/DECISION_MODEL.md](DECISION_MODEL.md) | How decisions are made and escalated | Draft | — |
| [docs/PRODUCT_VISION.md](PRODUCT_VISION.md) | Product vision and long-term goals | Draft | — |
| [docs/CONVERSATION_PRINCIPLES.md](CONVERSATION_PRINCIPLES.md) | How humans and AI collaborate | Active | — |
| [docs/INTENT_MAP.md](INTENT_MAP.md) | Intent-to-action mapping | Draft | — |

---

## How to Use This Index

### For Engineering Sessions
1. Start each session by reading this INDEX.md
2. Navigate to the document you need based on category
3. Check the "Source of Truth Hierarchy" if information conflicts
4. If you need new documents, add them to this index

### For New Documents
1. Create the markdown file in `/docs/`
2. Add entry to this INDEX.md in the appropriate section
3. Include: filename, one-sentence purpose, status (Draft/Active/Deprecated), commit hash
4. Commit with message: `docs(index): add [document name]`

### For Deprecated Documents
1. DO NOT DELETE the file
2. Change status to "Deprecated" in this index
3. Add note: "Superseded by [new document]"
4. Commit with message: `docs(index): deprecate [document name]`

---

## Maintenance Rules

**Every new document MUST be added to this index immediately.**

**INDEX.md is the navigation entry point for every AI session.**

**Deprecated documents are never deleted; they are marked as Deprecated here.**

**All documents link to their source; broken links indicate missing files.**

**Status meanings:**
- **Active** - Current, authoritative, used in operations
- **Draft** - Under development, not yet authoritative
- **Deprecated** - Superseded by another document, kept for history

**Update frequency:** After each document creation or status change.

---

## Quick Navigation

- **Just starting?** → Read REVIEWER.md + TODAY.md + PROJECT_STATE.md
- **Need architecture rules?** → Read REVIEWER.md Section III + ARCHITECTURE.md
- **Running a campaign?** → Read FIRST_CAMPAIGN_CHECKLIST.md + CAMPAIGN_PIPELINE.md
- **Checking integrations?** → Read ALTEGIO_API_CAPABILITIES.md + INTEGRATION_STATUS.md
- **Understanding decisions?** → Read DECISIONS.md + KNOWN_STATE.md
- **Need to escalate?** → Read REVIEWER.md Section XXIII (Escalation Path)

---

**Last Updated:** 2026-08-02  
**Next Review:** After each new document creation
