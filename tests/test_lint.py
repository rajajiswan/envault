"""Tests for envault.lint."""

import pytest
from envault.lint import lint_env, LintResult, LintIssue


def _codes(result: LintResult):
    return [i.code for i in result.issues]


def test_clean_env_returns_ok():
    content = "DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=abc123\n"
    result = lint_env(content)
    assert result.ok
    assert result.summary() == "No issues found."


def test_comments_and_blank_lines_ignored():
    content = "# This is a comment\n\nAPP_ENV=production\n"
    result = lint_env(content)
    assert result.ok


def test_missing_equals_raises_e001():
    result = lint_env("BADLINE\n")
    assert "E001" in _codes(result)


def test_empty_key_raises_e002():
    result = lint_env("=value\n")
    assert "E002" in _codes(result)


def test_invalid_key_chars_raises_e003():
    result = lint_env("MY-KEY=value\n")
    assert "E003" in _codes(result)


def test_key_starting_with_digit_raises_e004():
    result = lint_env("1KEY=value\n")
    assert "E004" in _codes(result)


def test_empty_value_raises_w001():
    result = lint_env("EMPTY_VAL=\n")
    assert "W001" in _codes(result)


def test_duplicate_key_raises_w002():
    content = "MY_KEY=first\nMY_KEY=second\n"
    result = lint_env(content)
    assert "W002" in _codes(result)
    dup = next(i for i in result.issues if i.code == "W002")
    assert dup.line == 2
    assert "line 1" in dup.message


def test_multiple_issues_accumulated():
    content = "1BAD=val\nDUP=a\nDUP=b\nNO_EQUALS\n"
    result = lint_env(content)
    assert not result.ok
    assert len(result.issues) >= 3


def test_summary_lists_all_issues():
    content = "EMPTY=\nDUP=x\nDUP=y\n"
    result = lint_env(content)
    summary = result.summary()
    assert "issue(s) found" in summary
    assert "W001" in summary
    assert "W002" in summary


def test_lint_issue_str():
    issue = LintIssue(line=3, key="FOO", code="W001", message="Empty value")
    s = str(issue)
    assert "Line 3" in s
    assert "W001" in s
    assert "FOO" in s
