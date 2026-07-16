# FTTE — Full-Text Timestamped Extract

**Version:** 0.1.0
**Status:** Draft for community review

---

## Statement

Every user of any global platform has a right to receive, on demand, a complete extract of every input they have ever provided to that platform, in full text (or full-fidelity binary for non-text media), with an accurate timestamp of when the input was received by the platform.

This is not a novel right. It is the minimum standard that follows from the basic reciprocity: **the platform has that record. The user should have the same record.** When the two records match, the individual can audit their own actions and, because platform reactions bracket every action a user takes, the individual can audit the platform's behaviour around them as a side effect.

## What full-text timestamped means

**Full-text.** Every ASCII stroke, character, keystroke sequence, message, comment, edit, edit-history entry, search query, click event that produced a text artifact, and every other text-bearing input the user provided. Not summaries. Not derived features. The literal text the user typed or spoke that the platform converted to text.

**Full-fidelity binary.** For non-text inputs (photos, videos, audio, uploaded files) — the original binary the user provided, at the resolution and format the user provided it. If the platform re-encoded, both the original and the re-encoded version.

**Timestamped.** Each item carries the accurate timestamp of when the platform received it — not a truncated day-level stamp, not an inferred stamp, but the actual receipt time to at least second-level precision. Timezone recorded.

**Extractable on demand.** Available on request, delivered in a reasonable time, in an open machine-readable format. Not gated behind a customer-service escalation. Not delivered in a locked or proprietary format that requires the platform's own tooling to read.

## Why the standard matters

Currently, platforms have full-text timestamped records of what their users did on them. Users do not. This asymmetry means:

- The platform can reconstruct any interaction sequence to defend itself in any dispute. The user cannot.
- The platform can train models on the full record of user behaviour. The user cannot audit what the platform learned.
- If the platform ever loses, corrupts, or misrepresents a user's own history, the user has no independent record to check against.
- The user carries the burden of protecting data the platform is actually holding.

FTTE closes the gap by making the same record available to both parties.

## What FTTE does not require

- FTTE does not require the platform to give the user anything the platform does not already have. This is not a new data-collection obligation; it is a reciprocal-access obligation on data already collected.
- FTTE does not require the platform to disclose other users' data. Only the requesting user's own inputs and the platform's own reactions to those inputs.
- FTTE does not require any specific format beyond "open and machine-readable." JSON, CSV, JSONL, HTML, XML, plain text, and standardised media formats all satisfy the standard.
- FTTE does not require real-time delivery. On-demand within a reasonable window (typically 24 hours for text records; longer windows may be reasonable for very large media archives).

## What compliant delivery looks like

A compliant FTTE delivery is a single downloadable archive containing, at minimum:

1. `/text/` — every text-bearing input by the user, one record per input, in a JSON-lines format with fields: `id`, `timestamp_utc`, `timezone`, `source` (which product/feature), `text`, and any interaction context necessary to reconstruct the sequence.
2. `/media/` — every non-text user input in original format, with a companion manifest carrying the same timestamp fields.
3. `/interactions/` — the platform's own reactions to each user input where a reaction was generated (search results shown, ranked feed items, recommendations, moderation actions taken, etc.). This is what turns the extract from a diary into an audit trail.
4. `/metadata.json` — the schema version, the delivery timestamp, the account identifier, and a hash of every file in the archive so the user can verify integrity.

## The audit property

When a user has an FTTE-compliant record on their own storage, timestamps aligned, three properties follow:

1. **Reciprocity.** The user knows the platform does not have any input by the user that the user does not also have. No hidden text, no phantom entries.
2. **Sequence integrity.** Each user action is bracketed by the platform's reactions just before and after it. This lets the user reconstruct not just what they did, but how the platform responded around every action.
3. **Portability.** The record moves. If the user switches platforms, closes an account, or wants to bring their history to a new tool, they carry a portable, verifiable record with them.

## Compliance in the absence of platform action

Until platforms deliver FTTE-compliant extracts natively, users are left to assemble the equivalent record from whatever extraction paths the platforms currently document or tolerate. That assembly is what [`data-liberation-kit`](../README.md) does.

A kit-assembled record is not a substitute for platform-delivered FTTE. It is a floor. When platforms meet or exceed the standard natively, the kit's role shrinks to verification.

## Reference implementation

- [`data-liberation-kit`](../README.md) — the reference implementation that assembles FTTE-shaped records from currently-available extraction paths.

## Versioning

FTTE is community-versioned. Amendments and additions are submitted as PRs against this file. Semantic versioning applies: major for breaking changes to the required structure; minor for additive requirements; patch for clarifications.

## Non-adversarial posture

FTTE is a standard, not a complaint. It is offered to platforms as a target they can meet, not as an accusation. Platforms that meet or exceed it should be recognised. Platforms that fall short should be given time and community feedback before any dispute posture is considered.

## Related work

- Right of access under GDPR Article 15 (EU/EEA).
- Consumer data rights under CCPA/CPRA (California).
- Right to data portability under various national frameworks.

FTTE is compatible with and generally stronger than existing statutory rights of access. Compliance with FTTE typically satisfies statutory access requirements as a side effect.

---

*This standard is offered freely for adoption, adaptation, and citation. No attribution required, though attribution is welcomed.*
