"""Integration tests for CLI sync commands (export/import)."""

import json
import os
import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.cli_sync import export_cmd, import_cmd
from envault.vault import save_vault, _vault_path


PASSPHRASE = "cli-sync-pass"
VAULT_NAME = "cli_sync_vault"
SAMPLE_VARS = {"APP_ENV": "production", "PORT": "8080"}


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def clean_env(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    yield


def test_export_command_success(runner, tmp_path):
    save_vault(VAULT_NAME, SAMPLE_VARS, PASSPHRASE)
    export_file = str(tmp_path / "out.evault")

    result = runner.invoke(
        export_cmd,
        [VAULT_NAME, export_file, "--passphrase", PASSPHRASE],
    )
    assert result.exit_code == 0
    assert "exported" in result.output
    assert Path(export_file).exists()


def test_export_command_unknown_vault(runner, tmp_path):
    export_file = str(tmp_path / "out.evault")
    result = runner.invoke(
        export_cmd,
        ["nonexistent", export_file, "--passphrase", PASSPHRASE],
    )
    assert result.exit_code != 0


def test_import_command_success(runner, tmp_path):
    save_vault(VAULT_NAME, SAMPLE_VARS, PASSPHRASE)
    export_file = str(tmp_path / "out.evault")

    runner.invoke(export_cmd, [VAULT_NAME, export_file, "--passphrase", PASSPHRASE])
    _vault_path(VAULT_NAME).unlink()

    result = runner.invoke(
        import_cmd,
        [export_file, "--passphrase", PASSPHRASE],
    )
    assert result.exit_code == 0
    assert "imported successfully" in result.output


def test_import_command_wrong_passphrase(runner, tmp_path):
    save_vault(VAULT_NAME, SAMPLE_VARS, PASSPHRASE)
    export_file = str(tmp_path / "out.evault")

    runner.invoke(export_cmd, [VAULT_NAME, export_file, "--passphrase", PASSPHRASE])
    _vault_path(VAULT_NAME).unlink()

    result = runner.invoke(
        import_cmd,
        [export_file, "--passphrase", "wrong"],
    )
    assert result.exit_code != 0
    assert "failed" in result.output.lower()


def test_import_command_overwrite_flag(runner, tmp_path):
    save_vault(VAULT_NAME, SAMPLE_VARS, PASSPHRASE)
    export_file = str(tmp_path / "out.evault")

    runner.invoke(export_cmd, [VAULT_NAME, export_file, "--passphrase", PASSPHRASE])

    result = runner.invoke(
        import_cmd,
        [export_file, "--passphrase", PASSPHRASE, "--overwrite"],
    )
    assert result.exit_code == 0
    assert "imported successfully" in result.output
