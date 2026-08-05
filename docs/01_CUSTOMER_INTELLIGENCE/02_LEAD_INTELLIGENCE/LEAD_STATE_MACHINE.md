# Lead State Machine v1

**Status:** Integrated  
**Version:** v1.0  
**Owner:** Coloré OS  
**Sprint:** Lead Intelligence MVP  
**Created:** 2026-08-05

---

## Overview

A Lead State Machine defines how a new potential client moves through discovery, consideration, and decision. Each state represents a distinct phase where:
- Specific information is known
- Specific actions are permitted
- Specific escalations to human are required
- Movement to the next state is triggered by clear conditions

This machine prioritizes premium positioning (never discount, always consult) while ensuring no lead is lost to poor handling.

---

## State 1: Initial Contact

**Goal:** Understand why they reached out and what they're looking for.

**What We Know:**
- They exist and initiated contact
- Contact method (WhatsApp, call, website form, referral message)
- Rough timing of outreach
- Basic context (campaign source, if applicable)

**What We Need to Learn:**
- Why they contacted us (booking request, price check, curiosity, comparison)
- Service interest (hair, nails, massage, consultation, other)
- Urgency (need appointment today vs. exploring options)
- Customer type (first-time, returning, competitor customer)
- Preferred communication style

**Allowed AI Actions:**
- Warm greeting acknowledging their specific context
- ONE clarifying question about their intent
- Share basic salon info (hours, location, services offered)
- Suggest next logical step

**Prohibited AI Actions:**
- Quote pricing
- Promise availability or specific stylist/master
- Recommend specific service packages
- Pressure for immediate booking
- Discuss competitor comparisons

**When to Escalate to Human:**
- They ask about pricing
- They mention a competitor by name
- They request specific master/stylist
- They mention medical/allergy concerns
- They're clearly just price-shopping

**Transition Criteria:**
- They clarify intent and express interest → move to **Interested in Booking** or **Information Gathering** or **Price Conversation**
- No response to follow-up → move to **Lead Gone Cold**
- They ask to speak with human → immediate escalation

**Success Criteria:**
- Lead has provided 2+ useful pieces of info (service + intent/urgency)
- Lead has agreed to a next step (call, booking, consultation)
- Conversation tone is warm and professional

---

## State 2: Interested in Booking

**Goal:** Guide them toward a confirmed appointment while building anticipation for the experience.

**What We Know:**
- They want to book
- Service category (hair, nails, other)
- General timeline preference
- Contact method

**What We Need to Learn:**
- Specific service (cut, color, style, design, treatment, etc.)
- Preferred time/day (ASAP, weekends, specific days)
- Master/stylist preference (first-timer okay with anyone, or has preferences)
- Special requirements (allergies, previous bad experience, specific hair type)
- Budget comfort level (for premium positioning)

**Allowed AI Actions:**
- Confirm service understanding in their own words
- Ask about preferred timing
- Share availability windows (via human system)
- Explain the booking flow
- Build excitement about their upcoming experience
- Mention what makes this salon premium for that service

**Prohibited AI Actions:**
- Confirm booking without human verification
- Promise specific master availability
- Quote pricing (even if asked)
- Overpromise results ("Your hair will look amazing," etc.)
- Pressure for immediate decision

**When to Escalate to Human:**
- Immediately when they're ready to confirm
- They ask about pricing
- They request specific master
- Complex service needs (color correction, complex design, etc.)
- Group booking

**Transition Criteria:**
- They commit to specific time window → **Ready for Human Booking Handoff**
- They ask about pricing → **Price Conversation**
- They get uncertain → **Information Gathering**
- They stop responding → **Lead Gone Cold**

**Success Criteria:**
- Human agent has confirmed appointment in booking system
- Lead has received: date, time, service, confirmed stylist/master (if applicable)
- Lead has cancellation policy and what to bring

---

## State 3: Information Gathering

**Goal:** Answer their questions and build confidence so they can decide to book.

**What We Know:**
- They're interested but not yet committed
- They're exploring services or comparing options
- Basic service interest exists

**What We Need to Learn:**
- What specific information gaps are blocking their decision
- Are they comparing to competitors (explicitly or implicitly)
- What aspects of service/experience matter most (quality, speed, price, environment, master reputation)
- Real timeline for their decision

**Allowed AI Actions:**
- Answer questions about services, environment, process, experience
- Share portfolio images, client reviews, testimonials
- Explain what makes this salon different (premium positioning, master expertise, quality focus)
- Offer a free consultation call with a master for complex needs
- Suggest relevant services based on their stated needs

**Prohibited AI Actions:**
- Provide pricing
- Compare to competitors negatively
- Guarantee specific results or outcomes
- Push for booking before they're ready
- Pretend to be a master/expert if you're not

