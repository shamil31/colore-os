# Campaign Generation Pipeline: Complete Flow

**Date:** 2026-08-02  
**Scope:** End-to-end campaign generation from Altegio data to Integrilla export  
**Status:** DOCUMENTED FROM REPOSITORY

---

## Pipeline Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CAMPAIGN GENERATION PIPELINE                         │
└─────────────────────────────────────────────────────────────────────────────┘

Stage 1: ALTEGIO DATA ACQUISITION
┌──────────────────────────┐
│ sync_altegio_clients.py  │ → RevenueClient table
│ import_altegio_visit_... │ → RevenueClientVisit table
└──────────────────────────┘
           ↓
Stage 2: REVENUE CALCULATIONS
┌──────────────────────────────────────────┐
│ RevenueClient.total_spent (aggregated)   │
│ RevenueClientVisit.amount (per visit)    │
└──────────────────────────────────────────┘
           ↓
Stage 3: SEGMENTATION
┌─────────────────────────────┐
│ RevenueSegmentationEngine   │ (revenue_intelligence.py)
│ classify() → segment        │ (regular/delayed/lost)
└─────────────────────────────┘
           ↓
Stage 4: PRIORITY SCORING
┌──────────────────────────────┐
│ _collect_priority_rows()     │ (generate_priority_report.py)
│ Delay Weight × Monetary ×    │
│ Frequency Weight × 100       │
└──────────────────────────────┘
           ↓
Stage 5: CAMPAIGN ELIGIBILITY
┌────────────────────────────────┐
│ _has_phone() check             │ (generate_campaign_report.py)
│ phone != "" AND phone != "N/A" │
└────────────────────────────────┘
           ↓
Stage 6: TEMPLATE ASSIGNMENT
┌─────────────────────────────────┐
│ _assign_segment()               │ (generate_campaign_report.py)
│ Routes to: WhatsApp/SMS/Phone   │
│ Templates: FIRST_VISIT_01, etc. │
└─────────────────────────────────┘
           ↓
Stage 7: DEDUPLICATION
┌──────────────────────────┐
│ seen_client_ids set()    │ (generate_campaign_report.py)
│ Keep first occurrence    │
└──────────────────────────┘
           ↓
Stage 8: CAMPAIGN REPORT
┌──────────────────────────────┐
│ _print_campaign_line()       │ (generate_campaign_report.py)
│ Console output: READY/HOLD   │
└──────────────────────────────┘
           ↓
Stage 9: INTEGRILLA EXPORT
┌────────────────────────────────┐
│ export_integrilla.py           │
│ Output: campaign.xlsx          │
│ Columns: phone, name, template │
└────────────────────────────────┘
           ↓
