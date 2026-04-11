"""CLI commands for vault snapshots."""

from __future__ import annotations

import click

from envault.snapshot import (
    SnapshotError,
    create_snapshot,
    delete_snapshot,
    list_snapshots,
    restore_snapshot,
)


@click.group("snapshot")
def snapshot_cmd() -> None:
    """Manage point-in-time snapshots of a vault."""


@snapshot_cmd.command("create")
@click.argument("vault_name")
@click.option("--passphrase", prompt=True, hide_input=True)
@click.option("--label", default=None, help="Optional human-readable label.")
def create_cmd(vault_name: str, passphrase: str, label: str) -> None:
    """Capture the current state of VAULT_NAME as a snapshot."""
    try:
        path = create_snapshot(vault_name, passphrase, label)
        click.echo(f"Snapshot saved: {path}")
    except SnapshotError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@snapshot_cmd.command("list")
@click.argument("vault_name")
def list_cmd(vault_name: str) -> None:
    """List all snapshots for VAULT_NAME."""
    snaps = list_snapshots(vault_name)
    if not snaps:
        click.echo("No snapshots found.")
        return
    for s in snaps:
        click.echo(f"  {s['label']}  (ts={s['timestamp']})")


@snapshot_cmd.command("restore")
@click.argument("vault_name")
@click.argument("label")
@click.option("--passphrase", prompt=True, hide_input=True)
def restore_cmd(vault_name: str, label: str, passphrase: str) -> None:
    """Restore VAULT_NAME from snapshot LABEL."""
    try:
        env = restore_snapshot(vault_name, label, passphrase)
        click.echo(f"Restored {len(env)} key(s) from snapshot '{label}'.")
    except SnapshotError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@snapshot_cmd.command("delete")
@click.argument("vault_name")
@click.argument("label")
def delete_cmd(vault_name: str, label: str) -> None:
    """Delete snapshot LABEL for VAULT_NAME."""
    try:
        delete_snapshot(vault_name, label)
        click.echo(f"Snapshot '{label}' deleted.")
    except SnapshotError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
