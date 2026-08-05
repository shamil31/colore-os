# Lead Intelligence Model v1

**Status:** Integrated  
**Version:** v1.0  
**Owner:** Coloré OS  
**Sprint:** Lead Intelligence MVP  
**Created:** 2026-08-05

---

## Core Principle

Coloré OS does not decide based on message text.

It builds a model of the person: their intent, emotional state, readiness to decide, and capacity to trust.

From this model, it selects the next best action.

---

## Decision Pipeline

```
Message
    ↓
Intent
    ↓
Emotional State
    ↓
Trust Level (v1.1 backlog)
    ↓
Decision Readiness
    ↓
Next Best Action
```

Each stage adds information that previous stages don't capture.

---

## Stage 1: Message

**Input:** Raw lead communication (text, voice, form data)

**Output:** Structured message data (context, timing, channel, content)

**Process:**
- Parse contact method (WhatsApp, call, form, referral)
- Extract explicit content (service interest, urgency, budget hints)
- Note timing and frequency
- Preserve full text for review

**Limitations:**
- Text alone is insufficient
- Tone and intent are not the same as meaning
- People don't always say what they mean

---

## Stage 2: Intent

**Input:** Message + context

**Output:** Classified intent (booking, information, comparison, consultation, price check, etc.)

**Signals Used:**
- Explicit keywords (book, appointment, price, sample, compare, etc.)
- Question types (how much, when available, who is best, etc.)
- Information requests (portfolio, process, reviews, etc.)
- Implicit intent (asking about timing → urgency signal)

**Immediate Determines:**
- **Why did they contact us?** (primary intent)
- **What action are they ready for?** (booking, information, consultation, escalation)

**Learns From:**
- Real lead responses to our actions
- Booking conversion rate by stated intent
- False positives (lead says "information" but meant "not interested")

**Human Override:**
- If AI detects intent but lead later clarifies differently → human verifies

---

## Stage 3: Emotional State

**Input:** Intent + message tone + engagement pattern

**Output:** Emotional state (curious, confident, hesitant, anxious, frustrated, excited, etc.)

**Signals Used:**
- Message tone and language choice
- Engagement speed (immediate vs. delayed)
- Number of clarifying questions (high = hesitant or thorough)
- Language complexity (formal vs. casual)
- Exclamation usage, punctuation patterns

**Examples:**
- "I want to book" (confident, ready to decide)
- "I've been thinking about my hair..." (reflective, considering)
- "Can you guarantee the color will hold?" (anxious about results)
- "Just checking your pricing" (pragmatic, comparison shopping)

**Immediate Determines:**
- **How ready are they emotionally?** (confident vs. hesitant)
- **What tone should we use?** (match or complement their state)

**Learns From:**
- Real emotional state vs. AI classification accuracy
- Emotional state → conversion likelihood
- Which responses improve emotional state

**Human Override:**
- If lead shows anxiety about medical/allergy concerns → always escalate regardless

---

## Stage 4: Trust Level

**Status:** v1.1 backlog (not implemented in v1.0)

**Reserved For:**
- Trust signals: have they heard of us before, referrals, reviews they've read
- Brand perception: premium positioning acceptance
- Confidence in us vs. competitors
- Safety signals (license, certifications, portfolio proof)

**Will Learn From:**
- Lead biography (first-time vs. returning)
- Referral source (direct vs. via friend)
- Explicit trust questions (who recommended you, why us, etc.)
- Implicit trust markers (immediacy of booking after introduction)

---

## Stage 5: Decision Readiness

**Input:** Intent + Emotional State + Trust Level (when available) + conversation history

**Output:** Decision readiness score (ready now, ready soon, needs more info, not ready, rejected)

> **⚠️ REVIEW NOTE:** The specific Decision Readiness Categories (Ready Now/Soon/Needs Info/Not Ready/Rejected) were formulated operationally beyond the approved model. See Architecture Review in next cycle.

**Categories:**

### Ready Now (High Decision Readiness)
- Clear intent to book
- Confident emotional state
- Has enough information
- Commits to specific time/action

**AI Action:** Escalate to human for booking confirmation

**Example:** "I want to book with Maria next Saturday"

