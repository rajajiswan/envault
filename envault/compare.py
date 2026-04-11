"""Compare two vaults side-by-side, showing keys present in one but not the other."""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from envault.vault import load_vault
from envault.crypto import DecryptionError


class CompareError(Exception):
    pass


@dataclass
class CompareResult:
    only_in_a: List[str] = field(default_factory=list)
    only_in_b: List[str] = field(default_factory=list)
    in_both_same: List[str] = field(default_factory=list)
    in_both_different: List[Tuple[str, str, str]] = field(default_factory=list)  # (key, val_a, val_b)

    @property
    def total_differences(self) -> int:
        return len(self.only_in_a) + len(self.only_in_b) + len(self.in_both_different)

    @property
    def is_identical(self) -> bool:
        return self.total_differences == 0


def compare_vaults(
    name_a: str,
    passphrase_a: str,
    name_b: str,
    passphrase_b: str,
) -> CompareResult:
    """Load two vaults and compare their key/value pairs."""
    try:
        env_a: Dict[str, str] = load_vault(name_a, passphrase_a)
    except DecryptionError:
        raise CompareError(f"Failed to decrypt vault '{name_a}': wrong passphrase.")
    except FileNotFoundError:
        raise CompareError(f"Vault '{name_a}' does not exist.")

    try:
        env_b: Dict[str, str] = load_vault(name_b, passphrase_b)
    except DecryptionError:
        raise CompareError(f"Failed to decrypt vault '{name_b}': wrong passphrase.")
    except FileNotFoundError:
        raise CompareError(f"Vault '{name_b}' does not exist.")

    keys_a = set(env_a.keys())
    keys_b = set(env_b.keys())

    result = CompareResult()
    result.only_in_a = sorted(keys_a - keys_b)
    result.only_in_b = sorted(keys_b - keys_a)

    for key in sorted(keys_a & keys_b):
        if env_a[key] == env_b[key]:
            result.in_both_same.append(key)
        else:
            result.in_both_different.append((key, env_a[key], env_b[key]))

    return result
