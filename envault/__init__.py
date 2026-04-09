"""Envault - Securely store and sync .env files.

A CLI tool for encrypting and managing environment variable files
across multiple machines using local encrypted vaults.
"""

__version__ = "0.1.0"
__author__ = "Envault Team"
__license__ = "MIT"

from envault.crypto import encrypt, decrypt, DecryptionError
from envault.vault import save_vault, load_vault, list_vaults

__all__ = [
    "encrypt",
    "decrypt",
    "DecryptionError",
    "save_vault",
    "load_vault",
    "list_vaults",
    "__version__",
]
