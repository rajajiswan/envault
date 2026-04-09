"""Integration tests for the history CLI command."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_history import history_cmd
from envault.history import record_save, clear_history


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    monkeypatch.setattr("envault.history.HISTORY_DIR", tmp_path / "history")
    monkeypatch.setattr("envault.cli_history.HISTORY_DIR", tmp_path / "history", raising=False)
    # Patch list_vaults to return a known set
    monkeypatch.setattr(
        "envault.cli_history.list_vaults",
        lambda: ["myapp", "staging"],
    )
    yield


def test_history_no_entries(runner):
    result = runner.invoke(history_cmd, ["myapp"])
    assert result.exit_code == 0
    assert "No history found" in result.output


def test_history_shows_saved_entries(runner):
    record_save("myapp", key_count=3, source="cli")
    record_save("myapp", key_count=5, source="sync")
    result = runner.invoke(history_cmd, ["myapp"])
    assert result.exit_code == 0
    assert "keys=3" in result.output
    assert "keys=5" in result.output


def test_history_clear_flag(runner):
    record_save("myapp", key_count=2)
    result = runner.invoke(history_cmd, ["myapp", "--clear"])
    assert result.exit_code == 0
    assert "cleared" in result.output
    # Verify it's actually gone
    result2 = runner.invoke(history_cmd, ["myapp"])
    assert "No history found" in result2.output


def test_history_unknown_vault(runner):
    result = runner.invoke(history_cmd, ["unknown_vault"])
    assert result.exit_code != 0
    assert "not found" in result.output
