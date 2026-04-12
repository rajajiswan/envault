"""Tests for envault.access — vault access control."""

from __future__ import annotations

import pytest

import envault.access as access_mod
from envault.access import (
    allow_vault,
    check_access,
    deny_vault,
    get_rules,
    remove_rule,
)


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(access_mod, "_ACCESS_FILE", tmp_path / "access_control.json")
    yield


def test_check_access_no_rules_allows_everything():
    assert check_access("myapp", "alice") is True


def test_allow_vault_grants_access_to_label():
    allow_vault("myapp", "alice")
    assert check_access("myapp", "alice") is True


def test_allow_vault_restricts_unlisted_labels():
    allow_vault("myapp", "alice")
    assert check_access("myapp", "bob") is False


def test_deny_vault_blocks_label():
    deny_vault("myapp", "mallory")
    assert check_access("myapp", "mallory") is False


def test_deny_takes_precedence_over_allow():
    allow_vault("myapp", "alice")
    deny_vault("myapp", "alice")
    assert check_access("myapp", "alice") is False


def test_allow_vault_is_idempotent():
    allow_vault("myapp", "alice")
    allow_vault("myapp", "alice")
    rules = get_rules("myapp")
    assert rules["allowed"].count("alice") == 1


def test_deny_vault_is_idempotent():
    deny_vault("myapp", "mallory")
    deny_vault("myapp", "mallory")
    rules = get_rules("myapp")
    assert rules["denied"].count("mallory") == 1


def test_remove_rule_clears_label_from_both_lists():
    allow_vault("myapp", "alice")
    deny_vault("myapp", "alice")
    remove_rule("myapp", "alice")
    rules = get_rules("myapp")
    assert "alice" not in rules["allowed"]
    assert "alice" not in rules["denied"]


def test_remove_rule_nonexistent_is_noop():
    remove_rule("ghost", "nobody")  # should not raise


def test_get_rules_returns_none_when_unset():
    assert get_rules("unknown") is None


def test_multiple_vaults_are_independent():
    allow_vault("app1", "alice")
    allow_vault("app2", "bob")
    assert check_access("app1", "alice") is True
    assert check_access("app1", "bob") is False
    assert check_access("app2", "bob") is True
    assert check_access("app2", "alice") is False