Stage 10: INTEGRILLA EXECUTION
┌──────────────────────────────┐
│ ❌ NOT IMPLEMENTED           │
│ Message delivery scheduled   │
│ in Integrilla system         │
└──────────────────────────────┘
```

---

## Stage-by-Stage Documentation

### STAGE 1: ALTEGIO DATA ACQUISITION

**Purpose:** Sync client master data and visit history from Altegio API

**Input:** 
- Altegio API (HTTP)
- Environment: ALTEGIO_BASE_URL, ALTEGIO_PARTNER_TOKEN, ALTEGIO_LOGIN, ALTEGIO_PASSWORD, ALTEGIO_COMPANY_ID

**Output:** 
- PostgreSQL: revenue_clients table
- PostgreSQL: revenue_client_visits table

**Python File:** 
- `backend/app/scripts/sync_altegio_clients.py` (clients)
- `backend/app/scripts/import_altegio_visit_history.py` (visits)

**Functions/Classes:**
- `sync_altegio_clients.main()` → calls `_upsert_revenue_client()`
- `import_altegio_visit_history.main()` → calls `_upsert_revenue_client_visit()`
- `AltegioDataClient.get_all_clients_raw()`
- `AltegioDataClient.get_all_client_records_raw()`

**Dependencies:**
- `app.integrations.altegio.AltegioAuthClient`
- `app.integrations.altegio.AltegioDataClient`
- `app.integrations.altegio.AltegioEndpoints`
- `app.integrations.altegio.AltegioHttpClient`
- SQLAlchemy ORM

**Data Parsing:**
- `_parse_datetime()` - handles ISO8601 and custom formats
- `_coerce_float()` - normalizes amount strings
- `_coerce_int()` - normalizes numeric strings
- `_pick_*()` - field extraction from raw API response

**Status:** ✅ ACTIVE (Data sync completed per KNOWN_STATE.md)

**Execution:** 
```bash
python -m app.scripts.sync_altegio_clients
python -m app.scripts.import_altegio_visit_history
```

---

### STAGE 2: REVENUE CALCULATIONS

**Purpose:** Aggregate revenue data per client

**Input:** 
- RevenueClient rows (from Stage 1)
- RevenueClientVisit rows (from Stage 1)

**Output:** 
- RevenueClient.total_spent (aggregate)
- RevenueClient.last_visit_date (calculated)
- RevenueClient.last_visit_at (duplicate field, mirrors last_visit_date)
- RevenueClient.visit_count (mirrors total_visits)

**Python File:** 
- `backend/app/models/revenue_client.py` (schema)
- `backend/app/models/revenue_client_visit.py` (schema)
- Data is pre-aggregated during import

**Functions/Classes:**
- `sync_altegio_clients._upsert_revenue_client()` - stores total_spent
- `import_altegio_visit_history._upsert_revenue_client_visit()` - stores amount per visit

**Dependencies:**
- SQLAlchemy ORM
- PostgreSQL database

**Schema Fields:**
- RevenueClient: total_spent (Float), total_visits (Integer)
- RevenueClientVisit: amount (Float), last_visit_date (DateTime)

**Status:** ✅ COMPLETE (Verified per KNOWN_STATE.md)

**Note:** Revenue values come directly from Altegio API response; no recalculation or business logic applied here.

---

### STAGE 3: SEGMENTATION

**Purpose:** Classify clients into lifecycle segments (regular/delayed/lost)

**Input:** 
- RevenueClient rows with: last_visit_at, visit_count, last_service_name
- Current date/time

**Output:** 
- SegmentLabel enum: "regular", "delayed", "lost", "unknown"
- Segment-specific thresholds from environment

**Python File:** 
- `backend/app/services/revenue_intelligence.py`

**Functions/Classes:**
- `class RevenueSegmentationEngine`
- `RevenueSegmentationEngine.classify(client, now)` → (segment, days_since_last_visit)
- `RevenueSegmentationEngine._resolve_rule()` - service-based threshold selection
- `RevenueSegmentationEngine._load_service_rules()` - reads JSON env var

**Dependencies:**
- Python standard library (json, datetime)
- Environment: REVENUE_DEFAULT_DELAYED_DAYS, REVENUE_DEFAULT_LOST_DAYS, REVENUE_SERVICE_RULES_JSON

**Segmentation Logic:**
```
If last_visit_at is None:
  segment = "lost"
Else:
  days_overdue = max(0, today - last_visit_at)
  if days_overdue < delayed_days:
    segment = "regular"
  elif days_overdue < lost_days:
    segment = "delayed"
  else:
    segment = "lost"
```

**Status:** ✅ ACTIVE (Used in priority ranking and campaign assignment)

**Thresholds:** 
- Default delayed: 45 days
- Default lost: 90 days
- Overridable per service via JSON config

---

### STAGE 4: PRIORITY SCORING

**Purpose:** Rank clients by revenue opportunity and reactivation likelihood

**Input:** 
- RevenueClient rows with: total_visits, total_revenue, total_spent, last_visit_date
- RevenueClientVisit rows with: amount, last_visit_date
- Segment classification from Stage 3

**Output:** 
- ClientPriorityRow with: priority_score (0-100+), delay_weight, monetary_weight, frequency_weight, recency_score

**Python File:** 
- `backend/app/scripts/generate_priority_report.py`

**Functions/Classes:**
- `_collect_priority_rows()` - main aggregation function
- `ClientPriorityRow` dataclass - output structure
- `_normalize(value, min, max)` - score normalization to 0-1
- `_average_interval_days(visits)` - calculates expected revisit window

**Dependencies:**
- SQLAlchemy ORM
- RevenueClient, RevenueClientVisit models
- Datetime calculations

**Scoring Formula:**
```
Monetary Score = normalize(total_revenue, min_revenue, max_revenue) * 100
Frequency Score = normalize(total_visits, min_visits, max_visits) * 100
Delay Weight = normalize(delay_days, min_delay, max_delay)

Priority Score = (Delay Weight × Monetary Weight × Frequency Weight) × 100
```

**Normalization:** 0-1 range per dimension, clamped to [0, 1]

**Status:** ✅ ACTIVE (Part of campaign report generation)

**Execution:** 
```bash
python -m app.scripts.generate_priority_report
```

---

### STAGE 5: CAMPAIGN ELIGIBILITY

**Purpose:** Filter clients who can receive campaigns (have contact method)

**Input:** 
- ClientPriorityRow from Stage 4
- phone field from RevenueClient

**Output:** 
- Boolean: eligible (has valid phone) or not

**Python File:** 
- `backend/app/scripts/generate_campaign_report.py`

**Functions/Classes:**
- `_has_phone(phone)` - checks if phone is not empty/null/"N/A"/"None"/"null" (string comparison)

**Filter Logic:**
```python
def _has_phone(phone: str | None) -> bool:
    value = (phone or "").strip()
    return value not in {"", "N/A", "None", "null"}
