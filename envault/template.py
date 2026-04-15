"""Template rendering for .env files — substitute vault values into template strings."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envault.vault import load_vault

_PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


class TemplateError(Exception):
    """Raised when template rendering fails."""


@dataclass
class RenderResult:
    output: str
    resolved: List[str] = field(default_factory=list)
    missing: List[str] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        return len(self.missing) == 0


def list_template_variables(template: str) -> List[str]:
    """Return a deduplicated list of variable names found in *template*.

    Scans for all ``{{ KEY }}`` placeholders and returns the unique keys in
    the order they first appear.

    Args:
        template: Raw template string containing ``{{ KEY }}`` placeholders.

    Returns:
        Ordered list of unique placeholder variable names.
    """
    seen: dict[str, None] = {}
    for match in _PLACEHOLDER_RE.finditer(template):
        seen[match.group(1)] = None
    return list(seen)


def render_template(
    template: str,
    variables: Dict[str, str],
    strict: bool = False,
) -> RenderResult:
    """Replace {{ KEY }} placeholders in *template* with values from *variables*.

    Args:
        template: Raw template string containing ``{{ KEY }}`` placeholders.
        variables: Mapping of key -> value used for substitution.
        strict: If ``True``, raise :class:`TemplateError` for any missing key.

    Returns:
        A :class:`RenderResult` describing the rendered output and any gaps.
    """
    resolved: List[str] = []
    missing: List[str] = []

    def _replace(match: re.Match) -> str:  # type: ignore[type-arg]
        key = match.group(1)
        if key in variables:
            resolved.append(key)
            return variables[key]
        missing.append(key)
        if strict:
            raise TemplateError(f"Missing variable in template: '{key}'")
        return match.group(0)  # leave placeholder intact

    output = _PLACEHOLDER_RE.sub(_replace, template)
    return RenderResult(output=output, resolved=resolved, missing=missing)


def render_template_from_vault(
    template: str,
    vault_name: str,
    passphrase: str,
    strict: bool = False,
    vault_dir: Optional[str] = None,
) -> RenderResult:
    """Load *vault_name* and use its key/value pairs to render *template*."""
    kwargs = {"vault_dir": vault_dir} if vault_dir else {}
    env = load_vault(vault_name, passphrase, **kwargs)
    return render_template(template, env, strict=strict)
