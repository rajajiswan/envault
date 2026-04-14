"""Tests for envault.verify and envault.cli_verify."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.vault import save_vault, _vault_path
from envault.verify import verify_vault, VerifyError, VerifyResult
from envault.cli_verify import verify_cmd


PASS = "s3cr3t"
WRONG = "wrong-pass"


@pytest.fixture()
def vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    return tmp_path


def _make_vault(name: str, env: dict, passphrase: str = PASS) -> None:
    save_vault(name, env, passphrase)


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------

def test_verify_ok(vault_dir):
    _make_vault("myapp", {"HOST": "localhost", "PORT": "5432"})
    result = verify_vault("myapp", PASS)
    assert result.decryption_ok is True
    assert result.key_count == 2
    assert result.ok is True
    assert result.issues == []


def test_verify_wrong_passphrase(vault_dir):
    _make_vault("myapp", {"KEY": "value"})
    result = verify_vault("myapp", WRONG)
    assert result.decryption_ok is False
    assert result.ok is False
    assert result.error is not None


def test_verify_nonexistent_vault_raises(vault_dir):
    with pytest.raises(VerifyError, match="not found"):
        verify_vault("ghost", PASS)


def test_verify_result_ok_property_false_on_lint_errors(vault_dir, monkeypatch):
    """If lint finds issues the overall result should not be ok."""
    from envault.lint import LintResult, LintIssue

    _make_vault("myapp", {"VALID": "yes"})

    # Patch lint_env to always return a result with an issue
    fake_issue = LintIssue(code="E001", line=1, message="missing equals sign")
    fake_lint = LintResult(issues=[fake_issue])

    import envault.verify as verify_mod
    monkeypatch.setattr(verify_mod, "lint_env", lambda *a, **kw: fake_lint)

    result = verify_vault("myapp", PASS)
    assert result.decryption_ok is True
    assert result.ok is False


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def clean_env(vault_dir):
    return vault_dir


def test_cli_verify_success(runner, clean_env):
    _make_vault("prod", {"DB_URL": "postgres://localhost/db"})
    result = runner.invoke(verify_cmd, ["run", "prod", "--passphrase", PASS])
    assert result.exit_code == 0
    assert "PASS" in result.output


def test_cli_verify_wrong_passphrase(runner, clean_env):
    _make_vault("prod", {"DB_URL": "postgres://localhost/db"})
    result = runner.invoke(verify_cmd, ["run", "prod", "--passphrase", WRONG])
    assert result.exit_code != 0
    assert "FAIL" in result.output


def test_cli_verify_unknown_vault(runner, clean_env):
    result = runner.invoke(verify_cmd, ["run", "ghost", "--passphrase", PASS])
    assert result.exit_code != 0
    assert "Error" in result.output
