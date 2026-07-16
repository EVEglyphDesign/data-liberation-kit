#!/usr/bin/env python3
"""Google Photos continuous off-ramp via the Library API.

Uses OAuth to fetch new mediaItems and download them into the repo's
base-model layout. Falls back with a clear message if API access is
unavailable (deprecated for the account) so the user knows to switch to
Takeout bulk mode.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
    import requests
except ImportError as e:
    print(f"Missing dependency: {e.name}. Run ./scripts/setup.sh first.", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = REPO_ROOT / ".liberation-kit" / "config.yaml"

log = logging.getLogger("google-media")

API_BASE = "https://photoslibrary.googleapis.com/v1"


def load_config() -> dict:
    with CONFIG_PATH.open() as f:
        return yaml.safe_load(f)


def load_token() -> str:
    from scripts.credentials import decrypt_store
    store = decrypt_store(REPO_ROOT / ".liberation-kit" / "credentials.enc")
    tok = store.get("google-media", {}).get("access_token")
    if not tok:
        raise RuntimeError("no google-media access_token in credential store; run setup.sh")
    return tok


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def already_have(manifest_path: Path, item_id: str) -> bool:
    if not manifest_path.exists():
        return False
    with manifest_path.open() as f:
        for line in f:
            try:
                e = json.loads(line)
                if e.get("source", {}).get("original_id") == item_id:
                    return True
            except json.JSONDecodeError:
                continue
    return False


def poll_once(token: str) -> int:
    headers = {"Authorization": f"Bearer {token}"}
    saved = 0
    page_token = None
    while True:
        params = {"pageSize": 100}
        if page_token:
            params["pageToken"] = page_token
        r = requests.get(f"{API_BASE}/mediaItems", headers=headers, params=params, timeout=60)
        if r.status_code == 403:
            log.error("Google Photos API returned 403. Access may be revoked for this account. "
                      "Switch to bulk (Takeout) mode: ./modules/google-media/run-bulk.sh")
            return saved
        r.raise_for_status()
        payload = r.json()
        for item in payload.get("mediaItems", []):
            saved += maybe_save(item, headers)
        page_token = payload.get("nextPageToken")
        if not page_token:
            break
    return saved


def maybe_save(item: dict, headers: dict) -> int:
    item_id = item["id"]
    creation_str = item["mediaMetadata"]["creationTime"]  # RFC3339
    captured = datetime.fromisoformat(creation_str.replace("Z", "+00:00"))
    is_video = item.get("mediaMetadata", {}).get("video") is not None
    subdir = "videos" if is_video else "photos"
    manifest_path = (REPO_ROOT / "media" / "manifests" /
                     f"{captured.strftime('%Y-%m')}.jsonl")
    if already_have(manifest_path, item_id):
        return 0

    filename = item.get("filename") or f"{item_id}.bin"
    date_dir = (REPO_ROOT / "media" / subdir /
                captured.strftime("%Y") / captured.strftime("%m") / captured.strftime("%d"))
    date_dir.mkdir(parents=True, exist_ok=True)

    base_url = item["baseUrl"]
    # For photos, add =d for original; for videos, =dv
    suffix = "=dv" if is_video else "=d"
    dl = requests.get(base_url + suffix, headers=headers, timeout=300, stream=True)
    dl.raise_for_status()
    out = date_dir / filename
    if out.exists():
        h = hashlib.sha256(item_id.encode()).hexdigest()[:8]
        out = date_dir / f"{Path(filename).stem}.{h}{Path(filename).suffix}"
    with out.open("wb") as f:
        for chunk in dl.iter_content(chunk_size=1 << 20):
            if chunk:
                f.write(chunk)

    entry = {
        "id": sha256_file(out)[:16],
        "path": out.relative_to(REPO_ROOT).as_posix(),
        "content_hash": "sha256:" + sha256_file(out),
        "size_bytes": out.stat().st_size,
        "mime_type": item.get("mimeType", "application/octet-stream"),
        "captured_at_utc": captured.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "captured_at_local": captured.isoformat(),
        "extracted_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": {
            "module": "google-media",
            "path": "photos-library-api",
            "original_id": item_id,
            "original_filename": filename,
        },
        "original_format": item.get("mimeType"),
        "converted": False,
        "notes": [],
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("a") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")
    log.info("saved %s", entry["path"])
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s %(message)s")

    cfg = load_config().get("google-media", {})
    if not cfg.get("enabled"):
        log.info("google-media disabled; exiting.")
        return 0

    token = load_token()
    interval = int(cfg.get("continuous", {}).get("poll_interval_seconds", 900))
    if args.once:
        n = poll_once(token)
        log.info("done; saved %d", n)
        return 0

    while True:
        try:
            n = poll_once(token)
            log.info("poll complete; saved %d", n)
        except Exception:
            log.exception("poll failed; will retry")
        time.sleep(interval)


if __name__ == "__main__":
    raise SystemExit(main())
