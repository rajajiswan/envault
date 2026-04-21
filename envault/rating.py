"""Vault strength rating: score a vault's env vars for security quality."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from envault.vault import load_vault, _vault_path
from envault.crypto import DecryptionError


class RatingError(Exception):
    pass


@dataclass
class RatingResult:
    vault_name: str
    score: int          # 0-100
    grade: str          # A-F
    issues: List[str] = field(default_factory=list)
    key_scores: Dict[str, int] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.score >= 70


_WEAK_PATTERNS = [
    (re.compile(r"^(password|secret|key|token)$", re.I), "generic placeholder value"),
    (re.compile(r"^(1234|abcd|test|example|changeme|dummy)", re.I), "weak/placeholder value"),
]

_MIN_SECRET_LENGTH = 16
_SENSITIVE_RE = re.compile(r"(password|secret|token|key|api|auth)", re.I)


def _score_pair(key: str, value: str) -> tuple[int, list[str]]:
    """Return (score 0-100, list of issue strings) for a single key/value pair."""
    issues: list[str] = []
    score = 100

    if not value.strip():
        issues.append(f"{key}: empty value")
        return 0, issues

    if _SENSITIVE_RE.search(key):
        if len(value) < _MIN_SECRET_LENGTH:
            issues.append(f"{key}: secret value too short (< {_MIN_SECRET_LENGTH} chars)")
            score -= 40
        for pattern, reason in _WEAK_PATTERNS:
            if pattern.search(value):
                issues.append(f"{key}: {reason}")
                score -= 30
                break
        if value == key.lower():
            issues.append(f"{key}: value matches key name")
            score -= 30

    return max(0, score), issues


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 50:
        return "D"
    return "F"


def rate_vault(name: str, passphrase: str) -> RatingResult:
    """Load vault *name* and compute its security rating."""
    path = _vault_path(name)
    if not path.exists():
        raise RatingError(f"Vault '{name}' not found")
    try:
        env = load_vault(name, passphrase)
    except DecryptionError as exc:
        raise RatingError(str(exc)) from exc

    if not env:
        return RatingResult(vault_name=name, score=100, grade="A", issues=[], key_scores={})

    all_issues: list[str] = []
    key_scores: dict[str, int] = {}
    for key, value in env.items():
        s, iss = _score_pair(key, value)
        key_scores[key] = s
        all_issues.extend(iss)

    overall = int(sum(key_scores.values()) / len(key_scores))
    return RatingResult(
        vault_name=name,
        score=overall,
        grade=_grade(overall),
        issues=all_issues,
        key_scores=key_scores,
    )
