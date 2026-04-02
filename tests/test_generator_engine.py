"""
Integration tests for engine.generate() — all option combinations (Plan 03-03).
All tests must FAIL initially (RED phase) — generate() doesn't exist yet.
"""

import re
import pytest

from vk.generator.engine import GenerateOptions, generate
from vk.errors import GeneratorError


UUID4_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")


def opts(**kwargs) -> GenerateOptions:
    return GenerateOptions(**kwargs)


# ---------------------------------------------------------------------------
# Basic format dispatch
# ---------------------------------------------------------------------------


def test_generate_hex_default() -> None:
    result = generate(opts(format="hex", length=32))
    assert len(result) == 32
    assert re.fullmatch(r"[0-9a-f]+", result)


def test_generate_uuid4() -> None:
    result = generate(opts(format="uuid4"))
    assert len(result) == 36
    assert UUID4_RE.fullmatch(result)


def test_generate_ulid() -> None:
    result = generate(opts(format="ulid"))
    assert len(result) == 26
    assert re.fullmatch(r"[0-9A-Z]{26}", result)


def test_generate_custom() -> None:
    result = generate(opts(format="custom", alphabet="XYZ1", length=16))
    assert len(result) == 16
    assert all(c in set("XYZ1") for c in result)


def test_generate_alphanumeric() -> None:
    result = generate(opts(format="alphanumeric", length=32))
    assert len(result) == 32
    assert re.fullmatch(r"[A-Za-z0-9]+", result)


def test_generate_url_safe() -> None:
    result = generate(opts(format="url-safe", length=32))
    assert len(result) == 32
    assert re.fullmatch(r"[A-Za-z0-9_\-]+", result)


# ---------------------------------------------------------------------------
# Prefix / suffix assembly
# ---------------------------------------------------------------------------


def test_generate_prefix() -> None:
    result = generate(opts(format="alphanumeric", prefix="sk_", length=35))
    assert result.startswith("sk_")
    assert len(result) == 35


def test_generate_suffix() -> None:
    result = generate(opts(format="alphanumeric", suffix="_v1", length=35))
    assert result.endswith("_v1")
    assert len(result) == 35


def test_generate_prefix_and_suffix() -> None:
    result = generate(opts(format="alphanumeric", prefix="A_", suffix="_B", length=36))
    assert result.startswith("A_")
    assert result.endswith("_B")
    assert len(result) == 36


# ---------------------------------------------------------------------------
# --random-length override
# ---------------------------------------------------------------------------


def test_generate_random_length_hex() -> None:
    # random_length=8 chars for hex → 8 hex chars output
    result = generate(opts(format="hex", random_length=8))
    assert len(result) == 8
    assert re.fullmatch(r"[0-9a-f]+", result)


def test_generate_random_length_with_prefix() -> None:
    result = generate(opts(format="alphanumeric", prefix="pre_", random_length=10))
    assert result.startswith("pre_")
    assert len(result) == 14  # 4 + 10


# ---------------------------------------------------------------------------
# --group + --separator
# ---------------------------------------------------------------------------


def test_generate_grouped() -> None:
    result = generate(opts(format="alphanumeric", length=20, group=4, separator="-"))
    # 20 chars split into 5 groups of 4, joined by "-"
    assert re.fullmatch(r"[A-Za-z0-9]{4}(-[A-Za-z0-9]{4}){4}", result)


# ---------------------------------------------------------------------------
# --upper / --lower
# ---------------------------------------------------------------------------


def test_generate_upper() -> None:
    result = generate(opts(format="alphanumeric", length=32, upper=True))
    assert result == result.upper()


def test_generate_lower() -> None:
    result = generate(opts(format="alphanumeric", length=32, lower=True))
    assert result == result.lower()


# ---------------------------------------------------------------------------
# --no-ambiguous
# ---------------------------------------------------------------------------


def test_generate_no_ambiguous() -> None:
    ambiguous = set("0O1lI")
    for _ in range(10):
        result = generate(opts(format="alphanumeric", length=64, no_ambiguous=True))
        assert not any(c in ambiguous for c in result)


# ---------------------------------------------------------------------------
# --min-* satisfaction
# ---------------------------------------------------------------------------


def test_generate_min_classes() -> None:
    for _ in range(5):
        result = generate(
            opts(format="alphanumeric", length=32, min_upper=5, min_lower=5, min_digits=5)
        )
        assert sum(1 for c in result if c.isupper()) >= 5
        assert sum(1 for c in result if c.islower()) >= 5
        assert sum(1 for c in result if c.isdigit()) >= 5


# ---------------------------------------------------------------------------
# Constraint violations
# ---------------------------------------------------------------------------


def test_generate_raises_impossible_min_sum() -> None:
    with pytest.raises(GeneratorError):
        generate(opts(format="alphanumeric", min_upper=20, min_lower=20, length=30))


def test_generate_raises_missing_alphabet() -> None:
    with pytest.raises(GeneratorError):
        generate(opts(format="custom", alphabet=None, length=16))


# ---------------------------------------------------------------------------
# 10k safety limit
# ---------------------------------------------------------------------------


def test_generate_raises_after_10k_attempts() -> None:
    # alphanumeric has no symbols — min_symbols is impossible to satisfy
    with pytest.raises(GeneratorError) as exc_info:
        generate(opts(format="alphanumeric", min_symbols=10, length=32))
    assert "10,000 attempts" in str(exc_info.value)
