"""CLI commands for vault search."""
import click

from envault.search import SearchError, search_vaults


@click.command("search")
@click.argument("query")
@click.option("--vault", "-v", default=None, help="Limit search to a specific vault.")
@click.option("--passphrase", "-p", prompt=True, hide_input=True, help="Vault passphrase.")
@click.option("--keys-only", is_flag=True, default=False, help="Search only in keys.")
@click.option("--values-only", is_flag=True, default=False, help="Search only in values.")
@click.option("--case-sensitive", is_flag=True, default=False, help="Case-sensitive search.")
def search_cmd(
    query: str,
    vault: str,
    passphrase: str,
    keys_only: bool,
    values_only: bool,
    case_sensitive: bool,
) -> None:
    """Search for QUERY across vault keys and values."""
    if keys_only and values_only:
        raise click.UsageError("--keys-only and --values-only are mutually exclusive.")

    try:
        results = search_vaults(
            query,
            passphrase,
            vault_name=vault,
            keys_only=keys_only,
            values_only=values_only,
            case_sensitive=case_sensitive,
        )
    except SearchError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    if not results:
        click.echo("No matches found.")
        return

    current_vault = None
    for result in results:
        if result.vault_name != current_vault:
            current_vault = result.vault_name
            click.echo(f"\n[{current_vault}]")
        indicator = "K" if result.match_on == "key" else "V"
        click.echo(f"  ({indicator}) {result.key}={result.value}")
