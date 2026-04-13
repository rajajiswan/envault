"""Tests for envault.redact."""

import pytest

from envault.redact import (
    REDACT_PLACEHOLDER,
    RedactResult,
    _is_sensitive,
    format_redacted,
    redact_env,
)


# ---------------------------------------------------------------------------
# _is_sensitive
# ---------------------------------------------------------------------------

def test_is_sensitive_password():
    assert _is_sensitive("DB_PASSWORD") is True


def test_is_sensitive_token():
    assert _is_sensitive("GITHUB_TOKEN") is True


def test_is_sensitive_api_key():
    assert _is_sensitive("STRIPE_API_KEY") is True


def test_is_sensitive_plain_key_is_false():
    assert _is_sensitive("DATABASE_HOST") is False


def test_is_sensitive_extra_pattern():
    assert _is_sensitive("MY_PASSPHRASE", extra_patterns=["passphrase"]) is True


def test_is_sensitive_extra_pattern_not_matched_without_it():
    assert _is_sensitive("MY_PASSPHRASE") is False


# ---------------------------------------------------------------------------
# redact_env
# ---------------------------------------------------------------------------

_SAMPLE_ENV = {
    "APP_NAME": "myapp",
    "DB_PASSWORD": "supersecret",
    "GITHUB_TOKEN": "ghp_abc123",
    "PORT": "8080",
    "AWS_SECRET_ACCESS_KEY": "aws/secret",
}


def test_redact_env_returns_redact_result():
    result = redact_env(_SAMPLE_ENV)
    assert isinstance(result, RedactResult)


def test_redact_env_sensitive_keys_replaced():
    result = redact_env(_SAMPLE_ENV)
    assert result.redacted["DB_PASSWORD"] == REDACT_PLACEHOLDER
    assert result.redacted["GITHUB_TOKEN"] == REDACT_PLACEHOLDER
    assert result.redacted["AWS_SECRET_ACCESS_KEY"] == REDACT_PLACEHOLDER


def test_redact_env_non_sensitive_keys_unchanged():
    result = redact_env(_SAMPLE_ENV)
    assert result.redacted["APP_NAME"] == "myapp"
    assert result.redacted["PORT"] == "8080"


def test_redact_env_redacted_keys_list():
    result = redact_env(_SAMPLE_ENV)
    assert "DB_PASSWORD" in result.redacted_keys
    assert "APP_NAME" not in result.redacted_keys


def test_redact_env_redaction_count():
    result = redact_env(_SAMPLE_ENV)
    assert result.redaction_count == 3


def test_redact_env_explicit_keys():
    result = redact_env({"PORT": "8080", "APP_NAME": "x"}, explicit_keys=["PORT"])
    assert result.redacted["PORT"] == REDACT_PLACEHOLDER
    assert result.redacted["APP_NAME"] == "x"


def test_redact_env_custom_placeholder():
    result = redact_env({"DB_PASSWORD": "s3cr3t"}, placeholder="<hidden>")
    assert result.redacted["DB_PASSWORD"] == "<hidden>"


def test_redact_env_does_not_mutate_original():
    env = {"DB_PASSWORD": "original"}
    redact_env(env)
    assert env["DB_PASSWORD"] == "original"


# ---------------------------------------------------------------------------
# format_redacted
# ---------------------------------------------------------------------------

def test_format_redacted_produces_env_lines():
    result = redact_env({"APP_NAME": "myapp", "DB_PASSWORD": "secret"})
    output = format_redacted(result)
    assert "APP_NAME=myapp" in output
    assert f"DB_PASSWORD={REDACT_PLACEHOLDER}" in output
