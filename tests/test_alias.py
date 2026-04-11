"""Tests for envault.alias."""

from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import patch

from envault.alias import (
    AliasError,
    set_alias,
    remove_alias,
    resolve_alias,
    list_aliases,
    clear_aliases,
    _ALIAS_FILE,
)
from envault.vault import save_vault


@pytest.fixture()
def isolated(tmp_path, monkeypatch):
    """Redirect vault dir and alias file to tmp_path."""
    vault_dir = tmp_path / "vaults"
    vault_dir.mkdir()
    alias_file = tmp_path / "aliases.json"

    monkeypatch.setattr("envault.vault.VAULT_DIR", vault_dir)
    monkeypatch.setattr("envault.alias._ALIAS_FILE", alias_file)
    monkeypatch.setattr("envault.alias._vault_path",
                        lambda name: vault_dir / f"{name}.vault")
    return tmp_path


def _make_vault(name: str, vault_dir: Path) -> None:
    path = vault_dir / f"{name}.vault"
    save_vault(name, {"KEY": "val"}, "pass", vault_dir=vault_dir)


# ── set_alias ────────────────────────────────────────────────────────────────

def test_set_alias_creates_mapping(isolated):
    vault_dir = isolated / "vaults"
    _make_vault("production", vault_dir)
    set_alias("prod", "production")
    assert resolve_alias("prod") == "production"


def test_set_alias_unknown_vault_raises(isolated):
    with pytest.raises(AliasError, match="does not exist"):
        set_alias("ghost", "nonexistent")


def test_set_alias_overwrites_existing(isolated):
    vault_dir = isolated / "vaults"
    _make_vault("staging", vault_dir)
    _make_vault("production", vault_dir)
    set_alias("env", "staging")
    set_alias("env", "production")
    assert resolve_alias("env") == "production"


# ── remove_alias ─────────────────────────────────────────────────────────────

def test_remove_alias_deletes_entry(isolated):
    vault_dir = isolated / "vaults"
    _make_vault("staging", vault_dir)
    set_alias("stg", "staging")
    remove_alias("stg")
    assert resolve_alias("stg") is None


def test_remove_alias_nonexistent_is_noop(isolated):
    remove_alias("does-not-exist")  # should not raise


# ── list_aliases ─────────────────────────────────────────────────────────────

def test_list_aliases_empty_when_no_file(isolated):
    assert list_aliases() == {}


def test_list_aliases_returns_all(isolated):
    vault_dir = isolated / "vaults"
    _make_vault("a", vault_dir)
    _make_vault("b", vault_dir)
    set_alias("alpha", "a")
    set_alias("beta", "b")
    result = list_aliases()
    assert result == {"alpha": "a", "beta": "b"}


# ── clear_aliases ─────────────────────────────────────────────────────────────

def test_clear_aliases_removes_all(isolated):
    vault_dir = isolated / "vaults"
    _make_vault("x", vault_dir)
    set_alias("ex", "x")
    clear_aliases()
    assert list_aliases() == {}


def test_clear_aliases_noop_when_empty(isolated):
    clear_aliases()  # should not raise
