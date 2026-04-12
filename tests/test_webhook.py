"""Tests for envault.webhook."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from envault.webhook import (
    WebhookError,
    fire_event,
    list_webhooks,
    register_webhook,
    remove_webhook,
)


@pytest.fixture()
def isolated(tmp_path, monkeypatch):
    monkeypatch.setattr("envault.webhook._WEBHOOKS_FILE", tmp_path / "webhooks.json")
    monkeypatch.setattr("envault.vault.VAULT_DIR", tmp_path / "vaults")
    monkeypatch.setattr("envault.webhook._vault_path", lambda name: tmp_path / "vaults" / f"{name}.vault")
    return tmp_path


@pytest.fixture()
def _make_vault(isolated):
    def factory(name: str):
        vault_file = isolated / "vaults" / f"{name}.vault"
        vault_file.parent.mkdir(parents=True, exist_ok=True)
        vault_file.write_text("{}")
        return vault_file
    return factory


def test_register_webhook_creates_entry(isolated, _make_vault):
    _make_vault("prod")
    entry = register_webhook("prod", "https://example.com/hook")
    assert entry.vault_name == "prod"
    assert entry.url == "https://example.com/hook"
    assert "save" in entry.events


def test_register_webhook_unknown_vault_raises(isolated):
    with pytest.raises(WebhookError, match="does not exist"):
        register_webhook("ghost", "https://example.com/hook")


def test_register_webhook_custom_events(isolated, _make_vault):
    _make_vault("dev")
    entry = register_webhook("dev", "https://example.com/hook", events=["save"])
    assert entry.events == ["save"]


def test_list_webhooks_empty(isolated, _make_vault):
    _make_vault("staging")
    assert list_webhooks("staging") == []


def test_list_webhooks_returns_entries(isolated, _make_vault):
    _make_vault("prod")
    register_webhook("prod", "https://a.com")
    register_webhook("prod", "https://b.com")
    hooks = list_webhooks("prod")
    assert len(hooks) == 2
    urls = {h.url for h in hooks}
    assert urls == {"https://a.com", "https://b.com"}


def test_remove_webhook_returns_true(isolated, _make_vault):
    _make_vault("prod")
    register_webhook("prod", "https://example.com")
    result = remove_webhook("prod", "https://example.com")
    assert result is True
    assert list_webhooks("prod") == []


def test_remove_webhook_not_found_returns_false(isolated, _make_vault):
    _make_vault("prod")
    result = remove_webhook("prod", "https://notregistered.com")
    assert result is False


def test_fire_event_skips_wrong_event(isolated, _make_vault):
    _make_vault("prod")
    register_webhook("prod", "https://example.com", events=["save"])
    # No HTTP call expected — event doesn't match
    with patch("urllib.request.urlopen") as mock_open:
        failed = fire_event("prod", "load")
    mock_open.assert_not_called()
    assert failed == []


def test_fire_event_calls_matching_hook(isolated, _make_vault):
    _make_vault("prod")
    register_webhook("prod", "https://example.com", events=["save"])
    mock_resp = MagicMock()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
        failed = fire_event("prod", "save")
    assert mock_open.called
    assert failed == []


def test_fire_event_records_failure(isolated, _make_vault):
    import urllib.error
    _make_vault("prod")
    register_webhook("prod", "https://unreachable.example.com", events=["delete"])
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("timeout")):
        failed = fire_event("prod", "delete")
    assert "https://unreachable.example.com" in failed
