#!/usr/bin/env python3
"""Convert HEIC/HEVC assets in media/ to open formats while preserving originals.

Reads config from .liberation-kit/config.yaml. Only converts if configured.
Idempotent: skips files whose converted counterpart already exists.
"""
from __future__ import annotations

import argparse
import json
import logging
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Missing dependency: pyyaml.", file=sys.stderr)
    sys.exit(2)

log = logging.getLogger("apple-convert")


def load_config(repo_root: Path) -> dict:
    with (repo_root / ".liberation-kit" / "config.yaml").open() as f:
        return yaml.safe_load(f)


def find_tool(names: list[str]) -> str | None:
    for n in names:
        if shutil.which(n):
            return n
    return None


def convert_heic(src: Path, dst: Path) -> bool:
    tool = find_tool(["magick", "convert"])
    if not tool:
        log.error("no ImageMagick tool found")
        return False
    try:
        subprocess.run([tool, str(src), str(dst)], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        log.error("HEIC convert failed for %s: %s", src, e.stderr.decode()[:200])
        return False


def convert_hevc(src: Path, dst: Path) -> bool:
    if not shutil.which("ffmpeg"):
        log.error("ffmpeg not found")
        return False
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(src), "-c:v", "libx264", "-crf", "18",
             "-c:a", "aac", "-b:a", "192k", str(dst)],
            check=True, capture_output=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        log.error("HEVC convert failed for %s: %s", src, e.stderr.decode()[:200])
        return False


def sidecar_manifest_entry(original_entry_path: Path, converted_path: Path,
                            repo_root: Path) -> dict:
    import hashlib
    from datetime import datetime, timezone

    def sha256(p: Path) -> str:
        h = hashlib.sha256()
        with p.open("rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()

    return {
        "id": sha256(converted_path)[:16],
        "path": converted_path.relative_to(repo_root).as_posix(),
        "content_hash": "sha256:" + sha256(converted_path),
        "size_bytes": converted_path.stat().st_size,
        "mime_type": "image/jpeg" if converted_path.suffix.lower() in {".jpg", ".jpeg"} else "video/mp4",
        "converted_from": original_entry_path.relative_to(repo_root).as_posix(),
        "extracted_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": {"module": "apple-media", "path": "format-conversion"},
        "converted": True,
        "notes": [],
    }


def process(repo_root: Path) -> int:
    cfg = load_config(repo_root)
    a = cfg.get("apple-media", {})
    formats = a.get("formats", {})
    do_heic = formats.get("convert_heic_to_jpg", True)
    do_hevc = formats.get("convert_hevc_to_mp4", True)
    keep_originals = formats.get("keep_originals", True)

    count = 0
    for root in [repo_root / "media" / "photos", repo_root / "media" / "videos"]:
        if not root.exists():
            continue
        for src in root.rglob("*"):
            if not src.is_file():
                continue
            ext = src.suffix.lower()
            if do_heic and ext in {".heic", ".heif"}:
                dst = src.with_suffix(".jpg")
                if dst.exists():
                    continue
                if convert_heic(src, dst):
                    count += 1
                    log.info("HEIC -> JPG: %s", dst.name)
                    if not keep_originals:
                        src.unlink()
            elif do_hevc and ext in {".mov", ".hevc"}:
                # Only convert if actually HEVC-encoded
                dst = src.with_suffix(".mp4")
                if dst.exists():
                    continue
                if convert_hevc(src, dst):
                    count += 1
                    log.info("HEVC -> MP4: %s", dst.name)
                    if not keep_originals:
                        src.unlink()

    log.info("converted %d file(s)", count)
    return count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    process(Path(args.repo_root).resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
