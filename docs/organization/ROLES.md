# Role-Based Governance

## Purpose
This document defines the role model for Coloré OS. The project depends on roles, not on specific AI systems or individuals.

## Core Principle
A role may be performed by a human, an LLM, a local model, or a future system. Architecture and governance stay unchanged when the assignee changes.

## Roles

### Product Owner
- Purpose: Define product direction, business priorities, and success criteria.
- Responsibilities: Prioritize work, approve scope, confirm business value, and keep delivery aligned with revenue goals.
- Inputs: Business objectives, sprint goals, verified outcomes, stakeholder feedback.
- Outputs: Prioritized backlog, approved scope, milestone decisions.
- Decision Authority: Product direction and scope decisions.
- Interfaces: Architect, Engineering, QA, Operations, Reviewer.
- Success Criteria: Work advances the product mission and meets agreed business outcomes.

### Architect
- Purpose: Preserve system coherence, design quality, and architectural constraints.
- Responsibilities: Review design, maintain architectural rules, document decisions, and protect the integrity of the system.
- Inputs: Business goals, technical constraints, current architecture, decisions, implementation needs.
- Outputs: Architecture guidance, ADRs, design review outcomes, implementation guardrails.
- Decision Authority: Architectural decisions within approved governance.
- Interfaces: Product Owner, Engineering, Documentation, QA, Operations, Reviewer.
- Success Criteria: Changes remain consistent with the architecture and do not introduce avoidable rework.

### Engineering
- Purpose: Deliver implementation that satisfies approved requirements.
- Responsibilities: Build, maintain, test, integrate, and verify product changes.
- Inputs: Approved requirements, architecture guidance, task lifecycle, repository state.
- Outputs: Implemented changes, verified results, commit history, operational notes.
- Decision Authority: Implementation choices within the approved design and scope.
- Interfaces: Architect, Product Owner, QA, Operations, Documentation.
- Success Criteria: Work is implemented correctly, verified, and aligned with the sprint goal.

### Documentation
- Purpose: Keep project knowledge clear, current, and reusable.
- Responsibilities: Create, maintain, review, and structure project documentation.
- Inputs: Product context, architectural decisions, implementation outcomes, operational procedures.
- Outputs: Updated documentation, indexes, process notes, and decision records.
- Decision Authority: Documentation structure and clarity within the documented governance model.
- Interfaces: Architect, Engineering, QA, Operations, Reviewer.
- Success Criteria: Documentation is accurate, discoverable, and useful for humans and automation.

### QA
- Purpose: Validate that changes behave as intended and do not regress existing behavior.
- Responsibilities: Define checks, verify outcomes, identify defects, and confirm readiness.
- Inputs: Planned changes, acceptance criteria, implementation results, known risks.
- Outputs: Verification reports, defect reports, release readiness notes.
- Decision Authority: Acceptance and readiness within agreed quality criteria.
- Interfaces: Engineering, Architect, Product Owner, Operations.
- Success Criteria: Verification is complete, risks are visible, and release quality is understood.

### Operations
- Purpose: Keep the system running reliably and support delivery in real environments.
- Responsibilities: Monitor health, coordinate deployment, manage environment issues, and support continuity.
- Inputs: Release status, runtime signals, incident context, operational requirements.
- Outputs: Operational status updates, deployment notes, incident follow-up.
- Decision Authority: Operational readiness and rollout safety within approved procedures.
- Interfaces: Engineering, QA, Architect, Product Owner.
- Success Criteria: Delivery remains stable, issues are surfaced early, and recovery is orderly.

### Reviewer
- Purpose: Provide independent assessment before decisions are finalized.
- Responsibilities: Review work for correctness, completeness, risk, and alignment with governance.
- Inputs: Proposed changes, design, documentation, verification evidence.
- Outputs: Review feedback, approval or revision guidance.
- Decision Authority: Review outcome and recommendation.
- Interfaces: All roles.
- Success Criteria: Risks are identified early and the project moves forward with confidence.

## Current Assignments

### Product Owner
Current Assignee:
Human

### Architect
Current Assignee:
OpenAI GPT-5.5

### Engineering
Current Assignee:
GitHub Copilot

### Documentation
Current Assignee:
Human

### QA
Current Assignee:
Human

### Operations
Current Assignee:
Human

### Reviewer
Current Assignee:
Human
