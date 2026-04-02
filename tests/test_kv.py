"""Unit tests for KVStore data layer (04-01)."""

from __future__ import annotations

import hvac.exceptions
import pytest
import requests.exceptions
from unittest.mock import MagicMock, call

from vk.config import Settings
from vk.errors import VaultForbidden, VaultInvalidPath, VaultNotRunning
from vk.vault.client import VaultClient
from vk.vault.kv import KVStore


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_hvac():
    return MagicMock()


@pytest.fixture
def kv_store(mock_hvac):
    settings = Settings()
    client = VaultClient.__new__(VaultClient)
    client._settings = settings
    client._client = mock_hvac
    kv = KVStore(client=client, settings=settings)
    return kv, mock_hvac


# ---------------------------------------------------------------------------
# put() tests
# ---------------------------------------------------------------------------


def test_put_calls_create_or_update_with_correct_path(kv_store):
    kv, mock_hvac = kv_store
    kv.put("kv/api-keys/stripe/prod", "sk_abc123", format="hex", prefix="sk_", options={})
    mock_hvac.secrets.kv.v2.create_or_update_secret.assert_called_once()
    kwargs = mock_hvac.secrets.kv.v2.create_or_update_secret.call_args.kwargs
    assert kwargs["path"] == "api-keys/stripe/prod"
    assert kwargs["mount_point"] == "kv"


def test_put_stores_correct_metadata_schema(kv_store):
    kv, mock_hvac = kv_store
    kv.put("kv/api-keys/stripe/prod", "sk_abc123", format="hex", prefix="sk_", options={})
    kwargs = mock_hvac.secrets.kv.v2.create_or_update_secret.call_args.kwargs
    secret = kwargs["secret"]
    assert secret["value"] == "sk_abc123"
    assert secret["format"] == "hex"
    assert secret["prefix"] == "sk_"
    assert secret["total_length"] == 9  # len("sk_abc123")
    assert secret["notes"] == ""
    assert secret["tags"] == []
    assert secret["options"] == {}
    assert "created_at" in secret


def test_put_with_notes(kv_store):
    kv, mock_hvac = kv_store
    kv.put("kv/api-keys/stripe/prod", "sk_abc123", notes="stripe prod key")
    kwargs = mock_hvac.secrets.kv.v2.create_or_update_secret.call_args.kwargs
    assert kwargs["secret"]["notes"] == "stripe prod key"


def test_put_with_tags(kv_store):
    kv, mock_hvac = kv_store
    kv.put("kv/api-keys/stripe/prod", "sk_abc123", tags=["stripe", "prod"])
    kwargs = mock_hvac.secrets.kv.v2.create_or_update_secret.call_args.kwargs
    assert kwargs["secret"]["tags"] == ["stripe", "prod"]


def test_put_without_kv_prefix_in_path(kv_store):
    """Path without mount prefix should default to mount_point='kv'."""
    kv, mock_hvac = kv_store
    kv.put("api-keys/stripe/prod", "val123")
    kwargs = mock_hvac.secrets.kv.v2.create_or_update_secret.call_args.kwargs
    assert kwargs["mount_point"] == "kv"
    assert kwargs["path"] == "api-keys/stripe/prod"


# ---------------------------------------------------------------------------
# get() tests
# ---------------------------------------------------------------------------


def test_get_returns_secret_dict(kv_store):
    kv, mock_hvac = kv_store
    expected_data = {
        "value": "sk_abc123",
        "format": "hex",
        "created_at": "2026-04-01T00:00:00Z",
        "prefix": "sk_",
        "total_length": 9,
        "options": {},
        "notes": "",
        "tags": [],
    }
    mock_hvac.secrets.kv.v2.read_secret_version.return_value = {"data": {"data": expected_data}}
    result = kv.get("kv/api-keys/stripe/prod")
    assert result == expected_data


def test_get_calls_read_secret_version_with_correct_args(kv_store):
    kv, mock_hvac = kv_store
    mock_hvac.secrets.kv.v2.read_secret_version.return_value = {"data": {"data": {"value": "x"}}}
    kv.get("kv/api-keys/stripe/prod")
    mock_hvac.secrets.kv.v2.read_secret_version.assert_called_once_with(
        path="api-keys/stripe/prod",
        mount_point="kv",
        raise_on_deleted_version=True,
    )


def test_get_raises_vault_invalid_path_on_hvac_invalid_path(kv_store):
    kv, mock_hvac = kv_store
    mock_hvac.secrets.kv.v2.read_secret_version.side_effect = hvac.exceptions.InvalidPath(
        "not found"
    )
    with pytest.raises(VaultInvalidPath):
        kv.get("kv/api-keys/stripe/prod")


def test_get_raises_vault_invalid_path_when_response_is_none(kv_store):
    kv, mock_hvac = kv_store
    mock_hvac.secrets.kv.v2.read_secret_version.return_value = None
    with pytest.raises(VaultInvalidPath):
        kv.get("kv/api-keys/stripe/prod")


# ---------------------------------------------------------------------------
# list() tests
# ---------------------------------------------------------------------------


def test_list_returns_keys_from_response(kv_store):
    kv, mock_hvac = kv_store
    mock_hvac.secrets.kv.v2.list_secrets.return_value = {"data": {"keys": ["stripe/", "github/"]}}
    result = kv.list("kv/api-keys")
    assert result == ["stripe/", "github/"]


