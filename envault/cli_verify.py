"""CLI surface for the vault verification feature."""

from __future__ import annotations

import click

from envault.verify import verify_vault, VerifyError


@click.group("verify")
def verify_cmd() -> None:
    """Verify vault integrity and contents."""


@verify_cmd.command("run")
@click.argument("name")
@click.option("--passphrase", "-p", prompt=True, hide_input=True, help="Vault passphrase.")
@click.option("--strict", is_flag=True, default=False, help="Treat lint warnings as errors.")
def run_cmd(name: str, passphrase: str, strict: bool) -> None:
    """Verify that vault NAME can be decrypted and its contents are valid."""
    try:
        result = verify_vault(name, passphrase, strict=strict)
    except VerifyError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    if result.decryption_ok:
        click.echo(f"✔  Decryption OK  ({result.key_count} keys)")
    else:
        click.echo("✘  Decryption FAILED")

    if result.lint is not None:
        if result.lint.ok:
            click.echo("✔  Lint OK")
        else:
            click.echo(f"✘  Lint found {len(result.lint.issues)} issue(s):")
            for issue in result.lint.issues:
                click.echo(f"   {issue}")

    if result.issues:
        for problem in result.issues:
            if problem not in [str(i) for i in (result.lint.issues if result.lint else [])]:
                click.echo(f"   {problem}")

    status = "PASS" if result.ok else "FAIL"
    click.echo(f"\nVerification result: {status}")

    if not result.ok:
        raise SystemExit(1)
