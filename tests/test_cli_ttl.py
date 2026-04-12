"""Tests for envault.cli_ttl."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_ttl import ttl_cmd
from envault.vault import save_vault


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def clean_env(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _make_vault(name: str, vault_dir: Path) -> None:
    save_vault(name, {"K": "v"}, "secret", vault_dir)


def test_set_command_success(runner, clean_env):
    vd = clean_env
    _make_vault("myapp", vd)
    result = runner.invoke(ttl_cmd, ["set", "myapp", "3600", "--dir", str(vd)])
    assert result.exit_code == 0
    assert "expires at" in result.output


def test_set_command_unknown_vault(runner, clean_env):
    result = runner.invoke(ttl_cmd, ["set", "ghost", "60", "--dir", str(clean_env)])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_set_command_invalid_seconds(runner, clean_env):
    vd = clean_env
    _make_vault("myapp", vd)
    result = runner.invoke(ttl_cmd, ["set", "myapp", "0", "--dir", str(vd)])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_status_no_ttl(runner, clean_env):
    vd = clean_env
    _make_vault("myapp", vd)
    result = runner.invoke(ttl_cmd, ["status", "myapp", "--dir", str(vd)])
    assert result.exit_code == 0
    assert "No TTL" in result.output


def test_status_shows_remaining(runner, clean_env):
    vd = clean_env
    _make_vault("myapp", vd)
    runner.invoke(ttl_cmd, ["set", "myapp", "3600", "--dir", str(vd)])
    result = runner.invoke(ttl_cmd, ["status", "myapp", "--dir", str(vd)])
    assert result.exit_code == 0
    assert "remaining" in result.output


def test_clear_command_success(runner, clean_env):
    vd = clean_env
    _make_vault("myapp", vd)
    runner.invoke(ttl_cmd, ["set", "myapp", "3600", "--dir", str(vd)])
    result = runner.invoke(ttl_cmd, ["clear", "myapp", "--dir", str(vd)])
    assert result.exit_code == 0
    assert "cleared" in result.output


def test_clear_command_no_ttl_set(runner, clean_env):
    vd = clean_env
    _make_vault("myapp", vd)
    result = runner.invoke(ttl_cmd, ["clear", "myapp", "--dir", str(vd)])
    assert result.exit_code == 0
    assert "No TTL was set" in result.output
