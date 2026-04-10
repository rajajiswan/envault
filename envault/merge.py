"""Merge two vaults together, combining or overwriting keys."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envault.vault import load_vault, save_vault


class MergeError(Exception):
    """Raised when a merge operation fails."""


@dataclass
class MergeResult:
    added: List[str] = field(default_factory=list)
    overwritten: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    @property
    def total_changes(self) -> int:
        return len(self.added) + len(self.overwritten)


def merge_vaults(
    source_name: str,
    source_passphrase: str,
    target_name: str,
    target_passphrase: str,
    overwrite: bool = False,
    keys: Optional[List[str]] = None,
) -> MergeResult:
    """Merge key/value pairs from source vault into target vault.

    Args:
        source_name: Name of the vault to read from.
        source_passphrase: Passphrase for the source vault.
        target_name: Name of the vault to write into.
        target_passphrase: Passphrase for the target vault.
        overwrite: If True, existing keys in target are overwritten.
        keys: Optional list of specific keys to merge. If None, merge all.

    Returns:
        MergeResult describing what changed.
    """
    try:
        source_env: Dict[str, str] = load_vault(source_name, source_passphrase)
    except Exception as exc:
        raise MergeError(f"Failed to load source vault '{source_name}': {exc}") from exc

    try:
        target_env: Dict[str, str] = load_vault(target_name, target_passphrase)
    except Exception as exc:
        raise MergeError(f"Failed to load target vault '{target_name}': {exc}") from exc

    result = MergeResult()
    candidates = {k: v for k, v in source_env.items() if keys is None or k in keys}

    for key, value in candidates.items():
        if key in target_env:
            if overwrite:
                target_env[key] = value
                result.overwritten.append(key)
            else:
                result.skipped.append(key)
        else:
            target_env[key] = value
            result.added.append(key)

    try:
        save_vault(target_name, target_passphrase, target_env)
    except Exception as exc:
        raise MergeError(f"Failed to save target vault '{target_name}': {exc}") from exc

    return result