### Ready Soon (Medium Decision Readiness)
- Interested in booking
- Slightly hesitant (needs one more signal)
- Has most information but minor concerns
- Will decide after consultation or small clarification

**AI Action:** Provide missing piece (consultation, specific info, address concern)

**Example:** "I'm interested but want to know about color correction cost"

### Needs More Info (Low Decision Readiness)
- Curious about services/salon
- No timeline commitment
- Multiple information gaps
- Comparing options

**AI Action:** Answer questions, provide education, build confidence

**Example:** "What services do you offer? How long do appointments take?"

### Not Ready (Very Low Decision Readiness)
- Interested but external constraint (timing, budget, logistics)
- Exploring but no urgency
- Will consider in future but not now

**AI Action:** Acknowledge, keep door open, add to future campaign

**Example:** "I'll be in town in 3 months, save my info"

### Rejected (No Decision Readiness)
- Explicitly not interested
- Price too high
- Chose competitor
- Not our target market

**AI Action:** Respectful close, document reason, preserve for future

**Example:** "I decided to try the salon near my work"

---

## Stage 6: Next Best Action

**Input:** All previous stages

**Output:** Recommended action (message template, escalation, waiting period, closure)

**Logic:**

| Decision Readiness | Emotional State | Intent | Action |
|-------------------|-----------------|--------|--------|
| Ready Now | Confident | Booking | Escalate to human for booking |
| Ready Soon | Slightly Hesitant | Info Seeking | Provide missing info + offer consultation |
| Needs Info | Curious | Comparison | Answer question + offer portfolio/info |
| Not Ready | Interested | Future | Acknowledge + mark for future campaign |
| Rejected | Frustrated/Decided | No | Professional close + preserve relationship |

**Message Selection:**
- TODO: Document message template library and selection criteria

**Escalation Criteria:**
- Price question → immediate escalation
- Specific master/stylist request → escalation
- Medical/allergy concern → immediate escalation
- Complex service need → escalation to expert
- Lead ready to book → escalation to booking system

**Re-engagement Strategy:**
- TODO: Document when to follow up, frequency, message approach

**Closure Strategy:**
- TODO: Document graceful lead closure and door-open messaging

---

## What Determines Immediately (v1.0)

In this sprint, AI determines:
- **Intent** — why they contacted us
- **Emotional State** — are they confident or hesitant
- **Decision Readiness** — are they ready to book, or do they need more info
- **Next Best Action** — what should we do

---

## What Learns from Real Dialogs (v1.0+)

Over time, as we see real lead responses:
- Intent classification accuracy (did we guess right?)
- Which emotional states convert to bookings
- Which action types work best by emotional state
- Which information gaps block decisions most often
- Optimal timing for follow-ups

Learning happens in:
- **Learning Loop** (dedicated component)
- **Real campaign data** (replies, dialogs, bookings)
- **Human feedback** (did AI classification match reality?)

---

## What Always Stays with Humans (v1.0+)

These decisions are never AI-only:
- **Pricing decisions** — always human
- **Master/stylist assignment** — human assigns (AI can suggest)
- **Medical/safety concerns** — always human
- **Lead rejection** — human can override AI
- **Campaign strategy** — human decides (AI recommends)
- **Learning validation** — human verifies if pattern is real

---

## Relationship to Lead State Machine and Next Best Action Engine

**Lead Intelligence Model** = How do we understand this person?
- High-level reasoning about intent, emotion, readiness
- Guides which state they enter and what action to take

**Lead State Machine** = What happens in each state?
- Low-level operational model
- Defines allowed/prohibited actions per state
- Defines transition criteria
- Defines success criteria

**Next Best Action Engine** = What specific action should we take?
- Decision layer between understanding (Intelligence Model) and communication (Conversation Engine)
- Uses Lead Intelligence Model outputs (Intent, Emotion, Readiness)
- Uses Lead State Machine outputs (current state)
- Adds Trust and Business Context to make action decision
- Outputs: one specific action type from fixed catalog

