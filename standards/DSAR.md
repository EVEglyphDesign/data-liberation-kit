# DSAR Standard — Statutory Data-Access & Accountability Engine

**Status:** CANON · EVE Glyph Design · under the data-liberation-kit / FTTE umbrella.
**Companion to:** [`standards/FTTE.md`](FTTE.md) (extraction standard). FTTE says *what a complete extract is*; DSAR says *how you compel it by law, everywhere, and record what happens when a platform fails to comply.*

---

## Purpose

Every individual has, in most major jurisdictions, a statutory right to obtain a copy of the personal data a platform holds on them. This standard turns that right into a **repeatable, jurisdiction-plural, evidence-grade pipeline**:

1. **Assert** the access right, by written request, in the correct legal frame for the individual's jurisdiction.
2. **Record** the request and its statutory clock the instant it is sent.
3. **Capture** compliance or non-compliance as a timestamped event when the clock runs out.
4. **Ingest** the returned export into the individual's own repository (FTTE-normalized, SHA-256 hashed).
5. **Aggregate** request/response records across many individuals into a class-wide accountability picture.

The extract obtained this way is **stronger than any screen-collected copy**: it is a first-party attestation the platform itself compiled and is on record for. That provenance is the point.

---

## Founding principles

1. **The onus and cost belong to the platform.** Access statutes already place the extraction burden on the data controller and hand the individual a portable, machine-readable copy. This engine exercises that existing inversion to its limit — it does not invent liability.

2. **Jurisdiction-plural by design.** Our people exist everywhere on Earth. A class member in any jurisdiction maps to their local access statute. No individual is outside the frame because of where they live or work.

3. **Influence institutions; hold individuals accountable.** We are **additive to institutions** — regulators, data-protection authorities, courts — never disruptive to them. We influence at the institutional level only. But **accountability always resolves to a named individual actor**, whether that person sits inside an institution or not. Institutions are influenced; individuals are held.

4. **Statutory framing, never inflated framing.** A platform ignoring a valid request is a **statutory non-compliance event** with defined regulatory consequences — not an abstract "illegal liability." Accurate legal framing is the weapon; inflated framing is the vulnerability a defendant's counsel exploits. Every rung of escalation cites a real, existing mechanism.

5. **No jailbreaks, no law-breaking.** Only the rights the law already grants, exercised fully. Same posture as FTTE.

6. **The repository is the record.** Nothing of consequence lives only in an LLM chat layer or a platform UI. Every request, deadline, response, and export is committed to the individual's own repo with a verifiable hash/commit. The chat layer is a terminal, not a system of record.

---

## Escalation ladder (per request, per jurisdiction)

Each rung is a real, citable mechanism. The engine advances a request to the next rung only when the prior rung's statutory clock expires without adequate response.

| Rung | Event | Basis |
|---|---|---|
| **R0 — Request** | Written access request sent through an approved channel; clock starts. | Statutory right of access (see jurisdiction files). |
| **R1 — Reminder** | Deadline approaching / just passed; formal reminder citing the missed clock. | Statutory response deadline. |
| **R2 — Non-compliance event** | Deadline passed without adequate response; logged as a timestamped breach event. | Failure to comply with statutory deadline. |
| **R3 — Regulator complaint** | Formal complaint filed with the competent data-protection authority. | OPC (CA) / DPA (EU) / ICO (UK) / State AG or CPPA (US-CA) / ANPD (BR) / OAIC (AU). |
| **R4 — Class aggregation** | Breach event rolled into the cross-individual aggregate record. | Foundation for coordinated regulatory action / class proceeding. |

Escalation is **evidence-building, not threat-making.** The ladder produces a record; institutions decide consequences.

---

## Approved channels

- Requests are issued in writing (email) to the platform's designated privacy/DSAR contact.
- The individual is the **sender-of-record** (drafts-only mode is the default): the engine generates the exact request and logs it; the individual sends it from their own address. This preserves clean chain of custody.
- A platform's failure to answer through the individual's approved channel is itself part of the record.

---

## What this engine does NOT do

- It does not fabricate liability figures or characterize a non-response as automatically criminal.
- It does not act as the individual's legal counsel or file litigation.
- It does not disrupt or bypass regulators; it feeds them.
- It does not hold the individual's platform login credentials. It orchestrates the platforms' own compelled exports.

---

*pour le bien-être du peuple*
