"""Tests for vk repl command and REPL dispatch logic (UX-01)."""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

# RED: these imports do not exist yet — all tests will fail
from vk.cli.repl import _dispatch, _VK_COMMANDS
from vk.cli import app
import typer.main


runner = CliRunner()


def _get_cmd():
    """Helper: get the click Command from the typer app."""
    return typer.main.get_command(app)


class TestVkCommandsList:
    """Verify _VK_COMMANDS is correct for WordCompleter (D-03)."""

    def test_commands_list_has_list_not_list_keys(self):
        assert "list" in _VK_COMMANDS
        assert "list-keys" not in _VK_COMMANDS

    def test_commands_list_is_complete(self):
        expected = {
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
        }
        assert set(_VK_COMMANDS) == expected

    def test_commands_list_length(self):
        assert len(_VK_COMMANDS) == 12


class TestDispatchHelper:
    """Unit tests for _dispatch() without requiring a TTY."""

    def test_dispatch_exit_returns_false(self):
        cmd = _get_cmd()
        result = _dispatch(cmd, ["exit"])
        assert result is False

    def test_dispatch_quit_returns_false(self):
        cmd = _get_cmd()
        result = _dispatch(cmd, ["quit"])
        assert result is False

    def test_dispatch_generate_help_returns_true(self):
        """Valid command with --help should return True (loop continues)."""
        cmd = _get_cmd()
        result = _dispatch(cmd, ["generate", "--help"])
        assert result is True

    def test_dispatch_usage_error_returns_true(self):
        """Bad arguments raise UsageError — _dispatch catches it and returns True."""
        cmd = _get_cmd()
        # Unknown flag triggers UsageError
        result = _dispatch(cmd, ["generate", "--unknown-flag-xyz"])
        assert result is True  # loop continues; not crashed

    def test_dispatch_does_not_raise_system_exit(self):
        """standalone_mode=False must not let SystemExit escape."""
        cmd = _get_cmd()
        # --help in standalone_mode=True would sys.exit(0); with False it must not
        try:
            _dispatch(cmd, ["generate", "--help"])
        except SystemExit:
            pytest.fail("_dispatch() must not let SystemExit escape")


class TestCommandRegistration:
    """Verify __init__.py registers commands with correct names."""

    def test_list_command_registered_as_list(self):
        """'list' must be a valid vk command (not 'list-keys')."""
        result = runner.invoke(app, ["list", "--help"])
        # list should be found, not "No such command"
        assert "No such command" not in (result.output or "")

    def test_list_keys_is_not_a_valid_command(self):
        """'list-keys' must NOT be registered — it was the old broken name."""
        result = runner.invoke(app, ["list-keys", "--help"])
        # Should get "No such command 'list-keys'" exit, not a help page
        assert result.exit_code != 0

    def test_repl_command_registered(self):
        """'repl' must be a valid top-level vk command."""
        result = runner.invoke(app, ["repl", "--help"])
        assert "No such command" not in (result.output or "")

    def test_policy_command_registered(self):
        """'policy' must be a valid top-level vk command (registered in same __init__ change)."""
        result = runner.invoke(app, ["policy", "--help"])
        assert "No such command" not in (result.output or "")


class TestDispatchBroadExceptionGuard:
    """FINDING-2 fix: _dispatch() must catch unexpected exceptions and continue the REPL loop."""

    def test_dispatch_unexpected_exception_returns_true(self):
        """An unexpected exception (e.g. hvac.Forbidden) must NOT crash the REPL loop."""
        from unittest.mock import patch, MagicMock
        import hvac.exceptions

        cmd = _get_cmd()
        # Patch the inner cmd.main to raise hvac.Forbidden (simulates FINDING-2 scenario)
        with patch.object(cmd, "main", side_effect=hvac.exceptions.Forbidden("denied")):
            result = _dispatch(cmd, ["store", "kv/x", "val"])
        # REPL loop must continue (returns True), not crash
        assert result is True

    def test_dispatch_connection_error_returns_true(self):
        """A requests.ConnectionError must NOT crash the REPL loop."""
        import requests.exceptions

        cmd = _get_cmd()
        with patch.object(cmd, "main", side_effect=requests.exceptions.ConnectionError("down")):
            result = _dispatch(cmd, ["get", "kv/x"])
        assert result is True