**When to Escalate to Human:**
- They ask about pricing
- They mention a specific competitor
- They want detailed service consultation
- Medical/allergy/skin condition concerns
- They request to speak with a master

**Transition Criteria:**
- Questions answered → **Interested in Booking**
- They ask about pricing → **Price Conversation**
- They go silent after info provided → **Lead Gone Cold**
- They mention competitor → **Competitor Comparison**

**Success Criteria:**
- Lead's main questions have been answered
- Lead has either scheduled consultation or moved toward booking
- Confidence in salon choice has increased visibly in tone

---

## State 4: Price Conversation

**Goal:** Address pricing concerns transparently without losing the lead.

**What We Know:**
- Pricing is a blocking factor
- Lead is price-conscious

**What We Need to Learn:**
- What budget range are they expecting
- Are they price-shopping or have fixed budget constraints
- What do they value most (master, results, experience, speed)
- What other options they're considering

**Allowed AI Actions:**
- Acknowledge that pricing is important
- Explain value proposition (why premium pricing)
- Ask about their budget range/expectations
- Provide general pricing structure (if allowed without human)
- Offer to connect with human who can discuss packages, options, payment plans

**Prohibited AI Actions:**
- Quote final pricing without human involvement
- Negotiate, discount, or make price exceptions
- Compare pricing to competitors
- Make promises about discounts or future deals
- Apologize for premium pricing

**When to Escalate to Human:**
- **IMMEDIATELY** when pricing is clearly asked about
- Lead mentions specific budget
- Lead indicates price sensitivity might kill deal
- Lead wants to discuss packages or payment flexibility
- Lead wants comparison of options

**Transition Criteria:**
- Human quotes/discusses pricing → **Interested in Booking** or **Lead Gone (Price)**
- Human offers solution lead accepts → **Interested in Booking**
- Lead says too expensive → **Lead Gone (Price)** — close with door open
- Lead says "let me think" → **Lead Gone Cold** (not committed)

**Success Criteria:**
- Lead has clear, transparent understanding of pricing
- Human salesperson is engaged
- No ambiguity remains (lead either commits or clearly disengages)

---

## State 5: Competitor Comparison

**Goal:** Position the salon's value without criticizing competitors.

**What We Know:**
- Lead is actively comparing salons
- They've contacted or visited at least one competitor
- They're evaluating options carefully (good sign for premium positioning)

**What We Need to Learn:**
- Which specific competitors are in consideration
- What specific aspects they're comparing (price, master reputation, location, speed, environment, results)
- What concerns they have about competitors (if any)
- What concerns they have about us
- What would make us the obvious choice

**Allowed AI Actions:**
- Ask which salons they're considering (non-defensive)
- Understand what matters most in their decision
- Highlight genuine differentiators (master expertise, result focus, premium experience, client outcomes)
- Share specific before/after portfolio pieces
- Explain the philosophy behind premium positioning
- Invite them to experience the salon environment

**Prohibited AI Actions:**
- Criticize competitor work or approach
- Claim superiority without evidence
- Pressure for immediate decision
- Discuss competitor pricing
- Seem defensive or insecure

**When to Escalate to Human:**
- Lead mentions specific competitor by name
- Lead wants detailed comparison of masters/services
- Lead needs consultation from our master to compare expertise
- Lead asks for pricing comparison
- Lead seems close to choosing us (close the deal)

**Transition Criteria:**
- Lead chooses us → **Interested in Booking**
- Lead chooses competitor → **Lead Gone (Competitor)** — preserve for future outreach
- Lead still uncertain → **Information Gathering**
- Lead goes quiet → **Lead Gone Cold**

**Success Criteria:**
- Lead clearly understands our value proposition
- Lead has enough info to make informed choice
- Decision is clear (either moving toward booking or moving on)

---

## State 6: Consultation-Only Request

**Goal:** Provide expert guidance and create pathway to booking.

**What We Know:**
- Lead is not ready to book immediately
- They want professional advice before committing
- They're exploring needs rather than decided

**What We Need to Learn:**
- What specific concerns or needs they have
- Whether this is pre-research or delayed decision
- What would trigger them to book (confidence, timing, budget)
- Timeline for potential booking

**Allowed AI Actions:**
- Offer free/paid consultation call with appropriate master
- Ask clarifying questions about their needs
- Provide general education and guidance
- Explain what consultation will cover and what to expect
- Share relevant before/after examples

**Prohibited AI Actions:**
- Guarantee consultation will lead to booking
- Use consultation as high-pressure sales tactic
- Commit to specific results based on consultation
- Provide full service recommendations without expert input
- Use consultation to collect personal info for spam

