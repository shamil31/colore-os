# PROJECT CONSTITUTION: Coloré OS

**Effective Date:** 2026-08-02  
**Version:** 1.0  
**Audience:** Any assigned role performer entering the project  
**Purpose:** Single entry point before starting work on Coloré OS

---

## Project Identity

**Name:** Coloré OS  
**Type:** Revenue Operating System  
**Context:** Operates above existing salon infrastructure (Altegio CRM, Integrilla messaging)

### Brief Purpose
Coloré OS increases salon revenue by intelligently prioritizing clients, orchestrating reactivation campaigns, and learning from real outcomes—all without replacing existing systems.

**For full project details, read:** [.colore/02_PROJECT.md](../02_PROJECT.md)

---

## Immutable Principles

These principles are **permanent and non-negotiable** for the life of this project.

### 1. Revenue First
Every engineering decision is optimized for business outcome, never for code elegance or architectural purity.

### 2. Reality First  
All planning and reporting must be based on verified facts, never assumptions.

### 3. Finish Before Improve
Complete the current task. Refactoring and optimization come after.

### 4. Architectural Guardrails (Non-Negotiable)
- Coloré OS does **not** replace Altegio (CRM system of record)
- Coloré OS does **not** replace Integrilla (message transport layer)
- All data flows through this chain: **Altegio → Coloré OS → Integrilla → Client**

### 5. Use Existing Infrastructure
No platform replacement work. Build within constraints.

### 6. Model Independence
The structure of the project, its architecture, documentation, processes, contracts, and ADRs must not depend on any specific AI model. When the executor of a role changes, the project structure and governance remain unchanged.

### 7. Architecture Integration Mandatory
Every approved artifact must complete Architecture Integration before any new work begins.

**Process:** Approved → Architecture Review → Integration → Next Work

This ensures consistency, prevents rework, and maintains architectural coherence as the project scales.

**For architectural context, read:** [.colore/03_ARCHITECTURE.md](../03_ARCHITECTURE.md)

---

## Current Strategic Focus

### Sprint: FIRST REVENUE
**Status:** Active (started 2026-08-01)

**Primary Objective:**  
Get **one real client booking** initiated by Coloré OS.

**Main KPI:**  
First revenue ("Первая выручка")

**Why This Matters:**  
Proof of concept. One booking validates the model before scaling.

**Current Status:**  
- ✅ Campaign pipeline implemented (9 of 10 stages)
- ✅ Conversation playbook approved
- ✅ Integrilla export working
- ✅ **Sprint #1 Complete:** Lead Intelligence MVP (2026-08-05)
  - Lead State Machine v1 (10-state operational model)
  - Lead Intelligence Model v1 (decision framework)
  - SOP Document Lifecycle (document governance)
  - SOP Task Lifecycle (task execution governance)

**For current sprint details, read:** [.colore/00_Master/TODAY.md](./TODAY.md) | [.colore/00_Master/NEXT.md](./NEXT.md)

**For Lead Intelligence details, read:** [docs/01_CUSTOMER_INTELLIGENCE/02_LEAD_INTELLIGENCE/](../../docs/01_CUSTOMER_INTELLIGENCE/02_LEAD_INTELLIGENCE/)

---

## Strategic Decisions & Reasoning

| Decision | Reason | Impact |
|----------|--------|--------|
| Use Altegio as CRM system of record | Existing client infrastructure; no rebuilding | Revenue data flows from Altegio only |
| Use Integrilla as message transport | Existing channels to clients; battle-tested | No message logic in Coloré OS |
| Prioritize clients before messaging | Client value varies; focus on high-return targets | Enables revenue-optimized campaigns |
| Revenue loop over perfect code | One booking beats elegant refactoring | Ship now, learn from real data |
| Start with reactivation (Long Absence clients) | Existing relationships; lower activation cost | Fastest path to first revenue |

