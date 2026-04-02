"""CLI integration tests for vk export command (04-03)."""

from __future__ import annotations

import json
import pytest
from typer.testing import CliRunner
from unittest.mock import MagicMock, patch, call

from vk.cli import app
from vk.errors import VaultNotRunning

runner = CliRunner()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_secret(value: str = "sk_abc123", fmt: str = "hex") -> dict:
    return {
        "value": value,
        "created_at": "2026-04-01T00:00:00Z",
        "format": fmt,
        "prefix": "",
        "total_length": len(value),
        "options": {},
        "notes": "",
        "tags": [],
    }


# ---------------------------------------------------------------------------
# JSON format tests
# ---------------------------------------------------------------------------


def test_export_json_outputs_valid_json():
    mock_kv = MagicMock()
    # list returns one leaf key
    mock_kv.list.return_value = ["prod"]
    mock_kv.get.return_value = _make_secret("sk_abc123")
    with (
        patch("vk.cli.keys.KVStore", return_value=mock_kv),
        patch("vk.cli.keys.VaultClient"),
        patch("vk.cli.keys.Settings"),
    ):
        result = runner.invoke(app, ["export", "kv/api-keys", "--format", "json"])
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert isinstance(parsed, dict)


def test_export_json_contains_full_metadata():
    mock_kv = MagicMock()
    mock_kv.list.return_value = ["prod"]
    mock_kv.get.return_value = _make_secret("sk_abc123")
    with (
        patch("vk.cli.keys.KVStore", return_value=mock_kv),
        patch("vk.cli.keys.VaultClient"),
        patch("vk.cli.keys.Settings"),
    ):
        result = runner.invoke(app, ["export", "kv/api-keys", "--format", "json"])
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    # Find any leaf secret value
    first_secret = next(iter(parsed.values()))
    assert "value" in first_secret
    assert "format" in first_secret
    assert "created_at" in first_secret
    assert "total_length" in first_secret
    assert "options" in first_secret
    assert "notes" in first_secret
    assert "tags" in first_secret


def test_export_json_default_format():
    """No --format flag should default to json."""
    mock_kv = MagicMock()
    mock_kv.list.return_value = ["prod"]
    mock_kv.get.return_value = _make_secret("sk_abc123")
    with (
        patch("vk.cli.keys.KVStore", return_value=mock_kv),
        patch("vk.cli.keys.VaultClient"),
        patch("vk.cli.keys.Settings"),
    ):
        result = runner.invoke(app, ["export", "kv/api-keys"])
    assert result.exit_code == 0
    # Should be valid JSON
    parsed = json.loads(result.output)
    assert isinstance(parsed, dict)


# ---------------------------------------------------------------------------
# dotenv format tests
# ---------------------------------------------------------------------------


def test_export_dotenv_outputs_key_value_only():
    mock_kv = MagicMock()
    mock_kv.list.return_value = ["prod"]
    mock_kv.get.return_value = _make_secret("sk_abc123")
    with (
        patch("vk.cli.keys.KVStore", return_value=mock_kv),
        patch("vk.cli.keys.VaultClient"),
        patch("vk.cli.keys.Settings"),
    ):
        result = runner.invoke(app, ["export", "kv/api-keys", "--format", "dotenv"])
    assert result.exit_code == 0
    # Output should be KEY=value format, no metadata
    assert "PROD=sk_abc123" in result.output
    assert "created_at" not in result.output
    assert "format" not in result.output


def test_export_dotenv_key_name_non_alphanum_to_underscore():
    """Path segment 'api-key-prod' → key name 'API_KEY_PROD'."""
    mock_kv = MagicMock()
    mock_kv.list.return_value = ["api-key-prod"]
    mock_kv.get.return_value = _make_secret("myvalue")
    with (
        patch("vk.cli.keys.KVStore", return_value=mock_kv),
        patch("vk.cli.keys.VaultClient"),
        patch("vk.cli.keys.Settings"),
    ):
        result = runner.invoke(app, ["export", "kv/api-keys/my-service", "--format", "dotenv"])
    assert result.exit_code == 0
    assert "API_KEY_PROD=myvalue" in result.output


# ---------------------------------------------------------------------------
# Recursion tests
# ---------------------------------------------------------------------------


