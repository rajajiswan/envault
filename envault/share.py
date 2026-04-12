"""Vault sharing: generate and validate time-limited share tokens."""

import json
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path

from envault.vault import _vault_path, load_vault

_SHARES_FILE = Path.home() / ".envault" / "shares.json"


class ShareError(Exception):
    pass


def _load_store() -> dict:
    if not _SHARES_FILE.exists():
        return {}
    return json.loads(_SHARES_FILE.read_text())


def _save_store(store: dict) -> None:
    _SHARES_FILE.parent.mkdir(parents=True, exist_ok=True)
    _SHARES_FILE.write_text(json.dumps(store, indent=2))


def create_share(vault_name: str, passphrase: str, ttl_minutes: int = 60) -> str:
    """Create a share token for a vault. Raises ShareError if vault not found."""
    path = _vault_path(vault_name)
    if not path.exists():
        raise ShareError(f"Vault '{vault_name}' not found.")
    # Verify passphrase is valid
    load_vault(vault_name, passphrase)

    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)).isoformat()

    store = _load_store()
    store[token_hash] = {
        "vault": vault_name,
        "expires_at": expires_at,
        "passphrase_hash": hashlib.sha256(passphrase.encode()).hexdigest(),
    }
    _save_store(store)
    return token


def resolve_share(token: str) -> dict:
    """Resolve a share token. Returns vault info or raises ShareError."""
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    store = _load_store()
    entry = store.get(token_hash)
    if not entry:
        raise ShareError("Invalid or unknown share token.")
    expires_at = datetime.fromisoformat(entry["expires_at"])
    if datetime.now(timezone.utc) > expires_at:
        raise ShareError("Share token has expired.")
    return {"vault": entry["vault"], "expires_at": entry["expires_at"]}


def revoke_share(token: str) -> bool:
    """Revoke a share token. Returns True if it existed."""
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    store = _load_store()
    if token_hash not in store:
        return False
    del store[token_hash]
    _save_store(store)
    return True


def list_shares(vault_name: str | None = None) -> list[dict]:
    """List active (non-expired) share tokens, optionally filtered by vault."""
    store = _load_store()
    now = datetime.now(timezone.utc)
    results = []
    for token_hash, entry in store.items():
        if vault_name and entry["vault"] != vault_name:
            continue
        expires_at = datetime.fromisoformat(entry["expires_at"])
        results.append({
            "token_hash": token_hash[:12] + "...",
            "vault": entry["vault"],
            "expires_at": entry["expires_at"],
            "expired": now > expires_at,
        })
    return results
