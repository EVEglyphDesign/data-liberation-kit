"""Perplexity exporter.

Uses the authenticated threads endpoint that the Perplexity web app uses.
The user provides a session cookie at setup; the exporter walks the thread
list and pulls each thread's messages.

Endpoints are subject to change. If the shape changes, community PRs
welcome.
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

log = logging.getLogger("llm-history.perplexity")
REPO_ROOT = Path(__file__).resolve().parents[3]

try:
    import requests
except ImportError:
    requests = None


def _load_cookie() -> str | None:
    try:
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        from credentials import decrypt_store
        store = decrypt_store(REPO_ROOT / ".liberation-kit" / "credentials.enc")
        return store.get("perplexity", {}).get("session_cookie")
    except Exception:
        return None


def _normalise(conv_id: str, msg: dict, index: int) -> dict:
    ts = msg.get("created_at") or msg.get("timestamp")
    if isinstance(ts, str):
        try:
            ts_utc = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        except ValueError:
            ts_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    else:
        ts_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    role = "user" if msg.get("kind") == "query" or msg.get("role") == "user" else "assistant"
    text = msg.get("query") or msg.get("answer") or msg.get("text") or ""
    return {
        "conversation_id": conv_id,
        "message_id": f"{conv_id}-{index}",
        "timestamp_utc": ts_utc,
        "role": role,
        "content": text,
        "model": msg.get("model"),
        "tokens_in": None,
        "tokens_out": None,
        "attachments": [],
        "source": {"module": "llm-history", "provider": "perplexity"},
    }


def export():
    if requests is None:
        log.error("requests library not installed")
        return
    cookie = _load_cookie()
    if not cookie:
        log.info("no Perplexity session cookie in credential store; run ./scripts/setup.sh --with-perplexity")
        return

    sess = requests.Session()
    sess.headers["cookie"] = cookie
    sess.headers["user-agent"] = "data-liberation-kit/0.1"

    # List threads (endpoint shape may vary; this is the current documented one)
    page = 0
    while True:
        r = sess.get(f"https://www.perplexity.ai/rest/thread/list?limit=50&offset={page*50}", timeout=60)
        if r.status_code != 200:
            log.error("thread list failed: %s", r.status_code)
            break
        threads = r.json() if r.content else []
        if not threads:
            break
        for t in threads:
            tid = t.get("id") or t.get("uuid")
            if not tid:
                continue
            tr = sess.get(f"https://www.perplexity.ai/rest/thread/{tid}", timeout=60)
            if tr.status_code != 200:
                log.warning("thread %s fetch failed", tid)
                continue
            data = tr.json()
            msgs_in = data.get("entries") or data.get("messages") or []
            messages = [_normalise(tid, m, i) for i, m in enumerate(msgs_in)]
            messages.sort(key=lambda x: x["timestamp_utc"])
            if messages:
                yield tid, messages
            time.sleep(0.2)  # be polite
        page += 1
