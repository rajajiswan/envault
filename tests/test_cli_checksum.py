"""Tests for envault.cli_checksum."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_checksum import checksum_cmd
from envault.vault import save_vault


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def clean_env(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    return tmp_path


def _make_vault(name: str, passphrase: str, env: dict) -> None:
    save_vault(name, passphrase, env)


def test_record_command_success(runner, clean_env):
    _make_vault("app", "pass", {"KEY": "val"})
    result = runner.invoke(checksum_cmd, ["record", "app", "--passphrase", "pass"])
    assert result.exit_code == 0
    assert "Checksum recorded" in result.output


def test_record_command_unknown_vault(runner, clean_env):
    result = runner.invoke(checksum_cmd, ["record", "ghost", "--passphrase", "pass"])
    assert result.exit_code != 0
    assert "Error" in result.output or "Error" in (result.output + str(result.exception))


def test_verify_command_passes(runner, clean_env):
    _make_vault("app", "pass", {"KEY": "val"})
    runner.invoke(checksum_cmd, ["record", "app", "--passphrase", "pass"])
    result = runner.invoke(checksum_cmd, ["verify", "app", "--passphrase", "pass"])
    assert result.exit_code == 0
    assert "OK" in result.output


def test_verify_command_fails_after_change(runner, clean_env):
    _make_vault("app", "pass", {"KEY": "original"})
    runner.invoke(checksum_cmd, ["record", "app", "--passphrase", "pass"])
    _make_vault("app", "pass", {"KEY": "modified"})
    result = runner.invoke(checksum_cmd, ["verify", "app", "--passphrase", "pass"])
    assert result.exit_code != 0
    assert "MISMATCH" in result.output


def test_verify_command_no_checksum_recorded(runner, clean_env):
    _make_vault("app", "pass", {"KEY": "val"})
    result = runner.invoke(checksum_cmd, ["verify", "app", "--passphrase", "pass"])
    assert result.exit_code != 0


def test_show_command_displays_digest(runner, clean_env):
    _make_vault("app", "pass", {"KEY": "val"})
    runner.invoke(checksum_cmd, ["record", "app", "--passphrase", "pass"])
    result = runner.invoke(checksum_cmd, ["show", "app"])
    assert result.exit_code == 0
    assert len(result.output.strip()) == 64


def test_show_command_no_checksum(runner, clean_env):
    _make_vault("app", "pass", {"KEY": "val"})
    result = runner.invoke(checksum_cmd, ["show", "app"])
    assert result.exit_code == 0
    assert "No checksum" in result.output


def test_clear_command_removes_checksum(runner, clean_env):
    _make_vault("app", "pass", {"KEY": "val"})
    runner.invoke(checksum_cmd, ["record", "app", "--passphrase", "pass"])
    result = runner.invoke(checksum_cmd, ["clear", "app"])
    assert result.exit_code == 0
    assert "cleared" in result.output
    show = runner.invoke(checksum_cmd, ["show", "app"])
    assert "No checksum" in show.output
