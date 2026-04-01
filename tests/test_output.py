import sys
from io import StringIO

import pytest
from rich.console import Console

from vk.errors import (
    VaultAlreadyInitialized,
    VaultForbidden,
    VaultInvalidPath,
    VaultNotRunning,
    VaultSealed,
    VkError,
)


def capture_error_output(err) -> str:
    """Render print_error output to a string using a test console."""
    from vk import output as output_module

    buf = StringIO()
    test_console = Console(file=buf, highlight=False, markup=True)
    original = output_module.err_console
    output_module.err_console = test_console
    try:
        from vk.output import print_error

        print_error(err)
    finally:
        output_module.err_console = original
    return buf.getvalue()


def test_print_error_renders_rich_panel_with_message_and_hint():
    """Test 1: print_error renders a panel with red border, 'Error' title, message body, dimmed hint."""
    err = VaultNotRunning("Vault unreachable", hint="run `vk up`")
    output = capture_error_output(err)
    assert "Vault unreachable" in output
    assert "run `vk up`" in output
    assert "Error" in output


def test_print_error_no_hint_when_empty():
    """Test 2: print_error with empty hint renders panel WITHOUT a hint line."""
    err = VkError("msg")
    output = capture_error_output(err)
    assert "msg" in output
    # The → character should not appear when hint is empty
    assert "→" not in output


def test_handle_unexpected_exits_with_1(capsys, monkeypatch):
    """Test 3: Non-VkError caught → 'Unexpected error: {str(e)}' on stderr, sys.exit(1)."""
    from vk.output import handle_unexpected

    exit_calls = []
    monkeypatch.setattr(sys, "exit", lambda code: exit_calls.append(code))
    handle_unexpected(ValueError("something went wrong"))
    captured = capsys.readouterr()
    assert "Unexpected error" in captured.err
    assert "something went wrong" in captured.err
    assert exit_calls == [1]


def test_all_vkerror_subclasses_importable():
    """Test 4: All VkError subclasses are importable from vk.errors."""
    # Already imported at top — just verify they exist
    assert issubclass(VaultNotRunning, VkError)
    assert issubclass(VaultSealed, VkError)
    assert issubclass(VaultForbidden, VkError)
    assert issubclass(VaultInvalidPath, VkError)
    assert issubclass(VaultAlreadyInitialized, VkError)
