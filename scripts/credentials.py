#!/usr/bin/env python3
"""Encrypted credential store.

Stores per-module credentials in .liberation-kit/credentials.enc. Key is
stored in the OS keychain (macOS Keychain / Windows Credential Manager /
libsecret on Linux) via the `keyring` library; on systems without any
keychain support, falls back to an interactive prompt on each run.

Credentials never leave the user's machine.
"""
from __future__ import annotations

import argparse
import base64
import getpass
import json
import os
import secrets
import sys
from pathlib import Path

try:
    from cryptography.fernet import Fernet
except ImportError:
    print("Missing dependency: cryptography.", file=sys.stderr)
    sys.exit(2)

try:
    import keyring
    HAVE_KEYRING = True
except ImportError:
    HAVE_KEYRING = False


REPO_ROOT = Path(__file__).resolve().parent.parent
STORE_PATH = REPO_ROOT / ".liberation-kit" / "credentials.enc"
KEYRING_SERVICE = "data-liberation-kit"
KEYRING_USER = "encryption-key"


def _get_or_create_key() -> bytes:
    if HAVE_KEYRING:
        k = keyring.get_password(KEYRING_SERVICE, KEYRING_USER)
        if k:
            return k.encode()
        k = Fernet.generate_key()
        keyring.set_password(KEYRING_SERVICE, KEYRING_USER, k.decode())
        return k
    # Fallback: prompt
    pw = getpass.getpass("credential-store passphrase: ")
    return base64.urlsafe_b64encode(pw.encode().ljust(32, b"\0")[:32])


def encrypt_store(data: dict) -> None:
    key = _get_or_create_key()
    f = Fernet(key)
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STORE_PATH.write_bytes(f.encrypt(json.dumps(data).encode()))
    try:
        STORE_PATH.chmod(0o600)
    except Exception:
        pass


def decrypt_store(path: Path = STORE_PATH) -> dict:
    if not path.exists():
        return {}
    key = _get_or_create_key()
    f = Fernet(key)
    try:
        return json.loads(f.decrypt(path.read_bytes()).decode())
    except Exception:
        return {}


def set_credential(module: str, key: str, value: str) -> None:
    store = decrypt_store()
    store.setdefault(module, {})[key] = value
    encrypt_store(store)


def get_credential(module: str, key: str) -> str | None:
    store = decrypt_store()
    return store.get(module, {}).get(key)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--init", action="store_true", help="Create empty store if none exists.")
    p.add_argument("--set", nargs=3, metavar=("MODULE", "KEY", "VALUE"))
    p.add_argument("--get", nargs=2, metavar=("MODULE", "KEY"))
    p.add_argument("--list-modules", action="store_true")
    args = p.parse_args()

    if args.init:
        if not STORE_PATH.exists():
            encrypt_store({})
            print(f"initialised {STORE_PATH}")
        else:
            print("store already exists")
        return 0
    if args.set:
        set_credential(*args.set)
        print("set")
        return 0
    if args.get:
        v = get_credential(*args.get)
        print(v if v is not None else "")
        return 0
    if args.list_modules:
        store = decrypt_store()
        for m in store:
            print(m)
        return 0
    p.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
