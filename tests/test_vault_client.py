from unittest.mock import MagicMock, patch

import hvac.exceptions
import pytest
import requests.exceptions

from vk.config import Settings
from vk.errors import VaultForbidden, VaultNotRunning
from vk.vault.client import VaultClient


def make_client(mock_hvac_client=None, **settings_kwargs):
    """Helper: create VaultClient with a mocked hvac.Client."""
    settings = Settings()
    client = VaultClient(settings)
    if mock_hvac_client is not None:
        client._client = mock_hvac_client
    return client


def test_is_sealed_returns_true_when_health_reports_sealed():
    """Test 1: is_sealed() returns True when health status reports sealed=True."""
    mock_hvac = MagicMock()
    mock_hvac.sys.read_health_status.return_value = {"sealed": True, "initialized": True}
    client = make_client(mock_hvac)
    assert client.is_sealed() is True


def test_is_initialized_returns_true_when_health_reports_initialized():
    """Test 2: is_initialized() returns True when health reports initialized=True."""
    mock_hvac = MagicMock()
    mock_hvac.sys.read_health_status.return_value = {"sealed": False, "initialized": True}
    client = make_client(mock_hvac)
    assert client.is_initialized() is True


def test_vault_down_maps_to_vault_not_running():
    """Test 3: hvac.exceptions.VaultDown → VaultNotRunning with hint 'run `vk up`'."""
    mock_hvac = MagicMock()
    mock_hvac.sys.read_health_status.side_effect = hvac.exceptions.VaultDown()
    client = make_client(mock_hvac)
    with pytest.raises(VaultNotRunning) as exc_info:
        client.is_sealed()
    assert "vk up" in exc_info.value.hint


def test_connection_error_maps_to_vault_not_running():
    """Test 4: requests.exceptions.ConnectionError → VaultNotRunning with hint 'run `vk up`'."""
    mock_hvac = MagicMock()
    mock_hvac.sys.read_health_status.side_effect = requests.exceptions.ConnectionError()
    client = make_client(mock_hvac)
    with pytest.raises(VaultNotRunning) as exc_info:
        client.is_sealed()
    assert "vk up" in exc_info.value.hint


def test_forbidden_maps_to_vault_forbidden():
    """Test 5: hvac.exceptions.Forbidden → VaultForbidden with hint 'run `vk login`'."""
    mock_hvac = MagicMock()
    mock_hvac.sys.read_health_status.side_effect = hvac.exceptions.Forbidden(message="")
    client = make_client(mock_hvac)
    with pytest.raises(VaultForbidden) as exc_info:
        client.is_sealed()
    assert "vk login" in exc_info.value.hint


def test_unseal_is_noop_when_already_unsealed():
    """Test 6: unseal(key) is a no-op if already unsealed."""
    mock_hvac = MagicMock()
    mock_hvac.sys.read_health_status.return_value = {"sealed": False, "initialized": True}
    client = make_client(mock_hvac)
    client.unseal("test-key")
    # submit_unseal_key should NOT have been called
    mock_hvac.sys.submit_unseal_key.assert_not_called()


def test_kv_mount_exists_returns_bool():
    """Test 7: kv_mount_exists(mount_name) checks sys/mounts and returns bool without raising."""
    mock_hvac = MagicMock()
    mock_hvac.sys.list_mounted_secrets_engines.return_value = {"kv/": {}, "sys/": {}}
    client = make_client(mock_hvac)
    assert client.kv_mount_exists("kv") is True
    assert client.kv_mount_exists("secret") is False
