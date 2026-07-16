"""Claude (Anthropic) exporter.

Reads an Anthropic data export zip. Anthropic emits conversations.json plus
per-conversation JSON files depending on the export version; this module
handles both layouts.
"""
from __future__ import annotations

import json
import logging
import os
import zipfile
from datetime import datetime, timezone
from pathlib import Path

log = logging.getLogger("llm-history.claude")
REPO_ROOT = Path(__file__).resolve().parents[3]


def _normalise(conv_id: str, msg: dict) -> dict:
    text = msg.get("text") or msg.get("content") or ""
    if isinstance(text, list):
        text = "\n".join(t.get("text", "") if isinstance(t, dict) else str(t) for t in text)
    ts = msg.get("created_at") or msg.get("timestamp")
    if isinstance(ts, (int, float)):
        ts_utc = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat().replace("+00:00", "Z")
    elif isinstance(ts, str):
        try:
            ts_utc = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        except ValueError:
            ts_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    else:
        ts_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "conversation_id": conv_id,
        "message_id": msg.get("uuid") or msg.get("id"),
        "timestamp_utc": ts_utc,
        "role": msg.get("sender") or msg.get("role", "unknown"),
        "content": text,
        "model": msg.get("model"),
        "tokens_in": None,
        "tokens_out": None,
        "attachments": [a.get("file_name") for a in msg.get("attachments", []) if isinstance(a, dict)],
        "source": {"module": "llm-history", "provider": "claude"},
    }


def _from_zip(zip_path: Path):
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        # Modern export layout: conversations.json at root
        if "conversations.json" in names:
            with zf.open("conversations.json") as f:
                convs = json.load(f)
            for conv in convs:
                conv_id = conv.get("uuid") or conv.get("id")
                messages = [_normalise(conv_id, m) for m in conv.get("chat_messages", [])]
                messages.sort(key=lambda x: x["timestamp_utc"])
                if messages:
                    yield conv_id, messages
        else:
            # Older layout: per-conversation files under conversations/
            for name in names:
                if name.startswith("conversations/") and name.endswith(".json"):
                    with zf.open(name) as f:
                        conv = json.load(f)
                    conv_id = conv.get("uuid") or Path(name).stem
                    messages = [_normalise(conv_id, m) for m in conv.get("messages", [])]
                    messages.sort(key=lambda x: x["timestamp_utc"])
                    if messages:
                        yield conv_id, messages


def export():
    zip_env = os.environ.get("DLK_CLAUDE_EXPORT_ZIP")
    if zip_env and Path(zip_env).exists():
        yield from _from_zip(Path(zip_env))
        return
    incoming = REPO_ROOT / "_incoming" / "claude"
    if incoming.exists():
        for z in sorted(incoming.glob("*.zip")):
            log.info("using Claude export at %s", z)
            yield from _from_zip(z)
            return
    log.info("no Claude export found. Request one at https://claude.ai/ (Settings > Data > Export), place the zip in _incoming/claude/, then re-run.")
