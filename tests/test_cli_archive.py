"""CLI tests for the archive commands."""

import json
import pytest
from click.testing import CliRunner

from envault.cli_archive import archive_cmd
from envault.vault import save_vault, _vault_path


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def clean_env(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    return tmp_path


def _make_vault(name, env, passphrase="secret"):
    save_vault(name, env, passphrase)


# ---------------------------------------------------------------------------

def test_create_command_success(runner, clean_env, tmp_path):
    _make_vault("v1", {"FOO": "bar"}, "secret")
    dest = str(tmp_path / "out.json")
    result = runner.invoke(
        archive_cmd,
        ["create", "v1", "--passphrase", "secret", "--output", dest],
    )
    assert result.exit_code == 0
    assert "Archived 1 vault" in result.output
    assert "v1" in result.output


def test_create_command_unknown_vault(runner, clean_env, tmp_path):
    dest = str(tmp_path / "out.json")
    result = runner.invoke(
        archive_cmd,
        ["create", "ghost", "--passphrase", "pw", "--output", dest],
    )
    assert result.exit_code == 1
    assert "Error" in result.output


def test_extract_command_success(runner, clean_env, tmp_path):
    _make_vault("ex1", {"KEY": "val"}, "pw")
    dest = str(tmp_path / "arch.json")
    runner.invoke(
        archive_cmd,
        ["create", "ex1", "--passphrase", "pw", "--output", dest],
    )
    _vault_path("ex1").unlink()
    result = runner.invoke(
        archive_cmd,
        ["extract", dest, "--passphrase", "pw"],
    )
    assert result.exit_code == 0
    assert "Extracted 1 vault" in result.output


def test_extract_command_skips_existing(runner, clean_env, tmp_path):
    _make_vault("skip1", {"A": "1"}, "pw")
    dest = str(tmp_path / "skip.json")
    runner.invoke(
        archive_cmd,
        ["create", "skip1", "--passphrase", "pw", "--output", dest],
    )
    result = runner.invoke(
        archive_cmd,
        ["extract", dest, "--passphrase", "pw"],
    )
    assert result.exit_code == 0
    assert "No vaults extracted" in result.output


def test_extract_command_missing_file(runner, clean_env):
    result = runner.invoke(
        archive_cmd,
        ["extract", "/no/such/file.json", "--passphrase", "pw"],
    )
    assert result.exit_code == 1
    assert "Error" in result.output
