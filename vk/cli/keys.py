from typing import Optional
import typer


def generate(
    type: str = typer.Option("hex", "--type", help="Key format"),
    length: int = typer.Option(32, "--length", help="Key length"),
) -> None:
    """Generate a cryptographically secure API key."""
    typer.echo("vk generate: not yet implemented (Phase 3)")
    raise typer.Exit(1)


def store(path: str, value: str) -> None:
    """Store an externally supplied token in Vault at PATH."""
    typer.echo("vk store: not yet implemented (Phase 4)")
    raise typer.Exit(1)


def get(path: str, reveal: bool = typer.Option(False, "--reveal")) -> None:
    """Retrieve a secret from Vault at PATH."""
    typer.echo("vk get: not yet implemented (Phase 4)")
    raise typer.Exit(1)


def list_keys(path: str = typer.Argument("")) -> None:
    """List secrets under a Vault path."""
    typer.echo("vk list: not yet implemented (Phase 4)")
    raise typer.Exit(1)


def delete(path: str, permanent: bool = typer.Option(False, "--permanent")) -> None:
    """Delete a secret at PATH (soft delete by default)."""
    typer.echo("vk delete: not yet implemented (Phase 4)")
    raise typer.Exit(1)


def export(
    path: str,
    format: str = typer.Option("json", "--format", help="Output format: json or dotenv"),
) -> None:
    """Export secrets from Vault as JSON or dotenv format."""
    typer.echo("vk export: not yet implemented (Phase 4)")
    raise typer.Exit(1)
