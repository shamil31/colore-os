# SOP: Task Lifecycle v1

**Status:** Integrated  
**Version:** v1.0  
**Owner:** Coloré OS  
**Sprint:** Lead Intelligence MVP  
**Created:** 2026-08-05

---

## Task Lifecycle Stages

Every task (feature, fix, research, implementation) in Coloré OS follows this lifecycle:

```
IDEA
  ↓
RESEARCH
  ↓
DESIGN
  ↓
REVIEW
  ↓
BUILD
  ↓
VERIFY
  ↓
DEPLOY
  ↓
LEARN
```

---

## Stage 1: IDEA

**What:** Task is identified as needed but not yet scoped.

**Status Marker:** In BACKLOG.md or in conversation; not assigned.

**Ownership:** Anyone (CEO, CTO, Claude, team)

**Actions:**
- Identify the task or problem
- Write one-sentence description
- Add to BACKLOG.md
- Optionally: add reasoning or context

**Definition of Done:**
- Task appears in BACKLOG.md
- Purpose is clear in one sentence
- No active work has started

**Next Stage:** RESEARCH

---

## Stage 2: RESEARCH

**What:** Claude investigates if the task is feasible and what information is needed.

**Status Marker:** Task has research notes; owner is Claude.

**Ownership:** Claude (researcher)

**Actions:**
- Read relevant documentation
- Understand current system state
- Identify information gaps
- Assess feasibility
- Estimate scope (hours/days)
- List dependencies or blockers

**Research Output:**
- What do we know?
- What don't we know?
- Is this task feasible?
- What would block it?
- Rough time estimate

**Definition of Done:**
- Claude has investigated thoroughly
- Information gaps are documented
- Feasibility assessment is clear
- No unknowns remain (or are clearly noted)

**Can Exit With:**
- ✅ Ready for Design (feasible)
- ❌ Not Ready (blocked, missing info, should be deferred)
- ❓ Needs Decision (unclear business priority)

**Next Stage:** DESIGN (if feasible)

---

## Stage 3: DESIGN

**What:** Claude creates detailed plan for how to build/complete the task.

**Status Marker:** Task has design document or plan; owner is Claude.

**Ownership:** Claude (designer)

**Actions:**
- Create detailed step-by-step plan
- Identify files that will change
- Define success criteria
- List edge cases or tricky parts
- Estimate accurate time
- Create test plan (if applicable)

**Design Output:**
- How will we build this?
- What's the execution sequence?
- What could go wrong?
- How do we test it?
- What's our rollback plan?

**Design Standards:**
- Do not invent business logic (only propose technical approach)
- Ask for business clarification if needed
- Identify all dependencies upfront
- Flag any architectural concerns

**Definition of Done:**
- Claude is confident in the approach
- Step-by-step plan is documented
- All blockers are identified
- Ready for CTO/business review

**Next Stage:** REVIEW

---

## Stage 4: REVIEW

**What:** ChatGPT and Shamil review design for correctness and alignment.

**Status Marker:** Design has been reviewed; feedback is collected.

**Ownership:** ChatGPT (architecture) + Shamil (business)

**Reviewers' Focus:**
- **ChatGPT (CTO):** Is the design sound? Does it respect architecture? Will it scale?
- **Shamil (CEO):** Does this solve the business problem? Does it advance the sprint goal? Is scope right?

**Feedback Types:**
- ✅ Approved (proceed to build)
- 🔄 Revise Design (make changes and resubmit)
- ❌ Reject (return to research or defer to backlog)
- ❓ Question (needs clarification before approval)

**Review Process:**
1. Claude presents design
2. ChatGPT and Shamil provide feedback
3. Claude addresses feedback
4. If major rework needed → back to DESIGN
5. If minor adjustments → update and resubmit

**Definition of Done:**
- No blocking comments remain
- Both reviewers have signed off
- Design is approved for implementation

**Next Stage:** BUILD

---

## Stage 5: BUILD

**What:** Claude implements the task according to approved design.

**Status Marker:** Task is in development; code is being written.

**Ownership:** Claude (implementer)

**Actions:**
- Follow approved design step-by-step
- Write code/create content as planned
- Test locally before committing
- Create commits with clear messages
- Do not deviate from approved design (escalate if needed)
- Do not optimize prematurely (finish before improve)

**Build Standards:**
- One logical change per commit
- Meaningful commit messages
- No debug code left behind
- Follow existing code style
- Type hints on all functions (Python)
- Tests pass (if tests exist)