def test_export_recurses_into_sub_paths():
    """Sub-paths (trailing /) should be recursed into to find leaf secrets."""
    mock_kv = MagicMock()

    def list_side_effect(path):
        if path == "kv/api-keys":
            return ["stripe/"]
        elif "stripe" in path:
            return ["prod"]
        return []

    def get_side_effect(path):
        return _make_secret("sk_stripe_prod")

    mock_kv.list.side_effect = list_side_effect
    mock_kv.get.side_effect = get_side_effect

    with (
        patch("vk.cli.keys.KVStore", return_value=mock_kv),
        patch("vk.cli.keys.VaultClient"),
        patch("vk.cli.keys.Settings"),
    ):
        result = runner.invoke(app, ["export", "kv/api-keys", "--format", "json"])
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    # Should have collected the leaf secret under stripe/prod
    assert any("prod" in k for k in parsed.keys())


# ---------------------------------------------------------------------------
# Empty/error cases
# ---------------------------------------------------------------------------


def test_export_empty_path_shows_no_secrets_found():
    mock_kv = MagicMock()
    mock_kv.list.return_value = []
    with (
        patch("vk.cli.keys.KVStore", return_value=mock_kv),
        patch("vk.cli.keys.VaultClient"),
        patch("vk.cli.keys.Settings"),
    ):
        result = runner.invoke(app, ["export", "kv/api-keys"])
    assert result.exit_code == 0
    assert "No secrets found" in result.output


def test_export_vault_error_exits_1():
    mock_kv = MagicMock()
    mock_kv.list.side_effect = VaultNotRunning()
    with (
        patch("vk.cli.keys.KVStore", return_value=mock_kv),
        patch("vk.cli.keys.VaultClient"),
        patch("vk.cli.keys.Settings"),
    ):
        result = runner.invoke(app, ["export", "kv/api-keys"])
    assert result.exit_code == 1


# ---------------------------------------------------------------------------
# Invalid format
# ---------------------------------------------------------------------------


def test_export_unknown_format_exits_1():
    mock_kv = MagicMock()
    with (
        patch("vk.cli.keys.KVStore", return_value=mock_kv),
        patch("vk.cli.keys.VaultClient"),
        patch("vk.cli.keys.Settings"),
    ):
        result = runner.invoke(app, ["export", "kv/api-keys", "--format", "yaml"])
    assert result.exit_code == 1
    assert "yaml" in result.output or "yaml" in (result.stderr if hasattr(result, "stderr") else "")


# ---------------------------------------------------------------------------
# TD-3 fix: _collect_secrets() warns on unreadable secrets (not silent)
# ---------------------------------------------------------------------------


def test_collect_secrets_warns_on_vault_error(capsys):
    """TD-3 fix: unreadable secrets produce a stderr warning, not silent skip."""
    from vk.cli.keys import _collect_secrets
    from vk.errors import VaultInvalidPath
    from unittest.mock import MagicMock

    mock_kv = MagicMock()
    mock_kv.list.return_value = ["broken-key"]
    mock_kv.get.side_effect = VaultInvalidPath("kv/api-keys/broken-key")

    accumulated = {}
    _collect_secrets(mock_kv, "kv/api-keys", accumulated)

    # Secret was not added to accumulated
    assert len(accumulated) == 0

    # Warning was emitted to stderr
    captured = capsys.readouterr()
    assert "warning" in captured.err.lower() or "warning" in captured.out.lower()


def test_collect_secrets_warns_on_unexpected_exception(capsys):
    """TD-3 fix: unexpected exceptions also produce a stderr warning, not silent skip."""
    from vk.cli.keys import _collect_secrets
    from unittest.mock import MagicMock

    mock_kv = MagicMock()
    mock_kv.list.return_value = ["flaky-key"]
    mock_kv.get.side_effect = RuntimeError("unexpected")

    accumulated = {}
    _collect_secrets(mock_kv, "kv/api-keys", accumulated)

    assert len(accumulated) == 0
    captured = capsys.readouterr()
    assert "warning" in captured.err.lower() or "warning" in captured.out.lower()


def test_collect_secrets_continues_after_error():
    """_collect_secrets() must continue processing remaining keys after one fails."""
    from vk.cli.keys import _collect_secrets
    from vk.errors import VaultInvalidPath
    from unittest.mock import MagicMock

    mock_kv = MagicMock()
    mock_kv.list.return_value = ["broken-key", "good-key"]
    good_secret = _make_secret("sk_good")

    def get_side_effect(path):
        if "broken" in path:
            raise VaultInvalidPath(path)
        return good_secret

    mock_kv.get.side_effect = get_side_effect

    accumulated = {}
    _collect_secrets(mock_kv, "kv/api-keys", accumulated)

    # Only the good key was collected
    assert len(accumulated) == 1
    assert any("good-key" in k for k in accumulated.keys())
