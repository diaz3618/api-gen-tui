from __future__ import annotations
import time
from pathlib import Path

import requests
from python_on_whales import DockerClient, DockerException

from vk.config import Settings
from vk.errors import VaultNotRunning


# Compose file is relative to the repo root
_COMPOSE_FILE = Path(__file__).parent.parent.parent / "docker" / "docker-compose.yml"


class ComposeManager:
    """Manages the Vault Docker Compose stack via python-on-whales."""

    def __init__(
        self, settings: Settings | None = None, compose_file: Path = _COMPOSE_FILE
    ) -> None:
        self.settings = settings or Settings()
        self._client = DockerClient(compose_files=[str(compose_file)])

    def up(self, wait: bool = True) -> None:
        """Start the Vault stack in detached mode. Waits for Vault to be ready if wait=True."""
        self._client.compose.up(detach=True)
        if wait:
            self._wait_for_vault()

    def down(self) -> None:
        """Stop the Vault stack."""
        self._client.compose.down()

    def is_running(self) -> bool:
        """Return True if the vault container is running."""
        try:
            containers = self._client.compose.ps()
            return any(c.state.running for c in containers)
        except Exception:
            return False

    def is_container_running(self) -> bool:
        """Return True if the vault container named vk-vault is running."""
        try:
            containers = self._client.compose.ps()
            return any(c.name == "vk-vault" and c.state.running for c in containers)
        except Exception:
            return False

    def _wait_for_vault(self, timeout: int = 60) -> None:
        """Poll /v1/sys/health until Vault responds (any HTTP status = up).

        Vault returns:
          200 = initialized + unsealed
          429 = standby
          472 = DR mode
          473 = performance standby
          501 = not initialized
          503 = sealed

        Any of these means the HTTP listener is up. Connection refused = not yet ready.
        """
        health_url = f"{self.settings.vault_addr}/v1/sys/health"
        for _ in range(timeout):
            try:
                r = requests.get(health_url, timeout=1)
                if r.status_code in (200, 429, 472, 473, 501, 503):
                    return  # HTTP listener is up
            except requests.exceptions.ConnectionError:
                pass
            time.sleep(1)
        raise VaultNotRunning(
            "Vault did not become ready within 60 seconds.",
            hint="Check `docker compose logs vault` for errors.",
        )
