"""Tests for envault.compress and envault.cli_compress."""

from __future__ import annotations

import gzip
import json
import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.compress import CompressError, compress_vault, decompress_vault
from envault.cli_compress import compress_cmd
from envault.vault import save_vault, load_vault


PASSPHRASE = "test-secret"
VAULT_NAME = "compress-test"
ENV_DATA = {"APP_ENV": "production", "DEBUG": "false", "PORT": "8080"}


@pytest.fixture()
def vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path / "vaults"))
    (tmp_path / "vaults").mkdir(parents=True)
    return tmp_path


@pytest.fixture()
def populated_vault(vault_dir):
    save_vault(VAULT_NAME, ENV_DATA, PASSPHRASE)
    return vault_dir


# --- Unit tests ---

def test_compress_vault_creates_gz_file(populated_vault, tmp_path):
    out = compress_vault(VAULT_NAME, PASSPHRASE, dest_dir=str(tmp_path / "out"))
    assert out.exists()
    assert out.suffix == ".gz"


def test_compressed_file_is_valid_gzip(populated_vault, tmp_path):
    out = compress_vault(VAULT_NAME, PASSPHRASE, dest_dir=str(tmp_path / "out"))
    with gzip.open(out, "rb") as fh:
        payload = json.loads(fh.read())
    assert payload["vault"] == VAULT_NAME
    assert payload["data"] == ENV_DATA


def test_decompress_vault_roundtrip(populated_vault, tmp_path):
    out = compress_vault(VAULT_NAME, PASSPHRASE, dest_dir=str(tmp_path / "out"))
    restored_name = decompress_vault(str(out), PASSPHRASE, dest_name="compress-restored")
    assert restored_name == "compress-restored"
    data = load_vault("compress-restored", PASSPHRASE)
    assert data == ENV_DATA


def test_compress_nonexistent_vault_raises(vault_dir, tmp_path):
    with pytest.raises(CompressError, match="does not exist"):
        compress_vault("ghost-vault", PASSPHRASE, dest_dir=str(tmp_path))


def test_compress_wrong_passphrase_raises(populated_vault, tmp_path):
    with pytest.raises(CompressError):
        compress_vault(VAULT_NAME, "wrong-pass", dest_dir=str(tmp_path))


def test_decompress_bad_file_raises(tmp_path):
    bad = tmp_path / "bad.env.gz"
    bad.write_bytes(b"not gzip data")
    with pytest.raises(CompressError, match="Failed to read"):
        decompress_vault(str(bad), PASSPHRASE)


def test_decompress_invalid_payload_raises(tmp_path):
    bad = tmp_path / "bad.env.gz"
    with gzip.open(bad, "wb") as fh:
        fh.write(b"{\"broken\": true}")
    with pytest.raises(CompressError, match="Invalid compressed vault format"):
        decompress_vault(str(bad), PASSPHRASE)


# --- CLI tests ---

@pytest.fixture()
def runner():
    return CliRunner()


def test_pack_command_success(populated_vault, tmp_path, runner):
    result = runner.invoke(
        compress_cmd,
        ["pack", VAULT_NAME, "--passphrase", PASSPHRASE, "--dest", str(tmp_path / "out")],
    )
    assert result.exit_code == 0
    assert "Compressed vault" in result.output


def test_pack_command_unknown_vault(vault_dir, tmp_path, runner):
    result = runner.invoke(
        compress_cmd,
        ["pack", "no-such-vault", "--passphrase", PASSPHRASE, "--dest", str(tmp_path)],
    )
    assert result.exit_code == 1
    assert "Error" in result.output


def test_unpack_command_success(populated_vault, tmp_path, runner):
    gz_path = compress_vault(VAULT_NAME, PASSPHRASE, dest_dir=str(tmp_path / "out"))
    result = runner.invoke(
        compress_cmd,
        ["unpack", str(gz_path), "--passphrase", PASSPHRASE, "--name", "cli-restored"],
    )
    assert result.exit_code == 0
    assert "cli-restored" in result.output
