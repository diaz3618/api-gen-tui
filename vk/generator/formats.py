"""
Pure format generators. Each function returns a raw random string for its format.
No prefix/suffix/grouping/options — those are assembled by engine.generate().
All randomness uses secrets exclusively.
"""

from __future__ import annotations

import base64
import secrets
import uuid

from ulid import ULID


def gen_hex(n: int) -> str:
    """Return a lowercase hex string of n random bytes (output length = 2*n)."""
    return secrets.token_hex(n)


def gen_base64(n: int) -> str:
    """Return standard base64 of n random bytes, padding stripped."""
    return base64.b64encode(secrets.token_bytes(n)).decode().rstrip("=")


def gen_base64url(n: int) -> str:
    """Return URL-safe base64 of n random bytes, padding stripped (RFC 4648)."""
    return base64.urlsafe_b64encode(secrets.token_bytes(n)).decode().rstrip("=")


def gen_base32(n: int) -> str:
    """Return uppercase base32 of n random bytes, padding stripped."""
    return base64.b32encode(secrets.token_bytes(n)).decode().rstrip("=")


def gen_alphanumeric(n: int) -> str:
    """Return n random characters from [A-Za-z0-9]."""
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(secrets.choice(alphabet) for _ in range(n))


def gen_uuid4() -> str:
    """Return a canonical UUID4 string (36 chars with hyphens)."""
    return str(uuid.uuid4())


def gen_ulid() -> str:
    """Return a 26-character ULID string."""
    return str(ULID())


def gen_url_safe(n: int) -> str:
    """Return n random characters from [A-Za-z0-9-_]."""
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
    return "".join(secrets.choice(alphabet) for _ in range(n))


def gen_custom(n: int, alphabet: str) -> str:
    """Return n random characters from the caller-supplied alphabet."""
    return "".join(secrets.choice(alphabet) for _ in range(n))
