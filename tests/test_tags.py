"""Tests for envault tag management."""

import pytest
from click.testing import CliRunner
from envault.tags import add_tag, remove_tag, get_tags, find_by_tag, clear_tags
from envault.cli_tags import tags_cmd


@pytest.fixture
def tag_dir(tmp_path):
    return str(tmp_path)


# --- Unit tests for tags.py ---

def test_add_tag_creates_entry(tag_dir):
    add_tag("myapp", "production", vault_dir=tag_dir)
    assert "production" in get_tags("myapp", vault_dir=tag_dir)


def test_add_tag_no_duplicates(tag_dir):
    add_tag("myapp", "staging", vault_dir=tag_dir)
    add_tag("myapp", "staging", vault_dir=tag_dir)
    assert get_tags("myapp", vault_dir=tag_dir).count("staging") == 1


def test_remove_tag(tag_dir):
    add_tag("myapp", "dev", vault_dir=tag_dir)
    remove_tag("myapp", "dev", vault_dir=tag_dir)
    assert "dev" not in get_tags("myapp", vault_dir=tag_dir)


def test_remove_tag_nonexistent_is_noop(tag_dir):
    remove_tag("myapp", "ghost", vault_dir=tag_dir)  # should not raise


def test_get_tags_empty_for_unknown_vault(tag_dir):
    assert get_tags("unknown", vault_dir=tag_dir) == []


def test_find_by_tag(tag_dir):
    add_tag("app1", "prod", vault_dir=tag_dir)
    add_tag("app2", "prod", vault_dir=tag_dir)
    add_tag("app3", "dev", vault_dir=tag_dir)
    result = find_by_tag("prod", vault_dir=tag_dir)
    assert "app1" in result
    assert "app2" in result
    assert "app3" not in result


def test_find_by_tag_no_matches(tag_dir):
    assert find_by_tag("nonexistent", vault_dir=tag_dir) == []


def test_clear_tags(tag_dir):
    add_tag("myapp", "t1", vault_dir=tag_dir)
    add_tag("myapp", "t2", vault_dir=tag_dir)
    clear_tags("myapp", vault_dir=tag_dir)
    assert get_tags("myapp", vault_dir=tag_dir) == []


# --- CLI tests for cli_tags.py ---

@pytest.fixture
def runner():
    return CliRunner()


def test_cli_add_and_list(runner, tag_dir, monkeypatch):
    monkeypatch.setattr("envault.tags._tags_path",
                        lambda vault_dir=None: __import__('pathlib').Path(tag_dir) / ".envault_tags.json")
    from envault import tags as tags_mod
    orig = tags_mod._tags_path
    tags_mod._tags_path = lambda vault_dir=None: __import__('pathlib').Path(tag_dir) / ".envault_tags.json"
    add_tag("web", "production", vault_dir=tag_dir)
    tags = get_tags("web", vault_dir=tag_dir)
    assert "production" in tags
    tags_mod._tags_path = orig


def test_cli_tags_add_output(runner, tmp_path, monkeypatch):
    import envault.tags as tags_mod
    import envault.cli_tags as cli_tags_mod
    monkeypatch.setattr(tags_mod, "_tags_path",
                        lambda vault_dir=None: tmp_path / ".envault_tags.json")
    result = runner.invoke(tags_cmd, ["add", "myapp", "beta"])
    assert result.exit_code == 0
    assert "beta" in result.output
    assert "myapp" in result.output


def test_cli_tags_find_output(runner, tmp_path, monkeypatch):
    import envault.tags as tags_mod
    monkeypatch.setattr(tags_mod, "_tags_path",
                        lambda vault_dir=None: tmp_path / ".envault_tags.json")
    add_tag("svc1", "shared", vault_dir=str(tmp_path))
    result = runner.invoke(tags_cmd, ["find", "shared"])
    assert result.exit_code == 0
    assert "svc1" in result.output
