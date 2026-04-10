"""Tests for envault.template — template rendering against vault values."""

from __future__ import annotations

import os
import pytest

from envault.template import (
    RenderResult,
    TemplateError,
    render_template,
    render_template_from_vault,
)
from envault.vault import save_vault


# ---------------------------------------------------------------------------
# render_template unit tests
# ---------------------------------------------------------------------------

def test_render_simple_substitution():
    result = render_template("Hello {{ NAME }}!", {"NAME": "world"})
    assert result.output == "Hello world!"
    assert result.resolved == ["NAME"]
    assert result.missing == []
    assert result.is_complete


def test_render_multiple_placeholders():
    tmpl = "HOST={{ HOST }} PORT={{ PORT }}"
    result = render_template(tmpl, {"HOST": "localhost", "PORT": "5432"})
    assert result.output == "HOST=localhost PORT=5432"
    assert set(result.resolved) == {"HOST", "PORT"}


def test_render_missing_key_leaves_placeholder():
    result = render_template("{{ MISSING }}", {})
    assert result.output == "{{ MISSING }}"
    assert result.missing == ["MISSING"]
    assert not result.is_complete


def test_render_strict_raises_on_missing_key():
    with pytest.raises(TemplateError, match="MISSING"):
        render_template("{{ MISSING }}", {}, strict=True)


def test_render_whitespace_inside_braces():
    result = render_template("{{  KEY  }}", {"KEY": "value"})
    assert result.output == "value"


def test_render_partial_substitution():
    tmpl = "A={{ A }} B={{ B }}"
    result = render_template(tmpl, {"A": "1"})
    assert "A=1" in result.output
    assert "{{ B }}" in result.output
    assert result.missing == ["B"]
    assert result.resolved == ["A"]


def test_render_no_placeholders():
    result = render_template("no placeholders here", {"KEY": "val"})
    assert result.output == "no placeholders here"
    assert result.resolved == []
    assert result.missing == []


# ---------------------------------------------------------------------------
# render_template_from_vault integration tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def vault_env(tmp_path):
    """Save a small vault and return (vault_dir, vault_name, passphrase)."""
    vault_dir = str(tmp_path)
    name = "myapp"
    passphrase = "s3cr3t"
    env = {"DB_HOST": "db.example.com", "DB_PORT": "5432", "APP_ENV": "production"}
    env_text = "\n".join(f"{k}={v}" for k, v in env.items())
    save_vault(name, env_text, passphrase, vault_dir=vault_dir)
    return vault_dir, name, passphrase


def test_render_from_vault_resolves_keys(vault_env):
    vault_dir, name, passphrase = vault_env
    tmpl = "postgres://{{ DB_HOST }}:{{ DB_PORT }}/mydb"
    result = render_template_from_vault(tmpl, name, passphrase, vault_dir=vault_dir)
    assert result.output == "postgres://db.example.com:5432/mydb"
    assert result.is_complete


def test_render_from_vault_missing_key_not_strict(vault_env):
    vault_dir, name, passphrase = vault_env
    result = render_template_from_vault(
        "{{ NONEXISTENT }}", name, passphrase, vault_dir=vault_dir
    )
    assert not result.is_complete
    assert "NONEXISTENT" in result.missing


def test_render_from_vault_strict_raises(vault_env):
    vault_dir, name, passphrase = vault_env
    with pytest.raises(TemplateError):
        render_template_from_vault(
            "{{ NONEXISTENT }}", name, passphrase, strict=True, vault_dir=vault_dir
        )
