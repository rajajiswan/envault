"""Webhook notifications for vault events."""

from __future__ import annotations

import json
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envault.vault import _vault_path


class WebhookError(Exception):
    pass


_WEBHOOKS_FILE = Path.home() / ".envault" / "webhooks.json"


@dataclass
class WebhookEntry:
    vault_name: str
    url: str
    events: List[str] = field(default_factory=lambda: ["save", "load", "delete"])


def _load_store() -> dict:
    if not _WEBHOOKS_FILE.exists():
        return {}
    return json.loads(_WEBHOOKS_FILE.read_text())


def _save_store(store: dict) -> None:
    _WEBHOOKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    _WEBHOOKS_FILE.write_text(json.dumps(store, indent=2))


def register_webhook(vault_name: str, url: str, events: Optional[List[str]] = None) -> WebhookEntry:
    """Register a webhook URL for a vault."""
    if not _vault_path(vault_name).exists():
        raise WebhookError(f"Vault '{vault_name}' does not exist.")
    store = _load_store()
    entry = {
        "url": url,
        "events": events or ["save", "load", "delete"],
    }
    store.setdefault(vault_name, []).append(entry)
    _save_store(store)
    return WebhookEntry(vault_name=vault_name, url=url, events=entry["events"])


def remove_webhook(vault_name: str, url: str) -> bool:
    """Remove a webhook by URL. Returns True if removed, False if not found."""
    store = _load_store()
    hooks = store.get(vault_name, [])
    new_hooks = [h for h in hooks if h["url"] != url]
    if len(new_hooks) == len(hooks):
        return False
    store[vault_name] = new_hooks
    _save_store(store)
    return True


def list_webhooks(vault_name: str) -> List[WebhookEntry]:
    """List all webhooks registered for a vault."""
    store = _load_store()
    return [
        WebhookEntry(vault_name=vault_name, url=h["url"], events=h["events"])
        for h in store.get(vault_name, [])
    ]


def fire_event(vault_name: str, event: str, payload: Optional[dict] = None) -> List[str]:
    """Fire webhooks for a vault event. Returns list of URLs that failed."""
    store = _load_store()
    failed: List[str] = []
    body = json.dumps({"vault": vault_name, "event": event, **(payload or {})}).encode()
    for hook in store.get(vault_name, []):
        if event not in hook.get("events", []):
            continue
        req = urllib.request.Request(
            hook["url"],
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=5):
                pass
        except (urllib.error.URLError, OSError):
            failed.append(hook["url"])
    return failed
