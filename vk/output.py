from __future__ import annotations

import sys

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()
err_console = Console(stderr=True)


def print_error(err: "VkError") -> None:  # noqa: F821
    """Render a VkError as a Rich Panel with red border, 'Error' title, and optional hint."""
    from vk.errors import VkError

    body = Text(err.message)
    if err.hint:
        body.append(f"\n→ {err.hint}", style="dim")
    err_console.print(Panel(body, title="Error", border_style="red"))


def handle_unexpected(e: Exception) -> None:
    """Print an unexpected error to stderr and exit with code 1."""
    print(f"Unexpected error: {e}", file=sys.stderr)
    sys.exit(1)
