"""cli_sanitize.py — CLI commands for the sanitize feature."""

from __future__ import annotations

import click

from envault.sanitize import SanitizeError, format_sanitize_report, sanitize_env
from envault.vault import load_vault


@click.group("sanitize")
def sanitize_cmd() -> None:
    """Mask sensitive values in a vault for safe display or export."""


@sanitize_cmd.command("show")
@click.argument("name")
@click.option("--passphrase", prompt=True, hide_input=True, help="Vault passphrase.")
@click.option("--mask", default="***", show_default=True, help="Mask string.")
@click.option(
    "--extra",
    multiple=True,
    metavar="PATTERN",
    help="Extra patterns that mark a key as sensitive (repeatable).",
)
@click.option(
    "--keep",
    multiple=True,
    metavar="KEY",
    help="Keys whose values should never be masked (repeatable).",
)
def show_cmd(
    name: str,
    passphrase: str,
    mask: str,
    extra: tuple,
    keep: tuple,
) -> None:
    """Display vault contents with sensitive values masked."""
    try:
        env = load_vault(name, passphrase)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc

    try:
        result = sanitize_env(
            env,
            mask=mask,
            extra_patterns=list(extra) or None,
            keep_keys=list(keep) or None,
        )
    except SanitizeError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Vault: {name}")
    click.echo("---")
    for key, value in sorted(result.env.items()):
        click.echo(f"{key}={value}")
    click.echo("---")
    click.echo(format_sanitize_report(result))
