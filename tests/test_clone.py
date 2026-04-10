"""Unit tests for envault.clone."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.clone import CloneError, CloneResult, clone_vault
from envault.crypto import DecryptionError
from envault.vault import _vault_path, save_vault, load_vault


@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    return tmp_path


def _make_vault(name: str, data: dict, passphrase: str, vault_dir: Path) -> None:
    save_vault(name, data, passphrase, vault_dir)


def test_clone_creates_destination(vault_dir: Path) -> None:
    _make_vault("src", {"KEY": "val"}, "pass", vault_dir)
    result = clone_vault("src", "dst", "pass", vault_dir=vault_dir)
    assert _vault_path("dst", vault_dir).exists()
    assert isinstance(result, CloneResult)
    assert result.key_count == 1


def test_clone_destination_is_loadable(vault_dir: Path) -> None:
    _make_vault("src", {"A": "1", "B": "2"}, "secret", vault_dir)
    clone_vault("src", "dst", "secret", vault_dir=vault_dir)
    data = load_vault("dst", "secret", vault_dir)
    assert data == {"A": "1", "B": "2"}


def test_clone_with_new_passphrase(vault_dir: Path) -> None:
    _make_vault("src", {"X": "y"}, "old", vault_dir)
    clone_vault("src", "dst", "old", dest_passphrase="new", vault_dir=vault_dir)
    data = load_vault("dst", "new", vault_dir)
    assert data == {"X": "y"}


def test_clone_new_passphrase_invalidates_old(vault_dir: Path) -> None:
    _make_vault("src", {"X": "y"}, "old", vault_dir)
    clone_vault("src", "dst", "old", dest_passphrase="new", vault_dir=vault_dir)
    with pytest.raises(DecryptionError):
        load_vault("dst", "old", vault_dir)


def test_clone_nonexistent_source_raises(vault_dir: Path) -> None:
    with pytest.raises(CloneError, match="does not exist"):
        clone_vault("ghost", "dst", "pass", vault_dir=vault_dir)


def test_clone_existing_destination_raises(vault_dir: Path) -> None:
    _make_vault("src", {}, "pass", vault_dir)
    _make_vault("dst", {}, "pass", vault_dir)
    with pytest.raises(CloneError, match="already exists"):
        clone_vault("src", "dst", "pass", vault_dir=vault_dir)


def test_clone_wrong_passphrase_raises(vault_dir: Path) -> None:
    _make_vault("src", {"K": "v"}, "correct", vault_dir)
    with pytest.raises(DecryptionError):
        clone_vault("src", "dst", "wrong", vault_dir=vault_dir)


def test_clone_result_fields(vault_dir: Path) -> None:
    _make_vault("alpha", {"ONE": "1", "TWO": "2", "THREE": "3"}, "pw", vault_dir)
    result = clone_vault("alpha", "beta", "pw", vault_dir=vault_dir)
    assert result.source == "alpha"
    assert result.destination == "beta"
    assert result.key_count == 3
