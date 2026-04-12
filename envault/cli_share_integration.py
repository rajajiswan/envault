"""Integration helpers: register share commands into the main CLI."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import click


def register(cli: "click.Group") -> None:
    """Attach the share command group to the root CLI group."""
    from envault.cli_share import share_cmd
    cli.add_command(share_cmd)


def share_summary_line(vault_name: str) -> str | None:
    """Return a one-line summary of active share tokens for a vault, or None."""
    from envault.share import list_shares, ShareError
    try:
        entries = [e for e in list_shares(vault_name=vault_name) if not e["expired"]]
    except ShareError:
        return None
    if not entries:
        return None
    count = len(entries)
    nearest = min(entries, key=lambda e: e["expires_at"])
    return (
        f"{count} active share token(s) for '{vault_name}'; "
        f"earliest expiry: {nearest['expires_at']}"
    )
