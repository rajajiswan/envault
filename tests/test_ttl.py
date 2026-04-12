"""Tests for envault.ttl."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

from envault.ttl import (
    TTLError,
    clear_ttl,
    get_ttl,
    is_expired,
    remaining_seconds,
    set_ttl,
)
from envault.vault import save_vault


@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    return tmp_path


def _make_vault(name: str, vault_dir: Path, passphrase: str = "pw") -> None:
    save_vault(name, {"KEY": "val"}, passphrase, vault_dir)


# ---------------------------------------------------------------------------

def test_set_ttl_returns_future_datetime(vault_dir):
    _make_vault("app", vault_dir)
    expiry = set_ttl("app", 3600, vault_dir)
    assert isinstance(expiry, datetime)
    assert expiry > datetime.now(timezone.utc)


def test_get_ttl_returns_none_when_unset(vault_dir):
    _make_vault("app", vault_dir)
    assert get_ttl("app", vault_dir) is None


def test_get_ttl_returns_stored_datetime(vault_dir):
    _make_vault("app", vault_dir)
    set_ttl("app", 60, vault_dir)
    expiry = get_ttl("app", vault_dir)
    assert expiry is not None
    assert expiry > datetime.now(timezone.utc)


def test_is_expired_false_for_future_ttl(vault_dir):
    _make_vault("app", vault_dir)
    set_ttl("app", 3600, vault_dir)
    assert is_expired("app", vault_dir) is False


def test_is_expired_true_for_past_ttl(vault_dir):
    _make_vault("app", vault_dir)
    set_ttl("app", 1, vault_dir)
    # Manually backdate the stored expiry
    from envault.ttl import _load_store, _save_store
    from datetime import timedelta
    store = _load_store(vault_dir)
    past = datetime.now(timezone.utc) - timedelta(seconds=10)
    store["app"] = past.isoformat()
    _save_store(vault_dir, store)
    assert is_expired("app", vault_dir) is True


def test_is_expired_false_when_no_ttl(vault_dir):
    _make_vault("app", vault_dir)
    assert is_expired("app", vault_dir) is False


def test_remaining_seconds_positive(vault_dir):
    _make_vault("app", vault_dir)
    set_ttl("app", 3600, vault_dir)
    secs = remaining_seconds("app", vault_dir)
    assert secs is not None
    assert secs > 0


def test_remaining_seconds_none_when_no_ttl(vault_dir):
    _make_vault("app", vault_dir)
    assert remaining_seconds("app", vault_dir) is None


def test_clear_ttl_returns_true_when_existed(vault_dir):
    _make_vault("app", vault_dir)
    set_ttl("app", 60, vault_dir)
    assert clear_ttl("app", vault_dir) is True
    assert get_ttl("app", vault_dir) is None


def test_clear_ttl_returns_false_when_not_set(vault_dir):
    _make_vault("app", vault_dir)
    assert clear_ttl("app", vault_dir) is False


def test_set_ttl_unknown_vault_raises(vault_dir):
    with pytest.raises(FileNotFoundError):
        set_ttl("ghost", 60, vault_dir)


def test_set_ttl_zero_seconds_raises(vault_dir):
    _make_vault("app", vault_dir)
    with pytest.raises(TTLError):
        set_ttl("app", 0, vault_dir)


def test_set_ttl_negative_seconds_raises(vault_dir):
    _make_vault("app", vault_dir)
    with pytest.raises(TTLError):
        set_ttl("app", -5, vault_dir)
