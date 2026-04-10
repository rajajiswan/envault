"""Backup and restore vault snapshots."""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path

from envault.vault import _vault_path, load_vault, save_vault


class BackupError(Exception):
    pass


def _backup_dir() -> Path:
    base = Path(os.environ.get("ENVAULT_DIR", Path.home() / ".envault"))
    backup_dir = base / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def _backup_path(vault_name: str, label: str) -> Path:
    return _backup_dir() / f"{vault_name}__{label}.bak"


def create_backup(vault_name: str, passphrase: str, label: str | None = None) -> Path:
    """Create a backup snapshot of a vault. Returns the backup file path."""
    vault_file = _vault_path(vault_name)
    if not vault_file.exists():
        raise BackupError(f"Vault '{vault_name}' does not exist.")

    # Verify passphrase is valid before backing up
    load_vault(vault_name, passphrase)

    if label is None:
        label = datetime.utcnow().strftime("%Y%m%dT%H%M%S")

    dest = _backup_path(vault_name, label)
    shutil.copy2(vault_file, dest)
    return dest


def list_backups(vault_name: str) -> list[dict]:
    """List all backups for a given vault, sorted newest first."""
    pattern = f"{vault_name}__*.bak"
    backups = sorted(_backup_dir().glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    result = []
    for path in backups:
        label = path.stem.split("__", 1)[1]
        result.append({
            "label": label,
            "path": str(path),
            "created": datetime.utcfromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        })
    return result


def restore_backup(vault_name: str, passphrase: str, label: str) -> None:
    """Restore a vault from a named backup snapshot."""
    src = _backup_path(vault_name, label)
    if not src.exists():
        raise BackupError(f"Backup '{label}' not found for vault '{vault_name}'.")

    dest = _vault_path(vault_name)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)

    # Verify the restored vault is readable with the given passphrase
    try:
        load_vault(vault_name, passphrase)
    except Exception as exc:
        dest.unlink(missing_ok=True)
        raise BackupError(f"Restored backup is unreadable: {exc}") from exc


def delete_backup(vault_name: str, label: str) -> None:
    """Delete a specific backup snapshot."""
    path = _backup_path(vault_name, label)
    if not path.exists():
        raise BackupError(f"Backup '{label}' not found for vault '{vault_name}'.")
    path.unlink()
