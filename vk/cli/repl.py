from __future__ import annotations

import shlex

import click
import typer

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory

from vk.output import console, err_console

# D-03: Full list of vk subcommands for WordCompleter tab completion
# 'list' (not 'list-keys') matches the explicit command registration in cli/__init__.py
_VK_COMMANDS = [
    "generate",
    "store",
    "get",
    "list",
    "delete",
    "export",
    "up",
    "down",
    "status",
    "vault-init",
    "login",
    "policy",
]


def _dispatch(cmd, args: list[str]) -> bool:
    """Dispatch a parsed arg list to the typer command.

    Returns True to continue the REPL loop, False to exit.
    Catches click.UsageError and SystemExit — never lets them escape (D-02).
    Broad except Exception guard ensures hvac/transport errors don't crash the loop (UX-01).
    """
    if args[0] in ("exit", "quit"):
        return False  # D-04: exit/quit keywords terminate the REPL
    try:
        # standalone_mode=False: returns int on typer.Exit, raises click.UsageError on bad args
        # — does NOT call sys.exit() (D-02, pitfall 1)
        cmd.main(args, standalone_mode=False)
    except click.UsageError as e:
        err_console.print(f"[red]Error:[/red] {e.format_message()}")
    except SystemExit:
        pass  # Safety guard — standalone_mode=False should not raise this, but just in case
    except Exception as e:
        # Broad guard: hvac/transport exceptions from storage commands must not crash the REPL
        # (UX-01: REPL loop must continue after any command error)
        err_console.print(f"[red]Error:[/red] {e}")
    return True


def repl() -> None:
    """Launch the interactive vk REPL shell."""
    # Deferred import to avoid circular dependency (repl.py → cli/__init__.py → repl.py)
    from vk.cli import app
    import typer.main

    cmd = typer.main.get_command(app)
    session: PromptSession = PromptSession(
        history=InMemoryHistory(),  # D-05: InMemoryHistory ONLY — no disk history
        completer=WordCompleter(_VK_COMMANDS, ignore_case=True),  # D-03
        complete_while_typing=True,
    )

    # Agent discretion: minimal banner (CONTEXT.md §the agent's Discretion)
    console.print("[bold]vk[/bold] — type [dim]exit[/dim] to quit, [dim]Ctrl+D[/dim] to exit")

    while True:
        try:
            line: str = session.prompt("vk> ")  # D-01: prompt is exactly "vk> "
        except EOFError:
            break  # D-04: Ctrl+D exits REPL
        except KeyboardInterrupt:
            continue  # D-04: Ctrl+C cancels current input line only

        try:
            args = shlex.split(line.strip())
        except ValueError as e:
            # Pitfall 5: malformed shlex (unclosed quotes) — print error, continue loop
            err_console.print(f"[red]Parse error:[/red] {e}")
            continue

        if not args:
            continue  # empty line — skip

        if not _dispatch(cmd, args):
            break  # _dispatch returned False → exit keyword was used
