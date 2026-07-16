"""Gemini exporter (via Google Takeout).

Reads the Gemini section of a Google Takeout archive. Takeout emits Gemini
history as HTML plus optional JSON depending on export flags.
"""
from __future__ import annotations

import json
import logging
import os
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path

log = logging.getLogger("llm-history.gemini")
REPO_ROOT = Path(__file__).resolve().parents[3]


def _parse_html(html: str, conv_id: str):
    """Extract messages from a Gemini HTML history file."""
    # Very light HTML parsing; Google's format has message blocks with data-role attributes.
    messages = []
    for match in re.finditer(
        r'<div[^>]+data-role="([^"]+)"[^>]+data-timestamp="([^"]+)"[^>]*>(.*?)</div>',
        html, flags=re.DOTALL,
    ):
        role, ts, content = match.group(1), match.group(2), match.group(3)
        text = re.sub(r"<[^>]+>", " ", content)
        text = re.sub(r"\s+", " ", text).strip()
        try:
            ts_utc = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        except ValueError:
            ts_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        messages.append({
            "conversation_id": conv_id,
            "message_id": f"{conv_id}-{len(messages)}",
            "timestamp_utc": ts_utc,
            "role": role,
            "content": text,
            "model": "gemini",
            "tokens_in": None,
            "tokens_out": None,
            "attachments": [],
            "source": {"module": "llm-history", "provider": "gemini"},
        })
    return messages


def _from_zip(zip_path: Path):
    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if "Gemini" in name and name.endswith(".html"):
                conv_id = Path(name).stem
                with zf.open(name) as f:
                    html = f.read().decode("utf-8", errors="replace")
                messages = _parse_html(html, conv_id)
                if messages:
                    yield conv_id, messages


def export():
    zip_env = os.environ.get("DLK_GEMINI_EXPORT_ZIP")
    if zip_env and Path(zip_env).exists():
        yield from _from_zip(Path(zip_env))
        return
    incoming = REPO_ROOT / "_incoming" / "gemini"
    if incoming.exists():
        for z in sorted(incoming.glob("*.zip")):
            log.info("using Gemini/Takeout archive at %s", z)
            yield from _from_zip(z)
            return
    log.info("no Gemini export found. Request Google Takeout (Gemini section) at https://takeout.google.com/, place the zip in _incoming/gemini/, then re-run.")
