# Coloré OS — Roles

Model-independent role definitions. These roles exist regardless of which human, AI model, or tool performs them. For the current tool assignment, see [`agents.md`](agents.md).

## Product

**Responsibility:** Business objectives, product prioritization, revenue strategy.

- Owns sprint goals and priority decisions.
- Approves scope changes.
- Makes final business calls when Engineering and Architecture disagree.
- Does not make architecture decisions.

## Architecture

**Responsibility:** System design, technology strategy, architectural governance.

- Owns architecture decisions and ADR approval.
- Reviews designs before implementation begins.
- Ensures system coherence across sprints.
- Prefers solutions that reduce long-term cost.
- Does not make business-priority decisions.

## Engineering

**Responsibility:** Implementation, research, design, documentation, code quality.

- Translates business objectives and approved designs into working systems.
- Performs research and design work ahead of review.
- Maintains architectural integrity within approved boundaries.
- Never overrides Architecture decisions; escalates conflicts instead of deciding unilaterally.
- Full implementation authority within approved architecture and current sprint scope.

## Operations

**Responsibility:** Execution, verification, deployment.

- Builds features from approved designs.
- Runs tests and verifies correctness.
- Executes deployment and monitors results.
- Does not change scope or architecture without escalation.

## Escalation Rule

Any role uncertain about a decision outside its responsibility must escalate to the owning role — never guess, never assume, never proceed on an unverified assumption.

```
Business question   -> Product
Architecture change -> Architecture
Implementation how   -> Engineering
Execution / deploy   -> Operations
```

## Source of Truth

This file owns abstract, model-independent role responsibility only. It does not name tools or people — see [`agents.md`](agents.md) for the current assignment.
