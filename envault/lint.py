"""Lint .env files for common issues: duplicates, empty values, invalid names."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


class LintError(Exception):
    """Raised when linting cannot be performed."""


@dataclass
class LintIssue:
    line: int
    key: str
    code: str
    message: str

    def __str__(self) -> str:
        return f"Line {self.line} [{self.code}] {self.key!r}: {self.message}"


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.issues) == 0

    def summary(self) -> str:
        if self.ok:
            return "No issues found."
        lines = [f"{len(self.issues)} issue(s) found:"]
        for issue in self.issues:
            lines.append(f"  {issue}")
        return "\n".join(lines)


_VALID_KEY_CHARS = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789_"
)


def lint_env(content: str) -> LintResult:
    """Lint raw .env content and return a LintResult with any issues."""
    result = LintResult()
    seen_keys: dict[str, int] = {}

    for lineno, raw in enumerate(content.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            result.issues.append(
                LintIssue(lineno, line, "E001", "Missing '=' separator")
            )
            continue

        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()

        if not key:
            result.issues.append(
                LintIssue(lineno, "", "E002", "Empty key name")
            )
            continue

        if not all(c in _VALID_KEY_CHARS for c in key):
            result.issues.append(
                LintIssue(lineno, key, "E003", "Key contains invalid characters")
            )

        if key[0].isdigit():
            result.issues.append(
                LintIssue(lineno, key, "E004", "Key must not start with a digit")
            )

        if value == "":
            result.issues.append(
                LintIssue(lineno, key, "W001", "Empty value")
            )

        if key in seen_keys:
            result.issues.append(
                LintIssue(
                    lineno, key, "W002",
                    f"Duplicate key (first seen on line {seen_keys[key]})"
                )
            )
        else:
            seen_keys[key] = lineno

    return result
