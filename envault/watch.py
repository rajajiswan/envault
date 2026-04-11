"""Watch a .env file for changes and auto-save to vault."""

import time
import os
from pathlib import Path
from typing import Callable, Optional

from envault.vault import save_vault, _parse_env


class WatchError(Exception):
    """Raised when a watch operation fails."""


class WatchEvent:
    """Represents a detected file change event."""

    def __init__(self, path: str, vault_name: str, keys_updated: int):
        self.path = path
        self.vault_name = vault_name
        self.keys_updated = keys_updated
        self.timestamp = time.time()

    def __repr__(self):
        return (
            f"WatchEvent(path={self.path!r}, vault={self.vault_name!r}, "
            f"keys={self.keys_updated})"
        )


def _get_mtime(path: str) -> float:
    """Return the modification time of a file, or 0.0 if it doesn't exist."""
    try:
        return os.path.getmtime(path)
    except FileNotFoundError:
        return 0.0


def watch_file(
    env_path: str,
    vault_name: str,
    passphrase: str,
    poll_interval: float = 1.0,
    max_events: Optional[int] = None,
    on_change: Optional[Callable[[WatchEvent], None]] = None,
) -> None:
    """Poll *env_path* and save to *vault_name* whenever it changes.

    Args:
        env_path: Path to the .env file to watch.
        vault_name: Vault name to save changes into.
        passphrase: Passphrase used to encrypt the vault.
        poll_interval: Seconds between modification-time checks.
        max_events: Stop after this many change events (None = run forever).
        on_change: Optional callback invoked with each WatchEvent.

    Raises:
        WatchError: If *env_path* does not exist at start time.
    """
    path = Path(env_path)
    if not path.exists():
        raise WatchError(f"File not found: {env_path}")

    last_mtime = _get_mtime(env_path)
    events_seen = 0

    while True:
        time.sleep(poll_interval)
        current_mtime = _get_mtime(env_path)

        if current_mtime != last_mtime:
            last_mtime = current_mtime
            env_vars = _parse_env(path.read_text())
            save_vault(vault_name, env_vars, passphrase)
            event = WatchEvent(
                path=env_path,
                vault_name=vault_name,
                keys_updated=len(env_vars),
            )
            if on_change:
                on_change(event)
            events_seen += 1
            if max_events is not None and events_seen >= max_events:
                break
