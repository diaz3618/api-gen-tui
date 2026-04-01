from __future__ import annotations
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    vault_addr: str = field(
        default_factory=lambda: os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
    )
    vault_port: int = field(default_factory=lambda: int(os.getenv("VAULT_PORT", "8200")))
    vault_root_token: str = field(default_factory=lambda: os.getenv("VAULT_ROOT_TOKEN", ""))
    vault_unseal_key: str = field(default_factory=lambda: os.getenv("VAULT_UNSEAL_KEY", ""))
    vault_kv_mount: str = field(default_factory=lambda: os.getenv("VAULT_KV_MOUNT", "kv"))
    vk_default_path_prefix: str = field(
        default_factory=lambda: os.getenv("VK_DEFAULT_PATH_PREFIX", "api-keys")
    )
    token_file: Path = field(
        default_factory=lambda: Path(os.path.expanduser(os.getenv("VK_TOKEN_FILE", "~/.vk/token")))
    )

    @classmethod
    def load(cls) -> "Settings":
        """Reload from environment (re-runs dotenv)."""
        load_dotenv(override=True)
        return cls()

    def effective_token(self, cli_token: str | None = None) -> str:
        """Return token using priority chain: CLI flag > VAULT_TOKEN env > token_file > .env root token."""
        if cli_token:
            return cli_token
        env_token = os.getenv("VAULT_TOKEN", "")
        if env_token:
            return env_token
        if self.token_file.exists():
            return self.token_file.read_text().strip()
        return self.vault_root_token
