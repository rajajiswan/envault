"""Vault file management: read, write, and parse encrypted .env vaults."""

from __future__ import annotations

import pathlib
from typing import Dict

from envault.crypto import encrypt, decrypt, DecryptionError  # noqa: F401 re-exported

DEFAULT_VAULT_DIR = pathlib.Path.home() / ".envault" / "vaults"


def _vault_path(name: str, vault_dir: pathlib.Path = DEFAULT_VAULT_DIR) -> pathlib.Path:
    vault_dir.mkdir(parents=True, exist_ok=True)
    return vault_dir / f"{name}.vault"


def save_vault(name: str, env_vars: Dict[str, str], passphrase: str,
               vault_dir: pathlib.Path = DEFAULT_VAULT_DIR) -> pathlib.Path:
    """Serialize *env_vars* to an encrypted vault file and return its path."""
    plaintext = "\n".join(f"{k}={v}" for k, v in env_vars.items())
    payload = encrypt(plaintext, passphrase)
    path = _vault_path(name, vault_dir)
    path.write_bytes(payload)
    return path


def load_vault(name: str, passphrase: str,
               vault_dir: pathlib.Path = DEFAULT_VAULT_DIR) -> Dict[str, str]:
    """Load and decrypt a vault, returning a dict of env variables.

    Raises:
        FileNotFoundError: If the vault does not exist.
        DecryptionError: If decryption fails.
    """
    path = _vault_path(name, vault_dir)
    if not path.exists():
        raise FileNotFoundError(f"Vault '{name}' not found at {path}")
    payload = path.read_bytes()
    plaintext = decrypt(payload, passphrase)
    return _parse_env(plaintext)


def list_vaults(vault_dir: pathlib.Path = DEFAULT_VAULT_DIR) -> list[str]:
    """Return names of all vaults stored in *vault_dir*."""
    if not vault_dir.exists():
        return []
    return [p.stem for p in sorted(vault_dir.glob("*.vault"))]


def _parse_env(text: str) -> Dict[str, str]:
    """Parse KEY=VALUE lines into a dictionary, ignoring comments and blanks."""
    result: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition("=")
        if sep:
            result[key.strip()] = value.strip()
    return result
