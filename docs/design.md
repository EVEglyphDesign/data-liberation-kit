# The base model — repository structure

Every peer who runs this kit ends up with the same layout in their own repo. That's the whole point: same shape everywhere, so tools, LLMs, and future modules all know where to find things.

## Layout

```
your-repo/
├── media/
│   ├── photos/
│   │   └── YYYY/MM/DD/           # original filename + hash suffix
│   ├── videos/
│   │   └── YYYY/MM/DD/
│   └── manifests/
│       └── YYYY-MM.jsonl         # one line per file, with metadata + hash
│
├── history/
│   ├── llm/
│   │   ├── chatgpt/YYYY/MM/       # per-conversation JSONL
│   │   ├── claude/YYYY/MM/
│   │   ├── perplexity/YYYY/MM/
│   │   ├── copilot/YYYY/MM/
│   │   └── gemini/YYYY/MM/
│   ├── platforms/
│   │   ├── google/                # Takeout-derived structured extracts
│   │   ├── apple/                 # iCloud + local extracts
│   │   └── ...                    # future platforms
│   └── manifests/
│       └── YYYY-MM.jsonl
│
├── interactions/                  # platform reactions bracketing your actions
│   └── YYYY/MM/DD.jsonl
│
├── metadata/
│   ├── schema.json                # base-model schema version this repo conforms to
│   ├── modules-enabled.json       # which modules are currently active
│   ├── storage-target.json        # where data is landing (may be encrypted)
│   └── integrity.json             # rolling hash of all manifests
│
├── .liberation-kit/               # kit config, not for user editing
│   ├── config.yaml
│   └── credentials.enc            # encrypted credentials, key never leaves user machine
│
└── README.md                      # generated for the peer's own repo
```

## Design principles

1. **Same shape everywhere.** Every peer's repo looks like this. Improvements to the base model propagate through simple schema-version bumps.

2. **Manifest-driven.** Every directory has a `manifests/YYYY-MM.jsonl` that carries the timestamps, hashes, source, and enough metadata to reconstruct the extraction. Manifests are cheap; media/history is expensive. Tools read manifests first.

3. **Timestamps are UTC.** Local time is preserved in a separate field but the canonical index is UTC. This is non-negotiable for the audit property.

4. **Hashes travel with content.** Every file has a hash in its manifest entry. Users can verify integrity independent of the platform, and independent of git.

5. **No inference in the base layout.** The kit stores what the platforms gave, in the shape the platforms gave it, plus timestamps and hashes. Derived indices (e.g. faces, transcriptions, embeddings) go in optional side directories that the user can regenerate at will.

6. **Credentials never leave the user's machine.** The kit uses OS-level keychains where available and an encrypted local file otherwise. `.liberation-kit/credentials.enc` is `.gitignore`d by default.

7. **Portability first.** The layout is designed to be readable without the kit installed. A user with just `jq`, `sqlite3`, and standard image tools can navigate their own repo.

## Manifest schema (v0.1.0)

Each line in a `manifests/YYYY-MM.jsonl` file is a self-contained JSON record:

```json
{
  "id": "sha256-prefix-of-content",
  "path": "media/photos/2026/07/15/IMG_1234.jpg",
  "content_hash": "sha256:abc123...",
  "size_bytes": 3145728,
  "mime_type": "image/jpeg",
  "captured_at_utc": "2026-07-15T21:03:17Z",
  "captured_at_local": "2026-07-15T16:03:17-05:00",
  "extracted_at_utc": "2026-07-15T22:14:02Z",
  "source": {
    "module": "apple-media",
    "path": "icloud-photos-api",
    "original_id": "asset-uuid-here",
    "original_filename": "IMG_1234.HEIC"
  },
  "original_format": "image/heic",
  "converted": true,
  "notes": []
}
```

Every module writes manifest entries in this shape. Future modules add fields under `source` without breaking existing consumers.

## LLM-swept content

When a peer runs the kit's LLM-sweep utility (`scripts/llm-sweep.sh`), their pointed LLM will scan any additional content they drop into `_incoming/` and place it in the correct location under the base-model layout with a compliant manifest entry. This is how peers bring in old exports, screenshots, backup archives, and anything else they already have.

The sweep is idempotent — running it twice does nothing the second time because manifest entries are keyed by content hash.

## Contributor swap-back

When a peer improves any part of the kit — a better Apple exporter, a new module, a schema refinement — they open a PR against this repo. If the improvement is better than what's in the base model, it becomes the base model and the schema version bumps. Everyone else picks up the improvement on the next `git pull`.

The base model is expected to evolve monthly. Peers are never forced to update.
