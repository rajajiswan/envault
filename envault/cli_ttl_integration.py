"""Helpers to integrate TTL enforcement into the main vault load path.

Call ``check_ttl_before_load`` from cli.py (or vault.py) before decrypting
a vault to prevent access to expired vaults.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import click

from envault.ttl import get_ttl, is_expired, remaining_seconds


def check_ttl_before_load(
    vault_name: str,
    vault_dir: Path,
    *,
    warn_threshold_seconds: int = 300,
) -> None:
    """Raise ``SystemExit`` if *vault_name* is expired; emit a warning if close.

    Parameters
    ----------
    vault_name:
        Name of the vault being accessed.
    vault_dir:
        Directory that contains vault files.
    warn_threshold_seconds:
        Emit a warning when less than this many seconds remain (default 5 min).
    """
    if is_expired(vault_name, vault_dir):
        expiry = get_ttl(vault_name, vault_dir)
        click.echo(
            f"Error: vault '{vault_name}' has expired"
            + (f" (expired at {expiry.strftime('%Y-%m-%d %H:%M:%S')} UTC)" if expiry else "")
            + ".",
            err=True,
        )
        raise SystemExit(1)

    secs: Optional[float] = remaining_seconds(vault_name, vault_dir)
    if secs is not None and secs < warn_threshold_seconds:
        minutes = int(secs // 60)
        seconds = int(secs % 60)
        click.echo(
            f"Warning: vault '{vault_name}' will expire in "
            f"{minutes}m {seconds}s.",
            err=True,
        )


def ttl_summary_line(vault_name: str, vault_dir: Path) -> str:
    """Return a human-readable one-line TTL summary for *vault_name*."""
    expiry = get_ttl(vault_name, vault_dir)
    if expiry is None:
        return "no TTL"
    secs = remaining_seconds(vault_name, vault_dir)
    if secs is not None and secs <= 0:
        return f"expired at {expiry.strftime('%Y-%m-%d %H:%M:%S')} UTC"
    return f"expires in {int(secs)}s ({expiry.strftime('%Y-%m-%d %H:%M:%S')} UTC)"
