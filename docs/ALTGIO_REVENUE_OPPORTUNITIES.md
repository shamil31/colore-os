# Altgio Revenue Opportunities

## Scope

This document is based only on evidence currently present in this repository.

Key finding: there is no explicit Altgio or Altegio integration implemented or documented by name in the repository.

The repository currently contains:

- implemented internal backend endpoints for local client data;
- documented CRM and booking workflow requirements in the scenario files;
- planned tool calls that imply future access to scheduling and CRM entities.

Where the repository does not verify an Altgio entity or endpoint, this document marks it as `Not evidenced in repo`.

## Current Altgio Integration Status

- Explicit Altgio endpoints implemented: None verified in the repository.
- Explicit Altgio SDK, API client, webhook handler, or auth flow: None verified in the repository.
- Internal backend endpoints implemented today: Yes.
- Planned CRM and booking access in product and scenario documentation: Yes.

## Every Available Altgio Entity Already Accessible Or Planned

### Implemented Today In The Repository

| Entity | Status | Evidence |
|---|---|---|
| Clients | Implemented internally in local backend | `backend/app/main.py`, `backend/app/api/clients.py`, `backend/app/models/client.py` |

### Planned In Repository Documentation

| Entity | Status | Evidence |
|---|---|---|
| Clients | Planned CRM lookup flow | `docs/SCENARIOS/SCENARIO_001_BOOK_APPOINTMENT.md`, `docs/SCENARIOS/SCENARIO_012_FIRST_CONTACT.md` |
| Appointments / Bookings | Planned CRM booking flow | `docs/SCENARIOS/SCENARIO_001_BOOK_APPOINTMENT.md`, `docs/SCENARIOS/SCENARIO_002_RESCHEDULE_APPOINTMENT.md`, `docs/SCENARIOS/SCENARIO_003_CANCEL_APPOINTMENT.md` |
| Services | Planned service lookup | `docs/SCENARIOS/SCENARIO_001_BOOK_APPOINTMENT.md`, `docs/SCENARIOS/SCENARIO_006_SERVICE_SELECTION.md` |
| Staff / Masters | Planned staff lookup | `docs/SCENARIOS/SCENARIO_001_BOOK_APPOINTMENT.md`, `docs/SCENARIOS/SCENARIO_011_MASTER_SELECTION.md` |
| Schedule / Availability | Planned schedule lookup | `docs/SCENARIOS/SCENARIO_001_BOOK_APPOINTMENT.md`, `docs/SCENARIOS/SCENARIO_006_SERVICE_SELECTION.md` |
| Promotions | Planned promotion-linked service access | `docs/SCENARIOS/SCENARIO_010_PROMOTION_INQUIRY.md` |
| Lead Qualification Status | Planned CRM lead-state recording | `docs/SCENARIOS/SCENARIO_007_LEAD_QUALIFICATION.md` |
| Human Handoff Status | Planned CRM handoff-state recording | `docs/SCENARIOS/SCENARIO_009_HUMAN_HANDOFF.md` |
| Communication History / CRM Context | Planned context retrieval and reuse | `docs/PRODUCT_VISION.md`, `docs/INTENT_MAP.md`, multiple scenario files |
| Address | Planned intent area, no tool call defined | `docs/INTENT_MAP.md` |
| Working Hours | Planned intent area, no tool call defined | `docs/INTENT_MAP.md` |
| Gift Certificates | Planned intent area, no tool call defined | `docs/INTENT_MAP.md` |

### Not Evidenced In The Repository

| Entity | Status | Evidence |
|---|---|---|
| Loyalty | Not evidenced in repo | No Altgio or loyalty-specific repository evidence found |
| Transactions | Not evidenced in repo | No transaction-specific repository evidence found |
| Visits | Not evidenced in repo | No visit-history entity explicitly defined |
| Birthdays | Not evidenced in repo | No birthday-specific repository evidence found |
| Tags | Not evidenced in repo | No tag-specific repository evidence found |
| Marketing Permissions | Not evidenced in repo | No consent or marketing-permission entity explicitly defined |

## Every Endpoint Already Implemented

These are the backend endpoints currently implemented in the repository.

No Altgio-specific API endpoint is implemented.

