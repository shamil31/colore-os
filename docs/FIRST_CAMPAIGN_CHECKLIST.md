# First Campaign Execution Checklist

## Data Pipeline
- [ ] Altegio clients imported (`python -m app.scripts.sync_altegio_clients`)
- [ ] Visit history synced (`python -m app.scripts.import_altegio_visit_history`)
- [ ] Revenue calculated and verified
- [ ] Priority scores computed and validated

## Campaign Generation
- [ ] Priority report generated (`python -m app.scripts.generate_priority_report`)
- [ ] Campaign report generated (`python -m app.scripts.generate_campaign_report`)
- [ ] Segmentation rules applied (READY/HOLD status correct)
- [ ] Deduplication verified (no duplicate client IDs)
- [ ] Integrilla export created (`python -m app.scripts.export_integrilla`)
- [ ] campaign.xlsx validated (279+ READY clients, phone format clean)

## Integrilla Integration
- [ ] campaign.xlsx imported into Integrilla
- [ ] Column mapping verified (phone, name, template_id)
- [ ] Phone numbers parse correctly (country code preserved)
- [ ] Templates available for all assigned segments
- [ ] Test message sent to internal number

## Launch
- [ ] Campaign scheduled in Integrilla
- [ ] Send status monitored (delivery, errors)
- [ ] Test client receives message

## Monitoring (First 24 Hours)
- [ ] Message delivery confirmed
- [ ] Client response tracking enabled
- [ ] Revenue impact visible (bookings, appointments)
- [ ] No critical errors in logs

## Reporting
- [ ] Results captured (deliveries, opens, clicks, bookings)
- [ ] Conversion rate calculated
- [ ] Revenue attributed to campaign
- [ ] Learnings documented for next cycle
