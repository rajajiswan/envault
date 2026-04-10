"""CLI commands for profile management."""

import click

from envault.profile import (
    ProfileError,
    add_vault_to_profile,
    create_profile,
    delete_profile,
    get_profile_vaults,
    list_profiles,
    remove_vault_from_profile,
)


@click.group("profile")
def profile_cmd():
    """Manage vault profiles."""


@profile_cmd.command("create")
@click.argument("profile")
def create_cmd(profile: str):
    """Create a new profile."""
    try:
        create_profile(profile)
        click.echo(f"Profile '{profile}' created.")
    except ProfileError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@profile_cmd.command("delete")
@click.argument("profile")
def delete_cmd(profile: str):
    """Delete a profile."""
    try:
        delete_profile(profile)
        click.echo(f"Profile '{profile}' deleted.")
    except ProfileError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@profile_cmd.command("add")
@click.argument("profile")
@click.argument("vault")
def add_cmd(profile: str, vault: str):
    """Add a vault to a profile."""
    try:
        add_vault_to_profile(profile, vault)
        click.echo(f"Vault '{vault}' added to profile '{profile}'.")
    except ProfileError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@profile_cmd.command("remove")
@click.argument("profile")
@click.argument("vault")
def remove_cmd(profile: str, vault: str):
    """Remove a vault from a profile."""
    try:
        remove_vault_from_profile(profile, vault)
        click.echo(f"Vault '{vault}' removed from profile '{profile}'.")
    except ProfileError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@profile_cmd.command("list")
def list_cmd():
    """List all profiles."""
    profiles = list_profiles()
    if not profiles:
        click.echo("No profiles found.")
    else:
        for p in profiles:
            click.echo(p)


@profile_cmd.command("show")
@click.argument("profile")
def show_cmd(profile: str):
    """Show vaults in a profile."""
    try:
        vaults = get_profile_vaults(profile)
        if not vaults:
            click.echo(f"Profile '{profile}' is empty.")
        else:
            for v in vaults:
                click.echo(v)
    except ProfileError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
