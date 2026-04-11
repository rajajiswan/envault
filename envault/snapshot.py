"""Snapshot support — capture and restore point-in-time copies of a vault's env contents."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List, Optional

from envault.vault import _vault_path, load_vault, save_vault


class SnapshotError(Exception):
    """Raised when a snapshot operation fails."""


def _snapshot_dir(vault_name: str) -> Path:
    base = _vault_path(vault_name).parent / "snapshots" / vault_name
    base.mkdir(parents=True, exist_ok=True)
    return base


def _snapshot_path(vault_name: str, label: str) -> Path:
    return _snapshot_dir(vault_name) / f"{label}.json"


def create_snapshot(vault_name: str, passphrase: str, label: Optional[str] = None) -> Path:
    """Decrypt *vault_name* and persist its key/value pairs as a plaintext snapshot."""
    env = load_vault(vault_name, passphrase)
    ts = int(time.time())
    label = label or str(ts)
    path = _snapshot_path(vault_name, label)
    if path.exists():
        raise SnapshotError(f"Snapshot '{label}' already exists for vault '{vault_name}'.")
    payload = {"vault": vault_name, "label": label, "timestamp": ts, "env": env}
    path.write_text(json.dumps(payload, indent=2))
    return path


def list_snapshots(vault_name: str) -> List[Dict]:
    """Return metadata for every snapshot belonging to *vault_name*, newest first."""
    snap_dir = _snapshot_dir(vault_name)
    results = []
    for p in snap_dir.glob("*.json"):
        try:
            data = json.loads(p.read_text())
            results.append({"label": data["label"], "timestamp": data["timestamp"]})
        except Exception:
            continue
    return sorted(results, key=lambda x: x["timestamp"], reverse=True)


def restore_snapshot(vault_name: str, label: str, passphrase: str) -> Dict[str, str]:
    """Re-encrypt the snapshot *label* back into the live vault and return the env dict."""
    path = _snapshot_path(vault_name, label)
    if not path.exists():
        raise SnapshotError(f"Snapshot '{label}' not found for vault '{vault_name}'.")
    data = json.loads(path.read_text())
    env: Dict[str, str] = data["env"]
    save_vault(vault_name, env, passphrase)
    return env


def delete_snapshot(vault_name: str, label: str) -> None:
    """Remove a single snapshot by label."""
    path = _snapshot_path(vault_name, label)
    if not path.exists():
        raise SnapshotError(f"Snapshot '{label}' not found for vault '{vault_name}'.")
    path.unlink()
