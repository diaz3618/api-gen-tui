"""Stub for vk policy command — full implementation in Plan 05-03."""

import typer


def policy(
    preset: str = typer.Argument(..., help="Preset: default|strong|hex|uuid|stripe"),
) -> None:
    """Emit a Vault HCL password policy from a generator preset."""
    typer.echo("vk policy: not yet implemented (Plan 05-03)")
    raise typer.Exit(1)
