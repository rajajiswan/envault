"""CLI commands for vault sharing."""

import click
from envault.share import ShareError, create_share, resolve_share, revoke_share, list_shares


@click.group("share")
def share_cmd():
    """Manage vault share tokens."""


@share_cmd.command("create")
@click.argument("vault_name")
@click.option("--passphrase", prompt=True, hide_input=True, help="Vault passphrase.")
@click.option("--ttl", default=60, show_default=True, help="Token lifetime in minutes.")
def create_cmd(vault_name: str, passphrase: str, ttl: int):
    """Generate a share token for VAULT_NAME."""
    try:
        token = create_share(vault_name, passphrase, ttl_minutes=ttl)
        click.echo(f"Share token (keep it secret):")
        click.echo(token)
        click.echo(f"Expires in {ttl} minute(s).")
    except ShareError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@share_cmd.command("resolve")
@click.argument("token")
def resolve_cmd(token: str):
    """Show vault info for a share TOKEN."""
    try:
        info = resolve_share(token)
        click.echo(f"Vault   : {info['vault']}")
        click.echo(f"Expires : {info['expires_at']}")
    except ShareError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@share_cmd.command("revoke")
@click.argument("token")
def revoke_cmd(token: str):
    """Revoke a share TOKEN."""
    removed = revoke_share(token)
    if removed:
        click.echo("Token revoked.")
    else:
        click.echo("Token not found.", err=True)
        raise SystemExit(1)


@share_cmd.command("list")
@click.option("--vault", default=None, help="Filter by vault name.")
@click.option("--all", "show_all", is_flag=True, help="Include expired tokens.")
def list_cmd(vault: str | None, show_all: bool):
    """List share tokens."""
    entries = list_shares(vault_name=vault)
    if not show_all:
        entries = [e for e in entries if not e["expired"]]
    if not entries:
        click.echo("No share tokens found.")
        return
    for entry in entries:
        status = "[EXPIRED]" if entry["expired"] else "[active] "
        click.echo(f"{status} vault={entry['vault']}  token={entry['token_hash']}  expires={entry['expires_at']}")
