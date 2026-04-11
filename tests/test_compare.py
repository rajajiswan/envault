"""Tests for envault.compare module."""

import pytest

from envault.compare import compare_vaults, CompareError, CompareResult
from envault.vault import save_vault


@pytest.fixture
def vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    return tmp_path


def _make_vault(name: str, data: dict, passphrase: str = "secret"):
    save_vault(name, data, passphrase)


def test_compare_identical_vaults(vault_dir):
    data = {"KEY": "value", "FOO": "bar"}
    _make_vault("alpha", data)
    _make_vault("beta", data)
    result = compare_vaults("alpha", "secret", "beta", "secret")
    assert result.is_identical
    assert result.total_differences == 0
    assert sorted(result.in_both_same) == ["FOO", "KEY"]


def test_compare_only_in_a(vault_dir):
    _make_vault("alpha", {"KEY": "value", "EXTRA": "only_a"})
    _make_vault("beta", {"KEY": "value"})
    result = compare_vaults("alpha", "secret", "beta", "secret")
    assert result.only_in_a == ["EXTRA"]
    assert result.only_in_b == []
    assert not result.is_identical


def test_compare_only_in_b(vault_dir):
    _make_vault("alpha", {"KEY": "value"})
    _make_vault("beta", {"KEY": "value", "NEW": "only_b"})
    result = compare_vaults("alpha", "secret", "beta", "secret")
    assert result.only_in_b == ["NEW"]
    assert result.only_in_a == []


def test_compare_different_values(vault_dir):
    _make_vault("alpha", {"KEY": "old"})
    _make_vault("beta", {"KEY": "new"})
    result = compare_vaults("alpha", "secret", "beta", "secret")
    assert len(result.in_both_different) == 1
    key, val_a, val_b = result.in_both_different[0]
    assert key == "KEY"
    assert val_a == "old"
    assert val_b == "new"


def test_compare_mixed(vault_dir):
    _make_vault("alpha", {"A": "1", "B": "same", "C": "old"})
    _make_vault("beta", {"B": "same", "C": "new", "D": "4"})
    result = compare_vaults("alpha", "secret", "beta", "secret")
    assert result.only_in_a == ["A"]
    assert result.only_in_b == ["D"]
    assert result.in_both_same == ["B"]
    assert result.total_differences == 3


def test_compare_nonexistent_vault_raises(vault_dir):
    _make_vault("alpha", {"KEY": "val"})
    with pytest.raises(CompareError, match="does not exist"):
        compare_vaults("alpha", "secret", "ghost", "secret")


def test_compare_wrong_passphrase_raises(vault_dir):
    _make_vault("alpha", {"KEY": "val"})
    _make_vault("beta", {"KEY": "val"})
    with pytest.raises(CompareError, match="wrong passphrase"):
        compare_vaults("alpha", "bad", "beta", "secret")
