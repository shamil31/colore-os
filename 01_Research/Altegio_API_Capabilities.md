# Altegio API Capabilities Audit

Date: 2026-08-01
Source: Official Altegio API documentation and official OpenAPI specifications on developer.alteg.io.

## Executive Summary

Coloré OS can write selected business decisions back into Altegio through official API methods.
The strongest and safest write-back surface for client-level business context is available in Business Management v1 client update endpoint, with supporting capabilities in comments, labels/tags, and loyalty operations.

Confirmed operational conclusion:
- Altegio can remain the operational CRM system of record.
- Coloré OS can persist execution context in Altegio without introducing a parallel client state store.

## Supported Write Operations

Confirmed official write operations relevant for CRM write-back:
- Client profile update: PUT /client/{location_id}/{id}
- Client comments add/delete:
  - POST /clients/{location_id}/clients/{client_id}/comments
  - DELETE /clients/{location_id}/clients/{client_id}/comments/{comment_id}
- Tag dictionary CRUD:
  - v2 preferred: POST/PUT/DELETE /locations/{company_id}/tags and /locations/{company_id}/tags/{tag_id}
  - v1 legacy/deprecated: /labels/... endpoints
- Custom field definitions CRUD (v1):
  - POST /custom_fields/{field_category}/{location_id}
  - PUT /custom_fields/{field_category}/{location_id}/{field_id}
  - DELETE /custom_fields/{field_category}/{location_id}/{field_id}
- Client custom field values update via client update payload:
  - PUT /client/{location_id}/{id} with custom_fields map
- Loyalty write operations:
  - Apply/cancel discount program on visit/card context
  - Apply/cancel card withdrawal
  - Loyalty card issue/remove and loyalty transactions
  - Membership/certificate chain-level balance and period operations

## Client Update Capabilities

Official writable fields in PUT /client/{location_id}/{id}:
- name
- surname
- middle_name
- phone
- email
- gender_id
- importance_id
- discount
- card
- birth_date
- comment
- spent
- balance
- sms_check
- sms_not
- labels
- custom_fields

Business interpretation for Coloré OS:
- Core write-back of execution decisions is possible through importance_id, labels, custom_fields, comment, and discount.

## Custom Fields

Capabilities:
- Custom field definitions can be created and managed via v1 custom fields endpoints.
- Client-level custom field values can be written through client update payload (custom_fields key-value map).

Applicable fields for Coloré OS (supported as custom values):
- AI Priority
- AI Segment
- VIP Level
- Campaign History
- Last Campaign
- Reactivation Status
- AI Score
- Campaign ID

## Comments

Capabilities:
- Internal client notes/comments can be written automatically.
- Comment log can be appended via dedicated comments endpoint.

Use for Coloré OS:
- Persistent, human-readable operational context.
- Timeline notes for campaign decisions and outcomes.

## Tags / Labels

Capabilities:
- Tags are supported and writable.
- v2 provides active CRUD for tags dictionary.
- Client assignment is supported in client update payload through labels field.

Use for Coloré OS:
- Fast operational flags for filtering and manual execution.

## Importance

Capabilities:
- importance_id is writable in client update.

Use for Coloré OS:
- Coarse priority class (for example operational triage and front-desk visibility).

## Discounts

Capabilities:
- Client discount can be written through discount field in client update.
- Loyalty-related discounts are applied through loyalty program endpoints in visit/card context.

Limit note:
- API does not expose a separate first-class semantic split for permanent/personal/loyalty discount types in one single client profile field.

## Loyalty

Capabilities:
- Card issue/removal and manual loyalty transactions.
- Program application/cancellation on visit/card context.
- Chain-level membership and certificate administrative operations.

Use for Coloré OS:
- Controlled campaign incentives where loyalty mechanics are needed.

## API Limitations

- v1 is full-featured but marked for gradual deprecation; new capabilities appear first in v2.
- v2 requires Accept: application/vnd.api.v2+json.
- v2 currently exposes read-focused Booking User endpoints in the documented surface used in this audit; primary client profile write-back remains on v1 client update endpoint.
- Client update requires required base fields (name and phone) in payload.
- Terminology is mixed across versions (labels/tags, client/booking user aliases).
- Permission model is strict; write methods can fail with 403 when business user rights are insufficient.
- Platform rate limits apply (200 requests/min or 5 requests/sec per IP).

## Recommended Coloré OS Usage

Write-back priority for business decisions:
1. Comments
2. Custom Fields
3. Importance
4. Labels / Tags
5. Discount

Reasoning:
- This order minimizes operational risk while maximizing traceability and reversibility.
- It preserves Altegio as single operational truth for client execution context.

## Future Opportunities

- Standardize AI-to-CRM write-back dictionary (field code conventions for custom_fields).
- Expand campaign outcome persistence model directly in client context.
- Introduce controlled write-back policy by decision type and confidence level.
- Move more write operations to v2 as soon as equivalent write endpoints are officially available.
