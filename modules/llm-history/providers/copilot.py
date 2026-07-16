"""Microsoft Copilot exporter.

Reads a Microsoft data export (M365/Copilot subset). The export is
requested at https://account.microsoft.com/privacy — the resulting archive
contains a `Copilot/` folder with per-conversation JSON.
"""
from __future__ import annotations

import json
import logging
import os
import zipfile
from datetime import datetime, timezone
from pathlib import Path

log = logging.getLogger("llm-history.copilot")
REPO_ROOT = Path(__file__).resolve().parents[3]


def _normalise(conv_id: str, msg: dict) -> dict:
    ts = msg.get("createdAt") or msg.get("timestamp")
    try:
        ts_utc = datetime.fromisoformat(str(ts).replace("Z", "+00:00")).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    except Exception:
        ts_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "conversation_id": conv_id,
        "message_id": msg.get("id"),
        "timestamp_utc": ts_utc,
        "role": msg.get("author", "unknown"),
        "content": msg.get("text") or msg.get("content", ""),
        "model": msg.get("model"),
        "tokens_in": None,
        "tokens_out": None,
        "attachments": [],
        "source": {"module": "llm-history", "provider": "copilot"},
    }


def _from_zip(zip_path: Path):
    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if name.startswith("Copilot/") and name.endswith(".json"):
                with zf.open(name) as f:
                    conv = json.load(f)
                conv_id = conv.get("id") or Path(name).stem
                messages = [_normalise(conv_id, m) for m in conv.get("messages", [])]
                messages.sort(key=lambda x: x["timestamp_utc"])
                if messages:
                    yield conv_id, messages


def export():
    zip_env = os.environ.get("DLK_COPILOT_EXPORT_ZIP")
    if zip_env and Path(zip_env).exists():
        yield from _from_zip(Path(zip_env))
        return
    incoming = REPO_ROOT / "_incoming" / "copilot"
    if incoming.exists():
        for z in sorted(incoming.glob("*.zip")):
            log.info("using Copilot export at %s", z)
            yield from _from_zip(z)
            return
    log.info("no Copilot export found. Request one at https://account.microsoft.com/privacy, place the zip in _incoming/copilot/, then re-run.")
