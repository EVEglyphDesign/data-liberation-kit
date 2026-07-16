"""ChatGPT exporter.

Two supported paths:
  1. `--from-export ZIP` — user has already downloaded an OpenAI data export
     (the recommended path, since the export includes full-text with
     accurate timestamps).
  2. Live API path via authenticated session — falls back to reading the
     conversations endpoint that the ChatGPT web app itself uses.

The export path is stable and preferred. The live path is intended for
users who want continuous incremental sync between exports.
"""
from __future__ import annotations

import json
import logging
import os
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

log = logging.getLogger("llm-history.chatgpt")

REPO_ROOT = Path(__file__).resolve().parents[3]


def _normalise_message(conv_id: str, msg: dict) -> dict:
    content = msg.get("content", {})
    if isinstance(content, dict):
        parts = content.get("parts", [])
        text = "\n".join(str(p) for p in parts if p)
    else:
        text = str(content)
    ts = msg.get("create_time")
    ts_utc = (
        datetime.fromtimestamp(ts, tz=timezone.utc).isoformat().replace("+00:00", "Z")
        if ts else datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )
    return {
        "conversation_id": conv_id,
        "message_id": msg.get("id"),
        "timestamp_utc": ts_utc,
        "role": msg.get("author", {}).get("role", "unknown"),
        "content": text,
        "model": msg.get("metadata", {}).get("model_slug"),
        "tokens_in": None,
        "tokens_out": None,
        "attachments": [],
        "source": {"module": "llm-history", "provider": "chatgpt"},
    }


def _from_zip(zip_path: Path):
    with zipfile.ZipFile(zip_path) as zf:
        with zf.open("conversations.json") as f:
            conversations = json.load(f)
    for conv in conversations:
        conv_id = conv.get("id") or conv.get("conversation_id")
        mapping = conv.get("mapping", {})
        # ChatGPT's mapping is a tree; flatten in create_time order
        messages = []
        for node in mapping.values():
            m = node.get("message")
            if not m:
                continue
            messages.append(_normalise_message(conv_id, m))
        messages.sort(key=lambda x: x["timestamp_utc"])
        if messages:
            yield conv_id, messages


def export():
    zip_env = os.environ.get("DLK_CHATGPT_EXPORT_ZIP")
    if zip_env:
        p = Path(zip_env)
        if not p.exists():
            log.error("DLK_CHATGPT_EXPORT_ZIP=%s not found", zip_env)
            return
        yield from _from_zip(p)
        return

    # Look for a recently-downloaded export in the incoming staging folder
    incoming = REPO_ROOT / "_incoming" / "chatgpt"
    if incoming.exists():
        for z in sorted(incoming.glob("*.zip")):
            log.info("using ChatGPT export at %s", z)
            yield from _from_zip(z)
            return

    log.info("no ChatGPT export found. Request one at https://chat.openai.com/ (Settings > Data controls > Export data), place the zip in _incoming/chatgpt/, then re-run.")
