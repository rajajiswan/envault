"""Tests for envault.cli_remind."""

from __future__ import annotations

import json
import pytest
from datetime import datetime, timedelta
from click.testing import CliRunner
from unittest.mock import patch

from envault.cli_remind import remind_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def clean_env(tmp_path, monkeypatch):
    monkeypatch.setattr("envault.remind.REMINDERS_FILE", tmp_path / "reminders.json")
    monkeypatch.setattr("envault.vault.VAULT_DIR", tmp_path)
    return tmp_path


def test_set_command_success(runner, clean_env):
    with patch("envault.remind.list_vaults", return_value=["myapp"]):
        result = runner.invoke(remind_cmd, ["set", "myapp", "--days", "7", "--message", "rotate keys"])
    assert result.exit_code == 0
    assert "Reminder set" in result.output
    assert "myapp" in result.output


def test_set_command_unknown_vault(runner, clean_env):
    with patch("envault.remind.list_vaults", return_value=[]):
        result = runner.invoke(remind_cmd, ["set", "ghost", "--days", "3"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_status_command_no_reminder(runner, clean_env):
    result = runner.invoke(remind_cmd, ["status", "noapp"])
    assert result.exit_code == 0
    assert "No reminder" in result.output


def test_status_command_shows_due_date(runner, clean_env):
    with patch("envault.remind.list_vaults", return_value=["app"]):
        runner.invoke(remind_cmd, ["set", "app", "--days", "5", "--message", "check this"])
    result = runner.invoke(remind_cmd, ["status", "app"])
    assert result.exit_code == 0
    assert "Due:" in result.output
    assert "check this" in result.output


def test_status_command_shows_overdue(runner, clean_env):
    past = (datetime.utcnow() - timedelta(days=2)).isoformat()
    store = {"app": {"due": past, "message": ""}}
    (clean_env / "reminders.json").write_text(json.dumps(store))
    result = runner.invoke(remind_cmd, ["status", "app"])
    assert "OVERDUE" in result.output


def test_remove_command_success(runner, clean_env):
    with patch("envault.remind.list_vaults", return_value=["app"]):
        runner.invoke(remind_cmd, ["set", "app", "--days", "1"])
    result = runner.invoke(remind_cmd, ["remove", "app"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_command_not_found(runner, clean_env):
    result = runner.invoke(remind_cmd, ["remove", "ghost"])
    assert result.exit_code == 0
    assert "No reminder found" in result.output


def test_list_command_empty(runner, clean_env):
    result = runner.invoke(remind_cmd, ["list"])
    assert result.exit_code == 0
    assert "No reminders" in result.output


def test_list_command_shows_entries(runner, clean_env):
    with patch("envault.remind.list_vaults", return_value=["a", "b"]):
        runner.invoke(remind_cmd, ["set", "a", "--days", "3"])
        runner.invoke(remind_cmd, ["set", "b", "--days", "10"])
    result = runner.invoke(remind_cmd, ["list"])
    assert "a" in result.output
    assert "b" in result.output
