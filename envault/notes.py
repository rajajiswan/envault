"""Attach and manage plaintext notes on vaults."""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

NOTES_FILE = ".envault_notes.json"


class NoteError(Exception):
    """Raised when a notes operation fails."""


def _notes_path(vault_dir: str = ".") -> Path:
    return Path(vault_dir) / NOTES_FILE


def _load_store(vault_dir: str = ".") -> dict:
    p = _notes_path(vault_dir)
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


def _save_store(store: dict, vault_dir: str = ".") -> None:
    p = _notes_path(vault_dir)
    with p.open("w") as f:
        json.dump(store, f, indent=2)


def set_note(vault_name: str, text: str, vault_dir: str = ".") -> None:
    """Attach or replace a note on *vault_name*."""
    from envault.vault import _vault_path

    if not _vault_path(vault_name, vault_dir).exists():
        raise NoteError(f"Vault '{vault_name}' does not exist.")

    store = _load_store(vault_dir)
    store[vault_name] = {
        "text": text,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_store(store, vault_dir)


def get_note(vault_name: str, vault_dir: str = ".") -> Optional[dict]:
    """Return the note dict for *vault_name*, or None if absent."""
    store = _load_store(vault_dir)
    return store.get(vault_name)


def remove_note(vault_name: str, vault_dir: str = ".") -> None:
    """Delete the note attached to *vault_name* (no-op if none exists)."""
    store = _load_store(vault_dir)
    store.pop(vault_name, None)
    _save_store(store, vault_dir)


def list_notes(vault_dir: str = ".") -> dict:
    """Return a mapping of vault_name -> note dict for all annotated vaults."""
    return _load_store(vault_dir)
