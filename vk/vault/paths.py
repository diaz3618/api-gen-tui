from __future__ import annotations

from vk.errors import VaultInvalidPath

_KNOWN_MOUNTS = {"kv", "secret", "cubbyhole"}


def canonicalize_path(user_path: str) -> tuple[str, str]:
    """Split a user-supplied path into (mount_point, kv_path).

    Examples:
        "kv/api-keys/stripe/prod"  → ("kv", "api-keys/stripe/prod")
        "api-keys/stripe/prod"     → ("kv", "api-keys/stripe/prod")   # assumes default mount
        "/api-keys/stripe/prod"    → ("kv", "api-keys/stripe/prod")   # strips leading slash

    Raises:
        VaultInvalidPath: If path resolves to a bare mount point with no sub-path
                          (e.g. "kv" alone), which would silently produce an incorrect query.

    Returns:
        Tuple of (mount_point, path_within_mount) — both without leading/trailing slashes.
    """
    cleaned = user_path.strip("/")
    if not cleaned:
        raise VaultInvalidPath(user_path, hint="Provide a full path, e.g. kv/api-keys/stripe/prod")
    parts = cleaned.split("/", 1)
    # If first segment is a known mount point, split it off — but require a sub-path
    if parts[0] in _KNOWN_MOUNTS:
        if len(parts) < 2 or not parts[1]:
            raise VaultInvalidPath(
                user_path,
                hint=f"'{parts[0]}' is a mount point — provide a sub-path, e.g. {parts[0]}/api-keys/stripe/prod",
            )
        return parts[0], parts[1]
    return "kv", cleaned
