"""Tests for envault.prune."""

from __future__ import annotations

import os
import pytest

from envault.vault import save_vault, _vault_path
from envault.prune import prune_vaults, PruneResult


@pytest.fixture()
def vault_dir(tmp_path, monkeypatch):
    """Redirect vault storage to a temp directory."""
    monkeypatch.setattr(
        "envault.vault.VAULT_DIR", str(tmp_path), raising=False
    )
    monkeypatch.setattr(
        "envault.prune._vault_path",
        lambda name: os.path.join(str(tmp_path), f"{name}.vault"),
    )
    return tmp_path


def _make_vault(name: str, data: dict, passphrase: str, vault_dir: str) -> None:
    save_vault(name, data, passphrase, vault_dir=vault_dir)


def test_prune_removes_empty_vault(vault_dir):
    _make_vault("empty", {}, "pass", str(vault_dir))
    _make_vault("full", {"KEY": "val"}, "pass", str(vault_dir))

    result = prune_vaults("pass", remove_empty=True, vault_dir=str(vault_dir))

    assert "empty" in result.removed
    assert "full" in result.skipped
    assert not os.path.exists(os.path.join(str(vault_dir), "empty.vault"))
    assert os.path.exists(os.path.join(str(vault_dir), "full.vault"))


def test_prune_dry_run_does_not_delete(vault_dir):
    _make_vault("empty", {}, "pass", str(vault_dir))

    result = prune_vaults("pass", remove_empty=True, dry_run=True, vault_dir=str(vault_dir))

    assert "empty" in result.removed
    assert os.path.exists(os.path.join(str(vault_dir), "empty.vault"))


def test_prune_keep_empty_skips_empty_vault(vault_dir):
    _make_vault("empty", {}, "pass", str(vault_dir))

    result = prune_vaults("pass", remove_empty=False, vault_dir=str(vault_dir))

    assert "empty" not in result.removed
    assert "empty" in result.skipped


def test_prune_wrong_passphrase_records_error(vault_dir):
    _make_vault("secret", {"A": "1"}, "correct", str(vault_dir))

    result = prune_vaults("wrong", vault_dir=str(vault_dir))

    assert "secret" in result.errors
    assert "secret" not in result.removed


def test_prune_empty_directory_returns_empty_result(tmp_path):
    result = prune_vaults("pass", vault_dir=str(tmp_path))

    assert result.total_removed == 0
    assert result.skipped == []
    assert result.errors == []


def test_prune_nonexistent_directory_returns_empty_result(tmp_path):
    missing = str(tmp_path / "does_not_exist")
    result = prune_vaults("pass", vault_dir=missing)

    assert result.total_removed == 0