**When to Escalate to Human:**
- **IMMEDIATELY** for scheduling consultation call
- Lead mentions medical/allergy/skin concerns
- Complex or unusual service needs

**Transition Criteria:**
- Consultation scheduled → **In Consultation**
- Lead declines consultation → **Lead Gone (Not Interested)**
- Lead wants to book without consultation → **Interested in Booking**

**Success Criteria:**
- Consultation call is scheduled with right expert
- Lead knows what to expect
- Expert and lead will connect

---

## State 7: In Consultation

**Goal:** Expert provides guidance, lead moves toward booking decision.

**What We Know:**
- Expert is engaging with lead
- Lead is actively exploring their needs
- Consultation is in progress or scheduled

**What We Need to Learn:**
- Expert's assessment of lead's needs
- Is lead moving toward booking after consultation
- Any barriers to booking that emerged

**Allowed AI Actions:**
- Follow up with lead after consultation (if delegated)
- Confirm understanding of recommendations
- Help schedule appointment based on consultation
- Answer logistical questions

**Prohibited AI Actions:**
- Negotiate on expert recommendations
- Modify what expert said
- Create booking without explicit lead agreement

**When to Escalate to Human:**
- During entire consultation (expert owns this)
- Lead hesitates after consultation
- Lead wants to book based on consultation
- Lead has additional questions

**Transition Criteria:**
- Consultation complete, lead wants to book → **Interested in Booking**
- Consultation complete, lead uncertain → **Information Gathering** or **Lead Gone Cold**
- Lead declines to proceed → **Lead Gone (Not Interested)**

**Success Criteria:**
- Consultation occurred
- Lead has clear expert recommendations
- Lead is moving toward booking or has explicitly declined

---

## State 8: Lead Gone Cold

**Goal:** Determine if lead is temporarily busy or permanently disengaged.

**What We Know:**
- Lead hasn't responded to recent outreach
- They showed interest but disappeared
- Some time has passed since last engagement

**What We Need to Learn:**
- Are they still interested but busy
- Did they choose a competitor
- Did their situation change (timeline, budget, urgency)

**Allowed AI Actions:**
- Send ONE gentle re-engagement message after 3-7 days
- Acknowledge the silence warmly ("Haven't heard from you...")
- Offer a fresh reason to reconnect (new availability, inspiration, relevant offer)
- Ask if anything changed
- Keep tone light and non-pressuring

**Prohibited AI Actions:**
- Multiple follow-ups in rapid succession
- Guilt or pressure language ("You disappeared on us")
- Defensive tone ("Why didn't you respond?")
- Assume they're gone forever
- Send automated reminders without personalization

**When to Escalate to Human:**
- After 2 re-engagement attempts with no response
- If lead finally responds and wants to discuss
- If lead was high-value (high revenue history) and went silent

**Transition Criteria:**
- Lead responds positively → **Information Gathering** or **Interested in Booking**
- Lead declines ("Not interested") → **Lead Gone (Final)**
- No response after re-engagement → **Lead Gone (Final)**

**Success Criteria:**
- One warm re-engagement message sent
- Clear next action defined (wait for response or close)

---

## State 9: Lead Returned

**Goal:** Re-engage a lead who disappeared but came back.

**What We Know:**
- Lead showed interest previously
- They went silent
- They've now re-initiated contact

