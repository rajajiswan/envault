"""Namespace support for grouping vaults under logical prefixes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envault.vault import _vault_path, list_vaults

_NS_FILE = Path.home() / ".envault" / "namespaces.json"


class NamespaceError(Exception):
    """Raised when a namespace operation fails."""


def _load_store() -> Dict[str, List[str]]:
    if not _NS_FILE.exists():
        return {}
    with _NS_FILE.open() as fh:
        return json.load(fh)


def _save_store(store: Dict[str, List[str]]) -> None:
    _NS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with _NS_FILE.open("w") as fh:
        json.dump(store, fh, indent=2)


def create_namespace(name: str) -> None:
    """Create a new empty namespace."""
    store = _load_store()
    if name in store:
        raise NamespaceError(f"Namespace '{name}' already exists.")
    store[name] = []
    _save_store(store)


def delete_namespace(name: str, *, force: bool = False) -> None:
    """Delete a namespace. Raises if non-empty unless force=True."""
    store = _load_store()
    if name not in store:
        raise NamespaceError(f"Namespace '{name}' does not exist.")
    if store[name] and not force:
        raise NamespaceError(
            f"Namespace '{name}' is not empty. Use force=True to delete anyway."
        )
    del store[name]
    _save_store(store)


def add_vault_to_namespace(name: str, vault: str) -> None:
    """Add a vault to a namespace, verifying the vault exists."""
    if not _vault_path(vault).exists():
        raise NamespaceError(f"Vault '{vault}' does not exist.")
    store = _load_store()
    if name not in store:
        raise NamespaceError(f"Namespace '{name}' does not exist.")
    if vault not in store[name]:
        store[name].append(vault)
        _save_store(store)


def remove_vault_from_namespace(name: str, vault: str) -> None:
    """Remove a vault from a namespace (no-op if not present)."""
    store = _load_store()
    if name not in store:
        raise NamespaceError(f"Namespace '{name}' does not exist.")
    store[name] = [v for v in store[name] if v != vault]
    _save_store(store)


def list_namespaces() -> List[str]:
    """Return all namespace names."""
    return list(_load_store().keys())


def get_namespace(name: str) -> List[str]:
    """Return the list of vault names in a namespace."""
    store = _load_store()
    if name not in store:
        raise NamespaceError(f"Namespace '{name}' does not exist.")
    return list(store[name])
