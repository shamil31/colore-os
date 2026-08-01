# Reactivation Engine Spec

## 1. Business Goal

Launch the first commercial module that turns inactive or paused clients into new paid bookings as quickly as possible.

Primary objective:

- increase near-term salon revenue using existing client demand before expanding to broader lifecycle programs.

## 2. Required Data

Minimum business data required for a reactivation decision:

- client identity
- contact channel
- previous interaction context
- current lead or client status
- relevant service interest
- available booking slots
- response outcome status (booked, postponed, declined, no response)

Business definitions that must be confirmed by Product Owner:

- inactivity threshold (days): TODO
- reactivation segment rules: TODO
- message frequency limits: TODO
- offer policy by segment: TODO

## 3. Minimal Altegio Data Needed

For MVP, only the smallest practical Altegio data surface is required:

- client lookup (to identify the correct client record)
- service list (to anchor relevant next-step offers)
- schedule availability (to convert interest into an appointment quickly)
- booking creation (to turn reactivation into revenue)

Optional for later phases (not required for first MVP release):

- deep visit history
- loyalty balances
- transaction history
- marketing permissions automation

## 4. User Flow

1. Business selects a reactivation target segment for the day.
2. Client receives one concise reactivation message tied to prior context.
3. Client response branches:
   - ready to book
   - interested but needs options
   - not now
   - no response
4. Interested clients are moved directly to service/time selection.
5. Booking is created when client confirms.
6. Outcome is recorded for reporting and next follow-up timing.

## 5. Automation Flow

1. Retrieve selected segment and eligible clients.
2. Pull minimal context for each client.
3. Generate and send one reactivation message per client.
4. Route replies:
   - booking-ready -> schedule + create booking
   - uncertain -> service clarification + next step
   - postpone -> set later follow-up status
   - decline/no response -> mark and exit current cycle
5. Record conversion outcomes in a simple operational log.

## 6. Success Metrics

Core revenue metrics for MVP:

- reactivation-to-booking conversion rate
- number of bookings created from reactivation
- revenue from reactivated bookings
- response rate to reactivation outreach

Operational metrics:

- time from first reactivation message to booking
- no-response share
- postponed share

Baseline targets for first launch wave: TODO

## 7. MVP Scope

Included in first release:

- one reactivation campaign type
- one daily segment selection process
- one-message reactivation flow
- direct handoff to booking path
- booking outcome tracking
- minimal dashboard/reporting view (counts and conversion)

Commercial intent:

- prove fast, measurable revenue lift from existing client base.

## 8. Out Of Scope

Not included in first MVP:

- multi-step nurture journeys
- advanced personalization models
- loyalty logic
- VIP-specific retention programs
- birthday campaigns
- multichannel optimization experiments
- predictive scoring models
- complex BI analytics

## 9. Estimated Implementation Order

Revenue-first sequence:

1. Define business reactivation rules and segment criteria.
2. Enable minimal Altegio data access: client, services, schedule, booking.
3. Launch single-message reactivation flow.
4. Connect flow to booking completion.
5. Track bookings and revenue outcomes.
6. Run first operational cycle and review conversion.
7. Tighten messaging and timing based on results.

Release decision gate:

- continue to next retention modules only after Reactivation MVP demonstrates measurable booking and revenue impact.