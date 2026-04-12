"""Tests for envault.cli_share CLI commands."""

import json
from pathlib import Path
from datetime import datetime, timedelta, timezone

import pytest
from click.testing import CliRunner

from envault.cli_share import share_cmd
from envault.vault import save_vault


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def clean_env(tmp_path, monkeypatch):
    monkeypatch.setattr("envault.vault.VAULT_DIR", tmp_path)
    monkeypatch.setattr("envault.share._SHARES_FILE", tmp_path / "shares.json")
    monkeypatch.setattr("envault.share._vault_path", lambda name: tmp_path / f"{name}.vault")
    return tmp_path


def _make_vault(name: str, passphrase: str) -> None:
    save_vault(name, {"KEY": "value"}, passphrase)


def test_create_command_success(runner, clean_env):
    _make_vault("myapp", "secret")
    result = runner.invoke(share_cmd, ["create", "myapp", "--passphrase", "secret", "--ttl", "30"])
    assert result.exit_code == 0
    assert "Share token" in result.output
    assert "30 minute" in result.output


def test_create_command_unknown_vault(runner, clean_env):
    result = runner.invoke(share_cmd, ["create", "ghost", "--passphrase", "pass"])
    assert result.exit_code == 1
    assert "not found" in result.output.lower() or "not found" in (result.output + "").lower()


def test_resolve_command_success(runner, clean_env):
    _make_vault("myapp", "secret")
    create_result = runner.invoke(share_cmd, ["create", "myapp", "--passphrase", "secret"])
    token = [line for line in create_result.output.splitlines() if len(line) > 30][0].strip()
    result = runner.invoke(share_cmd, ["resolve", token])
    assert result.exit_code == 0
    assert "myapp" in result.output


def test_resolve_command_invalid_token(runner, clean_env):
    result = runner.invoke(share_cmd, ["resolve", "bad-token"])
    assert result.exit_code == 1


def test_revoke_command_success(runner, clean_env):
    _make_vault("myapp", "secret")
    create_result = runner.invoke(share_cmd, ["create", "myapp", "--passphrase", "secret"])
    token = [line for line in create_result.output.splitlines() if len(line) > 30][0].strip()
    result = runner.invoke(share_cmd, ["revoke", token])
    assert result.exit_code == 0
    assert "revoked" in result.output.lower()


def test_list_command_shows_entries(runner, clean_env):
    _make_vault("myapp", "secret")
    runner.invoke(share_cmd, ["create", "myapp", "--passphrase", "secret"])
    result = runner.invoke(share_cmd, ["list"])
    assert result.exit_code == 0
    assert "myapp" in result.output


def test_list_command_no_tokens(runner, clean_env):
    result = runner.invoke(share_cmd, ["list"])
    assert result.exit_code == 0
    assert "No share tokens" in result.output
