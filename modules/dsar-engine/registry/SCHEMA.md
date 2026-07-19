# DSAR Accrual Ledger — Schema

The ledger is the **evidence-grade record**. Every request and every deadline event is a row. Rows roll up from individual → platform → jurisdiction → class aggregate. Designed to scale 1 → 1,000,000+ individuals.

## Files

- `requests.csv` — one row per (individual × platform × jurisdiction) request. The atomic unit.
- `events.csv` — one row per lifecycle/escalation event against a request (append-only).
- `AGGREGATE.json` — computed rollup for the class-wide accountability picture (generated, not hand-edited).

## `requests.csv` columns

| Column | Meaning |
|---|---|
| `request_id` | Stable unique id: `DSAR-{individual_id}-{platform_id}-{jurisdiction}-{YYYYMMDD}-{seq}` |
| `individual_id` | Pseudonymous stable id for the class member (never raw PII in shared aggregate) |
| `individual_jurisdiction` | The member's governing jurisdiction key (e.g. `pipeda-ca`) |
| `platform_id` | From platforms.yaml |
| `jurisdiction` | Legal regime the request is filed under |
| `statute` | Statute + article/section cited |
| `channel` | `email` / `portal` |
| `sender_of_record` | The individual (drafts-only default) |
| `sent_date` | ISO date the request was sent |
| `deadline_date` | Computed from jurisdiction clock formula |
| `extended_deadline_date` | If a valid extension notice was received |
| `status` | `SENT / ACK / EXTENDED / FULFILLED / PARTIAL / REFUSED / NONCOMPLIANT` |
| `current_rung` | `R0 / R1 / R2 / R3 / R4` |
| `export_received` | boolean |
| `export_sha256` | Manifest hash of ingested export (FTTE lineage) |
| `export_repo_path` | Where the normalized export landed |
| `last_event_date` | ISO date of most recent event row |

## `events.csv` columns (append-only)

| Column | Meaning |
|---|---|
| `event_id` | Unique id |
| `request_id` | FK to requests.csv |
| `event_date` | ISO datetime |
| `rung` | Rung this event belongs to (R0–R4) |
| `event_type` | `REQUEST_SENT / ACK_RECEIVED / EXTENSION_NOTICE / RESPONSE_RECEIVED / DEADLINE_PASSED / NONCOMPLIANCE_LOGGED / REGULATOR_COMPLAINT_FILED / AGGREGATED` |
| `deadline_delta_days` | Days early(-)/late(+) vs statutory deadline; blank if N/A |
| `regulator` | Named authority if rung R3 |
| `institution` | Institution influenced (never disrupted) if applicable |
| `accountable_individual` | **Named individual actor** accountable for the event — resolves inside OR outside an institution. Core principle: institutions are influenced, individuals are held. |
| `evidence_ref` | Path/URL to the underlying artifact (email, portal receipt, screenshot) committed to repo |
| `notes` | Factual, statutory framing only — no inflated liability language |

## `AGGREGATE.json` (generated)

```json
{
  "generated_at": "<iso>",
  "class_size": 0,
  "by_platform": { "<platform_id>": { "requests": 0, "noncompliant": 0, "noncompliance_rate": 0.0 } },
  "by_jurisdiction": { "<jurisdiction>": { "requests": 0, "noncompliant": 0 } },
  "by_platform_jurisdiction": { "<platform_id>::<jurisdiction>": { "requests": 0, "noncompliant": 0, "median_response_days": null } },
  "noncompliance_events_total": 0,
  "regulator_complaints_total": 0
}
```

## Integrity rules

1. **events.csv is append-only.** Corrections are new rows, never edits — the audit trail is the value.
2. **No raw PII in the shared/class aggregate.** `individual_id` is pseudonymous; raw identity stays in the individual's own private repo.
3. **Every event references committed evidence** (`evidence_ref`). An event with no artifact in the repo is not admissible to the aggregate.
4. **Statutory framing only.** A non-response is a `NONCOMPLIANCE_LOGGED` event tied to a specific missed statutory deadline — never characterized as automatically criminal.

---
*pour le bien-être du peuple*