def test_list_with_correct_mount_and_path(kv_store):
    kv, mock_hvac = kv_store
    mock_hvac.secrets.kv.v2.list_secrets.return_value = {"data": {"keys": []}}
    kv.list("kv/api-keys")
    mock_hvac.secrets.kv.v2.list_secrets.assert_called_once_with(
        path="api-keys",
        mount_point="kv",
    )


def test_list_returns_empty_on_invalid_path(kv_store):
    kv, mock_hvac = kv_store
    mock_hvac.secrets.kv.v2.list_secrets.side_effect = hvac.exceptions.InvalidPath("no secrets")
    result = kv.list("kv/api-keys/nonexistent")
    assert result == []


def test_list_returns_empty_when_keys_missing_from_response(kv_store):
    kv, mock_hvac = kv_store
    mock_hvac.secrets.kv.v2.list_secrets.return_value = {}
    result = kv.list("kv/api-keys")
    assert result == []


# ---------------------------------------------------------------------------
# delete() tests
# ---------------------------------------------------------------------------


def test_delete_soft_calls_delete_latest_version(kv_store):
    kv, mock_hvac = kv_store
    kv.delete("kv/api-keys/stripe/prod")
    mock_hvac.secrets.kv.v2.delete_latest_version_of_secret.assert_called_once_with(
        path="api-keys/stripe/prod",
        mount_point="kv",
    )
    mock_hvac.secrets.kv.v2.destroy_secret_versions.assert_not_called()
    mock_hvac.secrets.kv.v2.delete_metadata_and_all_versions.assert_not_called()


def test_delete_permanent_calls_destroy_then_delete_metadata(kv_store):
    kv, mock_hvac = kv_store
    mock_hvac.secrets.kv.v2.read_secret_version.return_value = {
        "data": {"metadata": {"version": 3}}
    }
    kv.delete("kv/api-keys/stripe/prod", permanent=True)
    mock_hvac.secrets.kv.v2.destroy_secret_versions.assert_called_once_with(
        path="api-keys/stripe/prod",
        versions=[3],
        mount_point="kv",
    )
    mock_hvac.secrets.kv.v2.delete_metadata_and_all_versions.assert_called_once_with(
        path="api-keys/stripe/prod",
        mount_point="kv",
    )
    mock_hvac.secrets.kv.v2.delete_latest_version_of_secret.assert_not_called()


def test_delete_permanent_falls_back_to_version_1_on_error(kv_store):
    kv, mock_hvac = kv_store
    mock_hvac.secrets.kv.v2.read_secret_version.side_effect = hvac.exceptions.InvalidPath("gone")
    kv.delete("kv/api-keys/stripe/prod", permanent=True)
    mock_hvac.secrets.kv.v2.destroy_secret_versions.assert_called_once_with(
        path="api-keys/stripe/prod",
        versions=[1],
        mount_point="kv",
    )


# ---------------------------------------------------------------------------
# FINDING-1: Transport errors map to VaultNotRunning (FINDING-1 fix)
# ---------------------------------------------------------------------------


def test_put_connection_error_raises_vault_not_running(kv_store):
    kv, mock_hvac = kv_store
    mock_hvac.secrets.kv.v2.create_or_update_secret.side_effect = (
        requests.exceptions.ConnectionError("refused")
    )
    with pytest.raises(VaultNotRunning):
        kv.put("kv/api-keys/stripe/prod", "val")


def test_get_connection_error_raises_vault_not_running(kv_store):
    kv, mock_hvac = kv_store
    mock_hvac.secrets.kv.v2.read_secret_version.side_effect = requests.exceptions.ConnectionError(
        "refused"
    )
    with pytest.raises(VaultNotRunning):
        kv.get("kv/api-keys/stripe/prod")


def test_list_connection_error_raises_vault_not_running(kv_store):
    kv, mock_hvac = kv_store
    mock_hvac.secrets.kv.v2.list_secrets.side_effect = requests.exceptions.ConnectionError(
        "refused"
    )
    with pytest.raises(VaultNotRunning):
        kv.list("kv/api-keys")


def test_delete_connection_error_raises_vault_not_running(kv_store):
    kv, mock_hvac = kv_store
    mock_hvac.secrets.kv.v2.delete_latest_version_of_secret.side_effect = (
        requests.exceptions.ConnectionError("refused")
    )
    with pytest.raises(VaultNotRunning):
        kv.delete("kv/api-keys/stripe/prod")


# ---------------------------------------------------------------------------
# FINDING-2: hvac.Forbidden maps to VaultForbidden (FINDING-2 fix)
# ---------------------------------------------------------------------------


def test_put_forbidden_raises_vault_forbidden(kv_store):
    kv, mock_hvac = kv_store
    mock_hvac.secrets.kv.v2.create_or_update_secret.side_effect = hvac.exceptions.Forbidden(
        "permission denied"
    )
    with pytest.raises(VaultForbidden):
        kv.put("kv/api-keys/stripe/prod", "val")


def test_get_forbidden_raises_vault_forbidden(kv_store):
    kv, mock_hvac = kv_store
    mock_hvac.secrets.kv.v2.read_secret_version.side_effect = hvac.exceptions.Forbidden(
        "permission denied"
    )
    with pytest.raises(VaultForbidden):
        kv.get("kv/api-keys/stripe/prod")
