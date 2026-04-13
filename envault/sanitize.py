"""sanitize.py — Strip or mask sensitive values from env data before display or export."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envault.redact import _is_sensitive


class SanitizeError(Exception):
    """Raised when sanitization cannot be performed."""


@dataclass
class SanitizeResult:
    original_count: int
    sanitized_count: int
    env: Dict[str, str]
    sanitized_keys: List[str] = field(default_factory=list)

    @property
    def ratio(self) -> float:
        if self.original_count == 0:
            return 0.0
        return self.sanitized_count / self.original_count


_DEFAULT_MASK = "***"


def sanitize_env(
    env: Dict[str, str],
    mask: str = _DEFAULT_MASK,
    extra_patterns: Optional[List[str]] = None,
    keep_keys: Optional[List[str]] = None,
) -> SanitizeResult:
    """Return a copy of *env* with sensitive values replaced by *mask*.

    Args:
        env: Mapping of key→value pairs.
        mask: Replacement string for sensitive values.
        extra_patterns: Additional substrings that mark a key as sensitive.
        keep_keys: Keys whose values should never be masked, regardless of name.
    """
    if not isinstance(env, dict):
        raise SanitizeError("env must be a dict")

    keep = set(keep_keys or [])
    sanitized: Dict[str, str] = {}
    sanitized_keys: List[str] = []

    for key, value in env.items():
        if key not in keep and _is_sensitive(key, extra_patterns=extra_patterns):
            sanitized[key] = mask
            sanitized_keys.append(key)
        else:
            sanitized[key] = value

    return SanitizeResult(
        original_count=len(env),
        sanitized_count=len(sanitized_keys),
        env=sanitized,
        sanitized_keys=sanitized_keys,
    )


def format_sanitize_report(result: SanitizeResult) -> str:
    """Return a human-readable summary of a SanitizeResult."""
    lines = [
        f"Keys total   : {result.original_count}",
        f"Keys masked  : {result.sanitized_count}",
    ]
    if result.sanitized_keys:
        lines.append("Masked keys  : " + ", ".join(sorted(result.sanitized_keys)))
    else:
        lines.append("Masked keys  : (none)")
    return "\n".join(lines)
