# Altegio API Capabilities Audit

**Date:** 2026-08-02  
**Scope:** Write-back capabilities for Coloré OS decision layer  
**Status:** RESEARCH ONLY (No implementation)

---

## Questions & Findings

### 1. Can client categories be updated through Altegio API?

**Finding:** NO

**Evidence:**
- Current implementation: READ-ONLY endpoints only
- Altegio API endpoints implemented: `/v1/clients/{id}` (GET only)
- No PUT/PATCH/POST endpoints for client updates
- No category field in implemented AltegioClient data model

**Code Reference:** `backend/app/integrations/altegio/client.py` - AltegioDataClient supports only GET operations

**Conclusion:** Not available in current API wrapper. Requires official Altegio API documentation to confirm if endpoint exists.

---

### 2. Can client discount be updated through Altegio API?

**Finding:** NO

**Evidence:**
- Current implementation: READ-ONLY
- No discount field in AltegioClient model
- No update endpoints implemented
- No POST/PUT/PATCH methods for client mutations

**Code Reference:** `backend/app/integrations/altegio/models.py` - AltegioClient dataclass has no discount field

**Conclusion:** Not available in current API wrapper. Would require official API docs to verify if endpoint exists.

---

### 3. Can custom fields be updated through Altegio API?

**Finding:** NO

**Evidence:**
- Current implementation: READ-ONLY only
- raw_data field stores full response but is READ-ONLY
- No custom field update endpoints
- No generic field mutation capability

**Code Reference:** `backend/app/integrations/altegio/client.py` - No update/write methods

**Conclusion:** Not available in current implementation. Official API may support via generic fields endpoint (unknown).

---

### 4. Can visit status changes be tracked through API?

**Finding:** PARTIAL

**Evidence:**
- Visit records are fetched: `/v1/records/{company_id}` (READ-ONLY)
- Visit status field exists: `RevenueClientVisit.visit_status` captured from API response
- Status changes are NOT tracked (no webhook, no polling, no event stream)
- Current implementation is snapshot-only

**Code Reference:** `backend/app/models/revenue_client_visit.py` - visit_status field populated from API data only at import time

**Conclusion:** Visit status CAN be read. Real-time change tracking (webhooks, events) not implemented. Polling would be required for continuous monitoring.

---

## Summary Table

| Capability | Supported? | Implementation Status | Notes |
|------------|-----------|----------------------|-------|
| Client categories update | ❌ NO | Not implemented | Requires API docs |
| Client discount update | ❌ NO | Not implemented | Requires API docs |
| Custom fields update | ❌ NO | Not implemented | Requires API docs |
| Visit status tracking | ⚠️ PARTIAL | Read-only implemented | Polling/webhooks not implemented |

---

## Architecture Constraint

**Write-back to Altegio is intentionally postponed until AFTER Sprint FIRST REVENUE.**

Current use: Coloré OS is READ-ONLY from Altegio.

Decision: [KNOWN_STATE.md] Architecture decision accepted 2026-08-01 that write-back capability is allowed through official API, but implementation deferred.

---

## Next Steps

- [ ] Obtain detailed Altegio API documentation
- [ ] Verify PUT/PATCH endpoints for client updates
- [ ] Confirm custom field mutation support
- [ ] Evaluate webhook/event API for real-time status changes
- [ ] Plan write-back implementation (post-FIRST REVENUE)
