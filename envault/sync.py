"""Sync module for exporting and importing vault snapshots."""

import json
import os
import base64
from datetime import datetime, timezone
from pathlib import Path

from envault.vault import load_vault, save_vault, _vault_path
from envault.crypto import encrypt, decrypt, DecryptionError


class SyncError(Exception):
    """Raised when a sync operation fails."""


def export_vault(name: str, passphrase: str, export_path: str) -> None:
    """Export an encrypted vault snapshot to a portable file."""
    env_vars = load_vault(name, passphrase)

    payload = {
        "vault_name": name,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "version": 1,
        "entries": env_vars,
    }

    plaintext = json.dumps(payload).encode()
    ciphertext = encrypt(plaintext, passphrase)
    encoded = base64.b64encode(ciphertext).decode()

    export_data = json.dumps({"envault_export": True, "data": encoded})
    Path(export_path).write_text(export_data)


def import_vault(import_path: str, passphrase: str, overwrite: bool = False) -> str:
    """Import a vault snapshot from a portable file. Returns the vault name."""
    raw = Path(import_path).read_text()

    try:
        wrapper = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SyncError(f"Invalid export file format: {exc}") from exc

    if not wrapper.get("envault_export"):
        raise SyncError("File does not appear to be an envault export.")

    try:
        ciphertext = base64.b64decode(wrapper["data"])
        plaintext = decrypt(ciphertext, passphrase)
        payload = json.loads(plaintext.decode())
    except (DecryptionError, KeyError, json.JSONDecodeError) as exc:
        raise SyncError(f"Failed to decrypt or parse export: {exc}") from exc

    name = payload["vault_name"]
    vault_file = _vault_path(name)

    if vault_file.exists() and not overwrite:
        raise SyncError(
            f"Vault '{name}' already exists. Use --overwrite to replace it."
        )

    save_vault(name, payload["entries"], passphrase)
    return name
