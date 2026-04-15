"""CLI commands for pruning stale or empty vaults."""

from __future__ import annotations

import click

from envault.prune import prune_vaults, PruneError


@click.group("prune")
def prune_cmd() -> None:
    """Prune empty or unreadable vaults."""


@prune_cmd.command("run")
@click.option("--passphrase", prompt=True, hide_input=True, help="Vault passphrase.")
@click.option(
    "--keep-empty",
    is_flag=True,
    default=False,
    help="Do not remove empty vaults.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Show what would be pruned without deleting.",
)
def run_cmd(passphrase: str, keep_empty: bool, dry_run: bool) -> None:
    """Prune vaults that are empty or cannot be decrypted."""
    try:
        result = prune_vaults(
            passphrase,
            remove_empty=not keep_empty,
            dry_run=dry_run,
        )
    except PruneError as exc:
        raise click.ClickException(str(exc)) from exc

    if dry_run:
        click.echo("[dry-run] No files were deleted.")

    if result.removed:
        label = "Would remove" if dry_run else "Removed"
        for name in result.removed:
            click.echo(f"  {label}: {name}")
    else:
        click.echo("Nothing to prune.")

    if result.errors:
        click.echo("\nCould not read (skipped):")
        for name in result.errors:
            click.echo(f"  ! {name}")

    click.echo(
        f"\nSummary: {result.total_removed} removed, "
        f"{len(result.skipped)} kept, {len(result.errors)} unreadable."
    )
