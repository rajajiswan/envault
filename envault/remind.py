"""Reminder system for vaults — schedule reminders to review or rotate secrets."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

REMINDERS_FILE = Path.home() / ".envault" / "reminders.json"


class RemindError(Exception):
    pass


def _load_store() -> dict:
    if not REMINDERS_FILE.exists():
        return {}
    with REMINDERS_FILE.open() as f:
        return json.load(f)


def _save_store(store: dict) -> None:
    REMINDERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with REMINDERS_FILE.open("w") as f:
        json.dump(store, f, indent=2)


def set_reminder(vault_name: str, days: int, message: str = "") -> datetime:
    """Schedule a reminder for *vault_name* in *days* days."""
    from envault.vault import list_vaults

    if vault_name not in list_vaults():
        raise RemindError(f"Vault '{vault_name}' does not exist.")
    if days <= 0:
        raise RemindError("days must be a positive integer.")

    due = datetime.utcnow() + timedelta(days=days)
    store = _load_store()
    store[vault_name] = {"due": due.isoformat(), "message": message}
    _save_store(store)
    return due


def get_reminder(vault_name: str) -> Optional[dict]:
    """Return reminder info for *vault_name*, or None if not set."""
    store = _load_store()
    return store.get(vault_name)


def remove_reminder(vault_name: str) -> bool:
    """Remove a reminder. Returns True if it existed."""
    store = _load_store()
    if vault_name not in store:
        return False
    del store[vault_name]
    _save_store(store)
    return True


def list_reminders() -> dict:
    """Return all reminders keyed by vault name."""
    return _load_store()


def is_due(vault_name: str) -> bool:
    """Return True if the reminder for *vault_name* is past due."""
    entry = get_reminder(vault_name)
    if entry is None:
        return False
    return datetime.utcnow() >= datetime.fromisoformat(entry["due"])
