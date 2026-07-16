#!/usr/bin/env python3
"""Extract media assets from an idevicebackup2 staging directory into the repo.

Walks the backup manifest, locates DCIM/PhotoData assets, copies them into the
repo's media/photos and media/videos trees keyed by capture date, and writes
manifest entries.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import plistlib
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

log = logging.getLogger("apple-bulk")

VIDEO_EXTS = {".mov", ".mp4", ".m4v", ".hevc"}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def guess_mime(ext: str) -> str:
    e = ext.lower()
    return {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".heic": "image/heic", ".heif": "image/heif",
        ".png": "image/png", ".gif": "image/gif",
        ".mov": "video/quicktime", ".mp4": "video/mp4",
        ".m4v": "video/x-m4v", ".hevc": "video/hevc",
    }.get(e, "application/octet-stream")


def find_photos_db(staging: Path) -> Path | None:
    """Locate Photos.sqlite in the backup by its known relative path hash.

    idevicebackup2 stores files under sha1(domain-relativePath).
    """
    # Domain: CameraRollDomain; relativePath: Media/PhotoData/Photos.sqlite
    import hashlib as _h
    key = _h.sha1(b"CameraRollDomain-Media/PhotoData/Photos.sqlite").hexdigest()
    subdir = key[:2]
    candidate = staging / subdir / key
    if candidate.exists():
        return candidate
    # Fallback: search
    for p in staging.rglob("Photos.sqlite"):
        return p
    return None


def resolve_backup_file(staging: Path, domain: str, relpath: str) -> Path | None:
    import hashlib as _h
    key = _h.sha1(f"{domain}-{relpath}".encode()).hexdigest()
    p = staging / key[:2] / key
    return p if p.exists() else None


def write_manifest_entry(manifest_path: Path, entry: dict) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("a") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")


def already_have(manifest_path: Path, asset_uuid: str) -> bool:
    if not manifest_path.exists():
        return False
    with manifest_path.open() as f:
        for line in f:
            try:
                e = json.loads(line)
                if e.get("source", {}).get("original_id") == asset_uuid:
                    return True
            except json.JSONDecodeError:
                continue
    return False


def process(staging: Path, repo_root: Path, device_udid: str) -> int:
    photos_db = find_photos_db(staging)
    if not photos_db:
        log.error("could not locate Photos.sqlite in staging; is the backup complete?")
        return 0

    log.info("using Photos.sqlite at %s", photos_db)
    conn = sqlite3.connect(str(photos_db))
    conn.row_factory = sqlite3.Row

    # Schema varies by iOS version; we probe a couple of tables.
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if "ZASSET" not in tables:
        log.error("unexpected Photos.sqlite schema: no ZASSET table")
        return 0

    q = (
        "SELECT ZUUID, ZORIGINALFILENAME, ZFILENAME, ZDATECREATED, ZDIRECTORY, ZKIND "
        "FROM ZASSET WHERE ZORIGINALFILENAME IS NOT NULL"
    )
    count = 0
    for row in conn.execute(q):
        uuid = row["ZUUID"]
        fname = row["ZFILENAME"] or row["ZORIGINALFILENAME"]
        directory = row["ZDIRECTORY"] or ""
        # ZDATECREATED is Apple Cocoa timestamp: seconds since 2001-01-01 UTC
        cocoa_ts = row["ZDATECREATED"] or 0
        captured = datetime(2001, 1, 1, tzinfo=timezone.utc)
        captured = captured.fromtimestamp(978307200 + float(cocoa_ts), tz=timezone.utc)

        relpath = f"Media/DCIM/{directory}/{fname}"
        src = resolve_backup_file(staging, "CameraRollDomain", relpath)
        if not src:
            # Try PhotoData path
            relpath_alt = f"Media/PhotoData/{directory}/{fname}"
            src = resolve_backup_file(staging, "CameraRollDomain", relpath_alt)
        if not src:
            log.debug("skip %s (backup file not found)", fname)
            continue

        ext = Path(fname).suffix
        subdir = "videos" if ext.lower() in VIDEO_EXTS else "photos"
        date_dir = (repo_root / "media" / subdir /
                    captured.strftime("%Y") / captured.strftime("%m") / captured.strftime("%d"))
        date_dir.mkdir(parents=True, exist_ok=True)

        manifest_path = repo_root / "media" / "manifests" / f"{captured.strftime('%Y-%m')}.jsonl"
        if already_have(manifest_path, uuid):
            continue

        out = date_dir / fname
        if out.exists():
            h = sha256(src)[:8]
            out = date_dir / f"{Path(fname).stem}.{h}{ext}"
        shutil.copy2(src, out)

        entry = {
            "id": sha256(out)[:16],
            "path": out.relative_to(repo_root).as_posix(),
            "content_hash": "sha256:" + sha256(out),
            "size_bytes": out.stat().st_size,
            "mime_type": guess_mime(ext),
            "captured_at_utc": captured.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
            "captured_at_local": captured.isoformat(),
            "extracted_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "source": {
                "module": "apple-media",
                "path": "libimobiledevice-bulk",
                "device_udid": device_udid,
                "original_id": uuid,
                "original_filename": row["ZORIGINALFILENAME"],
            },
            "original_format": guess_mime(ext),
            "converted": False,
            "notes": [],
        }
        write_manifest_entry(manifest_path, entry)
        count += 1
        if count % 50 == 0:
            log.info("processed %d assets so far", count)

    log.info("bulk extract complete: %d asset(s)", count)
    return count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--staging", required=True)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--device-udid", required=True)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    process(Path(args.staging), Path(args.repo_root), args.device_udid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
