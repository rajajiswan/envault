"""CLI tests for the merge command."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_merge import merge_cmd
from envault.vault import save_vault, load_vault


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def clean_env(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_VAULT_DIR", str(tmp_path))
    return tmp_path


def _make_vault(name, passphrase, data):
    save_vault(name, passphrase, data)


def _invoke_merge(runner, src, dst, src_pass, dst_pass, extra_args=None):
    """Helper to invoke the merge command with common arguments."""
    args = ["run", src, dst, "--source-pass", src_pass, "--target-pass", dst_pass]
    if extra_args:
        args.extend(extra_args)
    return runner.invoke(merge_cmd, args)


def test_merge_command_success(runner, clean_env):
    _make_vault("src", "sp", {"FOO": "bar"})
    _make_vault("dst", "dp", {})

    result = _invoke_merge(runner, "src", "dst", "sp", "dp")

    assert result.exit_code == 0
    assert "Added" in result.output
    assert "FOO" in result.output


def test_merge_command_skip_without_overwrite(runner, clean_env):
    _make_vault("src", "sp", {"KEY": "new"})
    _make_vault("dst", "dp", {"KEY": "old"})

    result = _invoke_merge(runner, "src", "dst", "sp", "dp")

    assert result.exit_code == 0
    assert "Skipped" in result.output
    assert load_vault("dst", "dp")["KEY"] == "old"


def test_merge_command_overwrite_flag(runner, clean_env):
    _make_vault("src", "sp", {"KEY": "new"})
    _make_vault("dst", "dp", {"KEY": "old"})

    result = _invoke_merge(runner, "src", "dst", "sp", "dp", ["--overwrite"])

    assert result.exit_code == 0
    assert "Overwritten" in result.output
    assert load_vault("dst", "dp")["KEY"] == "new"


def test_merge_command_unknown_vault(runner, clean_env):
    _make_vault("dst", "dp", {})

    result = _invoke_merge(runner, "ghost", "dst", "sp", "dp")

    assert result.exit_code != 0
    assert "Error" in result.output


def test_merge_command_specific_keys(runner, clean_env):
    _make_vault("src", "sp", {"A": "1", "B": "2"})
    _make_vault("dst", "dp", {})

    result = _invoke_merge(runner, "src", "dst", "sp", "dp", ["--keys", "A"])

    assert result.exit_code == 0
    merged = load_vault("dst", "dp")
    assert "A" in merged
    assert "B" not in merged
