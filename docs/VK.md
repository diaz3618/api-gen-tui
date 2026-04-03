# vk — Local Vault API Key Manager

`vk` is a CLI tool that runs HashiCorp Vault in Docker and provides a
cryptographically secure API key/token generator. Generate a properly-formatted
key and store it in a locally-running Vault instance with a single command.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [First-time Setup](#first-time-setup)
- [Configuration](#configuration)
- [Commands Reference](#commands-reference)
  - [Infrastructure](#infrastructure)
  - [Key Management](#key-management)
  - [REPL Shell](#repl-shell)
  - [Policy](#policy)
- [Generator Formats](#generator-formats)
- [Generator Flags Reference](#generator-flags-reference)
- [Short Flag Reference](#short-flag-reference)

---

## Prerequisites

- **Docker** and **Docker Compose** — must be running on your machine
- **Python 3.12+**
- **uv** (recommended) or pip

---

## Installation

### With uv (recommended)

```bash
uv venv .venv
uv pip install -e .
source .venv/bin/activate
```

### With pip

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Verify:

```bash
vk --help
```

---

## First-time Setup

Run these three commands once, in order:

```bash
# 1. Start the Vault Docker container
vk up

# 2. Initialize Vault — writes VAULT_ROOT_TOKEN and VAULT_UNSEAL_KEY to .env
vk vault-init

# 3. Restart so Vault auto-unseals using the key now in .env
vk up

# 4. Authenticate — stores token at ~/.vk/token so subsequent commands work
vk login
```

After this, `vk status` should show everything green:

```
╭──────────────────── Vault Status ─────────────────────╮
│  URL         http://127.0.0.1:8200                     │
│  Seal state  Unsealed                                  │
│  KV mount    kv/ found                                 │
│  Docker      Running                                   │
╰────────────────────────────────────────────────────────╯
```

> **Important:** `.env` contains your root token and unseal key. Never commit it
> to git. It is already listed in `.gitignore`.

---

## Configuration

`vk` reads configuration from a `.env` file in the project root. Copy the
example template to get started:

```bash
cp .env.example .env
```

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `VAULT_ADDR` | `http://127.0.0.1:8200` | Vault server URL |
| `VAULT_PORT` | `8200` | Port exposed by the Docker container |
| `VAULT_ROOT_TOKEN` | *(set by `vk vault-init`)* | Root token for Vault authentication |
| `VAULT_UNSEAL_KEY` | *(set by `vk vault-init`)* | Unseal key used by `vk up` |
| `VAULT_KV_MOUNT` | `kv` | KV v2 mount path |
| `VK_DEFAULT_PATH_PREFIX` | `api-keys` | Default path prefix for `vk list` |

### Token Resolution Order

`vk` resolves the active token in this priority order:

1. `--token` flag (for `vk login`)
2. `~/.vk/token` file (written by `vk login`)
3. `VAULT_ROOT_TOKEN` in `.env`
4. `VAULT_TOKEN` environment variable

---

## Commands Reference

Every command supports `-h` / `--help`:

```bash
vk generate -h
vk store -h
```

---

### Infrastructure

#### `vk up`

Start the Vault Docker container and auto-unseal.

```bash
vk up
```

- Starts the Docker Compose stack
- Polls the Vault HTTP listener (up to 60 s)
- Auto-unseals using `VAULT_UNSEAL_KEY` from `.env` if available
- On a fresh install (no `.env` credentials), exits with a message to run `vk vault-init`

---

#### `vk down`

Stop the Vault Docker container.

```bash
vk down
```

---

#### `vk status`

Display Vault health, seal state, KV mount status, and Docker container state.

```bash
vk status
```

Exit codes: `0` = healthy, `2` = any issue (unreachable, sealed, KV missing, container stopped).

---

#### `vk vault-init`

Initialize Vault on first run. Writes `VAULT_ROOT_TOKEN` and `VAULT_UNSEAL_KEY`
to `.env`, enables the KV v2 engine, and immediately unseals.

```bash
vk vault-init
```

This command is **idempotent** — it refuses to run if credentials are already
present in `.env`.

---

#### `vk login`

Authenticate and persist your token to `~/.vk/token` (mode `0600`).

```bash
# Uses token from .env automatically
vk login

# Supply a token explicitly
vk login --token hvs.xxxx
vk login -t hvs.xxxx
```

---

### Key Management

#### `vk generate`

Generate a cryptographically secure API key or token and print it to stdout.
The last generated key is copied to the clipboard automatically.

```bash
# Basic usage — 32-char hex key
vk generate

# Choose a format and length
vk generate --type base64 --length 48
vk generate -t uuid4

# Add a prefix (e.g. Stripe-style)
vk generate --type alphanumeric --prefix sk_live_ --length 40

# Group into readable chunks
vk generate --type hex --length 32 --group 8 --separator -

# Generate and store directly in Vault
vk generate --type hex --length 32 --store myapp/stripe-key
vk generate -t base64 -l 48 -s myapp/openai-key

# Generate multiple keys
vk generate --count 5
vk generate -n 5

# Print entropy estimate
vk generate --entropy
vk generate -e
```

Full flag reference: see [Generator Flags Reference](#generator-flags-reference).

---

#### `vk store`

Store an externally supplied secret value in Vault.

```bash
vk store <path> <value> [options]

# Examples
vk store myapp/github-token "ghp_xxxxxxxxxxxx"
vk store myapp/openai-key "sk-xxxx" --notes "Production key" --tags "openai,prod"
vk store myapp/openai-key "sk-xxxx" -n "Production key" -t "openai,prod"
```

| Flag | Short | Description |
|---|---|---|
| `--notes` | `-n` | Optional annotation stored alongside the secret |
| `--tags` | `-t` | Comma-separated tags (e.g. `"openai,production"`) |

---

#### `vk get`

Retrieve a secret. Value is masked by default.

```bash
vk get <path>

# Show the plaintext value
vk get myapp/stripe-key --reveal
vk get myapp/stripe-key -r
```

Output includes: value (masked or revealed), format, creation time, length.

---

#### `vk list`

List secrets under a Vault path.

```bash
# List the default path (kv/api-keys)
vk list

# List under a specific path
vk list myapp
vk list kv/api-keys/myapp
```

---

#### `vk delete`

Delete a secret. Soft delete by default (recoverable via Vault UI or API).

```bash
# Soft delete (recoverable)
vk delete myapp/old-key

# Permanent — destroys all versions, cannot be undone
vk delete myapp/old-key --permanent
vk delete myapp/old-key -p
```

---

#### `vk export`

Export all secrets under a path to stdout as JSON or dotenv format.

```bash
# JSON (default)
vk export myapp
vk export myapp --format json

# dotenv format
vk export myapp --format dotenv
vk export myapp -f dotenv

# Pipe to a file
vk export myapp -f dotenv > myapp.env
```

**JSON output example:**
```json
{
  "kv/api-keys/myapp/stripe-key": {
    "value": "a3f4c1d9...",
    "format": "hex",
    "created_at": "2026-04-02T10:00:00Z"
  }
}
```

**dotenv output example:**
```
STRIPE_KEY=a3f4c1d9...
OPENAI_KEY=sk-xxxx
```

---

### REPL Shell

#### `vk repl`

Launch an interactive shell with tab completion and in-session history.

```bash
vk repl
```

```
vk — type help for commands, exit to quit, Ctrl+D to exit
vk> help
vk> generate -t hex -l 32
vk> store myapp/key "abc123"
vk> list myapp
vk> exit
```

**Available REPL commands:**

| Command | Description |
|---|---|
| `generate` | Generate a cryptographically secure API key or token |
| `store` | Store an externally supplied secret in Vault |
| `get` | Retrieve a secret from Vault (masked by default) |
| `list` | List secrets under a Vault path |
| `delete` | Delete a secret (soft delete; `--permanent` to destroy) |
| `export` | Export secrets as JSON or dotenv format |
| `up` | Start the Vault Docker container and auto-unseal |
| `down` | Stop the Vault Docker container |
| `status` | Show Vault health, seal state, and Docker status |
| `vault-init` | Initialize Vault and write credentials to `.env` |
| `login` | Authenticate and store token at `~/.vk/token` |
| `policy` | Emit a Vault HCL password policy from a preset |
| `help` / `h` / `?` | Show the command list |
| `exit` / `quit` | Exit the REPL |

**Key bindings:**

| Key | Action |
|---|---|
| `Tab` | Autocomplete command name |
| `↑` / `↓` | Navigate in-session history |
| `Ctrl+C` | Cancel current line |
| `Ctrl+D` | Exit REPL |

> **Note:** The REPL requires a real TTY. It cannot be driven by piped stdin.
> All commands work identically to their `vk <command>` equivalents.

---

### Policy

#### `vk policy`

Emit a Vault-compatible HCL password policy to stdout. Useful for configuring
Vault's built-in password generation.

```bash
vk policy <preset>

# Pipe to a file
vk policy strong > strong-policy.hcl
```

**Available presets:**

| Preset | Length | Rules |
|---|---|---|
| `default` | 32 | Alphanumeric, min 1 of each |
| `strong` | 32 | Lower ≥4, upper ≥4, digits ≥4, symbols(`!@#$%^&*`) ≥2 |
| `hex` | 64 | Hex characters only |
| `uuid` | 36 | Hex + `-` (UUID4 approximation) |
| `stripe` | 32 | Alphanumeric (pair with `--prefix sk_live_` in your app) |

---

## Generator Formats

| Format | Description | Example output |
|---|---|---|
| `hex` | Lowercase hexadecimal | `a3f4c1d9e2b7...` |
| `base64` | Standard Base64 (may contain `+`, `/`, `=`) | `dGVzdC10b2...` |
| `base64url` | URL-safe Base64 (no `+`/`/`) | `dGVzdC10b2...` |
| `base32` | Base32 (uppercase, no padding issues) | `MFRA2YTBM5...` |
| `alphanumeric` | Letters and digits only | `Kj8mNpQ3...` |
| `uuid4` | Random UUID v4 | `550e8400-e29b-41d4-a716-446655440000` |
| `ulid` | Sortable, URL-safe 26-char ID | `01ARZ3NDEKTSV4RRFFQ69G5FAV` |
| `url-safe` | Alphanumeric + `-` and `_` | `Kj8m-NpQ3_...` |
| `custom` | Your own alphabet via `--alphabet` | *(depends on alphabet)* |

---

## Generator Flags Reference

All flags for `vk generate`:

| Flag | Short | Default | Description |
|---|---|---|---|
| `--type` | `-t` | `hex` | Output format (see formats above) |
| `--length` | `-l` | `32` | Total output length including prefix/suffix |
| `--random-length` | `-L` | — | Explicit random portion length (overrides `--length` calc) |
| `--prefix` | `-p` | — | Fixed string prepended to the key |
| `--suffix` | `-x` | — | Fixed string appended to the key |
| `--separator` | `-d` | `_` | Separator between groups (used with `--group`) |
| `--group` | `-g` | — | Split random portion into chunks of N characters |
| `--no-ambiguous` | — | — | Remove visually similar characters (`0`, `O`, `1`, `l`, `I`) |
| `--upper` | `-u` | — | Force all output to uppercase |
| `--lower` | — | — | Force all output to lowercase |
| `--min-upper` | — | `0` | Minimum number of uppercase characters |
| `--min-lower` | — | `0` | Minimum number of lowercase characters |
| `--min-digits` | — | `0` | Minimum number of digit characters |
| `--min-symbols` | — | `0` | Minimum number of symbol characters |
| `--entropy` | `-e` | — | Print entropy estimate (bits) to stderr |
| `--count` | `-n` | `1` | Number of keys to generate |
| `--alphabet` | `-a` | — | Custom character set (requires `--type custom`) |
| `--store` | `-s` | — | Vault path to store the key after generation |

---

## Short Flag Reference

Quick reference for all single-dash flags:

| Flag | Long form | Command |
|---|---|---|
| `-h` | `--help` | All commands |
| `-t` | `--type` | `generate` |
| `-l` | `--length` | `generate` |
| `-L` | `--random-length` | `generate` |
| `-p` | `--prefix` | `generate` |
| `-x` | `--suffix` | `generate` |
| `-d` | `--separator` | `generate` |
| `-g` | `--group` | `generate` |
| `-u` | `--upper` | `generate` |
| `-e` | `--entropy` | `generate` |
| `-n` | `--count` | `generate` |
| `-a` | `--alphabet` | `generate` |
| `-s` | `--store` | `generate` |
| `-n` | `--notes` | `store` |
| `-t` | `--tags` | `store` |
| `-r` | `--reveal` | `get` |
| `-p` | `--permanent` | `delete` |
| `-f` | `--format` | `export` |
| `-t` | `--token` | `login` |
