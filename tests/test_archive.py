"""Tests for envault.archive."""

import json
import os
import pytest

from envault.vault import _vault_path, save_vault, load_vault
from envault.archive import ArchiveError, ArchiveResult, create_archive, extract_archive


@pytest.fixture()
def vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    return tmp_path


def _make_vault(name: str, env: dict, passphrase: str = "secret"):
    save_vault(name, env, passphrase)


# ---------------------------------------------------------------------------

def test_create_archive_returns_result(vault_dir, tmp_path):
    _make_vault("alpha", {"A": "1"}, "secret")
    _make_vault("beta", {"B": "2"}, "secret")
    dest = str(tmp_path / "out.json")
    result = create_archive(["alpha", "beta"], "secret", dest)
    assert isinstance(result, ArchiveResult)
    assert result.count == 2
    assert set(result.vaults) == {"alpha", "beta"}


def test_create_archive_file_is_valid_json(vault_dir, tmp_path):
    _make_vault("gamma", {"KEY": "val"}, "pw")
    dest = str(tmp_path / "archive.json")
    create_archive(["gamma"], "pw", dest)
    with open(dest) as fh:
        data = json.load(fh)
    assert "gamma" in data
    assert data["gamma"]["KEY"] == "val"


def test_create_archive_unknown_vault_raises(vault_dir, tmp_path):
    dest = str(tmp_path / "bad.json")
    with pytest.raises(ArchiveError, match="does not exist"):
        create_archive(["no_such_vault"], "pw", dest)


def test_create_archive_empty_list_raises(vault_dir, tmp_path):
    dest = str(tmp_path / "empty.json")
    with pytest.raises(ArchiveError, match="No vault names"):
        create_archive([], "pw", dest)


def test_extract_archive_roundtrip(vault_dir, tmp_path):
    _make_vault("source", {"X": "42"}, "pass")
    dest = str(tmp_path / "arch.json")
    create_archive(["source"], "pass", dest)

    # Remove original vault to prove extraction recreates it
    _vault_path("source").unlink()
    result = extract_archive(dest, "pass")
    assert "source" in result.vaults
    env = load_vault("source", "pass")
    assert env["X"] == "42"


def test_extract_archive_skips_existing_without_overwrite(vault_dir, tmp_path):
    _make_vault("dup", {"D": "old"}, "pw")
    dest = str(tmp_path / "dup.json")
    create_archive(["dup"], "pw", dest)
    result = extract_archive(dest, "pw", overwrite=False)
    assert result.count == 0


def test_extract_archive_overwrite_flag(vault_dir, tmp_path):
    _make_vault("over", {"O": "original"}, "pw")
    dest = str(tmp_path / "over.json")
    create_archive(["over"], "pw", dest)
    # Modify the vault in-place so we can detect overwrite
    save_vault("over", {"O": "changed"}, "pw")
    result = extract_archive(dest, "pw", overwrite=True)
    assert "over" in result.vaults
    env = load_vault("over", "pw")
    assert env["O"] == "original"


def test_extract_missing_archive_raises(vault_dir):
    with pytest.raises(ArchiveError, match="not found"):
        extract_archive("/nonexistent/path.json", "pw")


def test_extract_invalid_json_raises(vault_dir, tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("not json", encoding="utf-8")
    with pytest.raises(ArchiveError, match="Invalid archive"):
        extract_archive(str(bad_file), "pw")
