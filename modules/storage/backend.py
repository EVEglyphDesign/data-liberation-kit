"""Storage backend abstraction.

Modules write files into the repo's `media/` and `history/` trees. This
module provides the post-write hook that pushes bytes to the configured
storage target (GitHub-LFS, S3-compatible, or local-index).

The base-model layout is identical across backends. Only the "where do
the bytes physically live after write" differs.
"""
from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Missing dependency: pyyaml.", file=sys.stderr)
    sys.exit(2)

log = logging.getLogger("storage")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def load_config() -> dict:
    with (REPO_ROOT / ".liberation-kit" / "config.yaml").open() as f:
        return yaml.safe_load(f)


def _ensure_gitignore_lfs() -> None:
    gi = REPO_ROOT / ".gitattributes"
    entries = [
        "media/photos/** filter=lfs diff=lfs merge=lfs -text",
        "media/videos/** filter=lfs diff=lfs merge=lfs -text",
    ]
    existing = gi.read_text() if gi.exists() else ""
    with gi.open("a") as f:
        for e in entries:
            if e not in existing:
                f.write(e + "\n")


def push_github_lfs(paths: list[Path]) -> None:
    if not shutil.which("git"):
        log.error("git not on PATH")
        return
    if not shutil.which("git-lfs"):
        log.warning("git-lfs not installed; skipping push. Install git-lfs and re-run.")
        return
    _ensure_gitignore_lfs()
    subprocess.run(["git", "-C", str(REPO_ROOT), "add", "--"] + [str(p) for p in paths], check=True)
    if subprocess.run(["git", "-C", str(REPO_ROOT), "diff", "--cached", "--quiet"]).returncode != 0:
        subprocess.run(["git", "-C", str(REPO_ROOT), "commit", "-m", "data-liberation-kit: batch write"], check=True)
        subprocess.run(["git", "-C", str(REPO_ROOT), "push"], check=True)


def push_s3_compatible(paths: list[Path], cfg: dict) -> None:
    try:
        import boto3
    except ImportError:
        log.error("boto3 not installed; run ./scripts/setup.sh --with-s3")
        return
    from scripts.credentials import decrypt_store
    creds = decrypt_store(REPO_ROOT / ".liberation-kit" / "credentials.enc").get("storage-s3", {})
    session = boto3.session.Session(
        aws_access_key_id=creds.get("access_key_id"),
        aws_secret_access_key=creds.get("secret_access_key"),
        region_name=cfg.get("region", "auto"),
    )
    s3 = session.client("s3", endpoint_url=cfg.get("endpoint"))
    bucket = cfg["bucket"]
    prefix = cfg.get("prefix", "")
    for p in paths:
        key = prefix + str(p.relative_to(REPO_ROOT))
        s3.upload_file(str(p), bucket, key)
        log.info("uploaded %s -> s3://%s/%s", p.name, bucket, key)


def push_local_index(paths: list[Path], cfg: dict) -> None:
    base = Path(cfg["base_path"])
    if cfg.get("mount_check", True) and not base.exists():
        log.error("local target %s not mounted; refusing to write.", base)
        return
    for p in paths:
        rel = p.relative_to(REPO_ROOT)
        dst = base / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(p), str(dst))
        # Leave a symlink pointer in the repo so paths resolve
        p.symlink_to(dst)
        log.info("moved %s -> %s", rel, dst)


def push(paths: list[Path]) -> None:
    cfg = load_config().get("storage", {})
    target = cfg.get("target", "github-lfs")
    if target == "github-lfs":
        push_github_lfs(paths)
    elif target == "s3-compatible":
        push_s3_compatible(paths, cfg.get("s3_compatible", {}))
    elif target == "local-index":
        push_local_index(paths, cfg.get("local_index", {}))
    else:
        log.error("unknown storage target: %s", target)