| Method | Path | Purpose | Evidence |
|---|---|---|---|
| GET | `/` | Service status payload with project name, version, and runtime status | `backend/app/main.py` |
| GET | `/db` | PostgreSQL connectivity check | `backend/app/main.py`, `backend/app/db/database.py` |
| POST | `/clients` | Create client in local database | `backend/app/api/clients.py` |
| GET | `/clients` | List clients from local database | `backend/app/api/clients.py` |
| GET | `/clients/{client_id}` | Get one client from local database | `backend/app/api/clients.py` |
| PUT | `/clients/{client_id}` | Update one client in local database | `backend/app/api/clients.py` |
| DELETE | `/clients/{client_id}` | Delete one client from local database | `backend/app/api/clients.py` |

## Documented Planned Integration Operations

These are not implemented backend endpoints in the repository.

They are documented scenario-level tool calls that imply future CRM or booking integration access.

| Operation | Purpose | Evidence |
|---|---|---|
| `find_client` | Find client in CRM context | `docs/SCENARIOS/SCENARIO_001_BOOK_APPOINTMENT.md` and related scenario files |
| `get_services` | Retrieve service information | `docs/SCENARIOS/SCENARIO_001_BOOK_APPOINTMENT.md` and related scenario files |
| `get_schedule` | Retrieve availability / schedule | `docs/SCENARIOS/SCENARIO_001_BOOK_APPOINTMENT.md` and related scenario files |
| `get_masters` | Retrieve staff / master information | `docs/SCENARIOS/SCENARIO_001_BOOK_APPOINTMENT.md` and related scenario files |
| `create_booking` | Create appointment / booking | `docs/SCENARIOS/SCENARIO_001_BOOK_APPOINTMENT.md` and related scenario files |
| `find_booking` | Retrieve existing appointment / booking | `docs/SCENARIOS/SCENARIO_002_RESCHEDULE_APPOINTMENT.md`, `docs/SCENARIOS/SCENARIO_003_CANCEL_APPOINTMENT.md` |
| `update_booking` | Update existing appointment / booking | `docs/SCENARIOS/SCENARIO_002_RESCHEDULE_APPOINTMENT.md` |
| `cancel_booking` | Cancel existing appointment / booking | `docs/SCENARIOS/SCENARIO_003_CANCEL_APPOINTMENT.md` |
| `send_confirmation` | Send customer confirmation or handoff notice | multiple scenario files |

## Business Data That Can Be Retrieved

### 1. Clients

- Repository status: Implemented internally and planned for CRM lookup.
- Evidence: `backend/app/api/clients.py`, `docs/SCENARIOS/SCENARIO_001_BOOK_APPOINTMENT.md`.
- Business value: foundational identity, contact, and repeat-customer context.
- Revenue opportunity: higher conversion from inquiry to booking and lower client drop-off caused by repeated questions.
- Automation opportunity: identity lookup, deduplication, personalized replies, faster repeat booking.
- Difficulty: Low.

### 2. Appointments

- Repository status: Planned in scenario documentation only.
- Evidence: `docs/SCENARIOS/SCENARIO_001_BOOK_APPOINTMENT.md`, `docs/SCENARIOS/SCENARIO_002_RESCHEDULE_APPOINTMENT.md`, `docs/SCENARIOS/SCENARIO_003_CANCEL_APPOINTMENT.md`.
- Business value: direct control of booking conversion, rebooking, and cancellation recovery.
- Revenue opportunity: highest direct revenue lever because appointment creation and rescheduling affect filled chair time immediately.
- Automation opportunity: automatic booking, reschedule rescue, cancellation recovery, confirmation workflows.
- Difficulty: Medium.

### 3. Services

- Repository status: Planned in scenario documentation only.
- Evidence: `docs/SCENARIOS/SCENARIO_001_BOOK_APPOINTMENT.md`, `docs/SCENARIOS/SCENARIO_005_PRICE_INQUIRY.md`, `docs/SCENARIOS/SCENARIO_006_SERVICE_SELECTION.md`.
- Business value: accurate service matching and price explanation.
- Revenue opportunity: improves upsell, cross-sell, and conversion on high-intent questions.
- Automation opportunity: service recommendation, price quoting, service comparison, promotion matching.
- Difficulty: Low.

### 4. Staff

