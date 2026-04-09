"""Tests for envault sync (export/import) functionality."""

import json
import os
import pytest
from pathlib import Path

from envault.sync import export_vault, import_vault, SyncError
from envault.vault import save_vault, load_vault, _vault_path


PASSPHRASE = "sync-test-secret"
VAULT_NAME = "sync_test_vault"
SAMPLE_VARS = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc123"}


@pytest.fixture(autouse=True)
def clean_vaults(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    yield
    for f in tmp_path.glob("*.vault"):
        f.unlink()


def test_export_creates_file(tmp_path):
    save_vault(VAULT_NAME, SAMPLE_VARS, PASSPHRASE)
    export_file = tmp_path / "export.evault"
    export_vault(VAULT_NAME, PASSPHRASE, str(export_file))
    assert export_file.exists()


def test_export_file_is_valid_json(tmp_path):
    save_vault(VAULT_NAME, SAMPLE_VARS, PASSPHRASE)
    export_file = tmp_path / "export.evault"
    export_vault(VAULT_NAME, PASSPHRASE, str(export_file))
    data = json.loads(export_file.read_text())
    assert data.get("envault_export") is True
    assert "data" in data


def test_import_roundtrip(tmp_path):
    save_vault(VAULT_NAME, SAMPLE_VARS, PASSPHRASE)
    export_file = tmp_path / "export.evault"
    export_vault(VAULT_NAME, PASSPHRASE, str(export_file))

    _vault_path(VAULT_NAME).unlink()

    name = import_vault(str(export_file), PASSPHRASE)
    assert name == VAULT_NAME
    loaded = load_vault(VAULT_NAME, PASSPHRASE)
    assert loaded == SAMPLE_VARS


def test_import_wrong_passphrase_raises(tmp_path):
    save_vault(VAULT_NAME, SAMPLE_VARS, PASSPHRASE)
    export_file = tmp_path / "export.evault"
    export_vault(VAULT_NAME, PASSPHRASE, str(export_file))
    _vault_path(VAULT_NAME).unlink()

    with pytest.raises(SyncError):
        import_vault(str(export_file), "wrong-passphrase")


def test_import_existing_vault_raises_without_overwrite(tmp_path):
    save_vault(VAULT_NAME, SAMPLE_VARS, PASSPHRASE)
    export_file = tmp_path / "export.evault"
    export_vault(VAULT_NAME, PASSPHRASE, str(export_file))

    with pytest.raises(SyncError, match="already exists"):
        import_vault(str(export_file), PASSPHRASE, overwrite=False)


def test_import_existing_vault_overwrite(tmp_path):
    save_vault(VAULT_NAME, SAMPLE_VARS, PASSPHRASE)
    export_file = tmp_path / "export.evault"
    export_vault(VAULT_NAME, PASSPHRASE, str(export_file))

    name = import_vault(str(export_file), PASSPHRASE, overwrite=True)
    assert name == VAULT_NAME


def test_import_invalid_file_raises(tmp_path):
    bad_file = tmp_path / "bad.evault"
    bad_file.write_text("not valid json at all !!!")
    with pytest.raises(SyncError):
        import_vault(str(bad_file), PASSPHRASE)
