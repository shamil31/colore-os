# Coloré OS Runtime Bootstrap

## RUNTIME HEADER

This document is the runtime contract for Coloré OS development.
Reading it means entering the Coloré OS development runtime.
The LLM must restore context before answering.

## OPEN DAY PROTOCOL

If this document has been loaded, automatically execute Open Day without waiting for additional commands.

1. Confirm successful context loading.
2. Summarize the current project state.
3. Summarize completed work.
4. Summarize active architectural decisions.
5. Identify the current development phase.
6. Identify the current sprint.
7. Identify today’s objective.
8. Identify architectural risks.
9. Propose the next engineering task.
10. Wait for the user.

## COMMANDS

Open Day = Execute the Open Day protocol.

Close Day = Analyze the current session, update bootstrap.md, generate the next runtime state, and prepare tomorrow’s entry point.

## PROJECT SNAPSHOT

Current Phase: Launch readiness and revenue validation.

Current Sprint: FIRST REVENUE.

Current Position: Campaign infrastructure is complete and the project is waiting for the first real campaign launch decision. The immediate goal remains to prove one real booking path from lead to appointment.

Completed Since Last Session:
- Runtime bootstrap was converted into a runtime contract.
- Role-based operating docs were synchronized with the new entry-point model.
- The repository reached a model-independent runtime structure.
- Sprint #1 lead-intelligence work was completed and documented.

Open Questions:
- Whether the first campaign launch should proceed now.
- Which client segment should be used for the first live message sequence.
- Whether the next task should be launch execution or campaign validation.

Architecture Decisions:
- Coloré OS remains above existing systems and does not replace Altegio or Integrilla.
- Revenue delivery is prioritized over architectural optimization.
- Runtime state is maintained through bootstrap and master runtime documents.

Blocked Items:
- No code-level blocker is currently blocking runtime readiness.
- The main execution blocker is the decision to begin the first live campaign.

Risks:
- Launching before verified message flow readiness could create false confidence.
- Weak campaign execution discipline could reduce the value of the first revenue test.
- Incomplete runtime synchronization could cause mixed operating guidance.

Next Decision:
- Decide whether the next task is campaign launch execution or validation of the transport loop.

First Task Today:
- Confirm the next execution step and begin from the current runtime state.

## PROJECT PRINCIPLES

Single Source of Truth

One Document One Responsibility

Role-Based Governance

Model Independence

Contract First

## CURRENT ARCHITECTURE

Coloré OS operates as a revenue orchestration layer above existing business systems. Its architecture is centered on a runtime contract that establishes the operating context for any participant, a set of role-based governance documents that define accountability, and a master state layer that preserves the current sprint, active decisions, and execution focus. The system’s business logic is organized around revenue-oriented flows, while integration boundaries remain explicit so that existing operational platforms stay authoritative. The architecture is intentionally governed by contracts, verified state, and disciplined execution rather than by implementation detail or tool preference.

## SESSION MEMORY

The previous working session completed the runtime refactor by converting the bootstrap file into the central entry point, aligning the operating contract with Open Day and Close Day behavior, and synchronizing the runtime documentation so it speaks with one voice.

## DO NOT INCLUDE

- Long explanations
- README-like information
- Marketing text
- Technology stack details
- Backend implementation details
