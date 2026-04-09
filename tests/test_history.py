"""Unit tests for envault.history."""

from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import patch

from envault.history import (
    record_save,
    load_history,
    clear_history,
    format_history,
    HISTORY_DIR,
)


@pytest.fixture(autouse=True)
def isolated_history(tmp_path, monkeypatch):
    """Redirect HISTORY_DIR to a temp directory for each test."""
    fake_dir = tmp_path / "history"
    monkeypatch.setattr("envault.history.HISTORY_DIR", fake_dir)
    yield fake_dir


def test_record_save_creates_entry(isolated_history):
    entry = record_save("myapp", key_count=5)
    assert entry["action"] == "save"
    assert entry["key_count"] == 5
    assert entry["source"] == "cli"
    assert "timestamp" in entry


def test_load_history_empty_when_no_file(isolated_history):
    result = load_history("nonexistent")
    assert result == []


def test_record_save_accumulates_entries(isolated_history):
    record_save("myapp", key_count=3)
    record_save("myapp", key_count=7, source="sync")
    history = load_history("myapp")
    assert len(history) == 2
    assert history[0]["key_count"] == 3
    assert history[1]["key_count"] == 7
    assert history[1]["source"] == "sync"


def test_clear_history_removes_file(isolated_history):
    record_save("myapp", key_count=2)
    assert len(load_history("myapp")) == 1
    clear_history("myapp")
    assert load_history("myapp") == []


def test_clear_history_noop_when_no_file(isolated_history):
    # Should not raise even if file doesn't exist
    clear_history("ghost")


def test_format_history_empty():
    result = format_history([])
    assert result == "No history found."


def test_format_history_shows_entries():
    entries = [
        {"timestamp": "2024-01-01T00:00:00+00:00", "action": "save", "key_count": 4, "source": "cli"},
        {"timestamp": "2024-01-02T00:00:00+00:00", "action": "save", "key_count": 6, "source": "sync"},
    ]
    result = format_history(entries)
    assert "keys=4" in result
    assert "keys=6" in result
    assert "source=cli" in result
    assert "source=sync" in result
