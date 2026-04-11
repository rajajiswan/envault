"""Vault alias management — assign short names to vault identifiers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from envault.vault import _vault_path

_ALIAS_FILE = Path.home() / ".envault" / "aliases.json"


class AliasError(Exception):
    """Raised when an alias operation fails."""


def _load_aliases() -> Dict[str, str]:
    if not _ALIAS_FILE.exists():
        return {}
    with _ALIAS_FILE.open("r") as fh:
        return json.load(fh)


def _save_aliases(aliases: Dict[str, str]) -> None:
    _ALIAS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with _ALIAS_FILE.open("w") as fh:
        json.dump(aliases, fh, indent=2)


def set_alias(alias: str, vault_name: str) -> None:
    """Map *alias* to *vault_name*.  Raises AliasError if the vault doesn't exist."""
    if not _vault_path(vault_name).exists():
        raise AliasError(f"Vault '{vault_name}' does not exist.")
    aliases = _load_aliases()
    aliases[alias] = vault_name
    _save_aliases(aliases)


def remove_alias(alias: str) -> None:
    """Remove *alias*.  No-op if the alias doesn't exist."""
    aliases = _load_aliases()
    aliases.pop(alias, None)
    _save_aliases(aliases)


def resolve_alias(alias: str) -> Optional[str]:
    """Return the vault name for *alias*, or ``None`` if not found."""
    return _load_aliases().get(alias)


def list_aliases() -> Dict[str, str]:
    """Return a copy of the full alias mapping."""
    return dict(_load_aliases())


def clear_aliases() -> None:
    """Delete all stored aliases."""
    if _ALIAS_FILE.exists():
        _ALIAS_FILE.unlink()