**Definition of Done:**
- Implementation matches approved design
- All steps from design are complete
- Code compiles/runs without errors
- Ready for verification

**Next Stage:** VERIFY

---

## Stage 6: VERIFY

**What:** Shamil and ChatGPT verify that build matches design and works correctly.

**Status Marker:** Build is complete; verification is in progress.

**Ownership:** Shamil (business verification) + ChatGPT (technical verification)

**Verification Actions:**
- Test that it works as designed
- Check edge cases and error handling
- Verify no regressions in existing features
- Confirm it advances sprint goal
- Review code quality and clarity

**Verification Checklist:**
- [ ] Does it work? (no errors, expected behavior)
- [ ] Does it match design? (no unplanned deviations)
- [ ] Are there regressions? (did we break anything?)
- [ ] Does it advance the sprint goal?
- [ ] Is the code quality acceptable?
- [ ] Are there documentation updates needed?

**Verification Outcome:**
- ✅ Approved for Deployment (no issues found)
- 🔄 Needs Fixes (bugs or deviations found; return to BUILD)
- ❌ Reject (does not meet criteria; decide: fix or revert)

**Definition of Done:**
- All verification checks pass
- No blocking issues remain
- Ready for deployment/release

**Next Stage:** DEPLOY

---

## Stage 7: DEPLOY

**What:** Shamil deploys the task to production/live environment.

**Status Marker:** Code is live in production.

**Ownership:** Shamil (deployment authority)

**Actions:**
- Merge to main branch (if not already)
- Deploy to production environment
- Verify it's live and working
- Monitor for immediate issues
- Notify team that task is live

**Deployment Standards:**
- Never deploy without VERIFY sign-off
- Have rollback plan ready
- Monitor for 30 minutes after deployment
- Document any deployment notes

**Definition of Done:**
- Code is live in production
- System is working as expected
- Team is notified

**Next Stage:** LEARN

---

## Stage 8: LEARN

**What:** Team reflects on what worked, what didn't, and how to improve.

**Status Marker:** Task is complete; learning is captured.

**Ownership:** Whole team (CEO, CTO, Claude)

**Learning Actions:**
- Was the task completed on time?
- Did it advance the sprint goal?
- What went smoothly?
- What was harder than expected?
- What would we do differently next time?
- Did we invent new patterns worth documenting?

**Learning Outputs:**
- Lessons document (if significant learnings)
- SOP update (if this task revealed a gap)
- Playbook addition (if this is a recurring problem)
- Backlog updates (if new ideas emerged)

**Learn Questions:**
1. Did this task advance revenue? By how much (measurable)?
2. Did design predict implementation time accurately?
3. Did verification catch real bugs or was it checking unnecessary things?
4. Should this task become a template/playbook for future similar work?

**Definition of Done:**
- Learning is captured
- Team has discussed outcomes
- Insights are documented

**Task Lifecycle Complete** ✅

---

## Lifecycle Summary Table

| Stage | Status | Owner | Input | Output | Duration |
|-------|--------|-------|-------|--------|----------|
| IDEA | Backlog | Anyone | Need | Backlog Entry | Async |
| RESEARCH | Research | Claude | Task Desc | Feasibility Report | 1-2 days |
| DESIGN | Design | Claude | Requirements | Design Plan | 1-3 days |
| REVIEW | Review | ChatGPT + Shamil | Design | Approval or Feedback | 1-2 days |
| BUILD | In Progress | Claude | Approved Design | Working Code | 1-7 days |
| VERIFY | Verification | Shamil + ChatGPT | Implementation | Verification Report | 1 day |
| DEPLOY | Deployed | Shamil | Verified Code | Live System | Hours |
| LEARN | Learning | Team | Results | Lessons Document | 1 day |

---

## Key Rules

### Rule 1: No Skipping Stages
Every task goes through all stages. No exceptions.

**Example:** Cannot skip RESEARCH and go straight to BUILD. Cannot skip VERIFY.

### Rule 2: Clear Ownership at Each Stage
Each stage has a clear owner who is responsible for completion:
- RESEARCH → Claude
- DESIGN → Claude
- REVIEW → ChatGPT + Shamil
- BUILD → Claude
- VERIFY → Shamil + ChatGPT
- DEPLOY → Shamil
- LEARN → Team

### Rule 3: Staging Is Sequential, Not Parallel
Task moves through stages linearly. Previous stage must be complete before starting next.

