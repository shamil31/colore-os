# NEXT: Start Here

**Read this first every session.**

---

## CURRENT GOAL

Return the first paying client.

---

## CURRENT SPRINT

**FIRST REVENUE** (Active)

KPI: One real client booking initiated by Coloré OS

Status: Campaign infrastructure complete. Waiting for launch decision.

---

## CURRENT STATUS

✅ Campaign pipeline fully implemented (9 of 10 stages)
✅ Long Absence segment selected as first target
✅ Conversation-first strategy approved (no hard sell)
✅ Integrilla export working (campaign.xlsx created)
✅ Conversation Playbook complete (7 rules, 7 scenarios)
✅ Business Intelligence Model documented
✅ Altegio API audit complete (read-only status confirmed)
⏳ Waiting for first campaign launch decision

---

## NEXT ACTION

Launch first Long Absence campaign.

**Scope:** 10 clients (long absence segment, all with valid phone)

**Approach:**
1. Run: `python -m app.scripts.export_integrilla`
2. Review campaign.xlsx output
3. Import to Integrilla manually
4. Execute conversation playbook
5. Track metrics (replies → dialogs → bookings)

**Do NOT skip any step.**

---

## METRICS TO TRACK

- Replies: Clients who respond to first message
- Dialogs: Clients who have 2+ exchanges
- Bookings: Clients who book appointment in Altegio

---

## CURRENT RULES

**Revenue First.** Every decision optimized for getting bookings, not code elegance.

**Finish Before Improve.** Complete the campaign launch. Do not refactor mid-flight.

**Ship Before Scale.** Get one booking. Then optimize.

**Talk Before Sell.** Listen to client. Acknowledge their reason. Then offer solution.

**30 Minute Rule.** Conversations should complete in max 5 messages over 24-48 hours.

**Task Boundary.** Do not work on items not in NEXT ACTION. Everything else goes to BACKLOG.

---

## DO NOT BUILD YET

❌ Recovery Engine v2 (deferred)
❌ AI Scoring improvements (deferred)
❌ Analytics Dashboard (deferred)
❌ Multi-tenant support (deferred)
❌ Automatic Integrilla API integration (deferred)
❌ Advanced Reporting (deferred)

**Why?** First we prove the model works with one client. Then we scale.

---

## SUCCESS DEFINITION

**One real client who was in the "Long Absence" segment:**
1. Responds to our message
2. Has a dialog (2+ exchanges)
3. Books an appointment in Altegio
4. Shows up for the appointment

**When this happens, FIRST REVENUE sprint is DONE.**

---

## IF YOU ARE BLOCKED

1. Check KNOWN_STATE.md for verified facts
2. Check PROJECT_STATE.md for current status
3. Check TODAY.md for daily focus
4. Check DECISIONS.md for active rules
5. Check CLAUDE.md Section XXIII (Escalation Path)

---

## SESSION CHECKPOINT

Before you start work, confirm:

- [ ] I read this NEXT.md file
- [ ] I understand the current goal: get one booking
- [ ] I know the next action: launch first campaign
- [ ] I will not work on anything in "DO NOT BUILD YET"
- [ ] I will track replies → dialogs → bookings

**Do not proceed until all checkboxes are TRUE.**

---

**Last Updated:** 2026-08-02  
**Next Update:** After first campaign launch
