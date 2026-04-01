import typer
from vk.config import Settings
from vk.errors import VkError
from vk.output import console, err_console


def up() -> None:
    """Start the Vault Docker Compose stack and wait for readiness."""
    typer.echo("vk up: not yet implemented (Phase 2)")
    raise typer.Exit(1)


def down() -> None:
    """Stop the Vault Docker Compose stack."""
    typer.echo("vk down: not yet implemented (Phase 2)")
    raise typer.Exit(1)


def status() -> None:
    """Show Vault health, seal state, and Docker container status."""
    typer.echo("vk status: not yet implemented (Phase 2)")
    raise typer.Exit(1)


def vault_init() -> None:
    """Initialize Vault and write unseal key + root token to .env."""
    typer.echo("vk vault-init: not yet implemented (Phase 2)")
    raise typer.Exit(1)


def login(
    token: str = typer.Option(
        "", "--token", "-t", help="Vault token (defaults to VAULT_TOKEN env var)"
    ),
) -> None:
    """Authenticate with Vault and store token at ~/.vk/token."""
    typer.echo("vk login: not yet implemented (Phase 2)")
    raise typer.Exit(1)
