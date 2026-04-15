"""Archive module: bundle multiple vaults into a single encrypted archive file."""

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List

from envault.vault import _vault_path, load_vault, save_vault


class ArchiveError(Exception):
    pass


@dataclass
class ArchiveResult:
    archive_path: str
    vaults: List[str] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.vaults)


def create_archive(vault_names: List[str], passphrase: str, dest_path: str) -> ArchiveResult:
    """Bundle the given vaults (decrypted with passphrase) into a JSON archive."""
    if not vault_names:
        raise ArchiveError("No vault names provided.")

    bundle: Dict[str, Dict[str, str]] = {}
    for name in vault_names:
        path = _vault_path(name)
        if not path.exists():
            raise ArchiveError(f"Vault '{name}' does not exist.")
        bundle[name] = load_vault(name, passphrase)

    payload = json.dumps(bundle, indent=2)
    with open(dest_path, "w", encoding="utf-8") as fh:
        fh.write(payload)

    return ArchiveResult(archive_path=dest_path, vaults=list(vault_names))


def extract_archive(
    archive_path: str,
    passphrase: str,
    overwrite: bool = False,
) -> ArchiveResult:
    """Extract vaults from an archive file and save each one."""
    if not os.path.exists(archive_path):
        raise ArchiveError(f"Archive file not found: {archive_path}")

    with open(archive_path, "r", encoding="utf-8") as fh:
        try:
            bundle: Dict[str, Dict[str, str]] = json.load(fh)
        except json.JSONDecodeError as exc:
            raise ArchiveError(f"Invalid archive format: {exc}") from exc

    restored: List[str] = []
    for name, env in bundle.items():
        path = _vault_path(name)
        if path.exists() and not overwrite:
            continue
        save_vault(name, env, passphrase)
        restored.append(name)

    return ArchiveResult(archive_path=archive_path, vaults=restored)
