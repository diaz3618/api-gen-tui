"""CLI integration tests for store, get, list, delete commands (04-02)."""

from __future__ import annotations

import pytest
from typer.testing import CliRunner
from unittest.mock import MagicMock, patch

from vk.cli import app
from vk.errors import VaultNotRunning, VaultInvalidPath

runner = CliRunner()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_secret(value: str = "sk_abc123") -> dict:
    return {
        "value": value,
        "created_at": "2026-04-01T00:00:00Z",
        "format": "hex",
        "prefix": "sk_",
        "total_length": len(value),
        "options": {},
        "notes": "",
        "tags": [],
    }


def _patch_kv(mock_kv_instance):
    """Return a context manager that patches KVStore, VaultClient, and Settings."""
    return (
        patch("vk.cli.keys.KVStore", return_value=mock_kv_instance),
        patch("vk.cli.keys.VaultClient"),
        patch("vk.cli.keys.Settings"),
    )


# ---------------------------------------------------------------------------
# generate --store tests
# ---------------------------------------------------------------------------


def test_generate_store_calls_kv_put():
    mock_kv = MagicMock()
    with (
        patch("vk.cli.keys.KVStore", return_value=mock_kv),
        patch("vk.cli.keys.VaultClient"),
        patch("vk.cli.keys.Settings"),
    ):
        result = runner.invoke(
            app, ["generate", "--type", "hex", "--store", "kv/api-keys/stripe/prod"]
        )
    assert result.exit_code == 0
    mock_kv.put.assert_called_once()


def test_generate_store_prints_key_before_storing():
    """Key must appear in stdout even when store is called."""
    mock_kv = MagicMock()
    with (
        patch("vk.cli.keys.KVStore", return_value=mock_kv),
        patch("vk.cli.keys.VaultClient"),
        patch("vk.cli.keys.Settings"),
    ):
        result = runner.invoke(
            app, ["generate", "--type", "hex", "--store", "kv/api-keys/stripe/prod"]
        )
    assert result.exit_code == 0
    # Output should contain a key (non-empty stdout)
    assert result.output.strip() != ""


def test_generate_store_failure_does_not_suppress_key():
    """If store fails, key is still printed to stdout and exit code is 0."""
    mock_kv = MagicMock()
    mock_kv.put.side_effect = VaultNotRunning()
    with (
        patch("vk.cli.keys.KVStore", return_value=mock_kv),
        patch("vk.cli.keys.VaultClient"),
        patch("vk.cli.keys.Settings"),
    ):
        result = runner.invoke(
            app, ["generate", "--type", "hex", "--store", "kv/api-keys/stripe/prod"]
        )
    # Key still printed, exit 0
    assert result.exit_code == 0
    assert result.output.strip() != ""


# ---------------------------------------------------------------------------
# store tests
# ---------------------------------------------------------------------------


def test_store_calls_kv_put_with_external_format():
    mock_kv = MagicMock()
    with (
        patch("vk.cli.keys.KVStore", return_value=mock_kv),
        patch("vk.cli.keys.VaultClient"),
        patch("vk.cli.keys.Settings"),
    ):
        result = runner.invoke(app, ["store", "kv/api-keys/stripe/prod", "sk_abc123"])
    assert result.exit_code == 0
    mock_kv.put.assert_called_once()
    call_kwargs = mock_kv.put.call_args.kwargs
    assert call_kwargs["format"] == "external"
    assert call_kwargs["options"] == {}


def test_store_with_notes():
    mock_kv = MagicMock()
    with (
        patch("vk.cli.keys.KVStore", return_value=mock_kv),
        patch("vk.cli.keys.VaultClient"),
        patch("vk.cli.keys.Settings"),
    ):
        result = runner.invoke(
            app, ["store", "kv/api-keys/stripe/prod", "sk_abc123", "--notes", "stripe prod"]
        )
    assert result.exit_code == 0
    call_kwargs = mock_kv.put.call_args.kwargs
    assert call_kwargs["notes"] == "stripe prod"


def test_store_with_tags():
    mock_kv = MagicMock()
    with (
        patch("vk.cli.keys.KVStore", return_value=mock_kv),
        patch("vk.cli.keys.VaultClient"),
        patch("vk.cli.keys.Settings"),
    ):
        result = runner.invoke(
            app, ["store", "kv/api-keys/stripe/prod", "sk_abc123", "--tags", "stripe,prod"]
        )
    assert result.exit_code == 0
    call_kwargs = mock_kv.put.call_args.kwargs
    assert call_kwargs["tags"] == ["stripe", "prod"]


def test_store_vault_error_exits_1():
    mock_kv = MagicMock()
    mock_kv.put.side_effect = VaultNotRunning()
    with (
        patch("vk.cli.keys.KVStore", return_value=mock_kv),
        patch("vk.cli.keys.VaultClient"),
        patch("vk.cli.keys.Settings"),
    ):
        result = runner.invoke(app, ["store", "kv/api-keys/stripe/prod", "sk_abc123"])
    assert result.exit_code == 1


# ---------------------------------------------------------------------------
# get tests
# ---------------------------------------------------------------------------


def test_get_masks_value_by_default():
    mock_kv = MagicMock()
    mock_kv.get.return_value = _make_secret("sk_supersecret")
    with (
        patch("vk.cli.keys.KVStore", return_value=mock_kv),
        patch("vk.cli.keys.VaultClient"),
        patch("vk.cli.keys.Settings"),
    ):
        result = runner.invoke(app, ["get", "kv/api-keys/stripe/prod"])
    assert result.exit_code == 0
    assert "████████" in result.output
    assert "sk_supersecret" not in result.output