**Integrated Architecture:**
```
Raw Message
    ↓ (Intelligence Model)
Understand Intent + Emotion + Readiness + Historical Trust
    ↓
Select Starting State (or next state)
    ↓ (State Machine)
Define state context and constraints
    ↓ (Next Best Action Engine)
Evaluate all inputs + Business Context + Confidence
    ↓
Select one action type from catalog + Reason
    ↓ (Conversation Engine)
Transform action into one message, respecting Tone of Brand
    ↓
Deliver message to client
```

**For decision logic details, see:** [NEXT_BEST_ACTION_ENGINE.md](NEXT_BEST_ACTION_ENGINE.md)

**For message formulation details, see:** [CONVERSATION_ENGINE.md](CONVERSATION_ENGINE.md)

---

## Limitations & Constraints

### v1.0 Known Limitations
- Cannot detect trust level yet (v1.1)
- Cannot distinguish between similar intents without clarifying questions
- May misclassify emotional state based on tone patterns (false positives/negatives)
- No memory of lead across multiple contacts (will fix in v1.1)
- Cannot assess lead quality (revenue potential) yet

### Inherent Constraints
- AI should never decide pricing
- AI should never promise results
- AI should escalate safety concerns (medical, mental health, etc.)
- AI should not override clear human feedback
- AI's understanding improves with human feedback

### When to Escalate Instead of Model
- Lead seems distressed or anxious
- Lead has medical/allergy/accessibility needs
- Lead directly asks for human
- AI confidence is low (multiple contradictory signals)
- Rare situation outside training data

---

## Measuring Intelligence Quality

How do we know if the model is working?

### Quantitative Metrics
- **Intent Accuracy:** Did AI classification match actual lead intent?
- **Decision Readiness Accuracy:** Did we predict booking conversion correctly?
- **Action Effectiveness:** Did recommended action move lead closer to booking?
- **Conversation Length:** Optimal is 3-5 exchanges to decision
- **Escalation Rate:** % of leads escalated to human (should be low for routine, high for critical)

### Qualitative Feedback
- Human reviewers: "Did AI understand this lead correctly?"
- Lead satisfaction: "Did the AI help or hinder?"
- Campaign results: "Did higher-quality leads correlate with higher conversion?"

---

## Evolution Roadmap

### v1.0 (Current)
- Intent classification
- Emotional state detection
- Decision readiness scoring
- Action selection

### v1.1 (Next)
- Add Trust Level stage
- Add lead persistence across channels
- Improve emotional state accuracy
- Add lead quality scoring

### v1.2 (Future)
- Multi-intent detection (leads with mixed signals)
- Personalization by lead type
- Predictive follow-up timing
- Competitor intelligence integration

### v2.0 (Long-term)
- Dynamic message generation (instead of templates)
- Proactive lead re-engagement prediction
- Cross-channel context awareness
- Integration with Active Client Intelligence

---

## Open Questions

1. **Emotional State Signals:** What are the reliable signals for each emotional state? How do we avoid false positives?

2. **Decision Readiness Thresholds:** What's the exact threshold for "Ready Now" vs. "Ready Soon"? Is it binary or continuous?

3. **Learning Velocity:** How many real lead examples do we need to confidently improve the model? 10? 100? 1000?

4. **False Negative Cost:** What's the cost if we misclassify "Ready Now" as "Needs Info"? How do we prevent that?

5. **Multi-Intent Handling:** What if a lead has multiple intents (want to book AND compare prices)? How do we prioritize?

6. **Emotional State Drift:** If a lead's emotional state changes during conversation, how does system adapt?

7. **Intent Confidence:** Should AI share its confidence level with humans? ("I'm 73% confident this is a booking intent")

8. **Lead Quality Scoring:** When we add quality scoring, how does it affect action selection? (High-quality lead gets escalated faster?)

---

## Relationship to Other Components

**Lead State Machine** → Executes decisions from this model  
**Decision Core** → Uses this model to rank leads and select campaigns  
**Learning Loop** → Validates if this model's predictions matched reality  
**Message Templates** → Implements the actions recommended by this model  
**Altegio Integration** → Stores lead data this model uses for classification  

---

## Notes

This model is intentionally designed to improve as we get real data.

No version claims perfection. Each version acknowledges its limitations and roadmap for improvement.

The goal is not to replace human judgment but to **accelerate human decision-making** by understanding leads deeply before humans interact with them.
