# envault

> A CLI tool for securely storing and syncing `.env` files across machines using encrypted local vaults.

---

## Installation

```bash
pip install envault
```

Or with [pipx](https://pypa.github.io/pipx/) (recommended):

```bash
pipx install envault
```

---

## Usage

**Initialize a new vault in your project:**
```bash
envault init
```

**Store your `.env` file in the vault:**
```bash
envault store .env
```

**Sync and restore your `.env` on another machine:**
```bash
envault pull --output .env
```

**List stored secrets:**
```bash
envault list
```

Envault encrypts your environment variables using AES-256 before storing them locally. A master password or key file is required to lock and unlock the vault.

```bash
# Example: push and pull with a named vault
envault push --vault myproject
envault pull --vault myproject --output .env
```

---

## Why envault?

- 🔒 AES-256 encryption out of the box
- 🖥️ Works fully offline — no third-party servers
- ⚡ Simple CLI with minimal setup
- 🔄 Easy syncing across machines via any file-sharing method (Git, Dropbox, etc.)

---

## License

This project is licensed under the [MIT License](LICENSE).

---

> **Note:** Never commit your vault master key or unencrypted `.env` files to version control. Add `.env` and `.envault/key` to your `.gitignore`.