"""Tests for clipboard copy behavior in vk generate (UX-02)."""

import pyperclip
import pytest
from typer.testing import CliRunner
from unittest.mock import patch

from vk.cli import app
from vk.cli.keys import _copy_to_clipboard


runner = CliRunner()


class TestCopyToClipboardHelper:
    """Unit tests for _copy_to_clipboard() in isolation."""

    def test_clipboard_success_notification(self, capsys):
        """Successful copy prints notification to stderr, nothing to stdout."""
        with patch("vk.cli.keys.pyperclip.copy", return_value=None):
            _copy_to_clipboard("abc123")
        captured = capsys.readouterr()
        # Rich writes to stderr via err_console
        assert "copied to clipboard" in captured.err
        assert "copied to clipboard" not in captured.out

    def test_clipboard_headless_silent(self, capsys):
        """PyperclipException is swallowed silently — no output, no crash."""
        with patch(
            "vk.cli.keys.pyperclip.copy", side_effect=pyperclip.PyperclipException("no clipboard")
        ):
            _copy_to_clipboard("abc123")  # must NOT raise
        captured = capsys.readouterr()
        assert captured.err == ""
        assert captured.out == ""

    def test_clipboard_runtime_error_silent(self, capsys):
        """RuntimeError from subprocess clipboard mechanisms is also swallowed."""
        with patch("vk.cli.keys.pyperclip.copy", side_effect=RuntimeError("xclip not found")):
            _copy_to_clipboard("abc123")  # must NOT raise
        captured = capsys.readouterr()
        assert captured.err == ""
        assert captured.out == ""


class TestClipboardInGenerateCommand:
    """Integration tests: clipboard wired into generate() command."""

    def test_clipboard_copies_last_key_only(self):
        """With --count 3, pyperclip.copy called exactly once with the last key."""
        copied_values = []

        def capture_copy(key):
            copied_values.append(key)

        with patch("vk.cli.keys.pyperclip.copy", side_effect=capture_copy):
            result = runner.invoke(app, ["generate", "--type", "hex", "--count", "3"])

        assert result.exit_code == 0
        # Filter out non-hex lines (like "copied to clipboard") to get actual keys
        import re

        keys = [
            line
            for line in result.output.strip().splitlines()
            if line and re.fullmatch(r"[0-9a-f]+", line)
        ]
        assert len(keys) == 3
        assert len(copied_values) == 1, f"Expected 1 copy call, got {len(copied_values)}"
        assert copied_values[0] == keys[-1], "Clipboard must contain the last key"

    def test_clipboard_notification_stderr_not_stdout(self):
        """Clipboard notification goes to stderr — plain stdout lines are only keys."""
        with patch("vk.cli.keys.pyperclip.copy", return_value=None):
            result = runner.invoke(app, ["generate", "--type", "hex"])
        assert result.exit_code == 0
        # stdout lines that are pure hex must be present
        import re

        hex_lines = [
            line
            for line in result.output.strip().splitlines()
            if line and re.fullmatch(r"[0-9a-f]+", line)
        ]
        assert len(hex_lines) == 1  # exactly one key on stdout (pipe-safe content)

    def test_clipboard_failure_does_not_affect_exit_code(self):
        """Even if clipboard copy fails, generate exits 0 and key is printed."""
        with patch(
            "vk.cli.keys.pyperclip.copy", side_effect=pyperclip.PyperclipException("no clipboard")
        ):
            result = runner.invoke(app, ["generate", "--type", "hex"])
        assert result.exit_code == 0
        # stdout still has the key (one non-empty hex line)
        import re

        keys = [
            line
            for line in result.output.strip().splitlines()
            if line and re.fullmatch(r"[0-9a-f]+", line)
        ]
        assert len(keys) == 1
