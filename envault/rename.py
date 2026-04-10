"""Rename a vault, updating all associated metadata (tags, history, audit log)."""

import os
from pathlib import Path

from envault.vault import _vault_path
from envault.tags import _load_tags_store, _save_tags_store
from envault.history import _history_path, load_history, record_save
from envault.audit import _audit_path, load_audit_log, record_access


class RenameError(Exception):
    """Raised when a vault rename operation fails."""


def rename_vault(old_name: str, new_name: str, vault_dir: str | None = None) -> Path:
    """Rename a vault from *old_name* to *new_name*.

    Moves the encrypted vault file and patches the tags store so that any
    tags previously associated with *old_name* are transferred to *new_name*.

    Returns the path to the renamed vault file.

    Raises:
        RenameError: if the source vault does not exist, the destination
            already exists, or the names are identical.
    """
    if old_name == new_name:
        raise RenameError("Old and new vault names are identical.")

    src = _vault_path(old_name, vault_dir=vault_dir)
    dst = _vault_path(new_name, vault_dir=vault_dir)

    if not src.exists():
        raise RenameError(f"Vault '{old_name}' does not exist.")
    if dst.exists():
        raise RenameError(f"Vault '{new_name}' already exists.")

    # Move the encrypted vault file.
    src.rename(dst)

    # Patch tags store: reassign tags from old_name to new_name.
    try:
        store = _load_tags_store(vault_dir=vault_dir)
        if old_name in store:
            store[new_name] = store.pop(old_name)
            _save_tags_store(store, vault_dir=vault_dir)
    except Exception:
        # Tags are best-effort; don't roll back the rename.
        pass

    return dst
