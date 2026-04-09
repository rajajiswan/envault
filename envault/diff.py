"""Diff utilities for comparing vault contents."""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class VaultDiff:
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, Tuple[str, str]] = field(default_factory=dict)
    unchanged: Dict[str, str] = field(default_factory=dict)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        lines: List[str] = []
        for key, value in sorted(self.added.items()):
            lines.append(f"  + {key}={value}")
        for key, value in sorted(self.removed.items()):
            lines.append(f"  - {key}={value}")
        for key, (old, new) in sorted(self.changed.items()):
            lines.append(f"  ~ {key}: {old!r} -> {new!r}")
        if not lines:
            return "  (no changes)"
        return "\n".join(lines)


def diff_envs(
    old: Dict[str, str], new: Dict[str, str]
) -> VaultDiff:
    """Compare two env dicts and return a VaultDiff."""
    result = VaultDiff()
    all_keys = set(old) | set(new)

    for key in all_keys:
        if key in old and key not in new:
            result.removed[key] = old[key]
        elif key not in old and key in new:
            result.added[key] = new[key]
        elif old[key] != new[key]:
            result.changed[key] = (old[key], new[key])
        else:
            result.unchanged[key] = old[key]

    return result