- Repository status: Planned in scenario documentation only.
- Evidence: `docs/SCENARIOS/SCENARIO_001_BOOK_APPOINTMENT.md`, `docs/SCENARIOS/SCENARIO_011_MASTER_SELECTION.md`.
- Business value: matching customer demand to the right performer increases booking quality and close rate.
- Revenue opportunity: better master selection increases conversion and supports premium-staff upsell.
- Automation opportunity: staff matching by service, availability, and preference.
- Difficulty: Low.

### 5. Loyalty

- Repository status: Not evidenced in repo.
- Evidence: no loyalty-specific implementation or planning evidence found.
- Business value: repeat retention and discount control.
- Revenue opportunity: retention and repeat-visit frequency.
- Automation opportunity: points reminders, benefit prompts, retention campaigns.
- Difficulty: High.

### 6. Transactions

- Repository status: Not evidenced in repo.
- Evidence: no transaction-specific implementation or planning evidence found.
- Business value: revenue attribution and customer value analysis.
- Revenue opportunity: precise upsell targeting and owner reporting.
- Automation opportunity: payment-linked segmentation and offer targeting.
- Difficulty: High.

### 7. Visits

- Repository status: Not evidenced in repo.
- Evidence: no visit-history entity explicitly defined in repository code or docs.
- Business value: treatment history and reactivation timing.
- Revenue opportunity: repeat-visit prompts and churn rescue.
- Automation opportunity: visit-based follow-up sequences and replenishment reminders.
- Difficulty: Medium.

### 8. Birthdays

- Repository status: Not evidenced in repo.
- Evidence: no birthday-specific implementation or planning evidence found.
- Business value: high-response retention campaigns.
- Revenue opportunity: birthday-triggered offers and return visits.
- Automation opportunity: automated birthday messages and limited-time offer flows.
- Difficulty: Medium.

### 9. Tags

- Repository status: Not evidenced in repo.
- Evidence: no tag-specific implementation or planning evidence found.
- Business value: segmentation for service preference, value tier, and campaign fit.
- Revenue opportunity: better targeting for upsell and win-back campaigns.
- Automation opportunity: behavior-based segmentation and routing.
- Difficulty: Medium.

### 10. Marketing Permissions

- Repository status: Not evidenced in repo.
- Evidence: no consent or marketing-permission entity explicitly defined in repository code or docs.
- Business value: compliant outbound communication.
- Revenue opportunity: safe campaign expansion across channels.
- Automation opportunity: channel-specific consent filtering and campaign eligibility.
- Difficulty: Medium.

### 11. Schedule / Availability

- Repository status: Planned in scenario documentation only.
- Evidence: `docs/SCENARIOS/SCENARIO_001_BOOK_APPOINTMENT.md`, `docs/SCENARIOS/SCENARIO_006_SERVICE_SELECTION.md`.
- Business value: real-time slot control is required for fast conversion.
- Revenue opportunity: faster booking close rate and better utilization of open time.
- Automation opportunity: slot suggestion, fallback times, gap filling.
- Difficulty: Low.

### 12. Promotions

- Repository status: Planned in scenario documentation only.
- Evidence: `docs/SCENARIOS/SCENARIO_010_PROMOTION_INQUIRY.md`.
- Business value: converting price-sensitive demand without manual admin involvement.
- Revenue opportunity: promotional conversion and campaign monetization.
- Automation opportunity: promotion eligibility checking and offer-guided booking.
- Difficulty: Medium.

### 13. CRM Context / Communication History

- Repository status: Planned in product and scenario documentation only.
- Evidence: `docs/PRODUCT_VISION.md`, `docs/INTENT_MAP.md`, multiple scenario files referencing CRM and history.
- Business value: prevents repetitive questioning and improves service quality.
- Revenue opportunity: higher conversion through continuity and better retention through context-aware follow-up.
- Automation opportunity: contextual replies, next-best action prompts, handoff compression.
- Difficulty: Medium.

### 14. Lead Qualification Status

- Repository status: Planned in scenario documentation only.
- Evidence: `docs/SCENARIOS/SCENARIO_007_LEAD_QUALIFICATION.md`.
- Business value: separates hot leads from low-intent traffic.
- Revenue opportunity: faster sales follow-up on the highest-value demand.
- Automation opportunity: lead scoring, route-to-booking, follow-up cadence.
- Difficulty: Medium.

