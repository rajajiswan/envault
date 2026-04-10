"""Unit tests for envault.merge."""

from __future__ import annotations

import pytest

from envault.merge import MergeError, MergeResult, merge_vaults
from envault.vault import load_vault, save_vault


@pytest.fixture()
def vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_VAULT_DIR", str(tmp_path))
    return tmp_path


def _make_vault(name: str, passphrase: str, data: dict, vault_dir) -> None:
    save_vault(name, passphrase, data)


def test_merge_adds_new_keys(vault_dir):
    _make_vault("src", "pass1", {"A": "1", "B": "2"}, vault_dir)
    _make_vault("dst", "pass2", {"C": "3"}, vault_dir)

    result = merge_vaults("src", "pass1", "dst", "pass2")

    assert "A" in result.added
    assert "B" in result.added
    assert result.skipped == []
    merged = load_vault("dst", "pass2")
    assert merged["A"] == "1"
    assert merged["C"] == "3"


def test_merge_skips_existing_without_overwrite(vault_dir):
    _make_vault("src", "pass1", {"A": "new"}, vault_dir)
    _make_vault("dst", "pass2", {"A": "old"}, vault_dir)

    result = merge_vaults("src", "pass1", "dst", "pass2", overwrite=False)

    assert "A" in result.skipped
    assert result.overwritten == []
    assert load_vault("dst", "pass2")["A"] == "old"


def test_merge_overwrites_when_flag_set(vault_dir):
    _make_vault("src", "pass1", {"A": "new"}, vault_dir)
    _make_vault("dst", "pass2", {"A": "old"}, vault_dir)

    result = merge_vaults("src", "pass1", "dst", "pass2", overwrite=True)

    assert "A" in result.overwritten
    assert load_vault("dst", "pass2")["A"] == "new"


def test_merge_specific_keys_only(vault_dir):
    _make_vault("src", "pass1", {"A": "1", "B": "2", "C": "3"}, vault_dir)
    _make_vault("dst", "pass2", {}, vault_dir)

    result = merge_vaults("src", "pass1", "dst", "pass2", keys=["A", "C"])

    assert set(result.added) == {"A", "C"}
    merged = load_vault("dst", "pass2")
    assert "B" not in merged


def test_merge_unknown_source_raises(vault_dir):
    _make_vault("dst", "pass2", {}, vault_dir)
    with pytest.raises(MergeError, match="source"):
        merge_vaults("nonexistent", "x", "dst", "pass2")


def test_merge_unknown_target_raises(vault_dir):
    _make_vault("src", "pass1", {"A": "1"}, vault_dir)
    with pytest.raises(MergeError, match="target"):
        merge_vaults("src", "pass1", "nonexistent", "x")


def test_merge_result_total_changes():
    r = MergeResult(added=["A", "B"], overwritten=["C"], skipped=["D"])
    assert r.total_changes == 3
