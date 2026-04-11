"""Tests for envault.expire."""

from __future__ import annotations

import pytest
from datetime import datetime, timezone, timedelta
from pathlib import Path

from envault.expire import (
    ExpireError,
    set_expiry,
    clear_expiry,
    get_expiry,
    is_expired,
    check_not_expired,
)
from envault.vault import save_vault


@pytest.fixture()
def vault_dir(tmp_path: Path) -> str:
    return str(tmp_path)


def _make_vault(name: str, vault_dir: str) -> None:
    save_vault(name, {"KEY": "value"}, "pass", vault_dir=vault_dir)


def _future(seconds: int = 3600) -> datetime:
    return datetime.now(timezone.utc) + timedelta(seconds=seconds)


def _past(seconds: int = 3600) -> datetime:
    return datetime.now(timezone.utc) - timedelta(seconds=seconds)


def test_set_expiry_stores_datetime(vault_dir):
    _make_vault("myapp", vault_dir)
    exp = _future()
    set_expiry("myapp", exp, vault_dir=vault_dir)
    stored = get_expiry("myapp", vault_dir=vault_dir)
    assert stored is not None
    assert abs((stored - exp).total_seconds()) < 1


def test_get_expiry_returns_none_when_not_set(vault_dir):
    _make_vault("myapp", vault_dir)
    assert get_expiry("myapp", vault_dir=vault_dir) is None


def test_set_expiry_unknown_vault_raises(vault_dir):
    with pytest.raises(ExpireError, match="does not exist"):
        set_expiry("ghost", _future(), vault_dir=vault_dir)


def test_is_expired_false_for_future(vault_dir):
    _make_vault("myapp", vault_dir)
    set_expiry("myapp", _future(), vault_dir=vault_dir)
    assert is_expired("myapp", vault_dir=vault_dir) is False


def test_is_expired_true_for_past(vault_dir):
    _make_vault("myapp", vault_dir)
    set_expiry("myapp", _past(), vault_dir=vault_dir)
    assert is_expired("myapp", vault_dir=vault_dir) is True


def test_is_expired_false_when_no_expiry(vault_dir):
    _make_vault("myapp", vault_dir)
    assert is_expired("myapp", vault_dir=vault_dir) is False


def test_check_not_expired_passes_for_future(vault_dir):
    _make_vault("myapp", vault_dir)
    set_expiry("myapp", _future(), vault_dir=vault_dir)
    check_not_expired("myapp", vault_dir=vault_dir)  # should not raise


def test_check_not_expired_raises_for_past(vault_dir):
    _make_vault("myapp", vault_dir)
    set_expiry("myapp", _past(), vault_dir=vault_dir)
    with pytest.raises(ExpireError, match="expired at"):
        check_not_expired("myapp", vault_dir=vault_dir)


def test_clear_expiry_removes_entry(vault_dir):
    _make_vault("myapp", vault_dir)
    set_expiry("myapp", _past(), vault_dir=vault_dir)
    clear_expiry("myapp", vault_dir=vault_dir)
    assert get_expiry("myapp", vault_dir=vault_dir) is None
    assert is_expired("myapp", vault_dir=vault_dir) is False


def test_clear_expiry_noop_when_not_set(vault_dir):
    _make_vault("myapp", vault_dir)
    clear_expiry("myapp", vault_dir=vault_dir)  # should not raise
