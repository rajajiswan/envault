"""CLI commands for vault notes."""

from __future__ import annotations

import click
from envault.notes import NoteError, set_note, get_note, remove_note, list_notes


@click.group("notes")
def notes_cmd():
    """Attach notes to vaults."""


@notes_cmd.command("set")
@click.argument("vault_name")
@click.argument("text")
@click.option("--dir", "vault_dir", default=".", show_default=True)
def set_cmd(vault_name: str, text: str, vault_dir: str) -> None:
    """Attach or replace a note on VAULT_NAME."""
    try:
        set_note(vault_name, text, vault_dir)
        click.echo(f"Note saved for '{vault_name}'.")
    except NoteError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@notes_cmd.command("get")
@click.argument("vault_name")
@click.option("--dir", "vault_dir", default=".", show_default=True)
def get_cmd(vault_name: str, vault_dir: str) -> None:
    """Print the note attached to VAULT_NAME."""
    note = get_note(vault_name, vault_dir)
    if note is None:
        click.echo(f"No note found for '{vault_name}'.")
    else:
        click.echo(f"{note['text']}  (updated: {note['updated_at']})")


@notes_cmd.command("remove")
@click.argument("vault_name")
@click.option("--dir", "vault_dir", default=".", show_default=True)
def remove_cmd(vault_name: str, vault_dir: str) -> None:
    """Remove the note attached to VAULT_NAME."""
    remove_note(vault_name, vault_dir)
    click.echo(f"Note removed for '{vault_name}' (if any).")


@notes_cmd.command("list")
@click.option("--dir", "vault_dir", default=".", show_default=True)
def list_cmd(vault_dir: str) -> None:
    """List all vaults that have notes."""
    store = list_notes(vault_dir)
    if not store:
        click.echo("No notes found.")
        return
    for name, entry in store.items():
        click.echo(f"{name}: {entry['text']}  (updated: {entry['updated_at']})")
