"""Search across vault keys and values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envault.vault import load_vault, list_vaults


@dataclass
class SearchResult:
    vault_name: str
    key: str
    value: str
    match_on: str  # 'key' | 'value'


class SearchError(Exception):
    pass


def search_vaults(
    query: str,
    passphrase: str,
    *,
    vault_name: Optional[str] = None,
    keys_only: bool = False,
    values_only: bool = False,
    case_sensitive: bool = False,
) -> List[SearchResult]:
    """Search for *query* across one or all vaults.

    Returns a list of :class:`SearchResult` objects.
    Raises :class:`SearchError` if no vaults exist.
    """
    names = [vault_name] if vault_name else list_vaults()
    if not names:
        raise SearchError("No vaults found.")

    needle = query if case_sensitive else query.lower()
    results: List[SearchResult] = []

    for name in names:
        try:
            env = load_vault(name, passphrase)
        except Exception as exc:  # noqa: BLE001
            raise SearchError(f"Could not load vault '{name}': {exc}") from exc

        for key, value in env.items():
            k = key if case_sensitive else key.lower()
            v = value if case_sensitive else value.lower()

            match_key = not values_only and needle in k
            match_val = not keys_only and needle in v

            if match_key:
                results.append(SearchResult(name, key, value, "key"))
            elif match_val:
                results.append(SearchResult(name, key, value, "value"))

    return results
