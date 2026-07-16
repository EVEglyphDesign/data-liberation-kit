#!/usr/bin/env python3
"""Apple media continuous off-ramp.

Polls the iCloud Photos API on the configured interval, downloads new assets
into the repo under media/photos/YYYY/MM/DD/, and writes manifest entries.

Uses pyicloud for the API surface. Credentials are loaded from the encrypted
credential store; nothing is transmitted anywhere except iCloud itself and the
user's configured storage target.

This is the reference implementation. Community forks are welcome to improve
speed, error handling, or format coverage.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Missing dependency: pyyaml. Run ./scripts/setup.sh first.", file=sys.stderr)
    sys.exit(2)

try:
    from pyicloud import PyiCloudService
except ImportError:
    print("Missing dependency: pyicloud. Run ./scripts/setup.sh first.", file=sys.stderr)
    sys.exit(2)


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = REPO_ROOT / ".liberation-kit" / "config.yaml"
CRED_PATH = REPO_ROOT / ".liberation-kit" / "credentials.enc"

log = logging.getLogger("apple-media")


def load_config() -> dict:
    with CONFIG_PATH.open() as f:
        return yaml.safe_load(f)


def load_credentials(module_name: str) -> dict:
    """Load credentials for the given module from the local encrypted store.

    The credential store is decrypted at daemon start using an OS-keychain-held
    key. Details in scripts/credentials.py.
    """
    from scripts.credentials import decrypt_store  # local helper
    store = decrypt_store(CRED_PATH)
    return store.get(module_name, {})


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def already_have(manifest_path: Path, asset_id: str) -> bool:
    if not manifest_path.exists():
        return False
    with manifest_path.open() as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry.get("source", {}).get("original_id") == asset_id:
                    return True
            except json.JSONDecodeError:
                continue
    return False


def write_manifest_entry(manifest_path: Path, entry: dict) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("a") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")


def download_asset(asset, target_dir: Path) -> Path:
    """Download an iCloud photo/video asset into target_dir. Returns the path."""
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = asset.filename
    out = target_dir / filename
    # If the exact filename exists, prefix with a short hash to avoid collision.
    if out.exists():
        # Read a bit to hash and produce a suffix
        with asset.download().raw as raw:
            data = raw.read()
        h = hashlib.sha256(data).hexdigest()[:8]
        stem = out.stem
        ext = out.suffix
        out = target_dir / f"{stem}.{h}{ext}"
        out.write_bytes(data)
    else:
        with asset.download().raw as raw:
            out.write_bytes(raw.read())
    return out


def entry_for(asset, downloaded: Path, cfg: dict) -> dict:
    captured = asset.created
    if captured.tzinfo is None:
        captured = captured.replace(tzinfo=timezone.utc)
    captured_utc = captured.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    now_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    rel = downloaded.relative_to(REPO_ROOT).as_posix()
    return {
        "id": sha256_file(downloaded)[:16],
        "path": rel,
        "content_hash": "sha256:" + sha256_file(downloaded),
        "size_bytes": downloaded.stat().st_size,
        "mime_type": getattr(asset, "mime_type", None) or "application/octet-stream",
        "captured_at_utc": captured_utc,
        "captured_at_local": captured.isoformat(),
        "extracted_at_utc": now_utc,
        "source": {
            "module": "apple-media",
            "path": "icloud-photos-api",
            "original_id": str(asset.id),
            "original_filename": asset.filename,
        },
        "original_format": getattr(asset, "mime_type", None),
        "converted": False,
        "notes": [],
    }


def poll_once(api: PyiCloudService, cfg: dict) -> int:
    photos = api.photos.all
    count = 0
    for asset in photos:
        try:
            captured = asset.created
            date_dir = REPO_ROOT / "media" / (
                "videos" if (asset.mime_type or "").startswith("video/") else "photos"
            ) / captured.strftime("%Y") / captured.strftime("%m") / captured.strftime("%d")
            manifest_path = REPO_ROOT / "media" / "manifests" / f"{captured.strftime('%Y-%m')}.jsonl"
            if already_have(manifest_path, str(asset.id)):
                continue
            path = download_asset(asset, date_dir)
            entry = entry_for(asset, path, cfg)
            write_manifest_entry(manifest_path, entry)
            log.info("saved %s", entry["path"])
            count += 1
        except Exception:
            log.exception("failed to save asset %s", getattr(asset, "id", "?"))
    return count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Poll once and exit.")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    cfg = load_config()
    apple_cfg = cfg.get("apple-media", {})
    if not apple_cfg.get("enabled"):
        log.info("apple-media is disabled in config; exiting.")
        return 0

    creds = load_credentials("apple-media")
    if not creds.get("apple_id"):
        log.error("no apple_id in credential store; run ./scripts/setup.sh first.")
        return 3

    api = PyiCloudService(creds["apple_id"], creds.get("password"))
    if api.requires_2fa:
        log.error("iCloud requires 2FA. Run ./modules/apple-media/first-run.py once.")
        return 4

    interval = int(apple_cfg.get("continuous", {}).get("poll_interval_seconds", 300))

    if args.once:
        saved = poll_once(api, apple_cfg)
        log.info("done; saved %d asset(s)", saved)
        return 0

    log.info("apple-media continuous mode: polling every %d seconds", interval)
    while True:
        try:
            saved = poll_once(api, apple_cfg)
            log.info("poll complete; saved %d asset(s)", saved)
        except Exception:
            log.exception("poll failed; will retry")
        time.sleep(interval)


if __name__ == "__main__":
    raise SystemExit(main())
