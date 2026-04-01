from __future__ import annotations


class PathBuilder:
    """Construct canonical Vault KV v2 paths.

    Convention: mount_point="kv", path="api-keys/<service>/<name>"
    Never include mount point in the path — hvac takes them separately.
    """

    def __init__(self, prefix: str = "api-keys") -> None:
        self.prefix = prefix.strip("/")

    def build(self, service: str, name: str, prefix: str | None = None) -> str:
        """Build the KV path (without mount point) for a key.

        Args:
            service: Service name (e.g. "stripe")
            name: Key name (e.g. "production")
            prefix: Override default prefix. Pass "" to disable prefix.

        Returns:
            str: e.g. "api-keys/stripe/production"
        """
        effective_prefix = self.prefix if prefix is None else prefix.strip("/")
        parts = [p for p in [effective_prefix, service.strip("/"), name.strip("/")] if p]
        return "/".join(parts)


def canonicalize_path(user_path: str) -> tuple[str, str]:
    """Split a user-supplied path into (mount_point, kv_path).

    Examples:
        "kv/api-keys/stripe/prod"  → ("kv", "api-keys/stripe/prod")
        "api-keys/stripe/prod"     → ("kv", "api-keys/stripe/prod")   # assumes default mount
        "/api-keys/stripe/prod"    → ("kv", "api-keys/stripe/prod")   # strips leading slash

    Returns:
        Tuple of (mount_point, path_within_mount) — both without leading/trailing slashes.
    """
    cleaned = user_path.strip("/")
    parts = cleaned.split("/", 1)
    # If first segment looks like a known mount point (single word, no dots), split it off
    known_mounts = {"kv", "secret", "cubbyhole"}
    if len(parts) > 1 and parts[0] in known_mounts:
        return parts[0], parts[1]
    return "kv", cleaned
