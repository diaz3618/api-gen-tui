from __future__ import annotations

import hvac
import hvac.exceptions
import requests.exceptions

from vk.config import Settings
from vk.errors import VaultForbidden, VaultNotRunning, VaultSealed


class VaultClient:
    """Wraps hvac.Client and maps all hvac exceptions to typed VkError subclasses."""

    def __init__(self, settings: Settings, token: str | None = None) -> None:
        self._settings = settings
        self._client = hvac.Client(
            url=settings.vault_addr,
            token=token or settings.effective_token(),
        )

    def _wrap(self, fn, *args, **kwargs):
        """Call fn(*args, **kwargs), mapping hvac exceptions to VkError subclasses."""
        try:
            return fn(*args, **kwargs)
        except (hvac.exceptions.VaultDown, requests.exceptions.ConnectionError) as e:
            raise VaultNotRunning(
                "Vault is not running",
                hint="run `vk up`",
            ) from e
        except hvac.exceptions.Forbidden as e:
            raise VaultForbidden(
                "Authentication failed or token expired",
                hint="run `vk login`",
            ) from e

    def is_initialized(self) -> bool:
        """Return True if Vault is initialized."""
        health = self._wrap(self._client.sys.read_health_status, method="GET")
        return health.get("initialized", False)

    def is_sealed(self) -> bool:
        """Return True if Vault is sealed."""
        health = self._wrap(self._client.sys.read_health_status, method="GET")
        return health.get("sealed", True)

    def initialize(self, secret_shares: int = 1, secret_threshold: int = 1) -> dict:
        """Initialize Vault and return keys + root_token dict."""
        return self._wrap(
            self._client.sys.initialize,
            secret_shares=secret_shares,
            secret_threshold=secret_threshold,
        )

    def unseal(self, key: str) -> None:
        """Unseal Vault using the provided key. No-op if already unsealed."""
        status = self._wrap(self._client.sys.read_health_status, method="GET")
        if not status.get("sealed", True):
            return  # already unsealed — no-op
        self._wrap(self._client.sys.submit_unseal_key, key=key)

    def kv_mount_exists(self, mount_name: str = "kv") -> bool:
        """Return True if the named KV mount exists."""
        try:
            mounts = self._wrap(self._client.sys.list_mounted_secrets_engines)
            return f"{mount_name}/" in mounts
        except Exception:
            return False

    def verify_token(self) -> bool:
        """Return True if current token is valid (can list mounts)."""
        try:
            self._client.sys.list_mounted_secrets_engines()
            return True
        except Exception:
            return False

    @property
    def raw(self) -> hvac.Client:
        """Escape hatch to raw hvac client for operations not wrapped here."""
        return self._client
