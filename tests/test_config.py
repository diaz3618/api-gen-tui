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


def test_settings_load_re_reads_env(monkeypatch, tmp_path):
    """Settings.load() must re-run dotenv (override=True) so REPL picks up credentials written by vault-init."""
    monkeypatch.setenv("VAULT_ADDR", "http://original:8200")
    from vk.config import Settings

    s1 = Settings()
    assert s1.vault_addr == "http://original:8200"

    # Simulate a different value being set after initial load
    monkeypatch.setenv("VAULT_ADDR", "http://updated:8200")
    s2 = Settings.load()
    assert s2.vault_addr == "http://updated:8200", (
        "Settings.load() must pick up env var changes (re-runs dotenv with override=True)"
    )


def test_settings_effective_token_priority(monkeypatch, tmp_path):
    """effective_token() must follow: cli_token > VAULT_TOKEN env > token_file > vault_root_token."""
    monkeypatch.setenv("VAULT_TOKEN", "env-token")
    monkeypatch.setenv("VAULT_ROOT_TOKEN", "dotenv-root-token")
    monkeypatch.delenv("VK_TOKEN_FILE", raising=False)
    from vk.config import Settings

    s = Settings()

    # CLI token takes priority over everything
    assert s.effective_token(cli_token="cli-token") == "cli-token"

    # VAULT_TOKEN env takes priority over token_file and root token
    assert s.effective_token() == "env-token"

    # With VAULT_TOKEN gone, token_file is next
    monkeypatch.delenv("VAULT_TOKEN", raising=False)
    token_file = tmp_path / "token"
    token_file.write_text("file-token")
    s2 = Settings()
    s2.token_file = token_file
    assert s2.effective_token() == "file-token"

    # With no token_file, falls back to vault_root_token
    s3 = Settings()
    s3.token_file = tmp_path / "nonexistent"
    assert s3.effective_token() == "dotenv-root-token"
