"""Tests for envault crypto and vault modules."""

import pathlib
import pytest

from envault.crypto import encrypt, decrypt, DecryptionError
from envault.vault import save_vault, load_vault, list_vaults, _parse_env


PASSPHRASE = "super-secret-passphrase"
SAMPLE_VARS = {"DB_HOST": "localhost", "DB_PORT": "5432", "API_KEY": "abc123"}


# ---------------------------------------------------------------------------
# crypto tests
# ---------------------------------------------------------------------------

def test_encrypt_decrypt_roundtrip():
    payload = encrypt("hello world", PASSPHRASE)
    assert decrypt(payload, PASSPHRASE) == "hello world"


def test_encrypt_produces_different_ciphertext_each_time():
    p1 = encrypt("same data", PASSPHRASE)
    p2 = encrypt("same data", PASSPHRASE)
    assert p1 != p2  # different salts


def test_decrypt_wrong_passphrase_raises():
    payload = encrypt("secret", PASSPHRASE)
    with pytest.raises(DecryptionError):
        decrypt(payload, "wrong-passphrase")


def test_decrypt_corrupted_payload_raises():
    payload = bytearray(encrypt("secret", PASSPHRASE))
    payload[20] ^= 0xFF  # flip a byte
    with pytest.raises(DecryptionError):
        decrypt(bytes(payload), PASSPHRASE)


# ---------------------------------------------------------------------------
# vault tests
# ---------------------------------------------------------------------------

def test_save_and_load_vault(tmp_path):
    save_vault("myproject", SAMPLE_VARS, PASSPHRASE, vault_dir=tmp_path)
    loaded = load_vault("myproject", PASSPHRASE, vault_dir=tmp_path)
    assert loaded == SAMPLE_VARS


def test_load_vault_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_vault("nonexistent", PASSPHRASE, vault_dir=tmp_path)


def test_load_vault_wrong_passphrase(tmp_path):
    save_vault("myproject", SAMPLE_VARS, PASSPHRASE, vault_dir=tmp_path)
    with pytest.raises(DecryptionError):
        load_vault("myproject", "bad-pass", vault_dir=tmp_path)


def test_list_vaults(tmp_path):
    assert list_vaults(vault_dir=tmp_path) == []
    save_vault("alpha", SAMPLE_VARS, PASSPHRASE, vault_dir=tmp_path)
    save_vault("beta", SAMPLE_VARS, PASSPHRASE, vault_dir=tmp_path)
    assert list_vaults(vault_dir=tmp_path) == ["alpha", "beta"]


def test_parse_env_ignores_comments_and_blanks():
    text = "# comment\n\nFOO=bar\nBAZ=qux\n"
    assert _parse_env(text) == {"FOO": "bar", "BAZ": "qux"}
