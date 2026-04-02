from __future__ import annotations

from typing import Optional

import typer

from vk.errors import GeneratorError
from vk.generator.engine import GenerateOptions, generate as _generate
from vk.output import print_error


def generate(
    type: str = typer.Option(
        "hex",
        "--type",
        help="Key format: hex|base64|base64url|base32|alphanumeric|uuid4|ulid|url-safe|custom",
    ),
    length: int = typer.Option(32, "--length", help="Total output length (prefix+random+suffix)"),
    random_length: Optional[int] = typer.Option(
        None, "--random-length", help="Explicit random portion length (overrides --length calc)"
    ),
    prefix: str = typer.Option("", "--prefix", help="Fixed string prepended to key"),
    suffix: str = typer.Option("", "--suffix", help="Fixed string appended to key"),
    separator: str = typer.Option("_", "--separator", help="Separator char for --group"),
    group: Optional[int] = typer.Option(
        None, "--group", help="Split random portion into chunks of N"
    ),
    no_ambiguous: bool = typer.Option(False, "--no-ambiguous", help="Remove 0,O,1,l,I from output"),
    min_upper: int = typer.Option(0, "--min-upper", help="Minimum uppercase characters"),
    min_lower: int = typer.Option(0, "--min-lower", help="Minimum lowercase characters"),
    min_digits: int = typer.Option(0, "--min-digits", help="Minimum digit characters"),
    min_symbols: int = typer.Option(0, "--min-symbols", help="Minimum symbol characters"),
    upper: bool = typer.Option(False, "--upper", help="Force all uppercase"),
    lower: bool = typer.Option(False, "--lower", help="Force all lowercase"),
    entropy: bool = typer.Option(False, "--entropy", help="Print entropy estimate to stderr"),
    count: int = typer.Option(1, "--count", help="Number of keys to generate"),
    alphabet: Optional[str] = typer.Option(
        None, "--alphabet", help="Custom alphabet for --type custom"
    ),
) -> None:
    """Generate a cryptographically secure API key or token."""
    opts = GenerateOptions(
        format=type,
        length=length,
        random_length=random_length,
        prefix=prefix,
        suffix=suffix,
        separator=separator,
        group=group,
        no_ambiguous=no_ambiguous,
        min_upper=min_upper,
        min_lower=min_lower,
        min_digits=min_digits,
        min_symbols=min_symbols,
        upper=upper,
        lower=lower,
        entropy=entropy,
        count=count,
        alphabet=alphabet,
    )
    try:
        for _ in range(count):
            key = _generate(opts)
            typer.echo(key)
    except GeneratorError as e:
        print_error(e)
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