```

**Status:** ✅ ACTIVE (Used to set READY/HOLD status)

**Note:** This is the ONLY eligibility check. No other validation (format, length, validity) at this stage.

---

### STAGE 6: TEMPLATE ASSIGNMENT

**Purpose:** Route clients to appropriate communication templates based on segment and value

**Input:** 
- ClientPriorityRow from Stage 4
- _has_phone() result from Stage 5

**Output:** 
- SegmentAssignment with: segment, channel, template_id, reason

**Python File:** 
- `backend/app/scripts/generate_campaign_report.py`

**Functions/Classes:**
- `_assign_segment(row)` - decision tree for template assignment
- `SegmentAssignment` dataclass - output structure
- `_band(score)` - classifies monetary score into High/Medium/Low

**Assignment Logic:**
```
1. If no phone → GONE_QUIET → Manual Review → GONE_QUIET_01
2. If total_visits <= 0 → GONE_QUIET → Manual Review → GONE_QUIET_01
3. If total_visits == 1 → FIRST_VISIT → WhatsApp → FIRST_VISIT_01
4. If delay_days > 30 → LONG_ABSENCE → SMS → LONG_ABSENCE_01
5. If 15 ≤ delay_days ≤ 30 → FRESH_LAPSE → WhatsApp → FRESH_LAPSE_01
6. If monetary ≥ 66 AND frequency ≥ 66 → VIP → Phone Call → VIP_01
7. Else → REGULAR → WhatsApp → REGULAR_01
```

**Status:** ✅ ACTIVE (Determines channel and template for Integrilla)

**Templates Available:**
- GONE_QUIET_01 (manual review)
- FIRST_VISIT_01 (first-time acquisition)
- LONG_ABSENCE_01 (SMS)
- FRESH_LAPSE_01 (WhatsApp)
- VIP_01 (phone)
- REGULAR_01 (WhatsApp)

---

### STAGE 7: DEDUPLICATION

**Purpose:** Remove duplicate clients (keep only first high-priority occurrence)

**Input:** 
- Sorted ClientPriorityRow list (by priority_score descending)

**Output:** 
- De-duplicated list (unique client_id)

**Python File:** 
- `backend/app/scripts/generate_campaign_report.py`

**Functions/Classes:**
- No dedicated function; logic in `main()`:
```python
seen_client_ids: set[int] = set()
for row in rows:
    if row.client_id in seen_client_ids:
        continue
    seen_client_ids.add(row.client_id)
    deduped_rows.append(row)
```

**Deduplication Strategy:** 
- Priority-based (higher priority kept)
- Single-occurrence per client_id
- No merge of client records

**Status:** ✅ ACTIVE (Applied before campaign report and export)

**Note:** This is the only deduplication stage. Data must be deduplicated before Integrilla export.

---

### STAGE 8: CAMPAIGN REPORT

**Purpose:** Display final campaign eligibility and routing decisions (console output)

**Input:** 
- De-duplicated ClientPriorityRow list from Stage 7
- SegmentAssignment from Stage 6

**Output:** 
- Console text output (human-readable campaign manifest)

**Python File:** 
- `backend/app/scripts/generate_campaign_report.py`

**Functions/Classes:**
- `main()` - orchestrates report generation
- `_print_campaign_line(row, assignment)` - formats console output

**Output Format:**
```
Client ID: {id} | Name: {name} | Phone: {phone} | Priority Score: {score} | 
Segment: {segment} | Send Status: {READY|HOLD} | Channel: {channel} | 
Template: {template_id} | Reason: {reason} | Revenue: {total_revenue} | 
Delay: {delay_days} | Visits: {total_visits}
```

**Status:** ✅ ACTIVE (Used for manual verification before export)

**Execution:** 
```bash
python -m app.scripts.generate_campaign_report
```

**Send Status Logic:**
- READY: has_phone(phone) AND segment != "Gone Quiet"
- HOLD: not eligible to send

---

### STAGE 9: INTEGRILLA EXPORT

**Purpose:** Export READY clients to XLSX for Integrilla import

**Input:** 
- De-duplicated ClientPriorityRow list from Stage 7
- SegmentAssignment from Stage 6
- Client phone, name, template_id

**Output:** 
- campaign.xlsx (Microsoft Excel format)
- Sheet name: "Campaign"
- Columns: phone, name, template_id

**Python File:** 
- `backend/app/scripts/export_integrilla.py`

**Functions/Classes:**
- `main()` - orchestrates export
- `IntegrillaRow` dataclass - output structure
- `_clean_phone(phone)` - validates and formats phone numbers

**Phone Validation:**
```python
def _clean_phone(phone: str | None) -> str | None:
    if not phone or not _has_phone(phone):
        return None
    
    # Remove all non-digit characters (+, spaces, -, (, ))
    digits_only = re.sub(r'\D', '', phone)
    
    # Require minimum 8 digits (country code + local)
    if not digits_only or len(digits_only) < 8:
        return None
    
    return digits_only
