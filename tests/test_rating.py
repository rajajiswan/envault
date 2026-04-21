"""Tests for envault.rating."""

from __future__ import annotations

import pytest

from envault.vault import save_vault
from envault.rating import rate_vault, RatingError, _score_pair, _grade


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    return tmp_path


def _make_vault(name: str, env: dict, passphrase: str = "pass") -> None:
    save_vault(name, env, passphrase)


# ---------------------------------------------------------------------------
# Unit tests for helpers
# ---------------------------------------------------------------------------

def test_score_pair_empty_value():
    score, issues = _score_pair("API_KEY", "")
    assert score == 0
    assert any("empty" in i for i in issues)


def test_score_pair_strong_secret():
    score, issues = _score_pair("API_KEY", "xK9#mP2$qRtL8nVw")
    assert score == 100
    assert issues == []


def test_score_pair_short_secret():
    score, issues = _score_pair("SECRET_KEY", "short")
    assert score < 100
    assert any("too short" in i for i in issues)


def test_score_pair_weak_placeholder():
    score, issues = _score_pair("PASSWORD", "changeme")
    assert score < 70
    assert any("placeholder" in i or "weak" in i for i in issues)


def test_score_pair_value_matches_key():
    score, issues = _score_pair("PASSWORD", "password")
    assert score < 70
    assert any("matches key" in i for i in issues)


def test_grade_boundaries():
    assert _grade(95) == "A"
    assert _grade(85) == "B"
    assert _grade(75) == "C"
    assert _grade(60) == "D"
    assert _grade(40) == "F"


# ---------------------------------------------------------------------------
# Integration tests against real vaults
# ---------------------------------------------------------------------------

def test_rate_vault_all_strong(vault_dir):
    _make_vault("myapp", {"API_KEY": "xK9#mP2$qRtL8nVw", "HOST": "localhost"})
    result = rate_vault("myapp", "pass")
    assert result.score == 100
    assert result.grade == "A"
    assert result.ok is True
    assert result.issues == []


def test_rate_vault_with_weak_secret(vault_dir):
    _make_vault("weak", {"SECRET": "test"})
    result = rate_vault("weak", "pass")
    assert result.score < 70
    assert result.ok is False
    assert len(result.issues) > 0


def test_rate_vault_empty_vault_is_perfect(vault_dir):
    _make_vault("empty", {})
    result = rate_vault("empty", "pass")
    assert result.score ==.grade == "A"


def test_rate_vault_wrong_passphrase_raises(vault_dir):
    _make_vault("secure", {"KEY": "value"})
    with pytest.raises(RatingError):
        rate_vault("secure", "wrong")


def test_rate_vault_nonexistent_raises(vault_dir):
    with pytest.raises(RatingError, match="not found"):
        rate_vault("ghost", "pass")


def test_rate_vault_key_scores_populated(vault_dir):
    _make_vault("app", {"API_TOKEN": "xK9#mP2$qRtL8nVw", "PASSWORD": "short"})
    result = rate_vault("app", "pass")
    assert "API_TOKEN" in result.key_scores
    assert "PASSWORD" in result.key_scores
    assert result.key_scores["API_TOKEN"] > result.key_scores["PASSWORD"]
