"""Passphrase rotation for encrypted vaults."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from envault.crypto import decrypt, encrypt, DecryptionError
from envault.vault import _vault_path, load_vault, save_vault


class RotationError(Exception):
    """Raised when passphrase rotation fails."""


def rotate_passphrase(
    vault_name: str,
    old_passphrase: str,
    new_passphrase: str,
    *,
    vault_dir: Optional[Path] = None,
) -> None:
    """Re-encrypt a vault under a new passphrase.

    Loads the vault with *old_passphrase*, then immediately re-saves it
    encrypted with *new_passphrase*.  The operation is atomic in the sense
    that the vault file is only overwritten after the new ciphertext has
    been produced successfully.

    Args:
        vault_name:     Name of the vault to rotate.
        old_passphrase: Current passphrase used to decrypt the vault.
        new_passphrase: Replacement passphrase used to re-encrypt the vault.
        vault_dir:      Optional override for the vault storage directory.

    Raises:
        RotationError: If the old passphrase is wrong or the vault does not
                       exist.
    """
    path = _vault_path(vault_name, vault_dir=vault_dir)
    if not path.exists():
        raise RotationError(f"Vault '{vault_name}' does not exist.")

    try:
        env_vars = load_vault(vault_name, old_passphrase, vault_dir=vault_dir)
    except DecryptionError as exc:
        raise RotationError(
            f"Could not decrypt vault '{vault_name}' with the supplied passphrase."
        ) from exc

    save_vault(vault_name, env_vars, new_passphrase, vault_dir=vault_dir)
