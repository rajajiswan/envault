"""Vault integrity verification — checks that a vault can be decrypted and its contents are valid."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envault.vault import load_vault, _vault_path
from envault.lint import lint_env, LintResult
from envault.crypto import DecryptionError


class VerifyError(Exception):
    """Raised when verification cannot be attempted."""


@dataclass
class VerifyResult:
    vault_name: str
    decryption_ok: bool
    key_count: int
    lint: Optional[LintResult] = None
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        """True only when decryption succeeded and there are no lint errors."""
        if not self.decryption_ok:
            return False
        if self.lint is not None and not self.lint.ok:
            return False
        return True

    @property
    def issues(self) -> List[str]:
        problems: List[str] = []
        if self.error:
            problems.append(self.error)
        if self.lint is not None:
            for issue in self.lint.issues:
                problems.append(str(issue))
        return problems


def verify_vault(name: str, passphrase: str, *, strict: bool = False) -> VerifyResult:
    """Attempt to decrypt *name* and lint its contents.

    Args:
        name: Vault name (without extension).
        passphrase: Passphrase used to decrypt the vault.
        strict: When *True*, lint warnings are treated as failures.

    Returns:
        A :class:`VerifyResult` describing the outcome.

    Raises:
        VerifyError: If the vault file does not exist.
    """
    path = _vault_path(name)
    if not path.exists():
        raise VerifyError(f"Vault '{name}' not found.")

    try:
        env = load_vault(name, passphrase)
    except DecryptionError as exc:
        return VerifyResult(
            vault_name=name,
            decryption_ok=False,
            key_count=0,
            error=str(exc),
        )

    raw = "\n".join(f"{k}={v}" for k, v in env.items())
    lint_result = lint_env(raw, strict=strict)

    return VerifyResult(
        vault_name=name,
        decryption_ok=True,
        key_count=len(env),
        lint=lint_result,
    )
