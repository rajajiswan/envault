"""Tests for envault.watch."""

import os
import time
from pathlib import Path

import pytest

from envault.watch import watch_file, WatchError, WatchEvent
from envault.vault import load_vault, _vault_path


@pytest.fixture()
def vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    return tmp_path


def _make_env_file(path: Path, content: str) -> Path:
    env_file = path / ".env"
    env_file.write_text(content)
    return env_file


def test_watch_error_on_missing_file(vault_dir):
    with pytest.raises(WatchError, match="File not found"):
        watch_file(
            env_path=str(vault_dir / "nonexistent.env"),
            vault_name="test",
            passphrase="secret",
            max_events=1,
        )


def test_watch_detects_change_and_saves(vault_dir, tmp_path):
    env_file = _make_env_file(tmp_path, "KEY=original\n")
    passphrase = "hunter2"
    vault_name = "watched"

    events = []

    def _on_change(event):
        events.append(event)

    # Modify the file slightly in the future so mtime changes.
    time.sleep(0.05)
    env_file.write_text("KEY=updated\nNEW=yes\n")
    # Force mtime to differ from initial read.
    new_mtime = env_file.stat().st_mtime + 1
    os.utime(env_file, (new_mtime, new_mtime))

    watch_file(
        env_path=str(env_file),
        vault_name=vault_name,
        passphrase=passphrase,
        poll_interval=0.01,
        max_events=1,
        on_change=_on_change,
    )

    assert len(events) == 1
    assert isinstance(events[0], WatchEvent)
    assert events[0].keys_updated == 2
    assert events[0].vault_name == vault_name

    loaded = load_vault(vault_name, passphrase)
    assert loaded["KEY"] == "updated"
    assert loaded["NEW"] == "yes"


def test_watch_event_repr():
    evt = WatchEvent(path="/tmp/.env", vault_name="myapp", keys_updated=3)
    assert "myapp" in repr(evt)
    assert "3" in repr(evt)


def test_watch_stops_after_max_events(vault_dir, tmp_path):
    env_file = _make_env_file(tmp_path, "A=1\n")
    passphrase = "pw"
    vault_name = "maxtest"
    count = {"n": 0}

    original_mtime = env_file.stat().st_mtime

    def bump_and_count(event):
        count["n"] += 1
        # bump mtime again for a second event if needed
        t = env_file.stat().st_mtime + 1
        os.utime(env_file, (t, t))

    # Bump mtime before starting
    t = original_mtime + 1
    os.utime(env_file, (t, t))

    watch_file(
        env_path=str(env_file),
        vault_name=vault_name,
        passphrase=passphrase,
        poll_interval=0.01,
        max_events=1,
        on_change=bump_and_count,
    )

    assert count["n"] == 1
