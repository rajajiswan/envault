"""Tests for envault.remind."""

from __future__ import annotations

import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from envault.remind import (
    RemindError,
    set_reminder,
    get_reminder,
    remove_reminder,
    list_reminders,
    is_due,
    REMINDERS_FILE,
)


@pytest.fixture()
def vault_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envault.remind.REMINDERS_FILE", tmp_path / "reminders.json")
    monkeypatch.setattr("envault.vault.VAULT_DIR", tmp_path)
    return tmp_path


def _make_vault(tmp_path: Path, name: str) -> None:
    from envault.vault import save_vault
    save_vault(name, {"KEY": "val"}, "pass", base_dir=tmp_path)


def test_set_reminder_returns_future_datetime(vault_dir, monkeypatch):
    monkeypatch.setattr("envault.remind.REMINDERS_FILE", vault_dir / "reminders.json")
    _make_vault(vault_dir, "myapp")
    with patch("envault.vault.list_vaults", return_value=["myapp"]):
        due = set_reminder("myapp", 7)
    assert due > datetime.utcnow()


def test_set_reminder_unknown_vault_raises(vault_dir, monkeypatch):
    monkeypatch.setattr("envault.remind.REMINDERS_FILE", vault_dir / "reminders.json")
    with patch("envault.vault.list_vaults", return_value=[]):
        with pytest.raises(RemindError, match="does not exist"):
            set_reminder("ghost", 3)


def test_set_reminder_invalid_days_raises(vault_dir, monkeypatch):
    monkeypatch.setattr("envault.remind.REMINDERS_FILE", vault_dir / "reminders.json")
    with patch("envault.vault.list_vaults", return_value=["myapp"]):
        with pytest.raises(RemindError, match="positive"):
            set_reminder("myapp", 0)


def test_get_reminder_returns_none_when_unset(vault_dir, monkeypatch):
    monkeypatch.setattr("envault.remind.REMINDERS_FILE", vault_dir / "reminders.json")
    assert get_reminder("noapp") is None


def test_get_reminder_returns_entry(vault_dir, monkeypatch):
    monkeypatch.setattr("envault.remind.REMINDERS_FILE", vault_dir / "reminders.json")
    with patch("envault.vault.list_vaults", return_value=["app"]):
        set_reminder("app", 5, message="rotate soon")
    entry = get_reminder("app")
    assert entry is not None
    assert "due" in entry
    assert entry["message"] == "rotate soon"


def test_remove_reminder_returns_true(vault_dir, monkeypatch):
    monkeypatch.setattr("envault.remind.REMINDERS_FILE", vault_dir / "reminders.json")
    with patch("envault.vault.list_vaults", return_value=["app"]):
        set_reminder("app", 2)
    assert remove_reminder("app") is True
    assert get_reminder("app") is None


def test_remove_reminder_nonexistent_returns_false(vault_dir, monkeypatch):
    monkeypatch.setattr("envault.remind.REMINDERS_FILE", vault_dir / "reminders.json")
    assert remove_reminder("ghost") is False


def test_is_due_false_for_future(vault_dir, monkeypatch):
    monkeypatch.setattr("envault.remind.REMINDERS_FILE", vault_dir / "reminders.json")
    with patch("envault.vault.list_vaults", return_value=["app"]):
        set10)
    assert is_due("app") is False


def test_is_due_true_for_past(vault_dir, monkeypatch):
    monkeypatch.setattr("envault.remind.REMINDERS_FILE", vault_dir / "reminders.json")
    past = (datetime.utcnow() - timedelta(days=1)).isoformat()
    store = {"app": {"due": past, "message": ""}}
    (vault_dir / "reminders.json").write_text(json.dumps(store))
    assert is_due("app") is True


def test_list_reminders_returns_all(vault_dir, monkeypatch):
    monkeypatch.setattr("envault.remind.REMINDERS_FILE", vault_dir / "reminders.json")
    with patch("envault.vault.list_vaults", return_value=["a", "b"]):
        set_reminder("a", 1)
        set_reminder("b", 2)
    result = list_reminders()
    assert set(result.keys()) == {"a", "b"}
