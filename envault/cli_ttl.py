"""CLI commands for managing vault TTLs."""

from __future__ import annotations

from pathlib import Path

import click

from envault.ttl import TTLError, clear_ttl, get_ttl, is_expired, remaining_seconds, set_ttl
from envault.vault import _vault_path

_DEFAULT_DIR = Path.home() / ".envault"


@click.group("ttl")
def ttl_cmd() -> None:
    """Manage time-to-live settings for vaults."""


@ttl_cmd.command("set")
@click.argument("vault_name")
@click.argument("seconds", type=int)
@click.option("--dir", "vault_dir", default=str(_DEFAULT_DIR), show_default=True)
def set_cmd(vault_name: str, seconds: int, vault_dir: str) -> None:
    """Set a TTL of SECONDS seconds on VAULT_NAME."""
    vd = Path(vault_dir)
    try:
        expiry = set_ttl(vault_name, seconds, vd)
        click.echo(f"TTL set. Vault '{vault_name}' expires at {expiry.strftime('%Y-%m-%d %H:%M:%S')} UTC.")
    except FileNotFoundError:
        click.echo(f"Error: vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    except TTLError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@ttl_cmd.command("status")
@click.argument("vault_name")
@click.option("--dir", "vault_dir", default=str(_DEFAULT_DIR), show_default=True)
def status_cmd(vault_name: str, vault_dir: str) -> None:
    """Show TTL status for VAULT_NAME."""
    vd = Path(vault_dir)
    expiry = get_ttl(vault_name, vd)
    if expiry is None:
        click.echo(f"No TTL set for '{vault_name}'.")
        return
    secs = remaining_seconds(vault_name, vd)
    expired = is_expired(vault_name, vd)
    status = "EXPIRED" if expired else f"{secs:.0f}s remaining"
    click.echo(f"Vault '{vault_name}': expires {expiry.strftime('%Y-%m-%d %H:%M:%S')} UTC — {status}")


@ttl_cmd.command("clear")
@click.argument("vault_name")
@click.option("--dir", "vault_dir", default=str(_DEFAULT_DIR), show_default=True)
def clear_cmd(vault_name: str, vault_dir: str) -> None:
    """Remove the TTL for VAULT_NAME."""
    vd = Path(vault_dir)
    removed = clear_ttl(vault_name, vd)
    if removed:
        click.echo(f"TTL cleared for '{vault_name}'.")
    else:
        click.echo(f"No TTL was set for '{vault_name}'.")
