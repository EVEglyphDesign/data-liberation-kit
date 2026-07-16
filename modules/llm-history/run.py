#!/usr/bin/env python3
"""LLM chat-history dispatcher.

Runs the enabled per-provider exporters, normalises each conversation to the
common schema, and writes to history/llm/<provider>/YYYY/MM/*.jsonl plus a
manifest entry per conversation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Missing dependency: pyyaml.", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
log = logging.getLogger("llm-history")


def load_config() -> dict:
    with (REPO_ROOT / ".liberation-kit" / "config.yaml").open() as f:
        return yaml.safe_load(f)


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def write_conversation(provider: str, conv_id: str, messages: list[dict]) -> Path:
    """Write a conversation JSONL under history/llm/<provider>/YYYY/MM/."""
    if not messages:
        raise ValueError("empty conversation")
    first_ts = messages[0]["timestamp_utc"]
    dt = datetime.fromisoformat(first_ts.replace("Z", "+00:00"))
    out_dir = REPO_ROOT / "history" / "llm" / provider / dt.strftime("%Y") / dt.strftime("%m")
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{conv_id}.jsonl"
    with out.open("w") as f:
        for msg in messages:
            f.write(json.dumps(msg, sort_keys=True) + "\n")
    return out


def manifest_entry(provider: str, out: Path, messages: list[dict]) -> dict:
    body = out.read_bytes()
    return {
        "id": hashlib.sha256(body).hexdigest()[:16],
        "path": out.relative_to(REPO_ROOT).as_posix(),
        "content_hash": "sha256:" + hashlib.sha256(body).hexdigest(),
        "size_bytes": len(body),
        "mime_type": "application/jsonl",
        "captured_at_utc": messages[0]["timestamp_utc"],
        "extracted_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": {"module": "llm-history", "provider": provider,
                    "message_count": len(messages)},
        "notes": [],
    }


def dispatch(provider: str) -> int:
    """Import and invoke the per-provider exporter. Returns conversation count."""
    module_name = f"providers.{provider}"
    try:
        mod = __import__(module_name, fromlist=["export"])
    except ImportError:
        log.warning("provider %s has no exporter; skipping. See WANTED.md.", provider)
        return 0
    conversations = mod.export()  # generator of (conv_id, [messages])
    count = 0
    for conv_id, messages in conversations:
        try:
            out = write_conversation(provider, conv_id, messages)
            entry = manifest_entry(provider, out, messages)
            first_ts = messages[0]["timestamp_utc"]
            dt = datetime.fromisoformat(first_ts.replace("Z", "+00:00"))
            mp = REPO_ROOT / "history" / "manifests" / f"{dt.strftime('%Y-%m')}.jsonl"
            mp.parent.mkdir(parents=True, exist_ok=True)
            with mp.open("a") as f:
                f.write(json.dumps(entry, sort_keys=True) + "\n")
            count += 1
        except Exception:
            log.exception("failed to write conversation %s from %s", conv_id, provider)
    log.info("%s: wrote %d conversation(s)", provider, count)
    return count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", help="Run only this provider.")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    cfg = load_config().get("llm-history", {})
    if not cfg.get("enabled"):
        log.info("llm-history disabled; exiting.")
        return 0

    providers = cfg.get("models", {})
    if args.provider:
        providers = {args.provider: True}

    total = 0
    for name, on in providers.items():
        if not on:
            continue
        total += dispatch(name)
    log.info("done; %d conversation(s) total", total)
    return 0


if __name__ == "__main__":
    # Make providers/ importable
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
