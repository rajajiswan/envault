"""CLI tests for envault import commands."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_import_env import import_cmd
from envault.vault import save_vault


PASSPHRASE = "s3cr3t"


@pytest.fixture()
def runner():
    return CliRunner(mix_stderr=False)


@pytest.fixture()
def clean_env(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_VAULT_DIR", str(tmp_path))
    return tmp_path


def _env_file(tmp_path: Path, content: str) -> Path:
    p = tmp_path / ".env"
    p.write_text(textwrap.dedent(content))
    return p


def test_import_command_success(runner, clean_env):
    src = _env_file(clean_env, "HELLO=world\nFOO=bar\n")
    result = runner.invoke(
        import_cmd,
        ["run", "myapp", "--passphrase", PASSPHRASE, "--source", str(src)],
    )
    assert result.exit_code == 0
    assert "Imported : 2" in result.output
    assert "+ HELLO" in result.output
    assert "+ FOO" in result.output


def test_import_command_skips_existing(runner, clean_env):
    save_vault("myapp", "HELLO=old", PASSPHRASE)
    src = _env_file(clean_env, "HELLO=new\nBAR=baz\n")
    result = runner.invoke(
        import_cmd,
        ["run", "myapp", "--passphrase", PASSPHRASE, "--source", str(src)],
    )
    assert result.exit_code == 0
    assert "Skipped" in result.output
    assert "~ HELLO" in result.output


def test_import_command_overwrite(runner, clean_env):
    save_vault("myapp", "HELLO=old", PASSPHRASE)
    src = _env_file(clean_env, "HELLO=new\n")
    result = runner.invoke(
        import_cmd,
        ["run", "myapp", "--passphrase", PASSPHRASE, "--source", str(src), "--overwrite"],
    )
    assert result.exit_code == 0
    assert "+ HELLO" in result.output
    assert "Skipped" not in result.output


def test_import_command_key_filter(runner, clean_env):
    src = _env_file(clean_env, "A=1\nB=2\nC=3\n")
    result = runner.invoke(
        import_cmd,
        ["run", "myapp", "--passphrase", PASSPHRASE, "--source", str(src), "-k", "A", "-k", "C"],
    )
    assert result.exit_code == 0
    assert "Imported : 2" in result.output
    assert "+ B" not in result.output


def test_import_command_missing_file(runner, clean_env):
    result = runner.invoke(
        import_cmd,
        ["run", "myapp", "--passphrase", PASSPHRASE, "--source", "/no/such/file.env"],
    )
    assert result.exit_code != 0
    assert "File not found" in result.output


def test_import_command_empty_source(runner, clean_env):
    src = _env_file(clean_env, "# comment only\n")
    result = runner.invoke(
        import_cmd,
        ["run", "myapp", "--passphrase", PASSPHRASE, "--source", str(src)],
    )
    assert result.exit_code != 0
    assert "No valid KEY=VALUE" in result.output
