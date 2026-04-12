"""Tests for envault.share module."""

import json
import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

from envault.share import (
    ShareError,
    create_share,
    resolve_share,
    revoke_share,
    list_shares,
    _SHARES_FILE,
)
from envault.vault import save_vault


@pytest.fixture()
def vault_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envault.vault.VAULT_DIR", tmp_path)
    monkeypatch.setattr("envault.share._SHARES_FILE", tmp_path / "shares.json")
    monkeypatch.setattr("envault.share._vault_path", lambda name: tmp_path / f"{name}.vault")
    return tmp_path


def _make_vault(name: str, passphrase: str, tmp_path: Path) -> None:
    save_vault(name, {"KEY": "value"}, passphrase)


def test_create_share_returns_token(vault_dir, tmp_path):
    save_vault("myapp", {"KEY": "val"}, "secret")
    token = create_share("myapp", "secret", ttl_minutes=30)
    assert isinstance(token, str)
    assert len(token) > 20


def test_create_share_unknown_vault_raises(vault_dir):
    with pytest.raises(ShareError, match="not found"):
        create_share("ghost", "pass")


def test_create_share_wrong_passphrase_raises(vault_dir):
    save_vault("myapp", {"K": "v"}, "correct")
    with pytest.raises(Exception):
        create_share("myapp", "wrong")


def test_resolve_share_returns_vault_info(vault_dir):
    save_vault("myapp", {"K": "v"}, "pass")
    token = create_share("myapp", "pass", ttl_minutes=60)
    info = resolve_share(token)
    assert info["vault"] == "myapp"
    assert "expires_at" in info


def test_resolve_share_invalid_token_raises(vault_dir):
    with pytest.raises(ShareError, match="Invalid"):
        resolve_share("not-a-real-token")


def test_resolve_share_expired_token_raises(vault_dir):
    save_vault("myapp", {"K": "v"}, "pass")
    past = datetime.now(timezone.utc) - timedelta(minutes=1)
    token = create_share("myapp", "pass", ttl_minutes=60)
    # Patch the expiry to the past
    store = json.loads((vault_dir / "shares.json").read_text())
    for key in store:
        store[key]["expires_at"] = past.isoformat()
    (vault_dir / "shares.json").write_text(json.dumps(store))
    with pytest.raises(ShareError, match="expired"):
        resolve_share(token)


def test_revoke_share_removes_token(vault_dir):
    save_vault("myapp", {"K": "v"}, "pass")
    token = create_share("myapp", "pass")
    assert revoke_share(token) is True
    with pytest.raises(ShareError):
        resolve_share(token)


def test_revoke_unknown_token_returns_false(vault_dir):
    assert revoke_share("nonexistent-token") is False


def test_list_shares_returns_entries(vault_dir):
    save_vault("app1", {"K": "v"}, "p1")
    save_vault("app2", {"K": "v"}, "p2")
    create_share("app1", "p1")
    create_share("app2", "p2")
    entries = list_shares()
    assert len(entries) == 2


def test_list_shares_filtered_by_vault(vault_dir):
    save_vault("app1", {"K": "v"}, "p1")
    save_vault("app2", {"K": "v"}, "p2")
    create_share("app1", "p1")
    create_share("app2", "p2")
    entries = list_shares(vault_name="app1")
    assert all(e["vault"] == "app1" for e in entries)