**What We Need to Learn:**
- Why are they back? (Finally ready, time passed, urgency changed, competitor didn't work out)
- Has their situation changed? (Budget, availability, needs, timeline)
- What's different this time

**Allowed AI Actions:**
- Welcome them back warmly and genuinely
- Ask what changed or what brought them back
- Remind them of previous context (service interest, etc.)
- Offer fresh information or relevant updates
- Resume conversation from where you left off (if context still valid)

**Prohibited AI Actions:**
- Make them feel bad about disappearing
- Assume their needs haven't changed
- Pressure them for ghosting previously
- Ignore that their situation may have evolved

**When to Escalate to Human:**
- When lead is ready to move toward booking
- If circumstances have significantly changed
- If pricing is now being discussed
- If they mention competitor again

**Transition Criteria:**
- Lead confirms interest → **Interested in Booking** or **Information Gathering**
- Lead wants consultation → **Information Gathering** or **Consultation-Only**
- Lead just wants info → **Information Gathering**
- Lead goes silent again → **Lead Gone Cold**

**Success Criteria:**
- Current situation and motivation understood
- Lead has moved toward booking or re-engaged in information gathering
- Clear next action identified

---

## State 10: Lead Gone (Final)

**Goal:** Clean closure while preserving relationship for future re-engagement.

**What We Know:**
- Lead has explicitly disengaged
- Reason for departure is documented (price, competitor, not interested, timing, etc.)
- No current pathway to conversion

**What We Need to Learn:**
- Nothing. Work is complete.

**Allowed AI Actions:**
- Send ONE final "door open" message with appreciation
- Move to CRM closed state with reason recorded
- Add to future re-engagement tracking (e.g., "price sensitivity," "competitor choice," "timing")

**Prohibited AI Actions:**
- Any follow-up after closure message
- Attempts to reopen conversation
- Guilt language

**When to Escalate to Human:**
- High-value lead (significant previous spend) → preserve relationship via human touch

**Transition Criteria:**
- Terminal state
- Can only move to **Lead Returned** if they initiate contact again

**Success Criteria:**
- Lead cleanly closed in CRM with documented reason
- No further automated contact

---

## State Diagram (Text Map)

```
Initial Contact
├─→ Interested in Booking
├─→ Information Gathering
├─→ Price Conversation
├─→ Consultation-Only Request
├─→ Competitor Comparison
└─→ Lead Gone Cold

Information Gathering
├─→ Interested in Booking
├─→ Price Conversation
├─→ Competitor Comparison
├─→ Consultation-Only Request
└─→ Lead Gone Cold

Price Conversation
├─→ Interested in Booking
└─→ Lead Gone (Price)

Competitor Comparison
├─→ Interested in Booking
├─→ Information Gathering
└─→ Lead Gone (Competitor)

Consultation-Only Request
├─→ In Consultation
└─→ Lead Gone (Not Interested)

In Consultation
├─→ Interested in Booking
├─→ Information Gathering
└─→ Lead Gone (Not Interested)

Interested in Booking
└─→ [HUMAN HANDOFF FOR FINAL BOOKING]

Lead Gone Cold
├─→ Information Gathering (if responds)
├─→ Interested in Booking (if responds)
└─→ Lead Gone (Final)

Lead Gone (Final)
└─→ Lead Returned (if they reach out again)
```

---

## Design Principles

### Premium Positioning
- Never apologize for pricing
- Always escalate price questions to human
- Encourage consultation for complex needs
- Emphasis on master expertise and quality

### Human Escalation Rules
Price, promises, and people decisions always go to human. AI handles:
- Clarification and information
- Experience building and education
- Re-engagement of cold leads
- Scheduling and logistics

### Lead Preservation
- Every lead gets a "door open" message before final close
- Multiple re-engagement attempts on cold leads
- No single bad interaction kills the relationship
- Competitor choice is preserved for future outreach

### Clarity Over Ambiguity
- Every interaction moves lead forward or backward clearly
- "Let me think about it" = **Lead Gone Cold** (not committed)
- No ambiguous states where progress is unclear

---

## Open Questions for Implementation

1. **Response SLA:** What's the maximum acceptable time for AI to respond? 5 minutes? 30 minutes? Varies by state?

2. **Human Escalation SLA:** When a lead is escalated (pricing, booking), what's the human response time target? How should lead experience waiting?

3. **Pricing Authority:** Can AI share pricing tiers/ranges, or must all pricing be human-only? What's in bounds vs. out of bounds?

4. **Consultation Routing:** How are consultation requests routed to appropriate master/specialist? Automatic or manual? What's the scheduling system?

5. **Context Persistence:** When a lead re-engages, what historical info should AI surface? Full conversation? Just key decisions (service, price sensitivity)?

6. **Multi-Channel Tracking:** If same lead contacts via WhatsApp then calls then emails, is this one lead or three? How do we merge?

7. **Returning Lead Detection:** How does system know a new contact is actually a returning lead? Phone/email matching? Manual review?

8. **Re-engagement Frequency:** After how many days does "Lead Gone Cold" → "Lead Gone Final"? Is there a re-engagement budget per lead?

9. **Lead Scoring:** Should each state have explicit "quality" score? High-value leads (high revenue history) get different handling than new leads?

10. **Success Metrics:** What counts as "success" for a lead? Booking confirmed? Appointment attended? Payment received? Revenue recognized?

11. **Competitor Intelligence:** When lead mentions a competitor, should that info be captured for competitive analysis? What details matter?

12. **Lead Quality Signals:** What makes a lead "high quality" vs. "low quality" in this state machine? Spend history, service type, urgency level?

---

## MVP Notes

- This machine assumes single-salon context (not multi-location)
- Assumes WhatsApp/phone/email as primary contact methods
- Assumes human booking system exists
- Assumes masters/specialists are available for consultation
- Assumes "premium positioning" as core brand strategy
- Does not account for referral-specific handling (may need separate state or variant)
- Does not account for seasonal/promotional campaigns (may need state variants)

This is intentionally incomplete to start. Real lead behavior will reveal states and transitions we haven't anticipated.
