"""CLI commands for managing vault policies.

Policies define rules for what keys are required, forbidden, or
must match a specific pattern within a vault.
"""

import click
from envault.policy import (
    PolicyError,
    create_policy,
    delete_policy,
    add_rule,
    remove_rule,
    get_policy,
    list_policies,
    evaluate_policy,
)
from envault.vault import load_vault
from envault.crypto import DecryptionError


@click.group("policy")
def policy_cmd():
    """Manage vault policies (required/forbidden/pattern rules)."""


@policy_cmd.command("create")
@click.argument("name")
@click.option("--description", "-d", default="", help="Optional policy description.")
def create_cmd(name, description):
    """Create a new named policy."""
    try:
        create_policy(name, description=description)
        click.echo(f"Policy '{name}' created.")
    except PolicyError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@policy_cmd.command("delete")
@click.argument("name")
def delete_cmd(name):
    """Delete an existing policy."""
    try:
        delete_policy(name)
        click.echo(f"Policy '{name}' deleted.")
    except PolicyError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@policy_cmd.command("add-rule")
@click.argument("policy")
@click.argument("rule_type", metavar="TYPE", type=click.Choice(["required", "forbidden", "pattern"]))
@click.argument("key")
@click.option("--pattern", "-p", default=None, help="Regex pattern (required for 'pattern' type).")
def add_rule_cmd(policy, rule_type, key, pattern):
    """Add a rule to a policy.

    TYPE is one of: required, forbidden, pattern.
    KEY is the env variable name the rule applies to.
    """
    try:
        add_rule(policy, rule_type=rule_type, key=key, pattern=pattern)
        click.echo(f"Rule added to policy '{policy}': {rule_type} {key}" +
                   (f" ~ {pattern}" if pattern else ""))
    except PolicyError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@policy_cmd.command("remove-rule")
@click.argument("policy")
@click.argument("key")
def remove_rule_cmd(policy, key):
    """Remove a rule from a policy by key."""
    try:
        remove_rule(policy, key=key)
        click.echo(f"Rule for '{key}' removed from policy '{policy}'.")
    except PolicyError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@policy_cmd.command("show")
@click.argument("name")
def show_cmd(name):
    """Show rules defined in a policy."""
    try:
        pol = get_policy(name)
    except PolicyError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    rules = pol.get("rules", [])
    desc = pol.get("description", "")
    click.echo(f"Policy: {name}" + (f"  ({desc})" if desc else ""))
    if not rules:
        click.echo("  No rules defined.")
    else:
        for r in rules:
            pat = f"  ~ {r['pattern']}" if r.get("pattern") else ""
            click.echo(f"  [{r['type']:10s}] {r['key']}{pat}")


@policy_cmd.command("list")
def list_cmd():
    """List all defined policies."""
    policies = list_policies()
    if not policies:
        click.echo("No policies defined.")
    else:
        for name in policies:
            click.echo(f"  {name}")


@policy_cmd.command("evaluate")
@click.argument("policy")
@click.argument("vault")
@click.option("--passphrase", "-p", prompt=True, hide_input=True, help="Vault passphrase.")
def evaluate_cmd(policy, vault, passphrase):
    """Evaluate a policy against a vault and report violations."""
    try:
        env = load_vault(vault, passphrase)
    except DecryptionError:
        click.echo("Error: wrong passphrase.", err=True)
        raise SystemExit(1)
    except FileNotFoundError:
        click.echo(f"Error: vault '{vault}' not found.", err=True)
        raise SystemExit(1)

    try:
        result = evaluate_policy(policy, env)
    except PolicyError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    violations = result.get("violations", [])
    if not violations:
        click.echo(f"✓ Vault '{vault}' passes policy '{policy}'.")
    else:
        click.echo(f"✗ Vault '{vault}' violates policy '{policy}':")
        for v in violations:
            click.echo(f"  - {v}")
        raise SystemExit(1)
