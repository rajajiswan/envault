"""Tests for CLI commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path
import tempfile
import shutil

from envault.cli import cli
from envault.vault import save_vault, _vault_path


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


@pytest.fixture
def temp_env_file():
    """Create a temporary .env file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write("DATABASE_URL=postgres://localhost/test\n")
        f.write("API_KEY=secret123\n")
        temp_path = f.name
    
    yield temp_path
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def clean_vault_dir():
    """Ensure clean vault directory for tests."""
    vault_dir = _vault_path("").parent
    if vault_dir.exists():
        shutil.rmtree(vault_dir)
    yield
    if vault_dir.exists():
        shutil.rmtree(vault_dir)


def test_save_command(runner, temp_env_file, clean_vault_dir):
    """Test saving a vault via CLI."""
    result = runner.invoke(
        cli,
        ['save', temp_env_file, 'test-vault'],
        input='mypassword\nmypassword\n'
    )
    
    assert result.exit_code == 0
    assert "Saved" in result.output
    assert "test-vault" in result.output


def test_save_command_passphrase_mismatch(runner, temp_env_file, clean_vault_dir):
    """Test save command with mismatched passphrases."""
    result = runner.invoke(
        cli,
        ['save', temp_env_file, 'test-vault'],
        input='password1\npassword2\n'
    )
    
    assert result.exit_code == 1
    assert "do not match" in result.output


def test_load_command(runner, clean_vault_dir):
    """Test loading a vault via CLI."""
    # First create a vault
    save_vault('test-vault', 'SECRET=value123', 'mypassword')
    
    result = runner.invoke(
        cli,
        ['load', 'test-vault'],
        input='mypassword\n'
    )
    
    assert result.exit_code == 0
    assert "SECRET=value123" in result.output


def test_load_command_wrong_passphrase(runner, clean_vault_dir):
    """Test load command with wrong passphrase."""
    save_vault('test-vault', 'SECRET=value123', 'correct')
    
    result = runner.invoke(
        cli,
        ['load', 'test-vault'],
        input='wrong\n'
    )
    
    assert result.exit_code == 1
    assert "Incorrect passphrase" in result.output


def test_list_command(runner, clean_vault_dir):
    """Test listing vaults."""
    save_vault('vault1', 'DATA=1', 'pass')
    save_vault('vault2', 'DATA=2', 'pass')
    
    result = runner.invoke(cli, ['list'])
    
    assert result.exit_code == 0
    assert "vault1" in result.output
    assert "vault2" in result.output


def test_list_command_no_vaults(runner, clean_vault_dir):
    """Test list command when no vaults exist."""
    result = runner.invoke(cli, ['list'])
    
    assert result.exit_code == 0
    assert "No vaults found" in result.output
