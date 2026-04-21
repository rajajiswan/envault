"""Checksum generation and verification for vault integrity."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Optional

from envault.vault import _vault_path, load_vault


class ChecksumError(Exception):
    """Raised when a checksum operation fails."""


def _checksum_path(vault_name: str) -> Path:
    base = _vault_path(vault_name).parent
    return base / f"{vault_name}.checksum"


def compute_checksum(vault_name: str, passphrase: str) -> str:
    """Compute a SHA-256 checksum of the vault's decrypted contents."""
    try:
        env = load_vault(vault_name, passphrase)
    except FileNotFoundError:
        raise ChecksumError(f"Vault '{vault_name}' does not exist.")
    except Exception as exc:
        raise ChecksumError(f"Failed to load vault: {exc}") from exc

    canonical = json.dumps(env, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def save_checksum(vault_name: str, passphrase: str) -> str:
    """Compute and persist the checksum for a vault. Returns the hex digest."""
    digest = compute_checksum(vault_name, passphrase)
    path = _checksum_path(vault_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(digest)
    return digest


def load_checksum(vault_name: str) -> Optional[str]:
    """Return the stored checksum for a vault, or None if not recorded."""
    path = _checksum_path(vault_name)
    if not path.exists():
        return None
    return path.read_text().strip()


def verify_checksum(vault_name: str, passphrase: str) -> bool:
    """Return True if the current vault contents match the stored checksum."""
    stored = load_checksum(vault_name)
    if stored is None:
        raise ChecksumError(f"No checksum recorded for vault '{vault_name}'.")
    current = compute_checksum(vault_name, passphrase)
    return current == stored


def clear_checksum(vault_name: str) -> None:
    """Remove the stored checksum file for a vault."""
    path = _checksum_path(vault_name)
    if path.exists():
        path.unlink()
