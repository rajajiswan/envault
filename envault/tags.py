"""Tag management for envault vaults."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

TAGS_FILENAME = ".envault_tags.json"


def _tags_path(vault_dir: str | None = None) -> Path:
    base = Path(vault_dir) if vault_dir else Path.home() / ".envault"
    base.mkdir(parents=True, exist_ok=True)
    return base / TAGS_FILENAME


def _load_tags_store(vault_dir: str | None = None) -> Dict[str, List[str]]:
    path = _tags_path(vault_dir)
    if not path.exists():
        return {}
    with path.open("r") as f:
        return json.load(f)


def _save_tags_store(store: Dict[str, List[str]], vault_dir: str | None = None) -> None:
    path = _tags_path(vault_dir)
    with path.open("w") as f:
        json.dump(store, f, indent=2)


def add_tag(vault_name: str, tag: str, vault_dir: str | None = None) -> None:
    """Add a tag to a vault. No-op if tag already exists."""
    store = _load_tags_store(vault_dir)
    tags = store.setdefault(vault_name, [])
    if tag not in tags:
        tags.append(tag)
    _save_tags_store(store, vault_dir)


def remove_tag(vault_name: str, tag: str, vault_dir: str | None = None) -> None:
    """Remove a tag from a vault. No-op if tag does not exist."""
    store = _load_tags_store(vault_dir)
    tags = store.get(vault_name, [])
    if tag in tags:
        tags.remove(tag)
        store[vault_name] = tags
        _save_tags_store(store, vault_dir)


def get_tags(vault_name: str, vault_dir: str | None = None) -> List[str]:
    """Return list of tags for a vault."""
    store = _load_tags_store(vault_dir)
    return list(store.get(vault_name, []))


def find_by_tag(tag: str, vault_dir: str | None = None) -> List[str]:
    """Return all vault names that have the given tag."""
    store = _load_tags_store(vault_dir)
    return [name for name, tags in store.items() if tag in tags]


def clear_tags(vault_name: str, vault_dir: str | None = None) -> None:
    """Remove all tags from a vault."""
    store = _load_tags_store(vault_dir)
    if vault_name in store:
        del store[vault_name]
        _save_tags_store(store, vault_dir)
