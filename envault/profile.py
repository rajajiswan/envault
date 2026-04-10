"""Profile management for envault — group vaults under named profiles."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from envault.vault import _vault_path

_PROFILES_FILE = Path.home() / ".envault" / "profiles.json"


class ProfileError(Exception):
    """Raised when a profile operation fails."""


def _load_store() -> Dict[str, List[str]]:
    if not _PROFILES_FILE.exists():
        return {}
    with _PROFILES_FILE.open() as fh:
        return json.load(fh)


def _save_store(store: Dict[str, List[str]]) -> None:
    _PROFILES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with _PROFILES_FILE.open("w") as fh:
        json.dump(store, fh, indent=2)


def create_profile(profile: str) -> None:
    """Create an empty profile."""
    store = _load_store()
    if profile in store:
        raise ProfileError(f"Profile '{profile}' already exists.")
    store[profile] = []
    _save_store(store)


def delete_profile(profile: str) -> None:
    """Delete a profile (does not delete vaults)."""
    store = _load_store()
    if profile not in store:
        raise ProfileError(f"Profile '{profile}' not found.")
    del store[profile]
    _save_store(store)


def add_vault_to_profile(profile: str, vault_name: str) -> None:
    """Add a vault to a profile."""
    store = _load_store()
    if profile not in store:
        raise ProfileError(f"Profile '{profile}' not found.")
    if not _vault_path(vault_name).exists():
        raise ProfileError(f"Vault '{vault_name}' does not exist.")
    if vault_name not in store[profile]:
        store[profile].append(vault_name)
        _save_store(store)


def remove_vault_from_profile(profile: str, vault_name: str) -> None:
    """Remove a vault from a profile."""
    store = _load_store()
    if profile not in store:
        raise ProfileError(f"Profile '{profile}' not found.")
    if vault_name in store[profile]:
        store[profile].remove(vault_name)
        _save_store(store)


def list_profiles() -> List[str]:
    """Return all profile names."""
    return list(_load_store().keys())


def get_profile_vaults(profile: str) -> List[str]:
    """Return vaults belonging to a profile."""
    store = _load_store()
    if profile not in store:
        raise ProfileError(f"Profile '{profile}' not found.")
    return list(store[profile])
