"""Audit log for tracking vault access and operations."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

DEFAULT_AUDIT_DIR = Path.home() / ".envault" / "audit"


def _audit_path(vault_name: str, audit_dir: Optional[Path] = None) -> Path:
    base = audit_dir or DEFAULT_AUDIT_DIR
    base.mkdir(parents=True, exist_ok=True)
    return base / f"{vault_name}.audit.jsonl"


def record_access(
    vault_name: str,
    operation: str,
    user: Optional[str] = None,
    details: Optional[str] = None,
    audit_dir: Optional[Path] = None,
) -> dict:
    """Append an audit entry for a vault operation."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "vault": vault_name,
        "operation": operation,
        "user": user or os.environ.get("USER", "unknown"),
        "details": details or "",
    }
    path = _audit_path(vault_name, audit_dir)
    with path.open("a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def load_audit_log(
    vault_name: str, audit_dir: Optional[Path] = None
) -> List[dict]:
    """Return all audit entries for a given vault."""
    path = _audit_path(vault_name, audit_dir)
    if not path.exists():
        return []
    entries = []
    with path.open("r") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def clear_audit_log(vault_name: str, audit_dir: Optional[Path] = None) -> None:
    """Delete the audit log for a given vault."""
    path = _audit_path(vault_name, audit_dir)
    if path.exists():
        path.unlink()


def format_audit_log(entries: List[dict]) -> str:
    """Format audit entries for human-readable display."""
    if not entries:
        return "No audit entries found."
    lines = []
    for e in entries:
        ts = e.get("timestamp", "?")
        op = e.get("operation", "?")
        user = e.get("user", "?")
        details = e.get("details", "")
        line = f"[{ts}] {op} by {user}"
        if details:
            line += f" — {details}"
        lines.append(line)
    return "\n".join(lines)
