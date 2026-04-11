"""Tests for envault.cli_notes."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.cli_notes import notes_cmd
from envault.vault import save_vault


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def clean_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    return str(tmp_path)


def _make_vault(name: str, vault_dir: str) -> None:
    save_vault(name, {"K": "v"}, "pass", vault_dir)


def test_set_command_success(runner: CliRunner, clean_env: str) -> None:
    _make_vault("app", clean_env)
    result = runner.invoke(notes_cmd, ["set", "app", "my note", "--dir", clean_env])
    assert result.exit_code == 0
    assert "Note saved" in result.output


def test_set_command_unknown_vault(runner: CliRunner, clean_env: str) -> None:
    result = runner.invoke(notes_cmd, ["set", "ghost", "hi", "--dir", clean_env])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_get_command_shows_note(runner: CliRunner, clean_env: str) -> None:
    _make_vault("app", clean_env)
    runner.invoke(notes_cmd, ["set", "app", "hello world", "--dir", clean_env])
    result = runner.invoke(notes_cmd, ["get", "app", "--dir", clean_env])
    assert result.exit_code == 0
    assert "hello world" in result.output


def test_get_command_no_note(runner: CliRunner, clean_env: str) -> None:
    _make_vault("app", clean_env)
    result = runner.invoke(notes_cmd, ["get", "app", "--dir", clean_env])
    assert "No note found" in result.output


def test_remove_command(runner: CliRunner, clean_env: str) -> None:
    _make_vault("app", clean_env)
    runner.invoke(notes_cmd, ["set", "app", "bye", "--dir", clean_env])
    result = runner.invoke(notes_cmd, ["remove", "app", "--dir", clean_env])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_list_command_shows_entries(runner: CliRunner, clean_env: str) -> None:
    _make_vault("x", clean_env)
    _make_vault("y", clean_env)
    runner.invoke(notes_cmd, ["set", "x", "note x", "--dir", clean_env])
    runner.invoke(notes_cmd, ["set", "y", "note y", "--dir", clean_env])
    result = runner.invoke(notes_cmd, ["list", "--dir", clean_env])
    assert "x" in result.output
    assert "y" in result.output


def test_list_command_empty(runner: CliRunner, clean_env: str) -> None:
    result = runner.invoke(notes_cmd, ["list", "--dir", clean_env])
    assert "No notes found" in result.output
