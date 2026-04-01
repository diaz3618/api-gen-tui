import os
import pytest
from pathlib import Path


def test_settings_loads_vault_addr_from_env(monkeypatch):
    monkeypatch.setenv("VAULT_ADDR", "http://127.0.0.1:8200")
    monkeypatch.delenv("VAULT_ROOT_TOKEN", raising=False)
    monkeypatch.delenv("VAULT_UNSEAL_KEY", raising=False)
    from vk.config import Settings

    s = Settings()
    assert s.vault_addr == "http://127.0.0.1:8200"


def test_settings_vault_kv_mount_defaults_to_kv(monkeypatch):
    monkeypatch.delenv("VAULT_KV_MOUNT", raising=False)
    from vk.config import Settings

    s = Settings()
    assert s.vault_kv_mount == "kv"


def test_settings_token_file_expands_tilde(monkeypatch):
    monkeypatch.delenv("VK_TOKEN_FILE", raising=False)
    from vk.config import Settings

    s = Settings()
    assert not str(s.token_file).startswith("~"), "token_file should expand ~ to absolute path"
    assert str(s.token_file).endswith("/.vk/token")
