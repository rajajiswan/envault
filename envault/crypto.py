"""Encryption and decryption utilities for envault vault files."""

import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet, InvalidToken


SALT_SIZE = 16
ITERATIONS = 480_000


class DecryptionError(Exception):
    """Raised when decryption fails, typically due to a wrong passphrase."""


def derive_key(passphrase: str, salt: bytes) -> bytes:
    """Derive a 32-byte Fernet-compatible key from a passphrase and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    raw_key = kdf.derive(passphrase.encode())
    return base64.urlsafe_b64encode(raw_key)


def encrypt(data: str, passphrase: str) -> bytes:
    """Encrypt plaintext data with a passphrase.

    Returns bytes in the format: <salt (16 bytes)> + <fernet token>.
    """
    salt = os.urandom(SALT_SIZE)
    key = derive_key(passphrase, salt)
    token = Fernet(key).encrypt(data.encode())
    return salt + token


def decrypt(payload: bytes, passphrase: str) -> str:
    """Decrypt a payload produced by :func:`encrypt`.

    Raises:
        DecryptionError: If the passphrase is wrong or the payload is corrupt.
    """
    salt = payload[:SALT_SIZE]
    token = payload[SALT_SIZE:]
    key = derive_key(passphrase, salt)
    try:
        return Fernet(key).decrypt(token).decode()
    except (InvalidToken, Exception) as exc:
        raise DecryptionError("Failed to decrypt vault — wrong passphrase or corrupted data.") from exc
