"""Redaction utilities for masking sensitive values in .env output."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class RedactError(Exception):
    """Raised when a redaction operation fails."""


# Keys whose values are always redacted regardless of user config
_DEFAULT_SENSITIVE_PATTERNS = (
    "password",
    "secret",
    "token",
    "api_key",
    "apikey",
    "private_key",
    "auth",
    "credential",
    "passwd",
)

REDACT_PLACEHOLDER = "***REDACTED***"


@dataclass
class RedactResult:
    original: Dict[str, str]
    redacted: Dict[str, str]
    redacted_keys: List[str] = field(default_factory=list)

    @property
    def redaction_count(self) -> int:
        return len(self.redacted_keys)


def _is_sensitive(key: str, extra_patterns: Optional[List[str]] = None) -> bool:
    """Return True if the key name matches any known sensitive pattern."""
    normalised = key.lower()
    patterns = list(_DEFAULT_SENSITIVE_PATTERNS)
    if extra_patterns:
        patterns.extend(p.lower() for p in extra_patterns)
    return any(pat in normalised for pat in patterns)


def redact_env(
    env: Dict[str, str],
    extra_patterns: Optional[List[str]] = None,
    explicit_keys: Optional[List[str]] = None,
    placeholder: str = REDACT_PLACEHOLDER,
) -> RedactResult:
    """Return a copy of *env* with sensitive values replaced by *placeholder*.

    Args:
        env: Mapping of key -> value to process.
        extra_patterns: Additional substrings that mark a key as sensitive.
        explicit_keys: Exact key names that must always be redacted.
        placeholder: Replacement string for redacted values.
    """
    redacted: Dict[str, str] = {}
    redacted_keys: List[str] = []
    explicit_set = set(explicit_keys or [])

    for key, value in env.items():
        if key in explicit_set or _is_sensitive(key, extra_patterns):
            redacted[key] = placeholder
            redacted_keys.append(key)
        else:
            redacted[key] = value

    return RedactResult(original=env, redacted=redacted, redacted_keys=sorted(redacted_keys))


def format_redacted(result: RedactResult) -> str:
    """Format a redacted env dict as a human-readable .env-style string."""
    lines = [f"{k}={v}" for k, v in result.redacted.items()]
    return "\n".join(lines)
