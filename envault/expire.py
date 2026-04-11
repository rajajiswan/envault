"""Vault expiry — set and check time-based expiration on vaults."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from envault.vault import _vault_path

_EXPIRE_FILE = ".envault_expiry.json"


class ExpireError(Exception):
    """Raised when an expiry-related operation fails."""


def _expiry_path(vault_dir: Optional[str] = None) -> Path:
    base = Path(vault_dir) if vault_dir else Path.home() / ".envault"
    return base / _EXPIRE_FILE


def _load_store(vault_dir: Optional[str] = None) -> dict:
    path = _expiry_path(vault_dir)
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def _save_store(store: dict, vault_dir: Optional[str] = None) -> None:
    path = _expiry_path(vault_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(store, f, indent=2)


def set_expiry(vault_name: str, expires_at: datetime, vault_dir: Optional[str] = None) -> None:
    """Set an expiration datetime (UTC) for a vault."""
    vp = _vault_path(vault_name, vault_dir)
    if not vp.exists():
        raise ExpireError(f"Vault '{vault_name}' does not exist.")
    store = _load_store(vault_dir)
    store[vault_name] = expires_at.astimezone(timezone.utc).isoformat()
    _save_store(store, vault_dir)


def clear_expiry(vault_name: str, vault_dir: Optional[str] = None) -> None:
    """Remove the expiration setting for a vault."""
    store = _load_store(vault_dir)
    store.pop(vault_name, None)
    _save_store(store, vault_dir)


def get_expiry(vault_name: str, vault_dir: Optional[str] = None) -> Optional[datetime]:
    """Return the expiration datetime for a vault, or None if not set."""
    store = _load_store(vault_dir)
    raw = store.get(vault_name)
    if raw is None:
        return None
    return datetime.fromisoformat(raw)


def is_expired(vault_name: str, vault_dir: Optional[str] = None) -> bool:
    """Return True if the vault has passed its expiration datetime."""
    expiry = get_expiry(vault_name, vault_dir)
    if expiry is None:
        return False
    return datetime.now(timezone.utc) >= expiry


def check_not_expired(vault_name: str, vault_dir: Optional[str] = None) -> None:
    """Raise ExpireError if the vault is expired."""
    if is_expired(vault_name, vault_dir):
        expiry = get_expiry(vault_name, vault_dir)
        raise ExpireError(
            f"Vault '{vault_name}' expired at {expiry.isoformat()}. "
            "Use 'envault expire clear' to remove the expiry."
        )