**For decision history, read:** [.colore/07_DECISIONS.md](../07_DECISIONS.md)

---

## Execution Framework

### Operating Rules
All assigned actors working on this project must follow:

**Read before starting:** [.colore/01_CONTRACT.md](../01_CONTRACT.md) (Universal Operating Contract)  
**Universal protocol:** [.colore/09_UAOP.md](../09_UAOP.md) (role-based operating standard)

### Source of Truth Priority
When information conflicts, use this hierarchy:

1. [.colore/00_Master/](./README.md) files (current state)
2. [.colore/01_CONTRACT.md](../01_CONTRACT.md), [.colore/02_PROJECT.md](../02_PROJECT.md), [.colore/03_ARCHITECTURE.md](../03_ARCHITECTURE.md)
3. [.colore/07_DECISIONS.md](../07_DECISIONS.md), [.colore/08_VERIFIED_HISTORY.md](../08_VERIFIED_HISTORY.md)
4. All other documentation

**Repository code always wins over documentation.**

---

## Before Starting Work

### 1. Read This Document (you are here)

### 2. Read Mandatory Runtime Docs
In order:
- [ ] [.colore/09_UAOP.md](../09_UAOP.md) — Universal AI Operating Protocol
- [ ] [.colore/01_CONTRACT.md](../01_CONTRACT.md) — Operating Contract
- [ ] [.colore/03_ARCHITECTURE.md](../03_ARCHITECTURE.md) — System Architecture

### 3. Read Current State
- [ ] [.colore/00_Master/TODAY.md](./TODAY.md) — Today's focus
- [ ] [.colore/00_Master/NEXT.md](./NEXT.md) — Next action
- [ ] [.colore/00_Master/KNOWN_STATE.md](./KNOWN_STATE.md) — Verified facts
- [ ] [.colore/00_Master/DECISIONS.md](./DECISIONS.md) — Active decisions

### 4. Verify Git State
```bash
git status                    # Check for uncommitted work
git log --oneline -5         # See recent commits
```

### 5. Ask Yourself
- [ ] Do I understand the current sprint goal?
- [ ] Do I know what NOT to build? (see NEXT.md)
- [ ] Have I read the conversation playbook? (docs/CONVERSATION_PLAYBOOK.md)
- [ ] Am I optimizing for revenue, not code elegance?

**Only then proceed with your task.**

---

## Learning from Outcomes

Every campaign teaches us:

- **Replies:** Which messages clients respond to
- **Dialogs:** Which objections we handle best
- **Bookings:** Which strategies drive actual revenue
- **Patterns:** What works, what doesn't

This learning feeds back into the next campaign cycle.

**For verified outcomes, read:** [.colore/08_VERIFIED_HISTORY.md](../08_VERIFIED_HISTORY.md)

---

## Deferred Work (Do Not Build Yet)

- ❌ AI Administrator (autonomous agent)
- ❌ Analytics Dashboard
- ❌ Multi-tenant support
- ❌ SaaS marketplace
- ❌ Automatic Integrilla write-back
- ❌ Advanced reporting

**Why?** Prove the model works with one client first. Then scale.

---

## Contact & Escalation

**Blocked or Uncertain?**

1. Check [.colore/00_Master/KNOWN_STATE.md](./KNOWN_STATE.md) for verified facts
2. Check [.colore/00_Master/DECISIONS.md](./DECISIONS.md) for active rules
3. Read [REVIEWER.md](../../REVIEWER.md) Section XXIII (Escalation Path)
4. Ask, don't assume

---

## Permanent Record

This document is the constitution of Coloré OS. It does not change with sprint goals or campaign outcomes.

**If you think something in this document needs to change:**
- Propose the change through the Architect role
- Document your reasoning
- Wait for approval before modifying

**The constitution protects the project's identity through all phases of growth.**

---

**Last Updated:** 2026-08-02  
**Next Review:** Upon major strategic shift or completion of FIRST REVENUE sprint
