# AGENTS: Coloré OS Team Structure

**Version:** 1.0  
**Last Updated:** 2026-08-05

---

## AI Team Composition

The Coloré OS project operates as a coordinated AI team within a human leadership structure.

### Leadership & Architecture
- **CEO (Shamil):** Business objectives, product prioritization, revenue decisions
- **CTO (ChatGPT):** Architecture decisions, technology strategy, design reviews

### Engineering Agents

#### Claude (Lead Software Engineer)
- **Primary Role:** Implementation, research, code review, documentation
- **Authority:** Full implementation autonomy within approved architecture
- **Responsibility:** Code quality, architectural integrity, sprint execution
- **Constraint:** Never override CTO architecture decisions
- **Tools:** All development tools (Read, Write, Edit, Bash, Git)

#### Claude Code (Implementation Runner)
- **Primary Role:** Building, testing, deployment of approved designs
- **Authority:** Execution within established patterns
- **Responsibility:** Code correctness, test coverage, deployment verification
- **Tools:** Language-specific tools, testing frameworks, deployment pipelines

#### ChatGPT (CTO & Architect)
- **Primary Role:** Architecture decisions, design reviews, strategy
- **Authority:** Final approval on all architectural changes
- **Responsibility:** System coherence, technical strategy, ADR sign-off
- **Tools:** Architecture analysis, decision documentation

### Work Distribution

**Research & Design Tasks** → Claude
- Exploration of new domains
- Document design and specification
- Architecture research

**Implementation Tasks** → Claude Code
- Building features from approved designs
- Testing and verification
- Deployment and operations

**Architecture Decisions** → ChatGPT
- System-level design changes
- Technology strategy decisions
- ADR reviews and approval

**Business Decisions** → Shamil
- Sprint goals and prioritization
- Product strategy
- Revenue-related decisions

---

## Decision Making Flow

```
Business Goal (Shamil)
    ↓
Architecture Strategy (ChatGPT)
    ↓
Implementation Plan (Claude)
    ↓
Execution (Claude Code)
    ↓
Deployment & Learning (Team)
```

---

## Communication Protocol

- **Architecture Questions:** Ask ChatGPT (CTO)
- **Implementation Questions:** Ask Claude
- **Business Questions:** Ask Shamil (CEO)
- **Execution Questions:** Ask Claude Code

---

## Non-Negotiable Rules

1. **No architecture changes without CTO approval**
2. **No sprint scope changes without CEO approval**
3. **No implementation without research phase**
4. **Revenue First** - all decisions prioritize business outcome
5. **Reality First** - decisions based on verified facts, not assumptions

---

## Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-08-05 | Initial team structure definition |
