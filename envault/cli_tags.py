"""CLI commands for vault tag management."""

import click
from envault.tags import add_tag, remove_tag, get_tags, find_by_tag, clear_tags


@click.group("tags")
def tags_cmd():
    """Manage tags on vaults."""


@tags_cmd.command("add")
@click.argument("vault_name")
@click.argument("tag")
def add_cmd(vault_name: str, tag: str):
    """Add TAG to VAULT_NAME."""
    add_tag(vault_name, tag)
    click.echo(f"Tag '{tag}' added to vault '{vault_name}'.")


@tags_cmd.command("remove")
@click.argument("vault_name")
@click.argument("tag")
def remove_cmd(vault_name: str, tag: str):
    """Remove TAG from VAULT_NAME."""
    remove_tag(vault_name, tag)
    click.echo(f"Tag '{tag}' removed from vault '{vault_name}'.")


@tags_cmd.command("list")
@click.argument("vault_name")
def list_cmd(vault_name: str):
    """List all tags for VAULT_NAME."""
    tags = get_tags(vault_name)
    if not tags:
        click.echo(f"No tags for vault '{vault_name}'.")
    else:
        click.echo(f"Tags for '{vault_name}': " + ", ".join(tags))


@tags_cmd.command("find")
@click.argument("tag")
def find_cmd(tag: str):
    """Find all vaults with TAG."""
    vaults = find_by_tag(tag)
    if not vaults:
        click.echo(f"No vaults found with tag '{tag}'.")
    else:
        click.echo(f"Vaults with tag '{tag}':")
        for name in vaults:
            click.echo(f"  - {name}")


@tags_cmd.command("clear")
@click.argument("vault_name")
def clear_cmd(vault_name: str):
    """Clear all tags from VAULT_NAME."""
    clear_tags(vault_name)
    click.echo(f"All tags cleared from vault '{vault_name}'.")