**Exception:** REVIEW feedback can trigger changes to DESIGN, which loops back.

### Rule 4: Exit Criteria Must Be Met
Cannot move to next stage until current stage's "Definition of Done" is 100% complete.

### Rule 5: Document the Loop
If feedback requires returning to an earlier stage:
```
DESIGN (v1)
  → Feedback → DESIGN (v1.1)
  → Review (v1.1)
  → Approved → BUILD
```

---

## Special Cases

### Hotfix Tasks
For emergency fixes:
1. Minimal RESEARCH (1 hour max)
2. Fast DESIGN (document the fix)
3. Accelerated REVIEW (1 hour)
4. BUILD immediately
5. VERIFY same day
6. DEPLOY immediately
7. LEARN afterwards (capture the issue + fix for future)

Mark as "HOTFIX - [task name]" in task history.

### Recurring Tasks
If a task is similar to previous ones:
1. Reference the previous task's LEARN output
2. RESEARCH can be shorter (apply previous learnings)
3. DESIGN can be template-based
4. BUILD follows known pattern
5. VERIFY checklist from similar task

### Exploratory Research Tasks
Some tasks are pure research (no build):
1. IDEA → RESEARCH → DESIGN (research plan) → REVIEW → LEARN
2. No BUILD or DEPLOY stages
3. Output is document, not code
4. LEARN is where findings are published

---

## Failure Modes & Recovery

### What If RESEARCH Shows Task is Impossible?
1. Document why (blockers, dependencies)
2. Add to BACKLOG for future (when blocker is resolved)
3. LEARN: What should we have known earlier?

### What If BUILD Takes Longer Than Estimated?
1. Continue building (don't cut corners)
2. Update task estimate
3. VERIFY proceeds normally
4. LEARN: Why was estimate wrong? Improve next time.

### What If VERIFY Finds Major Bugs?
1. Do not skip to DEPLOY
2. Loop back to BUILD → fix bugs
3. VERIFY again
4. Only then → DEPLOY

### What If DEPLOY Finds Issues?
1. Have rollback ready
2. Rollback to previous version
3. Loop back to BUILD (fix issues)
4. Re-VERIFY
5. Re-DEPLOY

---

## Preventing Common Mistakes

### Mistake: Skipping RESEARCH
**Why bad:** Build approach is wrong; wastes time.
**Prevention:** Enforce RESEARCH stage; don't allow BUILD without cleared feasibility.

### Mistake: Designing Without Business Input
**Why bad:** Build something that doesn't advance sprint goal.
**Prevention:** REVIEW stage must include Shamil (business authority).

### Mistake: Deploying Without VERIFY
**Why bad:** Bugs reach production; users affected.
**Prevention:** Shamil owns DEPLOY; cannot deploy without verification sign-off.

### Mistake: Skipping LEARN
**Why bad:** Same mistakes repeat; no improvement over time.
**Prevention:** Make LEARN mandatory; capture even if learnings are small.

---

## Task Status Tracking

**Current Status Indicators:**
- 🔷 IDEA (in backlog)
- 🔵 RESEARCH (in progress)
- 🟦 DESIGN (in progress)
- 🟨 REVIEW (waiting for feedback)
- 🟩 BUILD (in progress)
- 🟧 VERIFY (in progress)
- ⚫ DEPLOYED (live)
- ⭐ LEARN (learning captured)

---

## Related Processes

**Document Lifecycle** — How documents move from IDEA → INTEGRATED
**Sprint Planning** — How tasks are selected for a sprint
**Code Review** — How code quality is maintained during BUILD

---

## Open Questions

1. **Timeboxing:** Should we set maximum time per stage? (e.g., max 2 days for RESEARCH?)

2. **Parallel Tasks:** Can Claude work on multiple tasks simultaneously? Any limit?

3. **Feedback Loops:** If REVIEW feedback is minor, can we shortcut back to BUILD?

4. **Task Scaling:** Are large tasks broken into smaller sub-tasks? How small?

5. **Blocked Tasks:** If a task is blocked waiting for another task, what do we do?

6. **Definition of Success:** Who sets the success criteria? Claude? Shamil? Together?

7. **Regression Testing:** During VERIFY, what's the scope of regression testing?

---

## Version History

| Version | Date | Change |
|---------|------|--------|
| v1.0 | 2026-08-05 | Initial SOP created for Sprint #1 |
