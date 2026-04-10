"""Tests for envault.backup module."""

import os
import pytest
from pathlib import Path
from click.testing import CliRunner

from envault.vault import save_vault
from envault.backup import (
    BackupError,
    create_backup,
    list_backups,
    restore_backup,
    delete_backup,
)
from envault.cli_backup import backup_cmd


PASSPHRASE = "test-passphrase"
VAULT = "backup-test-vault"
ENV_VARS = {"APP_KEY": "abc123", "DB_URL": "postgres://localhost/test"}


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    yield tmp_path


def _make_vault(name=VAULT, passphrase=PASSPHRASE, env=None):
    save_vault(name, env or ENV_VARS, passphrase)


# --- Unit tests ---

def test_create_backup_returns_path():
    _make_vault()
    path = create_backup(VAULT, PASSPHRASE, label="v1")
    assert Path(path).exists()
    assert "v1" in str(path)


def test_create_backup_auto_label():
    _make_vault()
    path = create_backup(VAULT, PASSPHRASE)
    assert Path(path).exists()


def test_create_backup_nonexistent_vault_raises():
    with pytest.raises(BackupError, match="does not exist"):
        create_backup("ghost-vault", PASSPHRASE)


def test_create_backup_wrong_passphrase_raises():
    _make_vault()
    with pytest.raises(Exception):
        create_backup(VAULT, "wrong-passphrase", label="bad")


def test_list_backups_empty_when_none():
    assert list_backups(VAULT) == []


def test_list_backups_returns_entries():
    _make_vault()
    create_backup(VAULT, PASSPHRASE, label="snap1")
    create_backup(VAULT, PASSPHRASE, label="snap2")
    backups = list_backups(VAULT)
    assert len(backups) == 2
    labels = {b["label"] for b in backups}
    assert labels == {"snap1", "snap2"}


def test_restore_backup_allows_load():
    _make_vault()
    create_backup(VAULT, PASSPHRASE, label="snap")
    restore_backup(VAULT, PASSPHRASE, "snap")
    from envault.vault import load_vault
    env = load_vault(VAULT, PASSPHRASE)
    assert env == ENV_VARS


def test_restore_backup_missing_label_raises():
    _make_vault()
    with pytest.raises(BackupError, match="not found"):
        restore_backup(VAULT, PASSPHRASE, "nonexistent")


def test_delete_backup_removes_file():
    _make_vault()
    create_backup(VAULT, PASSPHRASE, label="to-delete")
    delete_backup(VAULT, "to-delete")
    assert list_backups(VAULT) == []


def test_delete_backup_nonexistent_raises():
    with pytest.raises(BackupError, match="not found"):
        delete_backup(VAULT, "ghost")


# --- CLI tests ---

@pytest.fixture
def runner():
    return CliRunner()


def test_cli_create_backup(runner):
    _make_vault()
    result = runner.invoke(backup_cmd, ["create", VAULT, "--passphrase", PASSPHRASE, "--label", "cli-snap"])
    assert result.exit_code == 0
    assert "Backup created" in result.output


def test_cli_list_backups(runner):
    _make_vault()
    create_backup(VAULT, PASSPHRASE, label="listed")
    result = runner.invoke(backup_cmd, ["list", VAULT])
    assert result.exit_code == 0
    assert "listed" in result.output


def test_cli_restore_backup(runner):
    _make_vault()
    create_backup(VAULT, PASSPHRASE, label="restore-me")
    result = runner.invoke(backup_cmd, ["restore", VAULT, "restore-me", "--passphrase", PASSPHRASE])
    assert result.exit_code == 0
    assert "restored" in result.output


def test_cli_delete_backup(runner):
    _make_vault()
    create_backup(VAULT, PASSPHRASE, label="del-me")
    result = runner.invoke(backup_cmd, ["delete", VAULT, "del-me"])
    assert result.exit_code == 0
    assert "deleted" in result.output
