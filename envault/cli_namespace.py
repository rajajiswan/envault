"""CLI commands for vault namespace management."""

import click

from envault.namespace import (
    NamespaceError,
    add_vault_to_namespace,
    create_namespace,
    delete_namespace,
    get_namespace,
    list_namespaces,
    remove_vault_from_namespace,
)


@click.group("namespace")
def namespace_cmd() -> None:
    """Manage vault namespaces."""


@namespace_cmd.command("create")
@click.argument("name")
def create_cmd(name: str) -> None:
    """Create a new namespace."""
    try:
        create_namespace(name)
        click.echo(f"Namespace '{name}' created.")
    except NamespaceError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@namespace_cmd.command("delete")
@click.argument("name")
@click.option("--force", is_flag=True, help="Delete even if non-empty.")
def delete_cmd(name: str, force: bool) -> None:
    """Delete a namespace."""
    try:
        delete_namespace(name, force=force)
        click.echo(f"Namespace '{name}' deleted.")
    except NamespaceError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@namespace_cmd.command("add")
@click.argument("name")
@click.argument("vault")
def add_cmd(name: str, vault: str) -> None:
    """Add a vault to a namespace."""
    try:
        add_vault_to_namespace(name, vault)
        click.echo(f"Vault '{vault}' added to namespace '{name}'.")
    except NamespaceError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@namespace_cmd.command("remove")
@click.argument("name")
@click.argument("vault")
def remove_cmd(name: str, vault: str) -> None:
    """Remove a vault from a namespace."""
    try:
        remove_vault_from_namespace(name, vault)
        click.echo(f"Vault '{vault}' removed from namespace '{name}'.")
    except NamespaceError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@namespace_cmd.command("list")
def list_cmd() -> None:
    """List all namespaces."""
    names = list_namespaces()
    if not names:
        click.echo("No namespaces found.")
    else:
        for n in names:
            click.echo(n)


@namespace_cmd.command("show")
@click.argument("name")
def show_cmd(name: str) -> None:
    """Show vaults in a namespace."""
    try:
        vaults = get_namespace(name)
        if not vaults:
            click.echo(f"Namespace '{name}' is empty.")
        else:
            for v in vaults:
                click.echo(v)
    except NamespaceError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
