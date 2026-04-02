"""Tests for vk policy command (UX-05) and UX-03/UX-04 verification."""

import pytest
from typer.testing import CliRunner

from vk.cli import app

# RED: _build_hcl and _PRESETS don't exist in the full implementation yet
from vk.cli.policy import _PRESETS, _build_hcl


runner = CliRunner()


class TestPolicyPresets:
    """All 5 presets emit valid Vault HCL."""

    @pytest.mark.parametrize(
        "preset,expected_length",
        [
            ("default", "32"),
            ("strong", "32"),
            ("hex", "64"),
            ("uuid", "36"),
            ("stripe", "32"),
        ],
    )
    def test_preset_emits_valid_hcl(self, preset, expected_length):
        result = runner.invoke(app, ["policy", preset])
        assert result.exit_code == 0, f"policy {preset} failed: {result.output}"
        assert f"length = {expected_length}" in result.output
        assert 'rule "charset"' in result.output
        assert "charset = " in result.output

    def test_strong_has_four_charset_rules(self):
        result = runner.invoke(app, ["policy", "strong"])
        assert result.exit_code == 0
        rule_count = result.output.count('rule "charset"')
        assert rule_count == 4, f"Expected 4 rules, got {rule_count}"

    def test_strong_has_symbol_chars(self):
        result = runner.invoke(app, ["policy", "strong"])
        assert result.exit_code == 0
        # Symbol charset must be in the output
        assert "!@#$%^&*" in result.output

    def test_strong_min_chars_for_lower_is_4(self):
        result = runner.invoke(app, ["policy", "strong"])
        assert result.exit_code == 0
        # After the lowercase charset line, min-chars = 4 must appear
        assert "min-chars = 4" in result.output

    def test_strong_min_chars_for_symbols_is_2(self):
        result = runner.invoke(app, ["policy", "strong"])
        assert result.exit_code == 0
        assert "min-chars = 2" in result.output

    def test_hex_charset_is_lowercase_hex(self):
        result = runner.invoke(app, ["policy", "hex"])
        assert result.exit_code == 0
        assert "0123456789abcdef" in result.output
        # Must NOT include uppercase (pure lowercase hex)
        assert "ABCDEF" not in result.output

    def test_uuid_has_approximation_comment(self):
        """UUID preset must include a comment about Vault's approximation limitation."""
        result = runner.invoke(app, ["policy", "uuid"])
        assert result.exit_code == 0
        # The comment documents that Vault cannot enforce true UUID4 format (pitfall 6)
        assert "approximation" in result.output.lower()

    def test_uuid_charset_includes_hyphen(self):
        result = runner.invoke(app, ["policy", "uuid"])
        assert result.exit_code == 0
        # UUID charset must include the hyphen character
        assert "-" in result.output

    def test_stripe_has_alnum_charset(self):
        result = runner.invoke(app, ["policy", "stripe"])
        assert result.exit_code == 0
        # Full alphanumeric charset
        assert "abcdefghijklmnopqrstuvwxyz" in result.output
        assert "ABCDEFGHIJKLMNOPQRSTUVWXYZ" in result.output
        assert "0123456789" in result.output

    def test_output_is_plain_stdout_no_rich_markup(self):
        """HCL output must be machine-readable — no Rich markup sequences (D-16)."""
        result = runner.invoke(app, ["policy", "default"])
        assert result.exit_code == 0
        # Rich markup tags must not appear in stdout
        assert "[red]" not in result.output
        assert "[bold]" not in result.output
        assert "[green]" not in result.output


class TestPolicyErrorHandling:
    """Unknown preset triggers GeneratorError → print_error → exit 1."""

    def test_unknown_preset_exits_1(self):
        result = runner.invoke(app, ["policy", "badpreset"])
        assert result.exit_code == 1

    def test_unknown_preset_shows_error_message(self):
        result = runner.invoke(app, ["policy", "notapreset"])
        # print_error() writes to stderr via err_console; CliRunner captures both
        combined = (result.output or "") + (result.stderr or "")
        assert "Unknown policy preset" in combined

    def test_unknown_preset_shows_valid_presets_hint(self):
        result = runner.invoke(app, ["policy", "wrongname"])
        combined = (result.output or "") + (result.stderr or "")
        # Hint should list valid presets so user knows what's available
        assert any(p in combined for p in ["default", "strong", "hex"])


class TestBuildHclHelper:
    """Unit tests for _build_hcl() in isolation."""

    def test_build_hcl_basic(self):
        hcl = _build_hcl(32, [("abc", 1)])
        assert "length = 32" in hcl
        assert 'rule "charset"' in hcl
        assert 'charset = "abc"' in hcl
        assert "min-chars = 1" in hcl

    def test_build_hcl_multiple_rules(self):
        hcl = _build_hcl(16, [("abc", 2), ("XYZ", 3)])
        assert hcl.count('rule "charset"') == 2
        assert "min-chars = 2" in hcl
        assert "min-chars = 3" in hcl

    def test_build_hcl_with_comment(self):
        hcl = _build_hcl(36, [("abc", 1)], comment="Test comment")
        assert "# Test comment" in hcl
        # Comment must appear before length declaration
        assert hcl.index("# Test comment") < hcl.index("length = 36")

    def test_build_hcl_no_comment_omits_hash(self):
        hcl = _build_hcl(32, [("abc", 1)])
        assert "#" not in hcl


class TestUX03AndUX04Verification:
    """Smoke tests: shell completion (UX-04) and rich output (UX-03)."""

    def test_install_completion_flag_in_help(self):
        """UX-04: typer auto-provides --install-completion; verify it's present."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "--install-completion" in result.output

    def test_show_completion_flag_in_help(self):
        """typer also provides --show-completion as a companion flag."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "--show-completion" in result.output

    def test_generate_stdout_is_plain_hex(self):
        """UX-03: generate stdout must remain pipe-clean plain text (D-09)."""
        result = runner.invoke(app, ["generate", "--type", "hex", "--length", "32"])
        assert result.exit_code == 0
        import re

        lines = result.output.strip().splitlines()
        hex_lines = [line for line in lines if line and re.fullmatch(r"[0-9a-f]+", line)]
        assert len(hex_lines) == 1
        key = hex_lines[0]
        # Must be valid hex, no Rich markup, no decorators
        assert re.fullmatch(r"[0-9a-f]+", key), f"Key is not plain hex: {key!r}"
        assert "[" not in key  # no Rich markup in stdout
