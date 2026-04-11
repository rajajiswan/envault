"""Tests for envault.pin module."""

from __future__ import annotations

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from envault.pin import (
    PinError,
    pin_vault,
    unpin_vault,
    list_pinned,
    is_pinned,
    _PINS_FILE,
)
from envault.vault import save_vault


@pytest.fixture()
def isolated(tmp_path, monkeypatch):
    """Redirect vault dir and pins file to tmp_path."""
    vault_dir = tmp_path / "vaults"
    vault_dir.mkdir()
    pins_file = tmp_path / "pins.json"

    monkeypatch.setattr("envault.vault.VAULT_DIR", vault_dir)
    monkeypatch.setattr("envault.pin._PINS_FILE", pins_file)
    monkeypatch.setattr("envault.pin._vault_path", lambda name: vault_dir / f"{name}.vault")
    return tmp_path


def _make_vault(name: str, vault_dir: Path) -> None:
    path = vault_dir / f"{name}.vault"
    path.write_text("placeholder")


def test_pin_vault_creates_entry(isolated, tmp_path):
    vault_dir = tmp_path / "vaults"
    _make_vault("myapp", vault_dir)
    pin_vault("myapp")
    assert is_pinned("myapp")


def test_pin_vault_is_idempotent(isolated, tmp_path):
    vault_dir = tmp_path / "vaults"
    _make_vault("myapp", vault_dir)
    pin_vault("myapp")
    pin_vault("myapp")
    assert list_pinned().count("myapp") == 1


def test_pin_nonexistent_vault_raises(isolated):
    with pytest.raises(PinError, match="does not exist"):
        pin_vault("ghost")


def test_unpin_vault_removes_entry(isolated, tmp_path):
    vault_dir = tmp_path / "vaults"
    _make_vault("myapp", vault_dir)
    pin_vault("myapp")
    unpin_vault("myapp")
    assert not is_pinned("myapp")


def test_unpin_not_pinned_is_noop(isolated, tmp_path):
    vault_dir = tmp_path / "vaults"
    _make_vault("myapp", vault_dir)
    # Should not raise
    unpin_vault("myapp")


def test_list_pinned_returns_existing_only(isolated, tmp_path):
    vault_dir = tmp_path / "vaults"
    _make_vault("app1", vault_dir)
    _make_vault("app2", vault_dir)
    pin_vault("app1")
    pin_vault("app2")
    # Simulate app2 vault being deleted
    (vault_dir / "app2.vault").unlink()
    pinned = list_pinned()
    assert "app1" in pinned
    assert "app2" not in pinned


def test_list_pinned_empty_when_no_pins_file(isolated):
    assert list_pinned() == []


def test_is_pinned_false_for_unknown(isolated):
    assert not is_pinned("unknown")
