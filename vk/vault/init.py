from __future__ import annotations

from pathlib import Path

from dotenv import dotenv_values

from vk.errors import VaultAlreadyInitialized

ENV_FILE = Path(".env")


class VaultInitializer:
    """Handles Vault initialization and credential writing to .env."""

    def __init__(self, env_file: Path = ENV_FILE) -> None:
        self._env_file = env_file

    def can_initialize(self) -> bool:
        """Return True if .env does NOT already have a non-empty VAULT_ROOT_TOKEN."""
        vals = dotenv_values(self._env_file) if self._env_file.exists() else {}
        token = vals.get("VAULT_ROOT_TOKEN", "")
        return not bool(token and token.strip())

    def write_credentials(self, root_token: str, unseal_key: str) -> None:
        """
        Merge-write VAULT_ROOT_TOKEN and VAULT_UNSEAL_KEY into .env.
        Reads existing lines, replaces matching keys, appends missing keys.
        Never touches lines for other keys.
        Raises VaultAlreadyInitialized if credentials already present.
        """
        if not self.can_initialize():
            raise VaultAlreadyInitialized(
                "Vault credentials already in .env — re-initialization would overwrite them.",
                hint="Delete VAULT_ROOT_TOKEN and VAULT_UNSEAL_KEY from .env manually if you want to re-init.",
            )

        lines = self._env_file.read_text().splitlines() if self._env_file.exists() else []
        updates = {
            "VAULT_ROOT_TOKEN": root_token,
            "VAULT_UNSEAL_KEY": unseal_key,
        }
        written: set[str] = set()
        new_lines = []
        for line in lines:
            key = line.split("=", 1)[0].strip()
            if key in updates:
                new_lines.append(f"{key}={updates[key]}")
                written.add(key)
            else:
                new_lines.append(line)
        for key, val in updates.items():
            if key not in written:
                new_lines.append(f"{key}={val}")
        self._env_file.write_text("\n".join(new_lines) + "\n")
