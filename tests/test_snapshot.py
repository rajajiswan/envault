"""Tests for envault.snapshot."""

from __future__ import annotations

import json
import os
import pytest

from envault.vault import save_vault
from envault.snapshot import (
    SnapshotError,
    create_snapshot,
    delete_snapshot,
    list_snapshots,
    restore_snapshot,
    _snapshot_dir,
)

PASS = "hunter2"


@pytest.fixture()
def vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    return tmp_path


def _make_vault(name: str, env: dict, passphrase: str = PASS) -> None:
    save_vault(name, env, passphrase)


# ---------------------------------------------------------------------------
# create_snapshot
# ---------------------------------------------------------------------------

def test_create_snapshot_returns_path(vault_dir):
    _make_vault("myapp", {"KEY": "val"})
    path = create_snapshot("myapp", PASS, label="snap1")
    assert path.exists()


def test_create_snapshot_file_is_valid_json(vault_dir):
    _make_vault("myapp", {"A": "1", "B": "2"})
    path = create_snapshot("myapp", PASS, label="v1")
    data = json.loads(path.read_text())
    assert data["vault"] == "myapp"
    assert data["label"] == "v1"
    assert data["env"] == {"A": "1", "B": "2"}


def test_create_snapshot_auto_label(vault_dir):
    _make_vault("myapp", {"X": "y"})
    path = create_snapshot("myapp", PASS)
    assert path.exists()
    data = json.loads(path.read_text())
    assert isinstance(int(data["label"]), int)


def test_create_snapshot_duplicate_label_raises(vault_dir):
    _make_vault("myapp", {"K": "v"})
    create_snapshot("myapp", PASS, label="dup")
    with pytest.raises(SnapshotError, match="already exists"):
        create_snapshot("myapp", PASS, label="dup")


# ---------------------------------------------------------------------------
# list_snapshots
# ---------------------------------------------------------------------------

def test_list_snapshots_empty_when_none(vault_dir):
    _make_vault("empty", {})
    assert list_snapshots("empty") == []


def test_list_snapshots_returns_newest_first(vault_dir):
    _make_vault("app", {"K": "1"})
    create_snapshot("app", PASS, label="first")
    create_snapshot("app", PASS, label="second")
    snaps = list_snapshots("app")
    assert len(snaps) == 2
    assert snaps[0]["label"] == "second"


# ---------------------------------------------------------------------------
# restore_snapshot
# ---------------------------------------------------------------------------

def test_restore_snapshot_overwrites_vault(vault_dir):
    _make_vault("app", {"OLD": "data"})
    create_snapshot("app", PASS, label="baseline")
    save_vault("app", {"NEW": "stuff"}, PASS)
    env = restore_snapshot("app", "baseline", PASS)
    assert env == {"OLD": "data"}


def test_restore_snapshot_missing_label_raises(vault_dir):
    _make_vault("app", {})
    with pytest.raises(SnapshotError, match="not found"):
        restore_snapshot("app", "ghost", PASS)


# ---------------------------------------------------------------------------
# delete_snapshot
# ---------------------------------------------------------------------------

def test_delete_snapshot_removes_file(vault_dir):
    _make_vault("app", {"K": "v"})
    path = create_snapshot("app", PASS, label="to_del")
    delete_snapshot("app", "to_del")
    assert not path.exists()


def test_delete_snapshot_nonexistent_raises(vault_dir):
    _make_vault("app", {})
    with pytest.raises(SnapshotError, match="not found"):
        delete_snapshot("app", "nope")
