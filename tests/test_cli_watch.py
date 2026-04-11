"""Tests for envault.cli_watch."""

import os
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from envault.cli_watch import watch_cmd
from envault.watch import WatchError


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def clean_env(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    return tmp_path


def test_watch_start_missing_file(runner, clean_env):
    result = runner.invoke(
        watch_cmd,
        ["start", "myvault", str(clean_env / "missing.env")],
        input="secret\n",
    )
    assert result.exit_code == 1
    assert "Error" in result.output


def test_watch_start_success(runner, clean_env):
    env_file = clean_env / ".env"
    env_file.write_text("FOO=bar\n")

    with patch("envault.cli_watch.watch_file") as mock_watch:
        mock_watch.return_value = None
        result = runner.invoke(
            watch_cmd,
            [
                "start",
                "myvault",
                str(env_file),
                "--interval",
                "0.5",
            ],
            input="mypassphrase\n",
        )

    assert result.exit_code == 0
    assert "Watching" in result.output
    mock_watch.assert_called_once()
    call_kwargs = mock_watch.call_args
    assert call_kwargs.kwargs["vault_name"] == "myvault" or call_kwargs.args[1] == "myvault"


def test_watch_start_keyboard_interrupt(runner, clean_env):
    env_file = clean_env / ".env"
    env_file.write_text("X=1\n")

    with patch("envault.cli_watch.watch_file", side_effect=KeyboardInterrupt):
        result = runner.invoke(
            watch_cmd,
            ["start", "myvault", str(env_file)],
            input="pw\n",
        )

    assert result.exit_code == 0
    assert "stopped" in result.output.lower()


def test_watch_start_watch_error(runner, clean_env):
    env_file = clean_env / ".env"
    env_file.write_text("X=1\n")

    with patch(
        "envault.cli_watch.watch_file",
        side_effect=WatchError("boom"),
    ):
        result = runner.invoke(
            watch_cmd,
            ["start", "myvault", str(env_file)],
            input="pw\n",
        )

    assert result.exit_code == 1
    assert "boom" in result.output
