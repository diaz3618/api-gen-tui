from __future__ import annotations

import time

import typer
from rich.panel import Panel
from rich.status import Status

from vk.config import Settings
from vk.docker.compose import ComposeManager
from vk.errors import VaultAlreadyInitialized, VaultForbidden, VaultNotRunning, VaultSealed, VkError
from vk.output import console, handle_unexpected, print_error
from vk.vault.client import VaultClient
from vk.vault.init import VaultInitializer


def up() -> None:
    """Start Vault, wait until ready, then auto-unseal."""
    settings = Settings()
    manager = ComposeManager(settings)
    client = VaultClient(settings, token=settings.vault_root_token or None)
    try:
        manager.up(wait=False)  # Start the Compose stack (don't wait via ComposeManager)
        # Poll /v1/sys/health with Rich spinner until ready or timeout
        with Status("Waiting for Vault to become ready…", spinner="dots", console=console):
            for _ in range(60):  # 60 retries × 1 s = 60 s timeout
                time.sleep(1)
                try:
                    if not client.is_sealed():
                        break  # already unsealed (rare — container re-used)
                    if client.is_initialized():
                        break  # initialized + sealed = need to unseal
                except VaultNotRunning:
                    continue  # still starting
            else:
                raise VaultNotRunning(
                    "Vault did not become ready within 60 seconds.",
                    hint="Check `docker compose logs vault` for errors.",
                )
        # Auto-unseal if sealed and unseal key available
        if client.is_sealed():
            if not settings.vault_unseal_key:
                raise VaultSealed(
                    "Vault is sealed and no VAULT_UNSEAL_KEY found in .env.",
                    hint="Run `vk vault-init` first to initialize and get an unseal key.",
                )
            client.unseal(settings.vault_unseal_key)
        # Success panel (per D-03)
        console.print(
            Panel(
                f"Vault is up and unsealed\n[dim]URL:[/dim] {settings.vault_addr}",
                title="Vault Ready",
                border_style="green",
            )
        )
    except VkError as err:
        print_error(err)
        raise typer.Exit(1)
    except Exception as e:
        handle_unexpected(e)


def down() -> None:
    """Stop the Vault Compose stack."""
    try:
        ComposeManager().down()
        console.print("[green]Vault stopped.[/green]")
    except VkError as err:
        print_error(err)
        raise typer.Exit(1)
    except Exception as e:
        handle_unexpected(e)


def status() -> None:
    """Display Vault health, seal state, KV mount, and Docker container state."""
    from rich.table import Table

    settings = Settings()
    manager = ComposeManager(settings)

    # Gather state defensively — never crash
    docker_running = manager.is_running()

    try:
        client = VaultClient(settings)
        initialized = client.is_initialized()
        sealed = client.is_sealed()
        kv_ok = client.kv_mount_exists("kv")
        vault_reachable = True
    except VkError:
        initialized = False
        sealed = True
        kv_ok = False
        vault_reachable = False

    # Build color-coded table
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Key", style="dim")
    table.add_column("Value")

    # Vault URL row — always shown
    table.add_row("URL", settings.vault_addr)

    # Seal state
    if not vault_reachable:
        table.add_row("Seal state", "[red]Unreachable[/red]")
    elif sealed:
        table.add_row("Seal state", "[yellow]Sealed[/yellow]")
    else:
        table.add_row("Seal state", "[green]Unsealed[/green]")

    # KV mount
    if kv_ok:
        table.add_row("KV mount", "[green]kv/ found[/green]")
    else:
        table.add_row("KV mount", "[red]Not found[/red]")

    # Docker container
    if docker_running:
        table.add_row("Docker", "[green]Running[/green]")
    else:
        table.add_row("Docker", "[red]Stopped / Missing[/red]")

    console.print(Panel(table, title="Vault Status"))

    # Exit code 2 if unhealthy (D-10)
    healthy = vault_reachable and not sealed and kv_ok and docker_running
    if not healthy:
        raise typer.Exit(2)


def vault_init() -> None:
    """Initialize Vault and write credentials to .env (idempotent)."""
    settings = Settings()
    initializer = VaultInitializer()
    client = VaultClient(settings, token=None)
    try:
        # Idempotency guard: abort if .env already has credentials (D-12)
        if not initializer.can_initialize():
            raise VaultAlreadyInitialized(
                "Vault credentials already in .env — re-initialization would overwrite them.",
                hint="Delete VAULT_ROOT_TOKEN and VAULT_UNSEAL_KEY from .env manually if you want to re-init.",
            )
        # is_initialized() guard — VAULT-04 requirement
        if client.is_initialized():
            raise VaultAlreadyInitialized(
                "Vault is already initialized.",
                hint="Use `vk login` to authenticate with the existing credentials.",
            )
        result = client.initialize(secret_shares=1, secret_threshold=1)
        root_token = result["root_token"]
        unseal_key = result["keys"][0]
        initializer.write_credentials(root_token=root_token, unseal_key=unseal_key)
        # Warning panel (D-13)
        console.print(
            Panel(
                "Credentials written to .env — DO NOT commit this file to git.",
                title="Vault Initialized",
                border_style="yellow",
            )
        )
        # Auto-unseal immediately after init
        client_with_token = VaultClient(settings, token=root_token)
        client_with_token.unseal(unseal_key)
        # Enable KV v2 mount
        try:
            client_with_token.raw.sys.enable_secrets_engine(
                backend_type="kv",
                path="kv",
                options={"version": "2"},
            )
            console.print("[green]KV v2 engine enabled at kv/[/green]")
        except Exception:
            # May already be mounted
            pass
        console.print("[green]Vault unsealed.[/green]")
    except VkError as err:
        print_error(err)
        raise typer.Exit(1)
    except Exception as e:
        handle_unexpected(e)


def login(
    token: str = typer.Option(
        None, "--token", "-t", help="Vault token (defaults to .env / env var)"
    ),
) -> None:
    """Authenticate and store token at ~/.vk/token."""
    import stat
    from pathlib import Path

    settings = Settings()
    effective = token or settings.effective_token()

    try:
        client = VaultClient(settings, token=effective)
        if not client.verify_token():
            raise VaultForbidden(
                "Token verification failed — the token is invalid or expired.",
                hint="run `vk login --token <token>` with a valid token from .env",
            )
        # Write token file (D-16, D-17)
        token_dir = Path.home() / ".vk"
        token_file = token_dir / "token"
        token_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        token_file.write_text(effective)
        token_file.chmod(0o600)
        console.print(f"[green]Token stored at {token_file}[/green]")
    except VkError as err:
        print_error(err)
        raise typer.Exit(1)
    except Exception as e:
        handle_unexpected(e)
