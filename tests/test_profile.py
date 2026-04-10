"""Tests for envault.profile."""

from __future__ import annotations

import pytest

from envault import profile as prof
from envault.profile import ProfileError


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    profiles_file = tmp_path / "profiles.json"
    monkeypatch.setattr(prof, "_PROFILES_FILE", profiles_file)
    # Patch vault path so existence checks work without real vaults
    monkeypatch.setattr(
        "envault.profile._vault_path",
        lambda name: tmp_path / f"{name}.vault",
    )
    yield tmp_path


def _make_vault(tmp_path, name):
    (tmp_path / f"{name}.vault").write_bytes(b"fake")


def test_create_profile(isolated):
    prof.create_profile("dev")
    assert "dev" in prof.list_profiles()


def test_create_duplicate_profile_raises(isolated):
    prof.create_profile("dev")
    with pytest.raises(ProfileError, match="already exists"):
        prof.create_profile("dev")


def test_delete_profile(isolated):
    prof.create_profile("dev")
    prof.delete_profile("dev")
    assert "dev" not in prof.list_profiles()


def test_delete_nonexistent_profile_raises(isolated):
    with pytest.raises(ProfileError, match="not found"):
        prof.delete_profile("ghost")


def test_add_vault_to_profile(isolated):
    _make_vault(isolated, "app")
    prof.create_profile("dev")
    prof.add_vault_to_profile("dev", "app")
    assert "app" in prof.get_profile_vaults("dev")


def test_add_vault_no_duplicates(isolated):
    _make_vault(isolated, "app")
    prof.create_profile("dev")
    prof.add_vault_to_profile("dev", "app")
    prof.add_vault_to_profile("dev", "app")
    assert prof.get_profile_vaults("dev").count("app") == 1


def test_add_nonexistent_vault_raises(isolated):
    prof.create_profile("dev")
    with pytest.raises(ProfileError, match="does not exist"):
        prof.add_vault_to_profile("dev", "missing")


def test_remove_vault_from_profile(isolated):
    _make_vault(isolated, "app")
    prof.create_profile("dev")
    prof.add_vault_to_profile("dev", "app")
    prof.remove_vault_from_profile("dev", "app")
    assert "app" not in prof.get_profile_vaults("dev")


def test_remove_vault_not_in_profile_is_noop(isolated):
    prof.create_profile("dev")
    prof.remove_vault_from_profile("dev", "ghost")  # should not raise


def test_list_profiles_empty(isolated):
    assert prof.list_profiles() == []


def test_get_profile_vaults_unknown_raises(isolated):
    with pytest.raises(ProfileError, match="not found"):
        prof.get_profile_vaults("unknown")
