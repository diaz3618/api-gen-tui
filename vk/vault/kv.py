"""
KVStore: Vault KV v2 data layer.
All KV operations use client.raw.secrets.kv.v2.* exclusively.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import hvac.exceptions

from vk.config import Settings
from vk.errors import VaultInvalidPath
from vk.vault.client import VaultClient
from vk.vault.paths import canonicalize_path


class KVStore:
    """KV v2 CRUD operations for vk secrets.

    All operations use client.raw.secrets.kv.v2.* exclusively.
    PathBuilder/canonicalize_path handle all path construction.
    """

    def __init__(self, client: VaultClient, settings: Settings) -> None:
        self._client = client
        self._settings = settings

    def _split(self, user_path: str) -> tuple[str, str]:
        """Split user-supplied path into (mount_point, kv_path)."""
        return canonicalize_path(user_path)

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def put(
        self,
        path: str,
        value: str,
        *,
        format: str = "external",
        prefix: str = "",
        options: dict[str, Any] | None = None,
        notes: str = "",
        tags: list[str] | None = None,
    ) -> None:
        """Store a secret at path with full metadata.

        Args:
            path: Full path e.g. "kv/api-keys/stripe/prod" or "api-keys/stripe/prod"
            value: The plaintext secret value
            format: Generator format ("hex", "base64", ...) or "external"
            prefix: Generator prefix (empty string if none)
            options: Full GenerateOptions.__dict__ snapshot or {} for external secrets
            notes: Optional user annotation
            tags: Optional list of string tags
        """
        mount, kv_path = self._split(path)
        secret = {
            "value": value,
            "created_at": self._now_iso(),
            "format": format,
            "prefix": prefix,
            "total_length": len(value),
            "options": options if options is not None else {},
            "notes": notes,
            "tags": tags if tags is not None else [],
        }
        self._client.raw.secrets.kv.v2.create_or_update_secret(
            path=kv_path,
            mount_point=mount,
            secret=secret,
        )

    def get(self, path: str) -> dict[str, Any]:
        """Retrieve a secret dict at path.

        Returns the full metadata dict including the "value" field.
        Raises VaultInvalidPath if the path does not exist.
        """
        mount, kv_path = self._split(path)
        try:
            response = self._client.raw.secrets.kv.v2.read_secret_version(
                path=kv_path,
                mount_point=mount,
                raise_on_deleted_version=True,
            )
        except hvac.exceptions.InvalidPath:
            raise VaultInvalidPath(path)
        if response is None:
            raise VaultInvalidPath(path)
        return response["data"]["data"]

    def list(self, path: str) -> list[str]:
        """List secret names under path.

        Returns a list of key names (may include trailing "/" for sub-paths).
        Returns [] if no secrets exist at path.
        """
        mount, kv_path = self._split(path)
        try:
            response = self._client.raw.secrets.kv.v2.list_secrets(
                path=kv_path,
                mount_point=mount,
            )
            return response.get("data", {}).get("keys", [])
        except hvac.exceptions.InvalidPath:
            return []

    def delete(self, path: str, *, permanent: bool = False) -> None:
        """Delete a secret at path.

        Default (soft delete): delete_latest_version_of_secret() — recoverable.
        permanent=True: destroy all versions + delete metadata — irrecoverable.
        """
        mount, kv_path = self._split(path)
        if not permanent:
            self._client.raw.secrets.kv.v2.delete_latest_version_of_secret(
                path=kv_path,
                mount_point=mount,
            )
        else:
            # Get current version to destroy
            try:
                response = self._client.raw.secrets.kv.v2.read_secret_version(
                    path=kv_path,
                    mount_point=mount,
                    raise_on_deleted_version=False,
                )
                version = response["data"]["metadata"]["version"]
            except (hvac.exceptions.InvalidPath, KeyError, TypeError):
                version = 1
            self._client.raw.secrets.kv.v2.destroy_secret_versions(
                path=kv_path,
                versions=[version],
                mount_point=mount,
            )
            self._client.raw.secrets.kv.v2.delete_metadata_and_all_versions(
                path=kv_path,
                mount_point=mount,
            )
