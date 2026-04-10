"""CLI tests for the clone command."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.cli_clone import clone_cmd
from envault.vault import save_vault, load_vault


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture(autouse=True)
def clean_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENVAULT_VAULT_DIR", str(tmp_path))
    import envault.vault as vault_mod
    import envault.clone as clone_mod
    monkeypatch.setattr(vault_mod, "_DEFAULT_VAULT_DIR", tmp_path)
    monkeypatch.setattr(clone_mod, "_vault_path",
                        lambda name, d=None: vault_mod._vault_path(name, tmp_path))
    monkeypatch.setattr(clone_mod, "load_vault",
                        lambda n, p, d=None: vault_mod.load_vault(n, p, tmp_path))
    monkeypatch.setattr(clone_mod, "save_vault",
                        lambda n, data, p, d=None: vault_mod.save_vault(n, data, p, tmp_path))


def _make_vault(name: str, data: dict, passphrase: str, vault_dir: Path) -> None:
    save_vault(name, data, passphrase, vault_dir)


def test_clone_command_success(runner: CliRunner, tmp_path: Path) -> None:
    _make_vault("src", {"FOO": "bar"}, "pass", tmp_path)
    result = runner.invoke(
        clone_cmd,
        ["run", "src", "dst", "--passphrase", "pass", "--new-passphrase", "pass"],
    )
    assert result.exit_code == 0
    assert "Cloned" in result.output
    assert "src" in result.output
    assert "dst" in result.output


def test_clone_command_unknown_source(runner: CliRunner) -> None:
    result = runner.invoke(
        clone_cmd,
        ["run", "ghost", "dst", "--passphrase", "pass", "--new-passphrase", "pass"],
    )
    assert result.exit_code != 0
    assert "Error" in result.output


def test_clone_command_wrong_passphrase(runner: CliRunner, tmp_path: Path) -> None:
    _make_vault("src", {"K": "v"}, "correct", tmp_path)
    result = runner.invoke(
        clone_cmd,
        ["run", "src", "dst", "--passphrase", "wrong", "--new-passphrase", "wrong"],
    )
    assert result.exit_code != 0
    assert "incorrect passphrase" in result.output


def test_clone_command_existing_destination(runner: CliRunner, tmp_path: Path) -> None:
    _make_vault("src", {}, "pass", tmp_path)
    _make_vault("dst", {}, "pass", tmp_path)
    result = runner.invoke(
        clone_cmd,
        ["run", "src", "dst", "--passphrase", "pass", "--new-passphrase", "pass"],
    )
    assert result.exit_code != 0
    assert "already exists" in result.output
