# Storage target selector

Where your data lands. Pick at first-run. Change your mind later.

## Options

### 1. GitHub-LFS (default)

Photos, videos, and history files push to your own private GitHub repository via Git-LFS. Consistent with the LLM-to-repo binding — everything ends up in one place under version control.

- **Pros:** integrated version history, small repos free, familiar tooling.
- **Cons:** free tier caps LFS at ~1 GB and bandwidth at ~1 GB/month. Larger archives need paid LFS storage packs.
- **When it fits:** most individuals with ≤10 GB of media. Consultants who already have GitHub.

### 2. S3-compatible bucket (S3 / R2 / B2)

You point the kit at your own S3-compatible bucket (AWS S3, Cloudflare R2, Backblaze B2, MinIO, etc.). The repo holds only the manifests; the media/history land in the bucket.

- **Pros:** cheapest at scale. R2 has no egress fees. B2 is very cheap per GB.
- **Cons:** requires you to set up a bucket and manage credentials.
- **When it fits:** larger archives (10 GB+), long-form video, users with existing cloud storage.

### 3. Local NAS or folder + GitHub index

Media stays on your local NAS or a folder on your machine. Only the manifests (hashes, timestamps, paths) go to the GitHub repo. The index tells any tool where to find the actual content.

- **Pros:** maximum sovereignty. The bytes never leave your premises.
- **Cons:** requires you to have local storage and to keep it available.
- **When it fits:** users with a home NAS, on-premise-only requirements, very large archives.

## Configuration

Selected via `./scripts/setup.sh`. Written to `.liberation-kit/config.yaml`:

```yaml
storage:
  target: github-lfs   # or: s3-compatible / local-index
  github_lfs:
    repo: "yourhandle/your-liberation-repo"
    branch: main
  s3_compatible:
    endpoint: "https://<accountid>.r2.cloudflarestorage.com"
    bucket: "your-bucket"
    region: "auto"
    prefix: "media/"
  local_index:
    base_path: "/Volumes/NAS/liberation"
    mount_check: true
```

## Switching targets later

Rerun `./scripts/setup.sh --reconfigure-storage`. The kit will migrate manifest entries but does not automatically move bytes between backends — the user runs a one-time migration script the setup will offer.

## Encryption at rest

- GitHub-LFS: repo can be private; contents are TLS in transit and encrypted at rest by GitHub.
- S3-compatible: user's own bucket policy applies. R2 and B2 both support at-rest encryption by default; the kit does not add a second encryption layer unless the user opts in.
- Local NAS: user's responsibility.

Optional client-side encryption before upload is on the [`WANTED.md`](../../WANTED.md) list — a community pickup.
