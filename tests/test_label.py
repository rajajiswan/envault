"""Tests for envault.label."""

from __future__ import annotations

import pytest

from envault.label import (
    LabelError,
    get_label,
    list_labels,
    remove_label,
    set_label,
)
from envault.vault import save_vault


@pytest.fixture()
def vault_dir(tmp_path, monkeypatch):
    """Redirect vault and label storage to a temp directory."""
    import envault.vault as vault_mod
    import envault.label as label_mod

    monkeypatch.setattr(vault_mod, "_VAULT_DIR", tmp_path)
    label_file = tmp_path / "labels.json"
    monkeypatch.setattr(label_mod, "_LABELS_FILE", label_file)
    return tmp_path


def _make_vault(name: str, passphrase: str = "secret") -> None:
    save_vault(name, {"KEY": "value"}, passphrase)


# ---------------------------------------------------------------------------
# set_label
# ---------------------------------------------------------------------------

def test_set_label_creates_entry(vault_dir):
    _make_vault("prod")
    set_label("prod", "Production")
    assert get_label("prod") == "Production"


def test_set_label_overwrites_existing(vault_dir):
    _make_vault("prod")
    set_label("prod", "Production")
    set_label("prod", "Prod (live)")
    assert get_label("prod") == "Prod (live)"


def test_set_label_unknown_vault_raises(vault_dir):
    with pytest.raises(LabelError, match="does not exist"):
        set_label("ghost", "Ghost Vault")


def test_set_label_empty_string_raises(vault_dir):
    _make_vault("dev")
    with pytest.raises(LabelError, match="empty"):
        set_label("dev", "   ")


# ---------------------------------------------------------------------------
# get_label
# ---------------------------------------------------------------------------

def test_get_label_returns_none_when_not_set(vault_dir):
    _make_vault("staging")
    assert get_label("staging") is None


# ---------------------------------------------------------------------------
# remove_label
# ---------------------------------------------------------------------------

def test_remove_label_clears_entry(vault_dir):
    _make_vault("prod")
    set_label("prod", "Production")
    remove_label("prod")
    assert get_label("prod") is None


def test_remove_label_nonexistent_is_noop(vault_dir):
    """Removing a label that was never set should not raise."""
    remove_label("nobody")


# ---------------------------------------------------------------------------
# list_labels
# ---------------------------------------------------------------------------

def test_list_labels_returns_all(vault_dir):
    _make_vault("a")
    _make_vault("b")
    set_label("a", "Alpha")
    set_label("b", "Beta")
    labels = list_labels()
    assert labels == {"a": "Alpha", "b": "Beta"}


def test_list_labels_empty_when_none_set(vault_dir):
    assert list_labels() == {}
