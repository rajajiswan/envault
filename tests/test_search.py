"""Tests for envault.search and cli_search."""
import pytest
from click.testing import CliRunner

from envault.search import SearchError, SearchResult, search_vaults
from envault.vault import save_vault
from envault.cli_search import search_cmd

PASS = "hunter2"


@pytest.fixture(autouse=True)
def clean_vaults(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    yield


def _make_vault(name: str, env: dict) -> None:
    content = "\n".join(f"{k}={v}" for k, v in env.items())
    save_vault(name, content, PASS)


def test_search_finds_key_match():
    _make_vault("prod", {"DATABASE_URL": "postgres://localhost", "SECRET": "abc"})
    results = search_vaults("DATABASE", PASS)
    assert len(results) == 1
    assert results[0].key == "DATABASE_URL"
    assert results[0].match_on == "key"


def test_search_finds_value_match():
    _make_vault("prod", {"DB": "postgres://localhost", "TOKEN": "mytoken"})
    results = search_vaults("postgres", PASS)
    assert any(r.key == "DB" and r.match_on == "value" for r in results)


def test_search_keys_only_skips_value_matches():
    _make_vault("dev", {"FOO": "needle", "needle_KEY": "bar"})
    results = search_vaults("needle", PASS, keys_only=True)
    assert all(r.match_on == "key" for r in results)


def test_search_values_only_skips_key_matches():
    _make_vault("dev", {"NEEDLE_KEY": "something", "OTHER": "needle"})
    results = search_vaults("needle", PASS, values_only=True)
    assert all(r.match_on == "value" for r in results)


def test_search_case_insensitive_by_default():
    _make_vault("dev", {"MY_KEY": "HelloWorld"})
    results = search_vaults("helloworld", PASS)
    assert len(results) == 1


def test_search_case_sensitive_no_match():
    _make_vault("dev", {"MY_KEY": "HelloWorld"})
    results = search_vaults("helloworld", PASS, case_sensitive=True)
    assert results == []


def test_search_no_vaults_raises():
    with pytest.raises(SearchError, match="No vaults found"):
        search_vaults("anything", PASS)


def test_search_specific_vault():
    _make_vault("alpha", {"ALPHA_KEY": "val"})
    _make_vault("beta", {"BETA_KEY": "val"})
    results = search_vaults("ALPHA", PASS, vault_name="alpha")
    assert all(r.vault_name == "alpha" for r in results)


# --- CLI tests ---

@pytest.fixture
def runner():
    return CliRunner()


def test_cli_search_success(runner):
    _make_vault("prod", {"API_KEY": "secret123"})
    result = runner.invoke(search_cmd, ["API", "--passphrase", PASS])
    assert result.exit_code == 0
    assert "API_KEY" in result.output


def test_cli_search_no_matches(runner):
    _make_vault("prod", {"FOO": "bar"})
    result = runner.invoke(search_cmd, ["ZZZNOMATCH", "--passphrase", PASS])
    assert result.exit_code == 0
    assert "No matches found" in result.output


def test_cli_search_mutually_exclusive_flags(runner):
    result = runner.invoke(
        search_cmd, ["query", "--passphrase", PASS, "--keys-only", "--values-only"]
    )
    assert result.exit_code != 0
