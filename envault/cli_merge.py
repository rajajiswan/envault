"""CLI commands for merging vaults."""

from __future__ import annotations

from typing import Optional

import click

from envault.merge import MergeError, merge_vaults


@click.group("merge")
def merge_cmd() -> None:
    """Merge keys from one vault into another."""


@merge_cmd.command("run")
@click.argument("source")
@click.argument("target")
@click.option("--source-pass", prompt=True, hide_input=True, help="Source vault passphrase.")
@click.option("--target-pass", prompt=True, hide_input=True, help="Target vault passphrase.")
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite existing keys in the target vault.",
)
@click.option(
    "--keys",
    default=None,
    help="Comma-separated list of keys to merge (default: all).",
)
def run_cmd(
    source: str,
    target: str,
    source_pass: str,
    target_pass: str,
    overwrite: bool,
    keys: Optional[str],
) -> None:
    """Merge keys from SOURCE vault into TARGET vault."""
    key_list = [k.strip() for k in keys.split(",")] if keys else None

    try:
        result = merge_vaults(
            source_name=source,
            source_passphrase=source_pass,
            target_name=target,
            target_passphrase=target_pass,
            overwrite=overwrite,
            keys=key_list,
        )
    except MergeError as exc:
        raise click.ClickException(str(exc))

    click.echo(f"Merge complete: {result.total_changes} change(s).")
    if result.added:
        click.echo(f"  Added    : {', '.join(sorted(result.added))}")
    if result.overwritten:
        click.echo(f"  Overwritten: {', '.join(sorted(result.overwritten))}")
    if result.skipped:
        click.echo(f"  Skipped  : {', '.join(sorted(result.skipped))} (use --overwrite to replace)")
