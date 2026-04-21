"""Tests for envault.checksum."""

from __future__ import annotations

import pytest

from envault.checksum import (
    ChecksumError,
    clear_checksum,
    compute_checksum,
    load_checksum,
    save_checksum,
    verify_checksum,
)
from envault.vault import save_vault


@pytest.fixture()
def vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    return tmp_path


def _make_vault(name: str, passphrase: str, env: dict) -> None:
    save_vault(name, passphrase, env)


def test_compute_checksum_returns_hex_string(vault_dir):
    _make_vault("app", "secret", {"KEY": "value"})
    digest = compute_checksum("app", "secret")
    assert isinstance(digest, str)
    assert len(digest) == 64


def test_compute_checksum_is_deterministic(vault_dir):
    _make_vault("app", "secret", {"A": "1", "B": "2"})
    d1 = compute_checksum("app", "secret")
    d2 = compute_checksum("app", "secret")
    assert d1 == d2


def test_compute_checksum_changes_when_contents_change(vault_dir):
    _make_vault("app", "secret", {"KEY": "v1"})
    d1 = compute_checksum("app", "secret")
    _make_vault("app", "secret", {"KEY": "v2"})
    d2 = compute_checksum("app", "secret")
    assert d1 != d2


def test_compute_checksum_nonexistent_vault_raises(vault_dir):
    with pytest.raises(ChecksumError, match="does not exist"):
        compute_checksum("ghost", "secret")


def test_save_and_load_checksum(vault_dir):
    _make_vault("app", "secret", {"X": "1"})
    digest = save_checksum("app", "secret")
    assert load_checksum("app") == digest


def test_load_checksum_returns_none_when_unrecorded(vault_dir):
    _make_vault("app", "secret", {"X": "1"})
    assert load_checksum("app") is None


def test_verify_checksum_passes_when_unchanged(vault_dir):
    _make_vault("app", "secret", {"KEY": "val"})
    save_checksum("app", "secret")
    assert verify_checksum("app", "secret") is True


def test_verify_checksum_fails_after_modification(vault_dir):
    _make_vault("app", "secret", {"KEY": "original"})
    save_checksum("app", "secret")
    _make_vault("app", "secret", {"KEY": "modified"})
    assert verify_checksum("app", "secret") is False


def test_verify_checksum_no_stored_raises(vault_dir):
    _make_vault("app", "secret", {"KEY": "val"})
    with pytest.raises(ChecksumError, match="No checksum recorded"):
        verify_checksum("app", "secret")


def test_clear_checksum_removes_stored_digest(vault_dir):
    _make_vault("app", "secret", {"KEY": "val"})
    save_checksum("app", "secret")
    clear_checksum("app")
    assert load_checksum("app") is None


def test_clear_checksum_noop_when_no_file(vault_dir):
    # Should not raise even if no checksum file exists.
    clear_checksum("nonexistent")
