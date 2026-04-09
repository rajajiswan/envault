#!/usr/bin/env python3
"""CLI interface for envault."""

import sys
import click
from getpass import getpass
from pathlib import Path

from envault.vault import save_vault, load_vault, list_vaults
from envault.crypto import DecryptionError


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Envault - Securely store and sync .env files."""
    pass


@cli.command()
@click.argument("env_file", type=click.Path(exists=True))
@click.argument("vault_name")
def save(env_file, vault_name):
    """Save an .env file to an encrypted vault."""
    env_path = Path(env_file)
    
    if not env_path.is_file():
        click.echo(f"Error: {env_file} is not a file", err=True)
        sys.exit(1)
    
    passphrase = getpass("Enter passphrase: ")
    confirm = getpass("Confirm passphrase: ")
    
    if passphrase != confirm:
        click.echo("Error: Passphrases do not match", err=True)
        sys.exit(1)
    
    content = env_path.read_text()
    save_vault(vault_name, content, passphrase)
    click.echo(f"✓ Saved {env_file} to vault '{vault_name}'")


@cli.command()
@click.argument("vault_name")
@click.option("-o", "--output", type=click.Path(), help="Output file path")
def load(vault_name, output):
    """Load and decrypt a vault."""
    passphrase = getpass("Enter passphrase: ")
    
    try:
        content = load_vault(vault_name, passphrase)
    except DecryptionError:
        click.echo("Error: Incorrect passphrase or corrupted vault", err=True)
        sys.exit(1)
    except FileNotFoundError:
        click.echo(f"Error: Vault '{vault_name}' not found", err=True)
        sys.exit(1)
    
    if output:
        Path(output).write_text(content)
        click.echo(f"✓ Loaded vault '{vault_name}' to {output}")
    else:
        click.echo(content)


@cli.command()
def list():
    """List all available vaults."""
    vaults = list_vaults()
    
    if not vaults:
        click.echo("No vaults found")
        return
    
    click.echo("Available vaults:")
    for vault in vaults:
        click.echo(f"  • {vault}")


if __name__ == "__main__":
    cli()
