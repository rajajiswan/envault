"""Vault labeling — attach human-friendly display labels to vault names."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from envault.vault import _vault_path

_LABELS_FILE = Path.home() / ".envault" / "labels.json"


class LabelError(Exception):
    """Raised when a label operation fails."""


def _load_store() -> Dict[str, str]:
    if not _LABELS_FILE.exists():
        return {}
    with _LABELS_FILE.open() as fh:
        return json.load(fh)


def _save_store(store: Dict[str, str]) -> None:
    _LABELS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with _LABELS_FILE.open("w") as fh:
        json.dump(store, fh, indent=2)


def set_label(vault_name: str, label: str) -> None:
    """Attach *label* to *vault_name*. Raises LabelError if vault does not exist."""
    if not _vault_path(vault_name).exists():
        raise LabelError(f"Vault '{vault_name}' does not exist.")
    if not label.strip():
        raise LabelError("Label must not be empty.")
    store = _load_store()
    store[vault_name] = label.strip()
    _save_store(store)


def remove_label(vault_name: str) -> None:
    """Remove the label for *vault_name* (no-op if none set)."""
    store = _load_store()
    store.pop(vault_name, None)
    _save_store(store)


def get_label(vault_name: str) -> Optional[str]:
    """Return the label for *vault_name*, or None if not set."""
    return _load_store().get(vault_name)


def list_labels() -> Dict[str, str]:
    """Return a mapping of vault_name -> label for all labeled vaults."""
    return dict(_load_store())
