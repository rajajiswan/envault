"""Tests for envault.lock and envault.cli_lock."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.lock import LockError, get_lock_info, is_locked, lock_vault, unlock_vault
from envault.cli_lock import lock_cmd


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    """Redirect VAULT_DIR and LOCK_DIR to tmp_path for every test."""
    vault_dir = tmp_path / "vaults"
    lock_dir = tmp_path / "locks"
    vault_dir.mkdir()
    lock_dir.mkdir()

    import envault.lock as lock_module
    monkeypatch.setattr(lock_module, "VAULT_DIR", vault_dir)
    monkeypatch.setattr(lock_module, "LOCK_DIR", lock_dir)

    # Create a dummy vault file so existence checks pass
    (vault_dir / "myapp.enc").write_text("dummy")
    return {"vault_dir": vault_dir, "lock_dir": lock_dir}


@pytest.fixture
def runner():
    return CliRunner()


# ---------------------------------------------------------------------------
# Unit tests — lock module
# ---------------------------------------------------------------------------

def test_lock_vault_creates_lock_file(isolated):
    lock_vault("myapp")
    assert is_locked("myapp")


def test_lock_vault_returns_metadata():
    info = lock_vault("myapp")
    assert info["vault"] == "myapp"
    assert "locked_at" in info


def test_lock_vault_with_reason():
    info = lock_vault("myapp", reason="maintenance")
    assert info["reason"] == "maintenance"


def test_lock_vault_already_locked_raises():
    lock_vault("myapp")
    with pytest.raises(LockError, match="already locked"):
        lock_vault("myapp")


def test_lock_nonexistent_vault_raises():
    with pytest.raises(LockError, match="does not exist"):
        lock_vault("ghost")


def test_unlock_vault_removes_lock_file():
    lock_vault("myapp")
    unlock_vault("myapp")
    assert not is_locked("myapp")


def test_unlock_not_locked_raises():
    with pytest.raises(LockError, match="not locked"):
        unlock_vault("myapp")


def test_get_lock_info_returns_none_when_unlocked():
    assert get_lock_info("myapp") is None


def test_get_lock_info_returns_dict_when_locked():
    lock_vault("myapp", reason="ci")
    info = get_lock_info("myapp")
    assert info is not None
    assert info["reason"] == "ci"


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

def test_cli_lock_on_success(runner):
    result = runner.invoke(lock_cmd, ["on", "myapp"])
    assert result.exit_code == 0
    assert "locked" in result.output


def test_cli_lock_on_with_reason(runner):
    result = runner.invoke(lock_cmd, ["on", "myapp", "--reason", "deploy"])
    assert result.exit_code == 0
    assert "deploy" in result.output


def test_cli_lock_off_success(runner):
    lock_vault("myapp")
    result = runner.invoke(lock_cmd, ["off", "myapp"])
    assert result.exit_code == 0
    assert "unlocked" in result.output


def test_cli_lock_status_locked(runner):
    lock_vault("myapp", reason="test")
    result = runner.invoke(lock_cmd, ["status", "myapp"])
    assert "LOCKED" in result.output
    assert "test" in result.output


def test_cli_lock_status_unlocked(runner):
    result = runner.invoke(lock_cmd, ["status", "myapp"])
    assert "unlocked" in result.output
