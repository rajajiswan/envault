"""Tests for envault.cli_prune."""

from __future__ import annotations

import os
import pytest
from click.testing import CliRunner

from envault.cli_prune import prune_cmd
from envault.vault import save_vault


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def clean_env(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "envault.vault.VAULT_DIR", str(tmp_path), raising=False
    )
    monkeypatch.setattr(
        "envault.prune._vault_path",
        lambda name: os.path.join(str(tmp_path), f"{name}.vault"),
    )
    return tmp_path


def _make_vault(name, data, passphrase, vault_dir):
    save_vault(name, data, passphrase, vault_dir=str(vault_dir))


def test_prune_command_nothing_to_prune(runner, clean_env):
    _make_vault("prod", {"KEY": "val"}, "pass", clean_env)

    result = runner.invoke(prune_cmd, ["run", "--passphrase", "pass"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "Nothing to prune" in result.output


def test_prune_command_removes_empty(runner, clean_env):
    _make_vault("empty", {}, "pass", clean_env)

    result = runner.invoke(prune_cmd, ["run", "--passphrase", "pass"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "Removed" in result.output
    assert "empty" in result.output


def test_prune_command_dry_run(runner, clean_env):
    _make_vault("empty", {}, "pass", clean_env)

    result = runner.invoke(
        prune_cmd, ["run", "--passphrase", "pass", "--dry-run"], catch_exceptions=False
    )

    assert result.exit_code == 0
    assert "dry-run" in result.output
    assert os.path.exists(os.path.join(str(clean_env), "empty.vault"))


def test_prune_command_shows_summary(runner, clean_env):
    _make_vault("empty", {}, "pass", clean_env)
    _make_vault("full", {"X": "1"}, "pass", clean_env)

    result = runner.invoke(prune_cmd, ["run", "--passphrase", "pass"], catch_exceptions=False)

    assert "Summary:" in result.output
    assert "1 removed" in result.output
    assert "1 kept" in result.output
