"""Import .env variables from external sources (files, stdin, URLs)."""
from __future__ import annotations

import sys
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envault.vault import _parse_env, save_vault


class ImportEnvError(Exception):
    """Raised when an import operation fails."""


@dataclass
class ImportResult:
    vault_name: str
    keys_imported: List[str] = field(default_factory=list)
    keys_skipped: List[str] = field(default_factory=list)
    source: str = ""

    @property
    def total(self) -> int:
        return len(self.keys_imported)

    @property
    def skipped(self) -> int:
        return len(self.keys_skipped)


def _read_source(source: Optional[str]) -> str:
    """Read raw .env content from a file path, URL, or stdin."""
    if source is None or source == "-":
        return sys.stdin.read()
    if source.startswith("http://") or source.startswith("https://"):
        try:
            with urllib.request.urlopen(source, timeout=10) as resp:  # noqa: S310
                return resp.read().decode()
        except Exception as exc:
            raise ImportEnvError(f"Failed to fetch URL '{source}': {exc}") from exc
    path = Path(source)
    if not path.exists():
        raise ImportEnvError(f"File not found: {source}")
    return path.read_text(encoding="utf-8")


def import_env(
    vault_name: str,
    passphrase: str,
    source: Optional[str],
    *,
    overwrite: bool = False,
    keys: Optional[List[str]] = None,
) -> ImportResult:
    """Parse and import env vars into *vault_name*, optionally filtering by *keys*."""
    raw = _read_source(source)
    parsed: Dict[str, str] = _parse_env(raw)

    if not parsed:
        raise ImportEnvError("No valid KEY=VALUE pairs found in source.")

    if keys:
        parsed = {k: v for k, v in parsed.items() if k in keys}

    result = ImportResult(
        vault_name=vault_name,
        source=source or "stdin",
    )

    from envault.vault import load_vault
    from envault.vault import _vault_path

    existing: Dict[str, str] = {}
    vp = _vault_path(vault_name)
    if vp.exists():
        try:
            existing = load_vault(vault_name, passphrase)
        except Exception as exc:
            raise ImportEnvError(f"Cannot open existing vault: {exc}") from exc

    merged = dict(existing)
    for k, v in parsed.items():
        if k in existing and not overwrite:
            result.keys_skipped.append(k)
        else:
            merged[k] = v
            result.keys_imported.append(k)

    env_text = "\n".join(f"{k}={v}" for k, v in merged.items())
    save_vault(vault_name, env_text, passphrase)
    return result
