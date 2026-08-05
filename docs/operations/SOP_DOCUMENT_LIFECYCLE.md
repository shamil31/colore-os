# SOP: Document Lifecycle v1

**Status:** Integrated  
**Version:** v1.0  
**Owner:** Coloré OS  
**Sprint:** Lead Intelligence MVP  
**Created:** 2026-08-05

---

## Document Lifecycle Stages

Every document in Coloré OS follows the same lifecycle:

```
IDEA
  ↓
DESIGN
  ↓
REVIEW
  ↓
APPROVED
  ↓
INTEGRATED
```

---

## Stage 1: IDEA

**What:** Document is conceived but not yet written.

**Status Marker:** Not in repository; exists only in conversation or backlog.

**Ownership:** Anyone (Claude, ChatGPT, Shamil, team)

**Actions:**
- Identify need for new document
- Add to BACKLOG.md with description
- Discuss purpose and scope

**Exit Criteria:**
- Document purpose is clear
- Scope is defined
- Owner (Claude for design) is assigned

**Next Stage:** DESIGN

---

## Stage 2: DESIGN

**What:** Document is written/designed by Claude.

**Status Marker:** Draft exists in conversation, scratchpad, or branch; not yet in main Git.

**Ownership:** Claude (designer) + Owner feedback loop

**Actions:**
- Claude creates first draft
- Claude iterates based on feedback
- May request clarification from ChatGPT/Shamil
- Document reflects approved business logic (no invention)

**Rules:**
- Do not invent missing details
- If information is missing, mark as TODO
- Do not create final content without approval
- Preserve exact meaning from approved source

**Exit Criteria:**
- Draft is complete and consistent
- All TODO sections marked clearly
- Claude is satisfied with quality
- Ready for external review

**Next Stage:** REVIEW

---

## Stage 3: REVIEW

**What:** ChatGPT and Shamil review document for accuracy and completeness.

**Status Marker:** Draft is reviewed; feedback is collected.

**Ownership:** ChatGPT (architecture) + Shamil (business) + Claude (implementer)

**Reviewers' Focus:**
- **ChatGPT:** Is the architecture sound? Are constraints respected? Is terminology correct?
- **Shamil:** Is the business logic correct? Does it match our strategy? Are there gaps?
- **Claude:** Can this be improved? Are there ambiguities?

**Feedback Types:**
- ✅ Approved (no changes needed)
- 🔄 Revise (needs specific changes)
- ❌ Reject (needs fundamental rework)
- ❓ Clarify (needs business decision)

**Process:**
1. Document is shared with reviewers
2. Reviewers provide feedback (async)
3. Claude addresses feedback
4. If major rework needed → return to DESIGN
5. If minor tweaks → update and resubmit

**Exit Criteria:**
- No blocking comments remain
- All reviewers have given thumbs-up or clear revision path
- Ready for approval

**Next Stage:** APPROVED

---

## Stage 4: APPROVED

**What:** Shamil approves the document for integration into Git.

**Status Marker:** Document has final approval; ready to be committed.

**Ownership:** Shamil (decision authority)

**Decision:**
- ✅ Approved for Integration
- ❌ Not Approved (return to DESIGN/REVIEW)

**Approval Criteria:**
- Document is accurate and complete
- Represents approved business logic
- Follows project standards
- Is ready for real use

**Exit Criteria:**
- Shamil has explicitly approved
- Document can be moved to Git
- Can be added to INDEX.md

**Next Stage:** INTEGRATED

---

## Stage 5: INTEGRATED

**What:** Document is committed to Git as source of truth.

**Status Marker:** Document is in `/root/colore-os/` with commit in history.

**Ownership:** Claude (integration executor)

**Actions:**
- Create file in correct directory (per architecture)
- Add metadata header (Status, Version, Owner)
- Update docs/INDEX.md with entry
- Update PROJECT_CONSTITUTION.md if applicable
- Create commit with message: `docs(section): add document name`

**File Metadata (required in every integrated document):**
```markdown
**Status:** Integrated  
**Version:** v1.0  
**Owner:** Coloré OS  
**Sprint:** [Sprint Name]  
**Created:** YYYY-MM-DD
```

**Commit Message Format:**
```
docs(section): add [document name]

Brief description of what this document is for.

Related: [any related documents or issues]
```

**Exit Criteria:**
- File exists in repository
- Commit is in Git history
- Document is listed in INDEX.md
- No broken links
- Document is now source of truth

---

## Lifecycle Summary Table

| Stage | Status | Owner | Input | Output | Duration |
|-------|--------|-------|-------|--------|----------|
| IDEA | Not in Repo | Anyone | Need + Purpose | Backlog Entry | Async |
| DESIGN | Draft | Claude | Requirements | Draft Document | 1-2 days |
| REVIEW | In Review | ChatGPT + Shamil | Draft | Feedback/Approval | 1-2 days |
| APPROVED | Approved | Shamil | Review Feedback | Approval | Hours |
| INTEGRATED | In Git | Claude | Approval | Committed Document | Hours |