### 15. Human Handoff Status

- Repository status: Planned in scenario documentation only.
- Evidence: `docs/SCENARIOS/SCENARIO_009_HUMAN_HANDOFF.md`.
- Business value: reduces lost revenue when automation cannot safely complete the request.
- Revenue opportunity: preserves revenue that would otherwise be lost during escalation gaps.
- Automation opportunity: escalation packaging, notification, and SLA tracking.
- Difficulty: Medium.

### 16. Gift Certificates

- Repository status: Intent exists, but no retrieval tool or backend implementation is defined.
- Evidence: `docs/INTENT_MAP.md`.
- Business value: prepaid revenue and acquisition of new visitors.
- Revenue opportunity: immediate cash collection and gifting-driven new client acquisition.
- Automation opportunity: certificate Q&A, balance or validity lookup if later integrated.
- Difficulty: Medium.

### 17. Address And Working Hours

- Repository status: Intent exists, but no retrieval tool or backend implementation is defined.
- Evidence: `docs/INTENT_MAP.md`.
- Business value: supports top-of-funnel conversion from first-contact questions.
- Revenue opportunity: prevents loss of warm leads on simple operational questions.
- Automation opportunity: instant answers without staff involvement.
- Difficulty: Low.

## Opportunity Ranking By Revenue Impact x Implementation Speed

Scoring in this section is an analytical prioritization, not a repository fact.

Scale used:

- Revenue Impact: High = 3, Medium = 2, Low = 1
- Implementation Speed: High = 3, Medium = 2, Low = 1
- Score = Revenue Impact x Implementation Speed

| Rank | Opportunity | Revenue Impact | Implementation Speed | Score | Why It Ranks Here |
|---|---|---:|---:|---:|---|
| 1 | Schedule / Availability | 3 | 3 | 9 | Directly affects booking conversion and is already a documented planned lookup across multiple scenarios. |
| 2 | Services | 3 | 3 | 9 | Supports price questions, service selection, and promotion matching with broad scenario coverage. |
| 3 | Clients | 3 | 3 | 9 | Already implemented internally and central to every automated workflow. |
| 4 | Appointments / Bookings | 3 | 2 | 6 | Highest direct revenue effect, but write operations are more complex than read-only lookups. |
| 5 | Staff / Masters | 2 | 3 | 6 | Strong effect on conversion and upsell with clear documented demand. |
| 6 | Promotions | 2 | 2 | 4 | Useful for price-sensitive conversion, but narrower than core booking flows. |
| 7 | CRM Context / Communication History | 2 | 2 | 4 | Improves close rate and customer experience across many flows. |
| 8 | Lead Qualification Status | 2 | 2 | 4 | Valuable for prioritizing sales effort, but secondary to direct booking. |
| 9 | Human Handoff Status | 2 | 2 | 4 | Protects revenue leakage in edge cases rather than creating primary demand. |
| 10 | Address And Working Hours | 2 | 2 | 4 | Simple information access that can rescue warm leads quickly. |
| 11 | Gift Certificates | 2 | 2 | 4 | Immediate cash potential, but the repo does not yet define retrieval flows. |
| 12 | Transactions | 3 | 1 | 3 | High analytics value, but no repository evidence of implementation or planning. |
| 13 | Visits | 2 | 1 | 2 | Retention value exists, but explicit visit data structures are not evidenced. |
| 14 | Birthdays | 2 | 1 | 2 | Good retention trigger, but not evidenced in current repository plans. |
| 15 | Tags | 2 | 1 | 2 | Segmentation value exists, but no repository evidence of tag structures. |
| 16 | Marketing Permissions | 2 | 1 | 2 | Important for compliance and campaigns, but not evidenced in current repository plans. |
| 17 | Loyalty | 2 | 1 | 2 | Retention value exists, but no loyalty structures or planning evidence are present. |

## Practical Conclusion

Based on the current repository, the fastest revenue-first path is not a new feature set but a verified CRM and booking integration layer around the entities already planned in the scenario system:

1. clients
2. services
3. schedule / availability
4. appointments / bookings
5. staff / masters

Everything beyond those areas is either documented at a broader intent level or not evidenced in the repository at all.