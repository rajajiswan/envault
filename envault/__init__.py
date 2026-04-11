"""envault — Securely store and sync .env files using encrypted local vaults."""

__version__ = "0.1.0"

from envault.crypto import encrypt, decrypt, derive_key, DecryptionError
from envault.vault import save_vault, load_vault, list_vaults
from envault.sync import export_vault, import_vault, SyncError
from envault.diff import diff_envs, has_changes, VaultDiff
from envault.history import record_save, load_history, clear_history
from envault.tags import add_tag, remove_tag, list_tags, find_by_tag
from envault.search import search_vaults, SearchResult, SearchError
from envault.audit import record_access, load_audit_log, clear_audit_log
from envault.rotate import rotate_passphrase, RotationError
from envault.lock import lock_vault, unlock_vault, is_locked, LockError
from envault.backup import create_backup, list_backups, restore_backup, BackupError
from envault.template import render_template, RenderResult, TemplateError
from envault.profile import create_profile, delete_profile, ProfileError
from envault.merge import merge_vaults, MergeResult, MergeError
from envault.rename import rename_vault, RenameError
from envault.clone import clone_vault, CloneResult, CloneError
from envault.compare import compare_vaults, CompareResult, CompareError
from envault.pin import pin_vault, unpin_vault, PinError
from envault.watch import watch_file, WatchEvent, WatchError

__all__ = [
    "__version__",
    "encrypt", "decrypt", "derive_key", "DecryptionError",
    "save_vault", "load_vault", "list_vaults",
    "export_vault", "import_vault", "SyncError",
    "diff_envs", "has_changes", "VaultDiff",
    "record_save", "load_history", "clear_history",
    "add_tag", "remove_tag", "list_tags", "find_by_tag",
    "search_vaults", "SearchResult", "SearchError",
    "record_access", "load_audit_log", "clear_audit_log",
    "rotate_passphrase", "RotationError",
    "lock_vault", "unlock_vault", "is_locked", "LockError",
    "create_backup", "list_backups", "restore_backup", "BackupError",
    "render_template", "RenderResult", "TemplateError",
    "create_profile", "delete_profile", "ProfileError",
    "merge_vaults", "MergeResult", "MergeError",
    "rename_vault", "RenameError",
    "clone_vault", "CloneResult", "CloneError",
    "compare_vaults", "CompareResult", "CompareError",
    "pin_vault", "unpin_vault", "PinError",
    "watch_file", "WatchEvent", "WatchError",
]
