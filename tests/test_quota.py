"""Tests for envault.quota."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.vault import save_vault
from envault.quota import (
    QuotaError,
    set_quota,
    get_quota,
    remove_quota,
    check_quota,
    _DEFAULT_QUOTA,
)


@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    return tmp_path


def _make_vault(name: str, keys: dict, passphrase: str, vault_dir: Path) -> None:
    env_text = "\n".join(f"{k}={v}" for k, v in keys.items())
    save_vault(name, env_text, passphrase, vault_dir)


# ---------------------------------------------------------------------------
# set_quota / get_quota
# ---------------------------------------------------------------------------

def test_set_quota_stores_limit(vault_dir):
    _make_vault("app", {"KEY": "val"}, "pass", vault_dir)
    set_quota("app", 50, vault_dir)
    assert get_quota("app", vault_dir) == 50


def test_get_quota_returns_default_when_unset(vault_dir):
    _make_vault("app", {"KEY": "val"}, "pass", vault_dir)
    assert get_quota("app", vault_dir) == _DEFAULT_QUOTA


def test_set_quota_unknown_vault_raises(vault_dir):
    with pytest.raises(QuotaError, match="does not exist"):
        set_quota("ghost", 10, vault_dir)


def test_set_quota_zero_raises(vault_dir):
    _make_vault("app", {"KEY": "val"}, "pass", vault_dir)
    with pytest.raises(QuotaError, match="at least 1"):
        set_quota("app", 0, vault_dir)


def test_set_quota_overwrites_previous(vault_dir):
    _make_vault("app", {"KEY": "val"}, "pass", vault_dir)
    set_quota("app", 10, vault_dir)
    set_quota("app", 25, vault_dir)
    assert get_quota("app", vault_dir) == 25


# ---------------------------------------------------------------------------
# remove_quota
# ---------------------------------------------------------------------------

def test_remove_quota_reverts_to_default(vault_dir):
    _make_vault("app", {"KEY": "val"}, "pass", vault_dir)
    set_quota("app", 5, vault_dir)
    remove_quota("app", vault_dir)
    assert get_quota("app", vault_dir) == _DEFAULT_QUOTA


def test_remove_quota_nonexistent_is_noop(vault_dir):
    # Should not raise even if no quota was set
    remove_quota("ghost", vault_dir)


# ---------------------------------------------------------------------------
# check_quota
# ---------------------------------------------------------------------------

def test_check_quota_within_limit(vault_dir):
    _make_vault("app", {"A": "1", "B": "2"}, "pass", vault_dir)
    set_quota("app", 5, vault_dir)
    count, limit = check_quota("app", "pass", vault_dir)
    assert count == 2
    assert limit == 5


def test_check_quota_exceeded_raises(vault_dir):
    _make_vault("app", {"A": "1", "B": "2", "C": "3"}, "pass", vault_dir)
    set_quota("app", 2, vault_dir)
    with pytest.raises(QuotaError, match="exceeding quota"):
        check_quota("app", "pass", vault_dir)


def test_check_quota_exact_limit_is_ok(vault_dir):
    _make_vault("app", {"X": "1", "Y": "2"}, "pass", vault_dir)
    set_quota("app", 2, vault_dir)
    count, limit = check_quota("app", "pass", vault_dir)
    assert count == limit == 2
