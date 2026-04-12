"""Vault compression: gzip-compress vault exports for storage efficiency."""

from __future__ import annotations

import gzip
import json
import os
from pathlib import Path
from typing import Any

from envault.vault import _vault_path, load_vault, save_vault


class CompressError(Exception):
    """Raised when compression or decompression fails."""


def _compressed_path(name: str, directory: str | None = None) -> Path:
    base = Path(directory) if directory else Path.home() / ".envault" / "compressed"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"{name}.env.gz"


def compress_vault(name: str, passphrase: str, dest_dir: str | None = None) -> Path:
    """Compress a vault's encrypted payload into a .env.gz file.

    Args:
        name: Vault name.
        passphrase: Passphrase used to load the vault.
        dest_dir: Optional directory for the output file.

    Returns:
        Path to the compressed file.

    Raises:
        CompressError: If the vault cannot be read or written.
    """
    try:
        env_data: dict[str, str] = load_vault(name, passphrase)
    except FileNotFoundError:
        raise CompressError(f"Vault '{name}' does not exist.")
    except Exception as exc:
        raise CompressError(f"Could not load vault '{name}': {exc}") from exc

    payload = json.dumps({"vault": name, "data": env_data}).encode("utf-8")
    out_path = _compressed_path(name, dest_dir)

    try:
        with gzip.open(out_path, "wb") as fh:
            fh.write(payload)
    except OSError as exc:
        raise CompressError(f"Failed to write compressed file: {exc}") from exc

    return out_path


def decompress_vault(path: str, passphrase: str, dest_name: str | None = None) -> str:
    """Decompress a .env.gz file and save it as a new vault.

    Args:
        path: Path to the .env.gz file.
        passphrase: Passphrase to encrypt the restored vault.
        dest_name: Vault name to save under (defaults to embedded name).

    Returns:
        The vault name that was saved.

    Raises:
        CompressError: If the file cannot be read or the payload is invalid.
    """
    try:
        with gzip.open(path, "rb") as fh:
            raw = fh.read()
    except (OSError, gzip.BadGzipFile) as exc:
        raise CompressError(f"Failed to read compressed file '{path}': {exc}") from exc

    try:
        payload: dict[str, Any] = json.loads(raw.decode("utf-8"))
        env_data: dict[str, str] = payload["data"]
        vault_name: str = dest_name or payload["vault"]
    except (KeyError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise CompressError(f"Invalid compressed vault format: {exc}") from exc

    try:
        save_vault(vault_name, env_data, passphrase)
    except Exception as exc:
        raise CompressError(f"Could not save vault '{vault_name}': {exc}") from exc

    return vault_name
