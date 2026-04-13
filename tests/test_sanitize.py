"""Tests for envault.sanitize."""

from __future__ import annotations

import pytest

from envault.sanitize import SanitizeError, format_sanitize_report, sanitize_env


_SAMPLE_ENV = {
    "APP_NAME": "myapp",
    "DATABASE_PASSWORD": "s3cr3t",
    "API_KEY": "abc123",
    "SECRET_TOKEN": "tok_xyz",
    "PORT": "8080",
    "DEBUG": "true",
}


def test_sanitize_masks_sensitive_keys():
    result = sanitize_env(_SAMPLE_ENV)
    assert result.env["DATABASE_PASSWORD"] == "***"
    assert result.env["API_KEY"] == "***"
    assert result.env["SECRET_TOKEN"] == "***"


def test_sanitize_preserves_non_sensitive_keys():
    result = sanitize_env(_SAMPLE_ENV)
    assert result.env["APP_NAME"] == "myapp"
    assert result.env["PORT"] == "8080"
    assert result.env["DEBUG"] == "true"


def test_sanitize_counts_are_correct():
    result = sanitize_env(_SAMPLE_ENV)
    assert result.original_count == len(_SAMPLE_ENV)
    assert result.sanitized_count == 3
    assert set(result.sanitized_keys) == {"DATABASE_PASSWORD", "API_KEY", "SECRET_TOKEN"}


def test_custom_mask_string():
    result = sanitize_env({"PASSWORD": "secret"}, mask="[REDACTED]")
    assert result.env["PASSWORD"] == "[REDACTED]"


def test_extra_patterns_mark_additional_keys():
    env = {"MY_CREDENTIAL": "value", "NORMAL": "ok"}
    result = sanitize_env(env, extra_patterns=["credential"])
    assert result.env["MY_CREDENTIAL"] == "***"
    assert result.env["NORMAL"] == "ok"


def test_keep_keys_prevents_masking():
    env = {"API_KEY": "visible", "PASSWORD": "hidden"}
    result = sanitize_env(env, keep_keys=["API_KEY"])
    assert result.env["API_KEY"] == "visible"
    assert result.env["PASSWORD"] == "***"


def test_empty_env_returns_zero_counts():
    result = sanitize_env({})
    assert result.original_count == 0
    assert result.sanitized_count == 0
    assert result.ratio == 0.0


def test_ratio_calculation():
    env = {"PASSWORD": "x", "KEY": "y", "PLAIN": "z"}
    result = sanitize_env(env)
    # PASSWORD and KEY should be masked (2 out of 3)
    assert result.ratio == pytest.approx(2 / 3)


def test_invalid_env_raises_sanitize_error():
    with pytest.raises(SanitizeError):
        sanitize_env("not-a-dict")  # type: ignore[arg-type]


def test_format_sanitize_report_contains_counts():
    result = sanitize_env(_SAMPLE_ENV)
    report = format_sanitize_report(result)
    assert str(result.original_count) in report
    assert str(result.sanitized_count) in report


def test_format_sanitize_report_no_masked_keys():
    result = sanitize_env({"PLAIN": "value"})
    report = format_sanitize_report(result)
    assert "(none)" in report
