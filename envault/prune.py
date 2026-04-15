"""Prune stale or empty vaults from the vault directory."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List

from envault.vault import _vault_path, load_vault
from envault.crypto import DecryptionError


class PruneError(Exception):
    """Raised when pruning fails."""


@dataclass
class PruneResult:
    removed: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def total_removed(self) -> int:
        return len(self.removed)


def prune_vaults(
    passphrase: str,
    *,
    remove_empty: bool = True,
    dry_run: bool = False,
    vault_dir: str | None = None,
) -> PruneResult:
    """Remove vaults that are empty or cannot be decrypted.

    Args:
        passphrase: Passphrase used to attempt decryption of each vault.
        remove_empty: When True, vaults with zero keys are pruned.
        dry_run: When True, report what would be removed without deleting.
        vault_dir: Override the default vault storage directory.

    Returns:
        A PruneResult describing what was removed, skipped, or errored.
    """
    result = PruneResult()

    base = vault_dir or os.path.dirname(_vault_path("__probe__"))
    if not os.path.isdir(base):
        return result

    for fname in os.listdir(base):
        if not fname.endswith(".vault"):
            continue
        name = fname[: -len(".vault")]
        path = os.path.join(base, fname)

        try:
            env = load_vault(name, passphrase, vault_dir=vault_dir)
        except DecryptionError:
            result.errors.append(name)
            continue
        except Exception as exc:  # noqa: BLE001
            result.errors.append(name)
            continue

        if remove_empty and len(env) == 0:
            if not dry_run:
                os.remove(path)
            result.removed.append(name)
        else:
            result.skipped.append(name)

    return result
