"""Vault locking mechanism — temporarily lock a vault to prevent reads/writes."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

VAULT_DIR = Path.home() / ".envault" / "vaults"
LOCK_DIR = Path.home() / ".envault" / "locks"


class LockError(Exception):
    """Raised when a vault lock operation fails."""


def _lock_path(vault_name: str) -> Path:
    return LOCK_DIR / f"{vault_name}.lock"


def lock_vault(vault_name: str, reason: str = "") -> dict:
    """Lock a vault by creating a lock file. Raises LockError if already locked."""
    vault_file = VAULT_DIR / f"{vault_name}.enc"
    if not vault_file.exists():
        raise LockError(f"Vault '{vault_name}' does not exist.")

    lock_file = _lock_path(vault_name)
    if lock_file.exists():
        with lock_file.open() as f:
            info = json.load(f)
        raise LockError(
            f"Vault '{vault_name}' is already locked since {info['locked_at']}."
        )

    LOCK_DIR.mkdir(parents=True, exist_ok=True)
    info = {
        "vault": vault_name,
        "locked_at": datetime.now(timezone.utc).isoformat(),
        "reason": reason,
    }
    with lock_file.open("w") as f:
        json.dump(info, f, indent=2)
    return info


def unlock_vault(vault_name: str) -> None:
    """Remove the lock file for a vault. Raises LockError if not locked."""
    lock_file = _lock_path(vault_name)
    if not lock_file.exists():
        raise LockError(f"Vault '{vault_name}' is not locked.")
    lock_file.unlink()


def is_locked(vault_name: str) -> bool:
    """Return True if the vault currently has a lock file."""
    return _lock_path(vault_name).exists()


def get_lock_info(vault_name: str) -> dict | None:
    """Return lock metadata dict, or None if vault is not locked."""
    lock_file = _lock_path(vault_name)
    if not lock_file.exists():
        return None
    with lock_file.open() as f:
        return json.load(f)