---

## Key Rules

### Rule 1: No Bypassing Stages
Documents cannot skip stages. Every document goes through all five.

**Exception:** If a document is part of an existing approved category (like SOP documents), streamlined review is possible. Still requires all stages.

### Rule 2: No Modifications After Integration
Once integrated (in Git), changes go through revision cycle:
```
INTEGRATED (current)
  ↓
DESIGN (v1.1)
  ↓
REVIEW (v1.1)
  ↓
APPROVED (v1.1)
  ↓
INTEGRATED (v1.1)
```

Minor corrections (typos, links) can be fast-tracked if reviewer approves immediately.

### Rule 3: Document Status is in the Document
Every integrated document must include status header:
```markdown
**Status:** Integrated  
**Version:** v1.0  
```

### Rule 4: INDEX.md is the Authority
If a document exists in Git but is not in INDEX.md, it is not officially integrated.

### Rule 5: Trace Back to Approval
Every integrated document's commit message must link to approval decision (via chat, DECISIONS.md, or similar).

---

## Special Cases

### Hotfix Documents
If a critical bug or emergency requires a document:
1. Minimal DESIGN phase (approval text only)
2. Fast REVIEW (1-2 hours)
3. Shamil approval
4. Integration

Mark as "v0.1 - Hotfix" in metadata.

### Rapid Iteration Documents
If a document needs frequent updates (e.g., campaign checklists):
1. Design full structure
2. Review core logic
3. Approve with "review cycle" agreement
4. Integrate
5. Subsequent updates follow abbreviated cycle

### Deprecated Documents
When document is no longer used:
1. Do not delete from Git (history matters)
2. Change status to "Deprecated"
3. Update INDEX.md with note: "Superseded by [new document]"
4. Commit with message: `docs(index): deprecate [document name]`

---

## Document Standards

### File Location
Place document in appropriate section:
- **Customer Intelligence:** `/docs/01_CUSTOMER_INTELLIGENCE/[type]/`
- **Execution/SOP:** `/docs/02_EXECUTION/`
- **Infrastructure:** `/docs/03_INFRASTRUCTURE/`
- **Scenarios:** `/docs/04_SCENARIOS/`
- **Research:** `/docs/05_RESEARCH/`
- **Governance:** `/docs/06_GOVERNANCE/`

### File Naming
- Use SNAKE_CASE
- Descriptive names (e.g., `LEAD_STATE_MACHINE.md` not `lsm.md`)
- Add version only if multiple majors exist (e.g., `SOP_TASK_LIFECYCLE_v1.md`)

### File Metadata (Required)
```markdown
**Status:** [Integrated | Draft | Deprecated]  
**Version:** v1.0  
**Owner:** Coloré OS  
**Sprint:** [Sprint Name]  
**Created:** 2026-MM-DD
```

### File Content
- Start with title and metadata
- Overview/purpose section
- Main content
- Open questions (if any)
- Related documents
- TODO sections (if incomplete)

### Links
- Use relative paths: `[Link Text](../../path/to/file.md)`
- Test all links before integration
- Update broken links in INDEX.md

---

## Responsibilities

### Claude (Designer)
- Creates draft based on requirements
- Does not invent missing information
- Marks unclear sections as TODO
- Iterates based on feedback
- Commits final approved document
- Maintains INDEX.md

### ChatGPT (Architecture Reviewer)
- Verifies architectural correctness
- Checks terminology consistency
- Ensures constraints are respected
- Provides feedback within 24 hours

### Shamil (Business Reviewer)
- Verifies business logic correctness
- Ensures alignment with strategy
- Makes final approval decision
- Can request major revisions

### Git (Source of Truth)
- Records all approved documents
- Maintains history and version tracking
- Is the authority for what is integrated

---

## When Document Lifecycle is Needed

**YES, use full lifecycle for:**
- ✅ Architecture decisions
- ✅ SOP and procedures
- ✅ Business intelligence models
- ✅ Conversion/decision logic
- ✅ Integration guides
- ✅ System specifications

**NO, use fast track for:**
- ❌ Internal notes or scratch work
- ❌ Chat history
- ❌ One-off analysis
- ❌ Temporary research

---

## Open Questions

1. **Review SLA:** Should we set maximum review time (e.g., 48 hours)? What if reviewer is unavailable?

2. **Concurrent Reviews:** Should ChatGPT and Shamil review simultaneously or sequentially?

3. **Conflict Resolution:** If ChatGPT and Shamil disagree on changes, who decides?

4. **Emergency Documents:** What's the minimum viable process for critical hotfixes?

5. **Document Versioning:** When does v0.1 become v1.0? Is it based on first integration or first real use?

6. **Related Documents:** Should we track document dependencies (this document requires that one)?

7. **Archival Policy:** Documents older than 1 year, unused → should we deprecate or archive?

---

## Version History

| Version | Date | Change |
|---------|------|--------|
| v1.0 | 2026-08-05 | Initial SOP created for Sprint #1 |
