"""Access control for vaults — restrict which vaults a passphrase may open."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

VAULT_DIR = Path.home() / ".envault"
_ACCESS_FILE = VAULT_DIR / "access_control.json"


class AccessError(Exception):
    """Raised when an access control rule is violated or an operation fails."""


def _load_store() -> dict:
    if not _ACCESS_FILE.exists():
        return {}
    with _ACCESS_FILE.open("r") as fh:
        return json.load(fh)


def _save_store(store: dict) -> None:
    _ACCESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with _ACCESS_FILE.open("w") as fh:
        json.dump(store, fh, indent=2)


def allow_vault(vault_name: str, label: str) -> None:
    """Add *label* to the allow-list for *vault_name*."""
    store = _load_store()
    entry = store.setdefault(vault_name, {"allowed": [], "denied": []})
    if label not in entry["allowed"]:
        entry["allowed"].append(label)
    _save_store(store)


def deny_vault(vault_name: str, label: str) -> None:
    """Add *label* to the deny-list for *vault_name*."""
    store = _load_store()
    entry = store.setdefault(vault_name, {"allowed": [], "denied": []})
    if label not in entry["denied"]:
        entry["denied"].append(label)
    _save_store(store)


def remove_rule(vault_name: str, label: str) -> None:
    """Remove *label* from both allow and deny lists for *vault_name*."""
    store = _load_store()
    if vault_name not in store:
        return
    for lst in ("allowed", "denied"):
        store[vault_name][lst] = [
            l for l in store[vault_name][lst] if l != label
        ]
    _save_store(store)


def get_rules(vault_name: str) -> Optional[dict]:
    """Return the access rules for *vault_name*, or None if none exist."""
    return _load_store().get(vault_name)


def check_access(vault_name: str, label: str) -> bool:
    """Return True if *label* is allowed to access *vault_name*.

    Logic:
    - If a deny list exists and *label* is in it → denied.
    - If an allow list exists and is non-empty → only listed labels are allowed.
    - Otherwise → access is granted.
    """
    rules = get_rules(vault_name)
    if rules is None:
        return True
    if label in rules.get("denied", []):
        return False
    allowed = rules.get("allowed", [])
    if allowed and label not in allowed:
        return False
    return True
