"""
Tests for GenerateOptions constraint validation (Plan 03-01).
All tests must FAIL initially (RED phase) — modules don't exist yet.
"""

import pytest

from vk.generator.engine import GenerateOptions
from vk.generator.constraints import validate_options
from vk.errors import GeneratorError


# ---------------------------------------------------------------------------
# Helper to build opts with overrides
# ---------------------------------------------------------------------------


def opts(**kwargs) -> GenerateOptions:
    return GenerateOptions(**kwargs)


# ---------------------------------------------------------------------------
# Impossible combinations — must raise GeneratorError
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "kwargs, expected_fragment",
    [
        # min-* sum exceeds key length (explicit random portion = length)
        (
            {"min_upper": 10, "min_lower": 10, "min_digits": 10, "length": 20},
            "min-* sum (30)",
        ),
        # min-* sum exceeds explicit random_length
        (
            {"random_length": 5, "min_upper": 3, "min_lower": 3},
            "min-* sum (6)",
        ),
        # length too short when prefix consumes all room
        (
            {"length": 5, "prefix": "hello"},
            "random portion length",
        ),
        # custom format without alphabet
        (
            {"format": "custom", "alphabet": None, "length": 16},
            "--alphabet",
        ),
        # custom format with only one unique char
        (
            {"format": "custom", "alphabet": "AAAA", "length": 16},
            "2 unique",
        ),
        # length zero
        (
            {"length": 0},
            "positive",
        ),
        # length negative
        (
            {"length": -5},
            "positive",
        ),
    ],
)
def test_validate_options_raises(kwargs: dict, expected_fragment: str) -> None:
    o = opts(**kwargs)
    with pytest.raises(GeneratorError) as exc_info:
        validate_options(o)
    assert expected_fragment in str(exc_info.value), (
        f"Expected '{expected_fragment}' in error message, got: {exc_info.value}"
    )


# ---------------------------------------------------------------------------
# Valid combinations — must NOT raise
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "kwargs",
    [
        # basic hex with defaults
        {"format": "hex", "length": 32},
        # alphanumeric with reasonable min-* values well under length
        {"format": "alphanumeric", "min_upper": 5, "min_lower": 5, "length": 32},
        # custom format with valid alphabet
        {"format": "custom", "alphabet": "ABC123", "length": 16},
        # prefix + suffix still leaves positive random portion
        {"format": "hex", "length": 40, "prefix": "sk_", "suffix": "_v1"},
        # explicit random_length with min-* that fit
        {
            "format": "alphanumeric",
            "random_length": 20,
            "min_upper": 5,
            "min_lower": 5,
            "min_digits": 5,
        },
    ],
)
def test_validate_options_valid(kwargs: dict) -> None:
    o = opts(**kwargs)
    # Should not raise
    validate_options(o)
