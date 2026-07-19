# dsar-engine

**Compel every platform to hand you your data — by law, everywhere — and record what happens when they don't.**

This module extends `data-liberation-kit`. Where the other modules pull data through the paths platforms *document or tolerate*, `dsar-engine` exercises the **statutory access right** directly: it drafts the legal request, tracks the statutory clock, logs compliance or non-compliance as evidence, ingests the returned export into your repo (FTTE-normalized + SHA-256 hashed), and rolls individual records up into a class-wide accountability picture.

Read the doctrine first: [`../../standards/DSAR.md`](../../standards/DSAR.md).

## Why this and not "log in and scrape"

A DSAR export is a **first-party attestation the platform itself compiled** — provenance a screen-collected copy can never have. The onus and cost sit on the platform, which is the whole design intent. No credentials are ever held by the engine.

## Layout

```
dsar-engine/
  jurisdictions/     one file per legal regime (clock, scope, regulator, escalation)
  platforms/         platforms.yaml — one record per platform, extend freely
  templates/         statutory request emails (per regime) + generic reminder
  registry/          the accrual ledger: requests.csv, events.csv, SCHEMA.md, AGGREGATE.json
  schedule/          jobs.yaml — periodic reissue, deadline-watch, rollup, ingest
```

## The five moves (DSAR ladder)

`R0 Request → R1 Reminder → R2 Non-compliance event → R3 Regulator complaint → R4 Class aggregation`

Every rung cites a real mechanism. The ladder builds a record; institutions decide consequences.

## Jurisdictions shipped

PIPEDA (CA) · GDPR (EU) · UK GDPR · CCPA/CPRA (US-CA) · LGPD (BR) · APPs (AU) · `_TEMPLATE.md` for the rest.

**Verified statutory clocks:**
- PIPEDA 30d (+30 with notice) · GDPR 1mo (+2) · UK GDPR 1mo (+2) · CCPA/CPRA 45d (+45) · LGPD 15d · AU APP 12 30d.

## Mode

**Drafts-only by default.** The engine renders each request with your details and logs it; **you send from your own address** and stay sender-of-record. Clean chain of custody for the ledger.

## Principles (from the standard)

1. Onus + cost belong to the platform.
2. Jurisdiction-plural — a member anywhere maps to their local statute.
3. **Influence institutions; hold individuals accountable** — additive to regulators, never disruptive; accountability resolves to a named individual, inside or outside any institution.
4. Statutory framing only — never inflated liability.
5. No jailbreaks, no law-breaking.
6. The repository is the record.

## Status

Scaffold committed. Next wiring steps: verify per-platform DSAR contacts, connect a runner for `schedule/jobs.yaml`, and wire `ingest-exports` to the FTTE normalizer. The Amazon full-data-history request (2026-07-18, PIPEDA) is already seeded in `registry/`.

---
*pour le bien-être du peuple*
