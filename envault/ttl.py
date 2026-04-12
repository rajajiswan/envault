"""TTL (time-to-live) support for vaults — auto-expire after a set duration."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from envault.vault import _vault_path

_TTL_FILENAME = ".envault_ttl.json"


class TTLError(Exception):
    """Raised for TTL-related failures."""


def _ttl_path(vault_dir: Path) -> Path:
    return vault_dir / _TTL_FILENAME


def _load_store(vault_dir: Path) -> dict:
    p = _ttl_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_store(vault_dir: Path, store: dict) -> None:
    _ttl_path(vault_dir).write_text(json.dumps(store, indent=2))


def set_ttl(vault_name: str, seconds: int, vault_dir: Path) -> datetime:
    """Set a TTL for *vault_name*. Returns the computed expiry datetime (UTC)."""
    _vault_path(vault_name, vault_dir)  # raises FileNotFoundError if missing
    if seconds <= 0:
        raise TTLError("TTL must be a positive number of seconds.")
    expiry = datetime.now(timezone.utc) + timedelta(seconds=seconds)
    store = _load_store(vault_dir)
    store[vault_name] = expiry.isoformat()
    _save_store(vault_dir, store)
    return expiry


def get_ttl(vault_name: str, vault_dir: Path) -> Optional[datetime]:
    """Return the expiry datetime for *vault_name*, or None if not set."""
    store = _load_store(vault_dir)
    raw = store.get(vault_name)
    if raw is None:
        return None
    return datetime.fromisoformat(raw)


def is_expired(vault_name: str, vault_dir: Path) -> bool:
    """Return True if the vault's TTL has passed."""
    expiry = get_ttl(vault_name, vault_dir)
    if expiry is None:
        return False
    return datetime.now(timezone.utc) >= expiry


def clear_ttl(vault_name: str, vault_dir: Path) -> bool:
    """Remove the TTL entry for *vault_name*. Returns True if one existed."""
    store = _load_store(vault_dir)
    if vault_name not in store:
        return False
    del store[vault_name]
    _save_store(vault_dir, store)
    return True


def remaining_seconds(vault_name: str, vault_dir: Path) -> Optional[float]:
    """Seconds until expiry, or None if no TTL is set. Negative means expired."""
    expiry = get_ttl(vault_name, vault_dir)
    if expiry is None:
        return None
    return (expiry - datetime.now(timezone.utc)).total_seconds()
