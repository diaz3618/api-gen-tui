from __future__ import annotations

import dataclasses
from typing import Optional

import pyperclip
import typer
from rich.panel import Panel

from vk.config import Settings
from vk.errors import GeneratorError, VkError
from vk.generator.engine import GenerateOptions, generate as _generate
from vk.output import console, err_console, print_error
from vk.vault.client import VaultClient
from vk.vault.kv import KVStore

MASK = "████████"


def _copy_to_clipboard(key: str) -> None:
    """Copy key to clipboard; silently swallow all exceptions on headless environments (UX-02)."""
    try:
        pyperclip.copy(key)
        err_console.print("[dim]copied to clipboard[/dim]")  # stderr only (D-06, D-11)
    except Exception:
        pass  # Silent failure on headless/CI/SSH (D-06, UX-02) — no output, no crash


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
    store_path: Optional[str] = typer.Option(
        None, "--store", help="Vault path to store the generated key (e.g. kv/api-keys/stripe/prod)"
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
        last_key: str | None = None
        generated_keys: list[str] = []
        for _ in range(count):
            key = _generate(opts)
            typer.echo(key)
            last_key = key
            generated_keys.append(key)
    except GeneratorError as e:
        print_error(e)
        raise typer.Exit(1)

    # Clipboard copy of last key only (D-07, UX-02) — outside the try block
    if last_key is not None:
        _copy_to_clipboard(last_key)

    if store_path:
        try:
            settings = Settings.load()
            client = VaultClient(settings)
            kv = KVStore(client=client, settings=settings)
            if count == 1:
                kv.put(
                    store_path,
                    generated_keys[0],
                    format=opts.format,
                    prefix=opts.prefix,
                    options=dataclasses.asdict(opts),
                )
            else:
                for i, k in enumerate(generated_keys, start=1):
                    kv.put(
                        f"{store_path}-{i}",
                        k,
                        format=opts.format,
                        prefix=opts.prefix,
                        options=dataclasses.asdict(opts),
                    )
        except VkError as e:
            print_error(e)
            # Do NOT raise typer.Exit(1) — key was already printed, exit 0


def store(
    path: str = typer.Argument(..., help="Vault path e.g. kv/api-keys/stripe/prod"),
    value: str = typer.Argument(..., help="Secret value to store"),
    notes: str = typer.Option("", "--notes", help="Optional annotation"),
    tags: str = typer.Option("", "--tags", help="Comma-separated tags"),
) -> None:
    """Store an externally supplied token in Vault at PATH."""
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    try:
        settings = Settings.load()
        client = VaultClient(settings)
        kv = KVStore(client=client, settings=settings)
        kv.put(path, value, format="external", options={}, notes=notes, tags=tag_list)
        console.print(f"[green]Stored[/green] at {path}")
    except VkError as e:
        print_error(e)
        raise typer.Exit(1)


def get(
    path: str = typer.Argument(..., help="Vault path to retrieve"),
    reveal: bool = typer.Option(False, "--reveal", help="Show plaintext value"),
) -> None:
    """Retrieve a secret from Vault at PATH (masked by default)."""
    try:
        settings = Settings.load()
        client = VaultClient(settings)
        kv = KVStore(client=client, settings=settings)
        secret = kv.get(path)
        display_value = secret["value"] if reveal else MASK
        console.print(
            Panel(
                f"[bold]Value:[/bold] {display_value}\n"
                f"[dim]Format:[/dim] {secret.get('format', 'unknown')}\n"
                f"[dim]Created:[/dim] {secret.get('created_at', 'unknown')}\n"
                f"[dim]Length:[/dim] {secret.get('total_length', '?')}",
                title=path,
                border_style="blue",
            )
        )
    except VkError as e:
        print_error(e)
        raise typer.Exit(1)


def list_keys(
    path: str = typer.Argument("", help="Vault path prefix (default: kv/api-keys)"),
) -> None:
    """List secrets under a Vault path."""
    from rich.tree import Tree

    try:
        settings = Settings.load()
        client = VaultClient(settings)
        kv = KVStore(client=client, settings=settings)
        effective_path = path or f"{settings.vault_kv_mount}/{settings.vk_default_path_prefix}"
        keys = kv.list(effective_path)
        if not keys:
            console.print(f"No keys found at [dim]{effective_path}[/dim]")
            return
        tree = Tree(f"[bold]{effective_path}[/bold]")
        for key in keys:
            tree.add(f"[cyan]{key}[/cyan]")
        console.print(tree)
    except VkError as e:
        print_error(e)
        raise typer.Exit(1)


def delete(
    path: str = typer.Argument(..., help="Vault path to delete"),
    permanent: bool = typer.Option(False, "--permanent", help="Permanently destroy all versions"),
) -> None:
    """Delete a secret at PATH (soft delete by default; --permanent is irrecoverable)."""
    try:
        settings = Settings.load()
        client = VaultClient(settings)
        kv = KVStore(client=client, settings=settings)
        if permanent:
            console.print(
                Panel(
                    f"[bold yellow]WARNING:[/bold yellow] This will permanently destroy all versions of:\n{path}\nThis cannot be undone.",
                    border_style="yellow",
                )
            )
        kv.delete(path, permanent=permanent)
        action = "permanently destroyed" if permanent else "soft-deleted"
        console.print(f"[green]{action.capitalize()}[/green]: {path}")
    except VkError as e:
        print_error(e)
        raise typer.Exit(1)


def export(
    path: str = typer.Argument(..., help="Vault path prefix to export from"),
    format: str = typer.Option("json", "--format", help="Output format: json or dotenv"),
) -> None:
    """Export secrets from Vault as JSON or dotenv format."""
    import json
    import re

    if format not in ("json", "dotenv"):
        typer.echo(f"Unknown format: {format}", err=True)
        raise typer.Exit(1)

    try:
        settings = Settings.load()
        client = VaultClient(settings)
        kv = KVStore(client=client, settings=settings)

        secrets: dict = {}
        _collect_secrets(kv, path, secrets)

        if not secrets:
            console.print(f"No secrets found at [dim]{path}[/dim]")
            return

        if format == "json":
            typer.echo(json.dumps(secrets, indent=2))
        elif format == "dotenv":
            for secret_path, secret in secrets.items():
                last_segment = secret_path.rstrip("/").split("/")[-1]
                key_name = re.sub(r"[^A-Za-z0-9]", "_", last_segment).upper()
                typer.echo(f"{key_name}={secret['value']}")

    except VkError as e:
        print_error(e)
        raise typer.Exit(1)


def _collect_secrets(kv: KVStore, base_path: str, accumulated: dict) -> None:
    """Recursively collect all leaf secrets under base_path into accumulated dict.

    Unreadable secrets are skipped with a warning to stderr rather than silently dropped.
    """
    keys = kv.list(base_path)
    for key in keys:
        child_path = base_path.rstrip("/") + "/" + key.rstrip("/")
        if key.endswith("/"):
            _collect_secrets(kv, child_path, accumulated)
        else:
            try:
                secret = kv.get(child_path)
                accumulated[child_path] = secret
            except VkError as e:
                err_console.print(f"[yellow]warning:[/yellow] skipping {child_path}: {e.message}")
            except Exception as e:
                err_console.print(f"[yellow]warning:[/yellow] skipping {child_path}: {e}")
