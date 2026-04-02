"""
Constraint validation for GenerateOptions.
validate_options() raises GeneratorError on impossible option combinations.
All checks run before any generation attempt.
"""

from __future__ import annotations

from vk.errors import GeneratorError


def validate_options(opts: "GenerateOptions") -> None:  # type: ignore[name-defined]
    """
    Validate all option combinations. Raises GeneratorError with a descriptive
    message on the first impossible combination found.
    """
    # Check 1: length must be positive
    if opts.length <= 0:
        raise GeneratorError("length must be positive")

    # Check 2: compute random portion and ensure it's positive
    if opts.random_length is not None:
        random_len = opts.random_length
    else:
        random_len = opts.length - len(opts.prefix) - len(opts.suffix)

    if random_len <= 0:
        raise GeneratorError(
            f"random portion length is {random_len} — raise --length or shorten prefix/suffix"
        )

    # Check 3: min-* sum must not exceed random portion
    min_sum = opts.min_upper + opts.min_lower + opts.min_digits + opts.min_symbols
    if min_sum > random_len:
        raise GeneratorError(
            f"min-* sum ({min_sum}) exceeds key length ({random_len}) — "
            f"raise --length or lower minimums"
        )

    # Check 4: custom format requires alphabet
    if opts.format == "custom" and opts.alphabet is None:
        raise GeneratorError("--alphabet is required for custom format")

    # Check 5: custom alphabet must have at least 2 unique characters
    if opts.format == "custom" and opts.alphabet is not None:
        if len(set(opts.alphabet)) < 2:
            raise GeneratorError("--alphabet must contain at least 2 unique characters")
