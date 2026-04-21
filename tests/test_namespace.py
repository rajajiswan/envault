"""Tests for envault.namespace."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_namespace import namespace_cmd
from envault.namespace import (
    NamespaceError,
    add_vault_to_namespace,
    create_namespace,
    delete_namespace,
    get_namespace,
    list_namespaces,
    remove_vault_from_namespace,
    _NS_FILE,
)
from envault.vault import save_vault


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    ns_file = tmp_path / "namespaces.json"
    monkeypatch.setattr("envault.namespace._NS_FILE", ns_file)
    vault_dir = tmp_path / "vaults"
    vault_dir.mkdir()
    monkeypatch.setattr("envault.namespace._vault_path",
                        lambda name: vault_dir / f"{name}.vault")
    monkeypatch.setattr("envault.vault.VAULT_DIR", vault_dir)
    yield vault_dir


def _make_vault(vault_dir, name, passphrase="pass"):
    save_vault(name, {"KEY": "val"}, passphrase)


# --- unit tests ---

def test_create_namespace(isolated):
    create_namespace("prod")
    assert "prod" in list_namespaces()


def test_create_duplicate_namespace_raises(isolated):
    create_namespace("prod")
    with pytest.raises(NamespaceError, match="already exists"):
        create_namespace("prod")


def test_delete_namespace(isolated):
    create_namespace("staging")
    delete_namespace("staging")
    assert "staging" not in list_namespaces()


def test_delete_nonexistent_namespace_raises(isolated):
    with pytest.raises(NamespaceError, match="does not exist"):
        delete_namespace("ghost")


def test_delete_nonempty_namespace_raises(isolated):
    _make_vault(isolated, "myapp")
    create_namespace("prod")
    add_vault_to_namespace("prod", "myapp")
    with pytest.raises(NamespaceError, match="not empty"):
        delete_namespace("prod")


def test_delete_nonempty_namespace_with_force(isolated):
    _make_vault(isolated, "myapp")
    create_namespace("prod")
    add_vault_to_namespace("prod", "myapp")
    delete_namespace("prod", force=True)
    assert "prod" not in list_namespaces()


def test_add_vault_to_namespace(isolated):
    _make_vault(isolated, "app1")
    create_namespace("dev")
    add_vault_to_namespace("dev", "app1")
    assert "app1" in get_namespace("dev")


def test_add_vault_no_duplicates(isolated):
    _make_vault(isolated, "app1")
    create_namespace("dev")
    add_vault_to_namespace("dev", "app1")
    add_vault_to_namespace("dev", "app1")
    assert get_namespace("dev").count("app1") == 1


def test_add_unknown_vault_raises(isolated):
    create_namespace("dev")
    with pytest.raises(NamespaceError, match="does not exist"):
        add_vault_to_namespace("dev", "ghost")


def test_remove_vault_from_namespace(isolated):
    _make_vault(isolated, "app1")
    create_namespace("dev")
    add_vault_to_namespace("dev", "app1")
    remove_vault_from_namespace("dev", "app1")
    assert "app1" not in get_namespace("dev")


def test_remove_vault_noop_if_not_present(isolated):
    create_namespace("dev")
    remove_vault_from_namespace("dev", "ghost")  # should not raise


# --- CLI tests ---

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_create_and_list(runner, isolated):
    result = runner.invoke(namespace_cmd, ["create", "prod"])
    assert result.exit_code == 0
    result = runner.invoke(namespace_cmd, ["list"])
    assert "prod" in result.output


def test_cli_show_empty_namespace(runner, isolated):
    runner.invoke(namespace_cmd, ["create", "empty"])
    result = runner.invoke(namespace_cmd, ["show", "empty"])
    assert "empty" in result.output


def test_cli_show_unknown_namespace(runner, isolated):
    result = runner.invoke(namespace_cmd, ["show", "ghost"])
    assert result.exit_code == 1
    assert "Error" in result.output
