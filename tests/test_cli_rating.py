"""CLI tests for the rating command."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_rating import rating_cmd
from envault.vault import save_vault


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def clean_env(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    return tmp_path


def _make_vault(name: str, env: dict, passphrase: str = "pass") -> None:
    save_vault(name, env, passphrase)


def test_show_command_pass(runner, clean_env):
    _make_vault("prod", {"API_KEY": "xK9#mP2$qRtL8nVwZz"})
    result = runner.invoke(rating_cmd, ["show", "prod", "--passphrase", "pass"])
    assert result.exit_code == 0
    assert "Score" in result.output
    assert "PASS" in result.output


def test_show_command_fail(runner, clean_env):
    _make_vault("weak", {"SECRET": "abc"})
    result = runner.invoke(rating_cmd, ["show", "weak", "--passphrase", "pass"])
    assert result.exit_code == 0
    assert "FAIL" in result.output


def test_show_command_verbose(runner, clean_env):
    _make_vault("app", {"API_TOKEN": "xK9#mP2$qRtL8nVw", "PASSWORD": "bad"})
    result = runner.invoke(rating_cmd, ["show", "app", "--passphrase", "pass", "--verbose"])
    assert result.exit_code == 0
    assert "Per-key scores" in result.output
    assert "Issues" in result.output
    assert "API_TOKEN" in result.output


def test_show_command_verbose_no_issues(runner, clean_env):
    _make_vault("clean", {"HOST": "localhost"})
    result = runner.invoke(rating_cmd, ["show", "clean", "--passphrase", "pass", "--verbose"])
    assert result.exit_code == 0
    assert "No issues found" in result.output


def test_show_command_unknown_vault(runner, clean_env):
    result = runner.invoke(rating_cmd, ["show", "ghost", "--passphrase", "pass"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_show_command_wrong_passphrase(runner, clean_env):
    _make_vault("locked", {"KEY": "value"})
    result = runner.invoke(rating_cmd, ["show", "locked", "--passphrase", "wrong"])
    assert result.exit_code != 0
    assert "Error" in result.output