```

**Export Filter:**
- Only READY clients (has_phone AND segment != "Gone Quiet")
- Skip clients with invalid phone after cleaning
- Log excluded clients with reason

**Excel Generation:**
- Uses: `openpyxl` library
- Headers: phone (string), name (string), template_id (string)
- Data rows: cleaned phone digits + client name + template ID

**Status:** ✅ ACTIVE (Implemented 2026-08-02)

**Execution:** 
```bash
python -m app.scripts.export_integrilla
```

**Output Location:** `campaign.xlsx` (current working directory)

**Sample Output:**
| phone | name | template_id |
|-------|------|-------------|
| 79217571760 | Евгения Eleonorma | LONG_ABSENCE_01 |
| 79262181499 | Aleksandra TChertakova | LONG_ABSENCE_01 |

---

### STAGE 10: INTEGRILLA EXECUTION

**Purpose:** Send campaign messages to clients via Integrilla message transport

**Input:** 
- campaign.xlsx from Stage 9
- Integrilla system configuration

**Output:** 
- Message delivery events
- Client engagement metrics
- Revenue attribution

**Python File:** 
- ❌ NOT IMPLEMENTED

**Status:** ❌ NOT IMPLEMENTED

**Expected Flow (placeholder):**
```
1. Import campaign.xlsx into Integrilla
2. Map columns: phone → destination, template_id → message template
3. Validate message templates in Integrilla
4. Schedule message delivery
5. Track delivery status
6. Capture engagement metrics (delivery, open, click, booking)
7. Feed results back to Altegio via write-back API
```

**Dependencies (when implemented):**
- Integrilla API client (not in repository)
- Message template storage (Integrilla system)
- Delivery tracking mechanism
- Engagement logging

**Decision:** Write-back to Altegio and Integrilla integration deferred until AFTER Sprint FIRST REVENUE (per KNOWN_STATE.md)

**Note:** Manual import into Integrilla required for first campaign.

---

## Data Flow Summary

```
Altegio CRM
   ↓ (sync_altegio_clients + import_altegio_visit_history)
RevenueClient + RevenueClientVisit (PostgreSQL)
   ↓ (generate_priority_report)
ClientPriorityRow (in-memory)
   ↓ (RevenueSegmentationEngine)
Segment + SegmentAssignment (in-memory)
   ↓ (deduplication)
Unique clients (in-memory)
   ↓ (export_integrilla)
campaign.xlsx (file)
   ↓ (manual import to Integrilla)
Integrilla system
   ↓ (NOT IMPLEMENTED)
Client messages
   ↓
Engagement + Revenue
```

---

## Environment Variables Required

| Variable | Default | Purpose | Stage |
|----------|---------|---------|-------|
| ALTEGIO_BASE_URL | https://api.alteg.io/api | Altegio API endpoint | 1 |
| ALTEGIO_PARTNER_TOKEN | (required) | Auth token | 1 |
| ALTEGIO_LOGIN | (required) | Salon login | 1 |
| ALTEGIO_PASSWORD | (required) | Salon password | 1 |
| ALTEGIO_COMPANY_ID | (auto-resolve) | Company location ID | 1 |
| ALTEGIO_TIMEOUT | 20 | HTTP timeout (seconds) | 1 |
| REVENUE_DEFAULT_DELAYED_DAYS | 45 | Delayed segment threshold | 3 |
| REVENUE_DEFAULT_LOST_DAYS | 90 | Lost segment threshold | 3 |
| REVENUE_SERVICE_RULES_JSON | {} | Service-specific thresholds | 3 |
| POSTGRES_* | (from .env) | Database connection | All |

---

## Execution Sequence

**Manual execution order:**

```bash
# Stage 1: Data acquisition (daily or on-demand)
python -m app.scripts.sync_altegio_clients
python -m app.scripts.import_altegio_visit_history

# Stages 2-8: Campaign generation (on-demand)
python -m app.scripts.generate_campaign_report

# Stage 9: Integrilla export (on-demand)
python -m app.scripts.export_integrilla

# Stage 10: Manual import (currently external to codebase)
# Upload campaign.xlsx to Integrilla via UI
```

---

## Known Limitations & Deferred Work

- ❌ Stage 10 (Integrilla execution) not implemented
- ❌ No automated scheduling (all manual execution)
- ❌ No webhook/event processing from Integrilla
- ❌ No write-back to Altegio (deferred per architecture)
- ⚠️ Phone validation limited to digit count (no format validation)
- ⚠️ Duplicate fields in RevenueClient (total_visits vs visit_count, total_spent redundancy)
- ⚠️ No error recovery (script exit on first error)
- ⚠️ Console logging only (no structured logging)
