"""Tests for the compare CLI commands."""

import pytest
from click.testing import CliRunner

from envault.cli_compare import compare_cmd
from envault.vault import save_vault


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def clean_env(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    return tmp_path


def _make_vault(name: str, data: dict, passphrase: str = "secret"):
    save_vault(name, data, passphrase)


def test_compare_command_identical(runner, clean_env):
    _make_vault("a", {"KEY": "val"})
    _make_vault("b", {"KEY": "val"})
    result = runner.invoke(
        compare_cmd, ["run", "a", "b", "--pass-a", "secret", "--pass-b", "secret"]
    )
    assert result.exit_code == 0
    assert "identical" in result.output


def test_compare_command_shows_differences(runner, clean_env):
    _make_vault("a", {"KEY": "old", "ONLY_A": "x"})
    _make_vault("b", {"KEY": "new", "ONLY_B": "y"})
    result = runner.invoke(
        compare_cmd, ["run", "a", "b", "--pass-a", "secret", "--pass-b", "secret"]
    )
    assert result.exit_code == 0
    assert "ONLY_A" in result.output
    assert "ONLY_B" in result.output
    assert "KEY" in result.output
    assert "Total differences: 3" in result.output


def test_compare_command_show_values_flag(runner, clean_env):
    _make_vault("a", {"KEY": "old"})
    _make_vault("b", {"KEY": "new"})
    result = runner.invoke(
        compare_cmd,
        ["run", "a", "b", "--pass-a", "secret", "--pass-b", "secret", "--show-values"],
    )
    assert result.exit_code == 0
    assert "old" in result.output
    assert "new" in result.output


def test_compare_command_unknown_vault(runner, clean_env):
    _make_vault("a", {"KEY": "val"})
    result = runner.invoke(
        compare_cmd, ["run", "a", "ghost", "--pass-a", "secret", "--pass-b", "secret"]
    )
    assert result.exit_code != 0
    assert "does not exist" in result.output


def test_compare_command_wrong_passphrase(runner, clean_env):
    _make_vault("a", {"KEY": "val"})
    _make_vault("b", {"KEY": "val"})
    result = runner.invoke(
        compare_cmd, ["run", "a", "b", "--pass-a", "wrong", "--pass-b", "secret"]
    )
    assert result.exit_code != 0
    assert "wrong passphrase" in result.output
