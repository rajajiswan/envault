"""Tests for envault.notes."""

from __future__ import annotations

import pytest
from pathlib import Path
from envault.notes import NoteError, set_note, get_note, remove_note, list_notes
from envault.vault import save_vault


@pytest.fixture()
def vault_dir(tmp_path: Path) -> str:
    return str(tmp_path)


def _make_vault(name: str, vault_dir: str) -> None:
    save_vault(name, {"KEY": "val"}, "pass", vault_dir)


def test_set_note_creates_entry(vault_dir: str) -> None:
    _make_vault("app", vault_dir)
    set_note("app", "remember to rotate", vault_dir)
    note = get_note("app", vault_dir)
    assert note is not None
    assert note["text"] == "remember to rotate"
    assert "updated_at" in note


def test_set_note_overwrites_existing(vault_dir: str) -> None:
    _make_vault("app", vault_dir)
    set_note("app", "first", vault_dir)
    set_note("app", "second", vault_dir)
    note = get_note("app", vault_dir)
    assert note["text"] == "second"


def test_set_note_unknown_vault_raises(vault_dir: str) -> None:
    with pytest.raises(NoteError, match="does not exist"):
        set_note("ghost", "hi", vault_dir)


def test_get_note_returns_none_when_absent(vault_dir: str) -> None:
    _make_vault("app", vault_dir)
    assert get_note("app", vault_dir) is None


def test_remove_note_deletes_entry(vault_dir: str) -> None:
    _make_vault("app", vault_dir)
    set_note("app", "temp", vault_dir)
    remove_note("app", vault_dir)
    assert get_note("app", vault_dir) is None


def test_remove_note_noop_when_absent(vault_dir: str) -> None:
    _make_vault("app", vault_dir)
    remove_note("app", vault_dir)  # should not raise


def test_list_notes_returns_all(vault_dir: str) -> None:
    _make_vault("a", vault_dir)
    _make_vault("b", vault_dir)
    set_note("a", "note a", vault_dir)
    set_note("b", "note b", vault_dir)
    store = list_notes(vault_dir)
    assert set(store.keys()) == {"a", "b"}


def test_list_notes_empty_when_no_file(vault_dir: str) -> None:
    assert list_notes(vault_dir) == {}