def test_get_reveal_shows_plaintext():
    mock_kv = MagicMock()
    mock_kv.get.return_value = _make_secret("sk_supersecret")
    with (
        patch("vk.cli.keys.KVStore", return_value=mock_kv),
        patch("vk.cli.keys.VaultClient"),
        patch("vk.cli.keys.Settings"),
    ):
        result = runner.invoke(app, ["get", "kv/api-keys/stripe/prod", "--reveal"])
    assert result.exit_code == 0
    assert "sk_supersecret" in result.output


def test_get_shows_format_and_created_at():
    mock_kv = MagicMock()
    mock_kv.get.return_value = _make_secret()
    with (
        patch("vk.cli.keys.KVStore", return_value=mock_kv),
        patch("vk.cli.keys.VaultClient"),
        patch("vk.cli.keys.Settings"),
    ):
        result = runner.invoke(app, ["get", "kv/api-keys/stripe/prod"])
    assert result.exit_code == 0
    assert "hex" in result.output
    assert "2026-04-01" in result.output


def test_get_invalid_path_exits_1():
    mock_kv = MagicMock()
    mock_kv.get.side_effect = VaultInvalidPath("kv/api-keys/stripe/prod")
    with (
        patch("vk.cli.keys.KVStore", return_value=mock_kv),
        patch("vk.cli.keys.VaultClient"),
        patch("vk.cli.keys.Settings"),
    ):
        result = runner.invoke(app, ["get", "kv/api-keys/stripe/prod"])
    assert result.exit_code == 1


# ---------------------------------------------------------------------------
# list tests
# ---------------------------------------------------------------------------


def test_list_shows_tree_with_keys():
    mock_kv = MagicMock()
    mock_kv.list.return_value = ["stripe/", "github/"]
    with (
        patch("vk.cli.keys.KVStore", return_value=mock_kv),
        patch("vk.cli.keys.VaultClient"),
        patch("vk.cli.keys.Settings"),
    ):
        result = runner.invoke(app, ["list", "kv/api-keys"])
    assert result.exit_code == 0
    assert "stripe" in result.output
    assert "github" in result.output


def test_list_empty_shows_no_keys_found():
    mock_kv = MagicMock()
    mock_kv.list.return_value = []
    with (
        patch("vk.cli.keys.KVStore", return_value=mock_kv),
        patch("vk.cli.keys.VaultClient"),
        patch("vk.cli.keys.Settings"),
    ):
        result = runner.invoke(app, ["list", "kv/api-keys"])
    assert result.exit_code == 0
    assert "No keys found" in result.output


# ---------------------------------------------------------------------------
# delete tests
# ---------------------------------------------------------------------------


def test_delete_soft_default():
    mock_kv = MagicMock()
    with (
        patch("vk.cli.keys.KVStore", return_value=mock_kv),
        patch("vk.cli.keys.VaultClient"),
        patch("vk.cli.keys.Settings"),
    ):
        result = runner.invoke(app, ["delete", "kv/api-keys/stripe/prod"])
    assert result.exit_code == 0
    mock_kv.delete.assert_called_once_with("kv/api-keys/stripe/prod", permanent=False)


def test_delete_permanent_shows_warning_and_destroys():
    mock_kv = MagicMock()
    with (
        patch("vk.cli.keys.KVStore", return_value=mock_kv),
        patch("vk.cli.keys.VaultClient"),
        patch("vk.cli.keys.Settings"),
    ):
        result = runner.invoke(app, ["delete", "kv/api-keys/stripe/prod", "--permanent"])
    assert result.exit_code == 0
    mock_kv.delete.assert_called_once_with("kv/api-keys/stripe/prod", permanent=True)
    # Warning should appear in output
    assert "WARNING" in result.output or "permanent" in result.output.lower()


def test_delete_invalid_path_exits_1():
    mock_kv = MagicMock()
    mock_kv.delete.side_effect = VaultInvalidPath("kv/api-keys/stripe/prod")
    with (
        patch("vk.cli.keys.KVStore", return_value=mock_kv),
        patch("vk.cli.keys.VaultClient"),
        patch("vk.cli.keys.Settings"),
    ):
        result = runner.invoke(app, ["delete", "kv/api-keys/stripe/prod"])
    assert result.exit_code == 1


# ---------------------------------------------------------------------------
# generate --count --store path naming (Nyquist gap)
# ---------------------------------------------------------------------------


def test_generate_count_store_names_with_suffix():
    """generate --count 2 --store path must call kv.put with path-1 and path-2."""
    mock_kv = MagicMock()
    with (
        patch("vk.cli.keys.KVStore", return_value=mock_kv),
        patch("vk.cli.keys.VaultClient"),
        patch("vk.cli.keys.Settings"),
    ):
        result = runner.invoke(
            app,
            ["generate", "--type", "hex", "--count", "2", "--store", "kv/api-keys/batch"],
        )
    assert result.exit_code == 0
    assert mock_kv.put.call_count == 2
    paths_called = [call.args[0] for call in mock_kv.put.call_args_list]
    assert "kv/api-keys/batch-1" in paths_called
    assert "kv/api-keys/batch-2" in paths_called
