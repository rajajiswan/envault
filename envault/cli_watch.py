"""CLI commands for watching .env files and auto-saving to vault."""

import click

from envault.watch import watch_file, WatchError


@click.group("watch")
def watch_cmd():
    """Watch a .env file and auto-save changes to a vault."""


@watch_cmd.command("start")
@click.argument("vault_name")
@click.argument("env_file")
@click.option(
    "--passphrase",
    prompt=True,
    hide_input=True,
    help="Vault passphrase.",
)
@click.option(
    "--interval",
    default=1.0,
    show_default=True,
    type=float,
    help="Poll interval in seconds.",
)
def start_cmd(vault_name: str, env_file: str, passphrase: str, interval: float):
    """Start watching ENV_FILE and sync changes into VAULT_NAME.

    Press Ctrl+C to stop.
    """
    try:
        click.echo(
            f"Watching '{env_file}' → vault '{vault_name}' "
            f"(interval={interval}s). Press Ctrl+C to stop."
        )

        def _on_change(event):
            click.echo(
                f"  [changed] {event.keys_updated} key(s) saved to '{event.vault_name}'."
            )

        watch_file(
            env_path=env_file,
            vault_name=vault_name,
            passphrase=passphrase,
            poll_interval=interval,
            on_change=_on_change,
        )
    except WatchError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    except KeyboardInterrupt:
        click.echo("\nWatch stopped.")
