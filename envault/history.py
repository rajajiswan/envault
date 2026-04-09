"""Vault history tracking — records timestamps and metadata for vault saves."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

HISTORY_DIR = Path.home() / ".envault" / "history"


def _history_path(vault_name: str) -> Path:
    """Return the history file path for a given vault."""
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    return HISTORY_DIR / f"{vault_name}.json"


def record_save(vault_name: str, key_count: int, source: str = "cli") -> Dict[str, Any]:
    """Append a save event to the vault's history log."""
    entry: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": "save",
        "key_count": key_count,
        "source": source,
    }
    history = load_history(vault_name)
    history.append(entry)
    path = _history_path(vault_name)
    path.write_text(json.dumps(history, indent=2), encoding="utf-8")
    return entry


def load_history(vault_name: str) -> List[Dict[str, Any]]:
    """Load all history entries for a vault. Returns empty list if none."""
    path = _history_path(vault_name)
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def clear_history(vault_name: str) -> None:
    """Delete the history file for a vault."""
    path = _history_path(vault_name)
    if path.exists():
        path.unlink()


def format_history(history: List[Dict[str, Any]]) -> str:
    """Return a human-readable summary of history entries."""
    if not history:
        return "No history found."
    lines = []
    for i, entry in enumerate(reversed(history), 1):
        ts = entry.get("timestamp", "unknown")
        keys = entry.get("key_count", "?")
        src = entry.get("source", "?")
        lines.append(f"  {i:>3}. [{ts}] action=save  keys={keys}  source={src}")
    return "\n".join(lines)
