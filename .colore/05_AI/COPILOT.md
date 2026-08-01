# Colore Runtime - Copilot

## UAOP Reference
- Primary operating standard: `.colore/09_UAOP.md`.
- This file defines Copilot-specific role scope only.

## Current Source
- Prompt file exists at .colore/PROMPTS/copilot.md.

## Role Scope
- Implementation
- Code editing
- Repository navigation
- Documentation updates

## Required Baseline
- Follow UAOP boot sequence and workflow.
- Use Runtime as the primary project memory.
- When rules overlap, UAOP is authoritative.

## Cost Optimization
- Prefer local execution when possible.
- Avoid unnecessary Cloud Agent sessions.
- Keep prompts concise and task-focused.
- Read Runtime before asking questions already answered by project documentation.
- Minimize repeated repository scans.

## TODO
- Define Copilot start-of-day protocol.
- Define Copilot end-of-day protocol.
- Define required verification commands and reporting format.
