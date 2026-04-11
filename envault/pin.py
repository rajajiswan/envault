"""Pin/unpin vaults for quick access and listing pinned vaults."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from envault.vault import _vault_path

_PINS_FILE = Path.home() / ".envault" / "pins.json"


class PinError(Exception):
    """Raised when a pin operation fails."""


def _load_pins() -> List[str]:
    if not _PINS_FILE.exists():
        return []
    try:
        return json.loads(_PINS_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return []


def _save_pins(pins: List[str]) -> None:
    _PINS_FILE.parent.mkdir(parents=True, exist_ok=True)
    _PINS_FILE.write_text(json.dumps(pins, indent=2))


def pin_vault(name: str) -> None:
    """Pin a vault by name. Raises PinError if the vault does not exist."""
    if not _vault_path(name).exists():
        raise PinError(f"Vault '{name}' does not exist.")
    pins = _load_pins()
    if name in pins:
        return  # already pinned, idempotent
    pins.append(name)
    _save_pins(pins)


def unpin_vault(name: str) -> None:
    """Unpin a vault by name. No-op if vault is not pinned."""
    pins = _load_pins()
    if name not in pins:
        return
    pins.remove(name)
    _save_pins(pins)


def list_pinned() -> List[str]:
    """Return a list of currently pinned vault names."""
    pins = _load_pins()
    # Filter out any pins whose vault files have been removed
    return [p for p in pins if _vault_path(p).exists()]


def is_pinned(name: str) -> bool:
    """Return True if the vault is pinned."""
    return name in _load_pins()
