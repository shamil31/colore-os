# Coloré OS Runtime Bootstrap

## RUNTIME HEADER

This document is the Runtime Entry Contract.
Reading this document automatically starts a new development session.
The LLM MUST execute the Runtime Entry Procedure before answering anything else.

## RUNTIME ENTRY PROCEDURE

Immediately after reading this document, the LLM must:

1. Confirm runtime loaded.
2. Summarize the current project state.
3. Summarize the current architecture.
4. Summarize completed work.
5. Summarize the active sprint.
6. Summarize accepted ADR decisions.
7. List unresolved architectural questions.
8. Determine today’s first engineering task.
9. Recommend the logical continuation.
10. Wait for the user.

## COMMANDS

Open Day = Human alias for the same runtime entry behavior.

Close Day = Review today’s work, update the runtime snapshot, update sprint and architecture state, update unresolved questions, update the next engineering task, and generate the next bootstrap state.

## PROJECT SNAPSHOT

Where are we?
- The project is in the FIRST REVENUE sprint and is preparing for the first real revenue-oriented campaign execution path.

What has been completed?
- The runtime entry contract is now the authoritative bootstrap state.
- The runtime documentation has been aligned around a single entry model.
- The project’s role-based governance and model-independent structure are in place.

What are we designing now?
- The next design focus is the transition from runtime readiness to the first real revenue execution path.

What is blocked?
- The main blocker is the decision to proceed with the first live campaign step.

What decision is next?
- Decide whether the next task is launch execution or validation of the next engineering step.

## AUTHORITATIVE STATE

This file is the authoritative runtime state.
Other runtime documents may extend it.
None may contradict it.

## PROJECT PRINCIPLES

Single Source of Truth

One Document One Responsibility

Role-Based Governance

Model Independence

Contract First

## CURRENT ARCHITECTURE

Coloré OS operates as a revenue orchestration layer above existing business systems. Its architecture is governed by a runtime contract, role-based governance, and a master state layer that preserves the current sprint, active decisions, and execution focus. Business flows are organized around revenue outcomes, while integration boundaries remain explicit so that existing operational platforms stay authoritative. The architecture is designed for disciplined execution and state continuity rather than implementation detail.

## SESSION MEMORY

The previous session completed the runtime-entry refactor, aligned the operating documents around a single bootstrap entry point, and preserved the project’s role-based, model-independent operating structure.

## TEST MODE

Expected user action:
- @GitHub покажи .colore/bootstrap.md из репозитория shamil31/colore-os

Expected LLM behavior:
- Automatically execute the Runtime Entry Procedure.

## DO NOT INCLUDE

- Long explanations
- README-like information
- Marketing text
- Technology stack details
- Backend implementation details

END OF RUNTIME CONTRACT

If you are reading this document:
Execute the Runtime Entry Procedure immediately.
Do not ask how to start.
Do not ask whether Open Day should begin.
Runtime has already started.
