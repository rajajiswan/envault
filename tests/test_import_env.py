"""Tests for envault.import_env."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from envault.import_env import ImportEnvError, import_env
from envault.vault import _vault_path, load_vault, save_vault


PASSPHRASE = "hunter2"


@pytest.fixture()
def vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_VAULT_DIR", str(tmp_path))
    return tmp_path


def _env_file(tmp_path: Path, content: str) -> Path:
    p = tmp_path / ".env"
    p.write_text(textwrap.dedent(content))
    return p


def test_import_creates_new_vault(vault_dir, tmp_path):
    src = _env_file(tmp_path, "FOO=bar\nBAZ=qux\n")
    result = import_env("myapp", PASSPHRASE, str(src))
    assert result.total == 2
    assert set(result.keys_imported) == {"FOO", "BAZ"}
    data = load_vault("myapp", PASSPHRASE)
    assert data["FOO"] == "bar"
    assert data["BAZ"] == "qux"


def test_import_skips_existing_without_overwrite(vault_dir, tmp_path):
    save_vault("myapp", "FOO=original", PASSPHRASE)
    src = _env_file(tmp_path, "FOO=new\nBAR=added\n")
    result = import_env("myapp", PASSPHRASE, str(src))
    assert "FOO" in result.keys_skipped
    assert "BAR" in result.keys_imported
    data = load_vault("myapp", PASSPHRASE)
    assert data["FOO"] == "original"  # not overwritten
    assert data["BAR"] == "added"


def test_import_overwrites_when_flag_set(vault_dir, tmp_path):
    save_vault("myapp", "FOO=original", PASSPHRASE)
    src = _env_file(tmp_path, "FOO=updated\n")
    result = import_env("myapp", PASSPHRASE, str(src), overwrite=True)
    assert "FOO" in result.keys_imported
    assert result.keys_skipped == []
    data = load_vault("myapp", PASSPHRASE)
    assert data["FOO"] == "updated"


def test_import_filters_by_keys(vault_dir, tmp_path):
    src = _env_file(tmp_path, "A=1\nB=2\nC=3\n")
    result = import_env("myapp", PASSPHRASE, str(src), keys=["A", "C"])
    assert set(result.keys_imported) == {"A", "C"}
    data = load_vault("myapp", PASSPHRASE)
    assert "B" not in data


def test_import_missing_file_raises(vault_dir):
    with pytest.raises(ImportEnvError, match="File not found"):
        import_env("myapp", PASSPHRASE, "/nonexistent/.env")


def test_import_empty_source_raises(vault_dir, tmp_path):
    src = _env_file(tmp_path, "# just a comment\n")
    with pytest.raises(ImportEnvError, match="No valid KEY=VALUE"):
        import_env("myapp", PASSPHRASE, str(src))


def test_import_wrong_passphrase_on_existing_vault_raises(vault_dir, tmp_path):
    save_vault("myapp", "X=1", PASSPHRASE)
    src = _env_file(tmp_path, "Y=2\n")
    with pytest.raises(ImportEnvError, match="Cannot open existing vault"):
        import_env("myapp", "wrongpass", str(src))


def test_import_result_source_label(vault_dir, tmp_path):
    src = _env_file(tmp_path, "K=V\n")
    result = import_env("myapp", PASSPHRASE, str(src))
    assert result.source == str(src)


def test_import_stdin_label(vault_dir, monkeypatch, tmp_path):
    import io
    monkeypatch.setattr("sys.stdin", io.StringIO("STDIN_KEY=hello\n"))
    result = import_env("myapp", PASSPHRASE, "-")
    assert result.source == "stdin"
    assert "STDIN_KEY" in result.keys_imported
