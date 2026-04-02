"""
Tests for all 9 format generator functions (Plan 03-02).
All tests must FAIL initially (RED phase) — vk.generator.formats doesn't exist yet.
"""

import re
import pytest

from vk.generator.formats import (
    gen_hex,
    gen_base64,
    gen_base64url,
    gen_base32,
    gen_alphanumeric,
    gen_uuid4,
    gen_ulid,
    gen_url_safe,
    gen_custom,
)


# ---------------------------------------------------------------------------
# Byte-count formats: hex, base64, base64url, base32
# ---------------------------------------------------------------------------


def test_gen_hex_length_and_charset() -> None:
    result = gen_hex(16)
    assert len(result) == 32
    assert re.fullmatch(r"[0-9a-f]+", result)


def test_gen_hex_randomness() -> None:
    assert gen_hex(16) != gen_hex(16)


def test_gen_base64_length_and_charset() -> None:
    # 12 bytes → ceil(12/3)*4 = 16 chars (no padding needed)
    result = gen_base64(12)
    assert len(result) == 16
    assert re.fullmatch(r"[A-Za-z0-9+/]+", result)


def test_gen_base64url_length_and_charset() -> None:
    result = gen_base64url(12)
    assert len(result) == 16
    assert re.fullmatch(r"[A-Za-z0-9_\-]+", result)


def test_gen_base32_length_and_charset() -> None:
    # 10 bytes → ceil(10/5)*8 = 16 chars (no padding)
    result = gen_base32(10)
    assert len(result) == 16
    assert re.fullmatch(r"[A-Z2-7]+", result)


# ---------------------------------------------------------------------------
# Character-count formats: alphanumeric, url-safe, custom
# ---------------------------------------------------------------------------


def test_gen_alphanumeric_length_and_charset() -> None:
    result = gen_alphanumeric(32)
    assert len(result) == 32
    assert re.fullmatch(r"[A-Za-z0-9]+", result)


def test_gen_alphanumeric_randomness() -> None:
    assert gen_alphanumeric(32) != gen_alphanumeric(32)


def test_gen_url_safe_length_and_charset() -> None:
    result = gen_url_safe(32)
    assert len(result) == 32
    assert re.fullmatch(r"[A-Za-z0-9_\-]+", result)


def test_gen_url_safe_randomness() -> None:
    assert gen_url_safe(32) != gen_url_safe(32)


def test_gen_custom_length_and_charset() -> None:
    result = gen_custom(16, "ABC123")
    assert len(result) == 16
    assert all(c in set("ABC123") for c in result)


def test_gen_custom_randomness() -> None:
    assert gen_custom(16, "ABC123") != gen_custom(16, "ABC123")


# ---------------------------------------------------------------------------
# Fixed-length formats: uuid4, ulid
# ---------------------------------------------------------------------------

UUID4_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")


def test_gen_uuid4_length_and_format() -> None:
    result = gen_uuid4()
    assert len(result) == 36
    assert UUID4_RE.fullmatch(result), f"UUID4 regex mismatch: {result}"


def test_gen_ulid_length_and_charset() -> None:
    result = gen_ulid()
    assert len(result) == 26
    assert re.fullmatch(r"[0-9A-Z]{26}", result), f"ULID regex mismatch: {result}"
