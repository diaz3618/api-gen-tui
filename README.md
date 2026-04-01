# vk — Local Vault API Key Manager

> **Local-only tool.** `vk` runs HashiCorp Vault in Docker on your machine.
> It is not designed for production use or team sharing.

`vk` is a Python CLI tool that:
- Runs HashiCorp Vault in Docker with persistent storage
- Generates cryptographically secure API keys in multiple formats (hex, base64, UUID, ULID, and more)
- Stores generated keys in Vault with metadata
- Retrieves, lists, and exports keys

## Prerequisites

| Tool | Minimum version | Install |
|------|----------------|---------|
| Docker | 20.10+ (with Compose v2 plugin) | [docs.docker.com](https://docs.docker.com/get-docker/) |
| Python | 3.12+ | [python.org](https://www.python.org/downloads/) |
| uv | 0.10+ | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| xclip (Linux only) | any | `sudo apt install xclip` or `sudo dnf install xclip` |

`xclip` is required for clipboard support on Linux. On macOS, `pbcopy` is built in.
On headless systems (CI, SSH without X), clipboard copy fails silently — the key is still output.

## Quick Start — First Run

```bash
# 1. Clone and install
git clone https://github.com/your-org/api-gen-tui.git
cd api-gen-tui
make install         # creates .venv, installs all Python deps

# 2. Copy and review the config template
cp .env.example .env
# (no edits needed before vault-init — values are written automatically)

# 3. Start Vault
make up              # starts Docker container, waits for readiness

# 4. Initialize Vault (first time only)
make init            # writes unseal key + root token to .env
                     # ⚠️  Do not commit .env — it contains credentials

# 5. Generate and store your first key
uv run vk generate --type hex --length 32 --prefix sk_live_ \
    --store kv/api-keys/stripe/production
```

## Commands

| Command | Description |
|---------|-------------|
| `vk up` | Start Vault container, wait for readiness, auto-unseal |
| `vk down` | Stop Vault container |
| `vk status` | Show Vault health, seal state, and Docker status |
| `vk vault-init` | Initialize Vault (safe to re-run — idempotent) |
| `vk login` | Authenticate with Vault, store token at `~/.vk/token` |
| `vk generate` | Generate a cryptographically secure API key |
| `vk store <path> <value>` | Store an external token in Vault |
| `vk get <path>` | Retrieve a secret (masked by default; `--reveal` to show) |
| `vk list <path>` | List secrets as a tree view |
| `vk delete <path>` | Soft-delete a secret (`--permanent` for full removal) |
| `vk export <path>` | Export secrets as JSON or dotenv |
| `vk repl` | Open interactive shell with tab completion |

## Makefile Targets

```bash
make up       # vk up
make down     # vk down
make init     # vk vault-init
make status   # vk status
make test     # uv run pytest tests/ -v
make install  # uv sync (install deps)
make clean    # remove build artifacts
```

## Security

⚠️ **Local-only disclaimer:** `vk` is designed for individual developer use on a local machine.

- Vault runs with TLS disabled (acceptable for localhost only)
- The root token and unseal key are stored in `.env` for convenience — **never commit `.env` to git**
- `.env` is listed in `.gitignore` — verify this before your first commit: `git check-ignore .env`
- Secret values are masked in all output by default; use `--reveal` to show plaintext
- The REPL uses in-memory history — secret values are never written to a history file on disk

## Data Storage

- Vault data: Docker named volume `vk-vault-data` (persists across `docker compose` restarts)
- Auth token: `~/.vk/token` (mode 0600)
- Config: `.env` at repo root (gitignored)

## Vault Notes

- The file storage backend always seals Vault on restart — `vk up` auto-unseals using `.env`
- `vk vault-init` is idempotent — running it twice is safe (it checks `is_initialized()` first)
- KV v2 is mounted at `kv/` — default path convention is `kv/api-keys/<service>/<name>`

---

## api-gen-tui (Go TUI)

This repository also contains `api-gen-tui`, a Go TUI for generating API keys and tokens
interactively in the terminal. It is a standalone binary (`./api-gen-tui`) that does not
require Vault or Docker.

See the [Go TUI documentation](docs/) for build and usage instructions.
