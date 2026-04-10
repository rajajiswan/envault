"""Tests for envault.cli_profile."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault import profile as prof
from envault.cli_profile import profile_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def clean_env(tmp_path, monkeypatch):
    profiles_file = tmp_path / "profiles.json"
    monkeypatch.setattr(prof, "_PROFILES_FILE", profiles_file)
    monkeypatch.setattr(
        "envault.profile._vault_path",
        lambda name: tmp_path / f"{name}.vault",
    )
    yield tmp_path


def _make_vault(tmp_path, name):
    (tmp_path / f"{name}.vault").write_bytes(b"fake")


def test_create_command_success(runner, clean_env):
    result = runner.invoke(profile_cmd, ["create", "dev"])
    assert result.exit_code == 0
    assert "created" in result.output


def test_create_command_duplicate(runner, clean_env):
    runner.invoke(profile_cmd, ["create", "dev"])
    result = runner.invoke(profile_cmd, ["create", "dev"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_delete_command_success(runner, clean_env):
    runner.invoke(profile_cmd, ["create", "dev"])
    result = runner.invoke(profile_cmd, ["delete", "dev"])
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_delete_unknown_profile(runner, clean_env):
    result = runner.invoke(profile_cmd, ["delete", "ghost"])
    assert result.exit_code == 1


def test_add_and_show_vault(runner, clean_env):
    _make_vault(clean_env, "myapp")
    runner.invoke(profile_cmd, ["create", "dev"])
    result = runner.invoke(profile_cmd, ["add", "dev", "myapp"])
    assert result.exit_code == 0
    show = runner.invoke(profile_cmd, ["show", "dev"])
    assert "myapp" in show.output


def test_remove_vault(runner, clean_env):
    _make_vault(clean_env, "myapp")
    runner.invoke(profile_cmd, ["create", "dev"])
    runner.invoke(profile_cmd, ["add", "dev", "myapp"])
    result = runner.invoke(profile_cmd, ["remove", "dev", "myapp"])
    assert result.exit_code == 0
    show = runner.invoke(profile_cmd, ["show", "dev"])
    assert "myapp" not in show.output


def test_list_profiles_empty(runner, clean_env):
    result = runner.invoke(profile_cmd, ["list"])
    assert result.exit_code == 0
    assert "No profiles" in result.output


def test_list_profiles_shows_entries(runner, clean_env):
    runner.invoke(profile_cmd, ["create", "dev"])
    runner.invoke(profile_cmd, ["create", "prod"])
    result = runner.invoke(profile_cmd, ["list"])
    assert "dev" in result.output
    assert "prod" in result.output


def test_show_unknown_profile(runner, clean_env):
    result = runner.invoke(profile_cmd, ["show", "ghost"])
    assert result.exit_code == 1
