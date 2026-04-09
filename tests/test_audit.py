"""Tests for envault.audit module."""

import pytest
from pathlib import Path
from envault.audit import (
    record_access,
    load_audit_log,
    clear_audit_log,
    format_audit_log,
)


@pytest.fixture
def audit_dir(tmp_path):
    return tmp_path / "audit"


def test_record_access_creates_entry(audit_dir):
    entry = record_access("myapp", "save", user="alice", audit_dir=audit_dir)
    assert entry["vault"] == "myapp"
    assert entry["operation"] == "save"
    assert entry["user"] == "alice"
    assert "timestamp" in entry


def test_load_audit_log_empty_when_no_file(audit_dir):
    entries = load_audit_log("nonexistent", audit_dir=audit_dir)
    assert entries == []


def test_record_access_accumulates_entries(audit_dir):
    record_access("proj", "save", audit_dir=audit_dir)
    record_access("proj", "load", audit_dir=audit_dir)
    record_access("proj", "export", audit_dir=audit_dir)
    entries = load_audit_log("proj", audit_dir=audit_dir)
    assert len(entries) == 3
    ops = [e["operation"] for e in entries]
    assert ops == ["save", "load", "export"]


def test_clear_audit_log_removes_file(audit_dir):
    record_access("proj", "save", audit_dir=audit_dir)
    clear_audit_log("proj", audit_dir=audit_dir)
    entries = load_audit_log("proj", audit_dir=audit_dir)
    assert entries == []


def test_clear_audit_log_noop_when_missing(audit_dir):
    # Should not raise
    clear_audit_log("ghost", audit_dir=audit_dir)


def test_format_audit_log_empty():
    result = format_audit_log([])
    assert "No audit entries" in result


def test_format_audit_log_shows_fields(audit_dir):
    record_access("app", "load", user="bob", details="CLI", audit_dir=audit_dir)
    entries = load_audit_log("app", audit_dir=audit_dir)
    output = format_audit_log(entries)
    assert "load" in output
    assert "bob" in output
    assert "CLI" in output


def test_separate_vaults_have_separate_logs(audit_dir):
    record_access("vault_a", "save", audit_dir=audit_dir)
    record_access("vault_b", "load", audit_dir=audit_dir)
    a_entries = load_audit_log("vault_a", audit_dir=audit_dir)
    b_entries = load_audit_log("vault_b", audit_dir=audit_dir)
    assert len(a_entries) == 1
    assert len(b_entries) == 1
    assert a_entries[0]["operation"] == "save"
    assert b_entries[0]["operation"] == "load"


def test_details_optional(audit_dir):
    entry = record_access("app", "save", audit_dir=audit_dir)
    assert entry["details"] == ""
