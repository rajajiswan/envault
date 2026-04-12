"""CLI commands for managing vault webhooks."""

import click

from envault.webhook import (
    WebhookError,
    fire_event,
    list_webhooks,
    register_webhook,
    remove_webhook,
)


@click.group("webhook")
def webhook_cmd():
    """Manage webhook notifications for vault events."""


@webhook_cmd.command("add")
@click.argument("vault_name")
@click.argument("url")
@click.option(
    "--event",
    "events",
    multiple=True,
    default=["save", "load", "delete"],
    show_default=True,
    help="Event(s) to trigger this webhook.",
)
def add_cmd(vault_name: str, url: str, events: tuple):
    """Register a webhook URL for VAULT_NAME."""
    try:
        entry = register_webhook(vault_name, url, list(events))
        click.echo(f"Webhook registered for '{vault_name}' → {entry.url}")
        click.echo(f"  Events: {', '.join(entry.events)}")
    except WebhookError as exc:
        raise click.ClickException(str(exc))


@webhook_cmd.command("remove")
@click.argument("vault_name")
@click.argument("url")
def remove_cmd(vault_name: str, url: str):
    """Remove a webhook URL from VAULT_NAME."""
    removed = remove_webhook(vault_name, url)
    if removed:
        click.echo(f"Webhook removed from '{vault_name}'.")
    else:
        click.echo(f"No webhook with that URL found for '{vault_name}'.")


@webhook_cmd.command("list")
@click.argument("vault_name")
def list_cmd(vault_name: str):
    """List all webhooks registered for VAULT_NAME."""
    hooks = list_webhooks(vault_name)
    if not hooks:
        click.echo(f"No webhooks registered for '{vault_name}'.")
        return
    for hook in hooks:
        click.echo(f"  {hook.url}  [{', '.join(hook.events)}]")


@webhook_cmd.command("fire")
@click.argument("vault_name")
@click.argument("event")
def fire_cmd(vault_name: str, event: str):
    """Manually fire EVENT webhooks for VAULT_NAME."""
    failed = fire_event(vault_name, event)
    if not failed:
        click.echo(f"All webhooks fired for event '{event}' on '{vault_name}'.")
    else:
        click.echo(f"Failed to deliver to: {', '.join(failed)}")
