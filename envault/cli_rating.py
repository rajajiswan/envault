"""CLI commands for vault security rating."""

from __future__ import annotations

import click

from envault.rating import rate_vault, RatingError


@click.group("rating")
def rating_cmd() -> None:
    """Score a vault's security strength."""


@rating_cmd.command("show")
@click.argument("vault_name")
@click.option("--passphrase", prompt=True, hide_input=True, help="Vault passphrase")
@click.option("--verbose", "-v", is_flag=True, default=False, help="Show per-key scores and issues")
def show_cmd(vault_name: str, passphrase: str, verbose: bool) -> None:
    """Display the security rating for VAULT_NAME."""
    try:
        result = rate_vault(vault_name, passphrase)
    except RatingError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    status = "PASS" if result.ok else "FAIL"
    click.echo(f"Vault : {result.vault_name}")
    click.echo(f"Score : {result.score}/100  Grade: {result.grade}  [{status}]")

    if verbose:
        if result.key_scores:
            click.echo("\nPer-key scores:")
            for key, score in sorted(result.key_scores.items()):
                click.echo(f"  {key:<30} {score:>3}/100")
        if result.issues:
            click.echo("\nIssues:")
            for issue in result.issues:
                click.echo(f"  ⚠  {issue}")
        else:
            click.echo("\nNo issues found.")
    elif result.issues:
        click.echo(f"{len(result.issues)} issue(s) found. Use --verbose to see details.")
