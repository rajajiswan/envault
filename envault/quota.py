"""Vault quota management — enforce limits on number of keys per vault."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envault.vault import _vault_path, load_vault

_DEFAULT_QUOTA = 100


class QuotaError(Exception):
    """Raised when a quota operation fails."""


def _quota_path(vault_dir: Optional[Path] = None) -> Path:
    base = vault_dir or Path.home() / ".envault"
    return base / "quotas.json"


def _load_store(vault_dir: Optional[Path] = None) -> dict:
    path = _quota_path(vault_dir)
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def _save_store(store: dict, vault_dir: Optional[Path] = None) -> None:
    path = _quota_path(vault_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(store, fh, indent=2)


def set_quota(vault_name: str, limit: int, vault_dir: Optional[Path] = None) -> None:
    """Set the maximum number of keys allowed in a vault."""
    if limit < 1:
        raise QuotaError("Quota limit must be at least 1.")
    vp = _vault_path(vault_name, vault_dir)
    if not vp.exists():
        raise QuotaError(f"Vault '{vault_name}' does not exist.")
    store = _load_store(vault_dir)
    store[vault_name] = limit
    _save_store(store, vault_dir)


def get_quota(vault_name: str, vault_dir: Optional[Path] = None) -> int:
    """Return the quota limit for a vault (default if unset)."""
    store = _load_store(vault_dir)
    return store.get(vault_name, _DEFAULT_QUOTA)


def remove_quota(vault_name: str, vault_dir: Optional[Path] = None) -> None:
    """Remove an explicit quota, reverting to the default."""
    store = _load_store(vault_dir)
    store.pop(vault_name, None)
    _save_store(store, vault_dir)


def check_quota(
    vault_name: str, passphrase: str, vault_dir: Optional[Path] = None
) -> tuple[int, int]:
    """Return (current_key_count, limit). Raises QuotaError if limit exceeded."""
    limit = get_quota(vault_name, vault_dir)
    env = load_vault(vault_name, passphrase, vault_dir)
    count = len(env)
    if count > limit:
        raise QuotaError(
            f"Vault '{vault_name}' has {count} keys, exceeding quota of {limit}."
        )
    return count, limit
