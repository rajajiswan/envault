"""Tests for the diff CLI command."""

import os
import pytest
from click.testing import CliRunner

from envault.cli_diff import diff_cmd
from envault.vault import save_vault


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def clean_env(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_VAULT_DIR", str(tmp_path))
    return tmp_path


def test_diff_no_changes(runner, clean_env, tmp_path):
    env_data = {"KEY": "value", "FOO": "bar"}
    save_vault("myapp", env_data, "secret")

    env_file = tmp_path / ".env"
    env_file.write_text("KEY=value\nFOO=bar\n")

    result = runner.invoke(diff_cmd, ["myapp", str(env_file), "--passphrase", "secret"])
    assert result.exit_code == 0
    assert "No differences" in result.output


def test_diff_shows_changes(runner, clean_env, tmp_path):
    save_vault("myapp", {"KEY": "old", "REMOVE": "gone"}, "secret")

    env_file = tmp_path / ".env"
    env_file.write_text("KEY=new\nADDED=yes\n")

    result = runner.invoke(diff_cmd, ["myapp", str(env_file), "--passphrase", "secret"])
    assert result.exit_code == 0
    assert "+ ADDED" in result.output
    assert "- REMOVE" in result.output
    assert "~ KEY" in result.output


def test_diff_unknown_vault(runner, clean_env, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=value\n")

    result = runner.invoke(diff_cmd, ["ghost", str(env_file), "--passphrase", "x"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_diff_wrong_passphrase(runner, clean_env, tmp_path):
    save_vault("myapp", {"KEY": "value"}, "correct")

    env_file = tmp_path / ".env"
    env_file.write_text("KEY=value\n")

    result = runner.invoke(diff_cmd, ["myapp", str(env_file), "--passphrase", "wrong"])
    assert result.exit_code != 0
