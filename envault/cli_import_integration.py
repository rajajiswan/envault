"""Integration helpers to register the import command with the main CLI."""
from __future__ import annotations

import click

from envault.cli_import_env import import_cmd


def register(cli: click.Group) -> None:
    """Attach the *import* command group to *cli*."""
    cli.add_command(import_cmd, name="import")


def import_summary_line(vault_name: str, total: int, skipped: int) -> str:
    """Return a one-line human-readable summary of an import operation."""
    parts = [f"imported {total} key(s) into '{vault_name}'"]
    if skipped:
        parts.append(f"{skipped} skipped")
    return ", ".join(parts) + "."
