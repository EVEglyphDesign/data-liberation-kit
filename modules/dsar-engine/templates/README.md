# Request templates

One template per jurisdiction for the **R0 request** rung, plus a generic **R1 reminder**.

- `request-gdpr.md` — GDPR Art. 15 (EU/EEA). Also serves UK GDPR with minor edits (swap citation to UK GDPR + DPA 2018, regulator = ICO).
- `request-pipeda.md` — PIPEDA (Canada).
- `request-ccpa.md` — CCPA/CPRA (California).
- `reminder-generic.md` — R1 reminder, any jurisdiction (fill statute/regulator vars).

**To add:** LGPD (BR, 15-day clock, Art. 18), Australia APP 12 (30-day). Copy the closest template and swap citation + clock.

## Placeholders

`{{full_name}}` `{{account_identifier}}` `{{account_email}}` `{{platform_name}}` `{{contact_details}}` `{{sent_date}}` `{{request_id}}` `{{statute_name}}` `{{deadline_date}}` `{{deadline_status}}` `{{today}}` `{{regulator}}` `{{jurisdiction}}`

## Mode

**Drafts-only (default):** the engine renders the template with the individual's variables and logs it as request `{{request_id}}`. The **individual sends it from their own address** and remains sender-of-record. This preserves chain of custody for the accountability ledger.

---
*pour le bien-être du peuple*
