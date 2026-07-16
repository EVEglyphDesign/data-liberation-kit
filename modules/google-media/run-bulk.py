#!/usr/bin/env python3
"""Google Takeout bulk pull for Photos.

Drives the browser-based Takeout request-and-download loop using the user's
existing Google session cookies (which the user provides at setup via a
supported cookie-export or via the Chrome DevTools Protocol path). Polls
until the archive is ready, downloads, unpacks, and normalises into the
base-model layout.

Playwright is used for the browser automation surface because it works
cross-platform and can drive a real Chromium the user is logged into.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import shutil
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Missing dependency: pyyaml.", file=sys.stderr)
    sys.exit(2)

log = logging.getLogger("google-bulk")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def load_config() -> dict:
    with (REPO_ROOT / ".liberation-kit" / "config.yaml").open() as f:
        return yaml.safe_load(f)


def request_export_via_playwright(staging: Path) -> Path:
    """Drive takeout.google.com through the request flow.

    Requires the user's Chrome/Chromium user-data-dir path to reuse an
    existing logged-in session. Configured at setup.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        log.error("playwright not installed; run ./scripts/setup.sh --with-playwright")
        raise

    cfg = load_config().get("google-media", {}).get("bulk", {})
    user_data_dir = cfg.get("chrome_user_data_dir")
    if not user_data_dir:
        raise RuntimeError("chrome_user_data_dir not set; run setup with --with-google")

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir, headless=False,
            downloads_path=str(staging),
        )
        page = browser.new_page()
        page.goto("https://takeout.google.com/settings/takeout")
        # Deselect all, then select only Photos
        page.click("text=Deselect all")
        page.click("text=Google Photos")
        page.click("text=Next step")
        page.click("text=Create export")
        log.info("Takeout export requested. Waiting for email/download...")
        # Real automation is left minimal here; the loop polls the
        # Takeout downloads page every 15 minutes.
        while True:
            time.sleep(900)
            page.goto("https://takeout.google.com/manage")
            links = page.locator("a:has-text('Download')")
            if links.count() > 0:
                with page.expect_download() as dlinfo:
                    links.first.click()
                dl = dlinfo.value
                target = staging / dl.suggested_filename
                dl.save_as(str(target))
                log.info("downloaded %s", target)
                browser.close()
                return target


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def unpack_and_normalise(zip_path: Path, staging: Path) -> int:
    unpack_dir = staging / "unpacked"
    unpack_dir.mkdir(exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(unpack_dir)

    photos_root = unpack_dir / "Takeout" / "Google Photos"
    if not photos_root.exists():
        log.error("Takeout archive did not contain Google Photos folder")
        return 0

    count = 0
    for src in photos_root.rglob("*"):
        if not src.is_file():
            continue
        # Takeout emits .json companions with metadata; use them for capture time
        if src.suffix == ".json":
            continue
        json_companion = src.with_name(src.name + ".supplemental-metadata.json")
        if not json_companion.exists():
            json_companion = src.with_suffix(src.suffix + ".json")
        captured = None
        if json_companion.exists():
            try:
                meta = json.loads(json_companion.read_text())
                ts = meta.get("photoTakenTime", {}).get("timestamp")
                if ts:
                    captured = datetime.fromtimestamp(int(ts), tz=timezone.utc)
            except Exception:
                pass
        if not captured:
            captured = datetime.fromtimestamp(src.stat().st_mtime, tz=timezone.utc)

        is_video = src.suffix.lower() in {".mp4", ".mov", ".m4v", ".hevc"}
        subdir = "videos" if is_video else "photos"
        date_dir = (REPO_ROOT / "media" / subdir /
                    captured.strftime("%Y") / captured.strftime("%m") / captured.strftime("%d"))
        date_dir.mkdir(parents=True, exist_ok=True)

        h = sha256(src)
        dst = date_dir / src.name
        if dst.exists():
            dst = date_dir / f"{src.stem}.{h[:8]}{src.suffix}"
        shutil.copy2(src, dst)

        entry = {
            "id": h[:16],
            "path": dst.relative_to(REPO_ROOT).as_posix(),
            "content_hash": "sha256:" + h,
            "size_bytes": dst.stat().st_size,
            "mime_type": "video/mp4" if is_video else "image/jpeg",
            "captured_at_utc": captured.isoformat().replace("+00:00", "Z"),
            "captured_at_local": captured.isoformat(),
            "extracted_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "source": {
                "module": "google-media",
                "path": "takeout-bulk",
                "original_filename": src.name,
            },
            "original_format": src.suffix.lstrip("."),
            "converted": False,
            "notes": [],
        }
        manifest_path = REPO_ROOT / "media" / "manifests" / f"{captured.strftime('%Y-%m')}.jsonl"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with manifest_path.open("a") as f:
            f.write(json.dumps(entry, sort_keys=True) + "\n")
        count += 1
    log.info("normalised %d asset(s)", count)
    return count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", help="Use an already-downloaded Takeout zip instead of requesting one.")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    staging = REPO_ROOT / ".liberation-kit" / "staging" / f"google-bulk-{datetime.utcnow():%Y%m%dT%H%M%SZ}"
    staging.mkdir(parents=True, exist_ok=True)

    zip_path = Path(args.zip).resolve() if args.zip else request_export_via_playwright(staging)
    unpack_and_normalise(zip_path, staging)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
