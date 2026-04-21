"""envault.policy — Define and enforce naming/value policies on vault contents.

A policy is a set of rules applied to a vault's key-value pairs.  Each rule
can mandate:
  - Key naming conventions  (prefix, suffix, regex pattern)
  - Value constraints       (non-empty, max length, allowed characters)
  - Required keys           (keys that must be present)
  - Forbidden keys          (keys that must not be present)

Policies are stored as JSON alongside the vault directory.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envault.vault import _vault_path, load_vault

# ---------------------------------------------------------------------------
# Storage helpers
# ---------------------------------------------------------------------------

def _policy_path() -> Path:
    """Return the path to the shared policy store."""
    base = _vault_path("").parent
    return base / ".policies.json"


def _load_store() -> Dict:
    path = _policy_path()
    if path.exists():
        return json.loads(path.read_text())
    return {}


def _save_store(store: Dict) -> None:
    path = _policy_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2))


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------

class PolicyError(Exception):
    """Raised when a policy operation fails."""


@dataclass
class PolicyViolation:
    key: str
    rule: str
    message: str

    def __str__(self) -> str:
        return f"[{self.rule}] {self.key}: {self.message}"


@dataclass
class PolicyResult:
    vault_name: str
    violations: List[PolicyViolation] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.violations) == 0

    def summary(self) -> str:
        if self.ok:
            return f"✓ {self.vault_name}: policy passed"
        lines = [f"✗ {self.vault_name}: {len(self.violations)} violation(s)"]
        for v in self.violations:
            lines.append(f"  {v}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# CRUD for policies
# ---------------------------------------------------------------------------

def set_policy(vault_name: str, rules: Dict) -> None:
    """Attach *rules* to *vault_name*, replacing any existing policy.

    Supported rule keys:
      - ``key_pattern``   : regex every key must match
      - ``required_keys`` : list of keys that must be present
      - ``forbidden_keys``: list of keys that must not be present
      - ``max_value_len`` : maximum character length for any value
      - ``no_empty_values``: if true, empty-string values are violations
    """
    store = _load_store()
    store[vault_name] = rules
    _save_store(store)


def get_policy(vault_name: str) -> Optional[Dict]:
    """Return the policy dict for *vault_name*, or ``None`` if unset."""
    return _load_store().get(vault_name)


def remove_policy(vault_name: str) -> None:
    """Remove the policy for *vault_name* (no-op if absent)."""
    store = _load_store()
    store.pop(vault_name, None)
    _save_store(store)


def list_policies() -> Dict[str, Dict]:
    """Return all vault-name → rules mappings."""
    return dict(_load_store())


# ---------------------------------------------------------------------------
# Enforcement
# ---------------------------------------------------------------------------

def enforce_policy(vault_name: str, passphrase: str) -> PolicyResult:
    """Load *vault_name* and check it against its stored policy.

    Raises ``PolicyError`` if the vault does not exist or has no policy.
    Returns a :class:`PolicyResult` (which may contain violations).
    """
    policy = get_policy(vault_name)
    if policy is None:
        raise PolicyError(f"No policy defined for vault '{vault_name}'")

    try:
        env = load_vault(vault_name, passphrase)
    except FileNotFoundError:
        raise PolicyError(f"Vault '{vault_name}' does not exist")

    result = PolicyResult(vault_name=vault_name)

    key_pattern: Optional[str] = policy.get("key_pattern")
    required_keys: List[str] = policy.get("required_keys", [])
    forbidden_keys: List[str] = policy.get("forbidden_keys", [])
    max_value_len: Optional[int] = policy.get("max_value_len")
    no_empty_values: bool = policy.get("no_empty_values", False)

    present_keys = set(env.keys())

    # 1. Key naming pattern
    if key_pattern:
        compiled = re.compile(key_pattern)
        for k in present_keys:
            if not compiled.fullmatch(k):
                result.violations.append(PolicyViolation(
                    key=k,
                    rule="key_pattern",
                    message=f"does not match pattern '{key_pattern}'",
                ))

    # 2. Required keys
    for k in required_keys:
        if k not in present_keys:
            result.violations.append(PolicyViolation(
                key=k,
                rule="required_keys",
                message="required key is missing",
            ))

    # 3. Forbidden keys
    for k in forbidden_keys:
        if k in present_keys:
            result.violations.append(PolicyViolation(
                key=k,
                rule="forbidden_keys",
                message="forbidden key is present",
            ))

    # 4. Value length
    if max_value_len is not None:
        for k, v in env.items():
            if len(v) > max_value_len:
                result.violations.append(PolicyViolation(
                    key=k,
                    rule="max_value_len",
                    message=f"value length {len(v)} exceeds limit {max_value_len}",
                ))

    # 5. No empty values
    if no_empty_values:
        for k, v in env.items():
            if v == "":
                result.violations.append(PolicyViolation(
                    key=k,
                    rule="no_empty_values",
                    message="value must not be empty",
                ))

    return result
