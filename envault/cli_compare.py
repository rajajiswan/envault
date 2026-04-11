"""CLI commands for comparing two vaults."""

import click

from envault.compare import compare_vaults, CompareError


@click.group("compare")
def compare_cmd():
    """Compare two vaults side-by-side."""


@compare_cmd.command("run")
@click.argument("vault_a")
@click.argument("vault_b")
@click.option("--pass-a", prompt="Passphrase for vault A", hide_input=True, help="Passphrase for vault A.")
@click.option("--pass-b", prompt="Passphrase for vault B", hide_input=True, help="Passphrase for vault B.")
@click.option("--show-values", is_flag=True, default=False, help="Show differing values in plain text.")
def run_cmd(vault_a: str, vault_b: str, pass_a: str, pass_b: str, show_values: bool):
    """Compare VAULT_A and VAULT_B and report differences."""
    try:
        result = compare_vaults(vault_a, pass_a, vault_b, pass_b)
    except CompareError as exc:
        raise click.ClickException(str(exc))

    if result.is_identical:
        click.echo(click.style(f"Vaults '{vault_a}' and '{vault_b}' are identical.", fg="green"))
        return

    click.echo(f"Comparing '{vault_a}' vs '{vault_b}':\n")

    if result.only_in_a:
        click.echo(click.style(f"  Only in {vault_a} ({len(result.only_in_a)}):", fg="cyan"))
        for key in result.only_in_a:
            click.echo(f"    + {key}")

    if result.only_in_b:
        click.echo(click.style(f"  Only in {vault_b} ({len(result.only_in_b)}):", fg="yellow"))
        for key in result.only_in_b:
            click.echo(f"    + {key}")

    if result.in_both_different:
        click.echo(click.style(f"  Different values ({len(result.in_both_different)}):", fg="red"))
        for key, val_a, val_b in result.in_both_different:
            if show_values:
                click.echo(f"    ~ {key}: '{val_a}' -> '{val_b}'")
            else:
                click.echo(f"    ~ {key}")

    click.echo(f"\nTotal differences: {result.total_differences}")
