"""Clone a vault under a new name, optionally re-encrypting with a different passphrase."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from envault.vault import _vault_path, load_vault, save_vault


class CloneError(Exception):
    """Raised when a vault clone operation fails."""


@dataclass
class CloneResult:
    source: str
    destination: str
    key_count: int


def clone_vault(
    source_name: str,
    dest_name: str,
    source_passphrase: str,
    dest_passphrase: str | None = None,
    vault_dir: Path | None = None,
) -> CloneResult:
    """Clone *source_name* into a new vault called *dest_name*.

    If *dest_passphrase* is omitted the same passphrase is reused.
    Raises :class:`CloneError` if the source does not exist or the
    destination already exists.
    """
    src_path = _vault_path(source_name, vault_dir)
    dst_path = _vault_path(dest_name, vault_dir)

    if not src_path.exists():
        raise CloneError(f"Source vault '{source_name}' does not exist.")
    if dst_path.exists():
        raise CloneError(f"Destination vault '{dest_name}' already exists.")

    env_data = load_vault(source_name, source_passphrase, vault_dir)

    effective_passphrase = dest_passphrase if dest_passphrase is not None else source_passphrase
    save_vault(dest_name, env_data, effective_passphrase, vault_dir)

    return CloneResult(
        source=source_name,
        destination=dest_name,
        key_count=len(env_data),
    )
