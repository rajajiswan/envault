"""Tests for envault.diff module."""

import pytest
from envault.diff import diff_envs, VaultDiff


OLD = {"KEY_A": "alpha", "KEY_B": "beta", "KEY_C": "gamma"}
NEW = {"KEY_A": "alpha", "KEY_B": "CHANGED", "KEY_D": "delta"}


def test_diff_added():
    result = diff_envs(OLD, NEW)
    assert "KEY_D" in result.added
    assert result.added["KEY_D"] == "delta"


def test_diff_removed():
    result = diff_envs(OLD, NEW)
    assert "KEY_C" in result.removed
    assert result.removed["KEY_C"] == "gamma"


def test_diff_changed():
    result = diff_envs(OLD, NEW)
    assert "KEY_B" in result.changed
    assert result.changed["KEY_B"] == ("beta", "CHANGED")


def test_diff_unchanged():
    result = diff_envs(OLD, NEW)
    assert "KEY_A" in result.unchanged


def test_has_changes_true():
    result = diff_envs(OLD, NEW)
    assert result.has_changes is True


def test_has_changes_false():
    result = diff_envs(OLD, OLD)
    assert result.has_changes is False


def test_summary_no_changes():
    result = diff_envs(OLD, OLD)
    assert "(no changes)" in result.summary()


def test_summary_with_changes():
    result = diff_envs(OLD, NEW)
    summary = result.summary()
    assert "+ KEY_D" in summary
    assert "- KEY_C" in summary
    assert "~ KEY_B" in summary


def test_empty_dicts():
    result = diff_envs({}, {})
    assert not result.has_changes


def test_all_added():
    result = diff_envs({}, {"X": "1"})
    assert "X" in result.added
    assert not result.removed
