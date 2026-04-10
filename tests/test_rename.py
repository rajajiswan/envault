"""Tests for envault.rename."""

import pytest
from pathlib import Path

from envault.vault import save_vault, load_vault
from envault.tags import add_tag, get_tags
from envault.rename import rename_vault, RenameError


PASSPHRASE = "hunter2"


@pytest.fixture()
def vault_dir(tmp_path):
    """Return a temporary directory used as the vault store."""
    return str(tmp_path)


def _make_vault(name: str, vault_dir: str, data: dict | None = None) -> None:
    env = data or {"KEY": "value", "OTHER": "123"}
    save_vault(name, env, PASSPHRASE, vault_dir=vault_dir)


# ---------------------------------------------------------------------------
# rename_vault core behaviour
# ---------------------------------------------------------------------------

def test_rename_moves_vault_file(vault_dir):
    _make_vault("alpha", vault_dir)
    new_path = rename_vault("alpha", "beta", vault_dir=vault_dir)
    assert new_path.exists()
    assert not Path(vault_dir, "alpha.vault").exists()


def test_renamed_vault_is_loadable(vault_dir):
    _make_vault("alpha", vault_dir, {"DB_URL": "postgres://localhost/db"})
    rename_vault("alpha", "beta", vault_dir=vault_dir)
    data = load_vault("beta", PASSPHRASE, vault_dir=vault_dir)
    assert data["DB_URL"] == "postgres://localhost/db"


def test_rename_nonexistent_vault_raises(vault_dir):
    with pytest.raises(RenameError, match="does not exist"):
        rename_vault("ghost", "phantom", vault_dir=vault_dir)


def test_rename_to_existing_name_raises(vault_dir):
    _make_vault("alpha", vault_dir)
    _make_vault("beta", vault_dir)
    with pytest.raises(RenameError, match="already exists"):
        rename_vault("alpha", "beta", vault_dir=vault_dir)


def test_rename_identical_names_raises(vault_dir):
    _make_vault("alpha", vault_dir)
    with pytest.raises(RenameError, match="identical"):
        rename_vault("alpha", "alpha", vault_dir=vault_dir)


# ---------------------------------------------------------------------------
# tags are transferred
# ---------------------------------------------------------------------------

def test_rename_transfers_tags(vault_dir):
    _make_vault("alpha", vault_dir)
    add_tag("alpha", "production", vault_dir=vault_dir)
    add_tag("alpha", "backend", vault_dir=vault_dir)
    rename_vault("alpha", "beta", vault_dir=vault_dir)
    tags = get_tags("beta", vault_dir=vault_dir)
    assert "production" in tags
    assert "backend" in tags


def test_rename_clears_old_name_tags(vault_dir):
    _make_vault("alpha", vault_dir)
    add_tag("alpha", "staging", vault_dir=vault_dir)
    rename_vault("alpha", "beta", vault_dir=vault_dir)
    tags = get_tags("alpha", vault_dir=vault_dir)
    assert tags == []


def test_rename_vault_without_tags_is_fine(vault_dir):
    _make_vault("alpha", vault_dir)
    new_path = rename_vault("alpha", "beta", vault_dir=vault_dir)
    assert new_path.exists()
    assert get_tags("beta", vault_dir=vault_dir) == []
