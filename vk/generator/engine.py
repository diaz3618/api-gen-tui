"""
Generator engine: GenerateOptions dataclass and generate() function.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from typing import Optional

from vk.errors import GeneratorError
from vk.generator import formats
from vk.generator.constraints import validate_options

_AMBIGUOUS = set("0O1lI")
_SYMBOL_CHARS = "!@#$%^&*"


@dataclass
class GenerateOptions:
    format: str = "hex"  # hex|base64|base64url|base32|alphanumeric|uuid4|ulid|url-safe|custom
    length: int = 32  # total output length (prefix+random+suffix)
    random_length: Optional[int] = None  # explicit random portion length; overrides length calc
    prefix: str = ""
    suffix: str = ""
    separator: str = "_"
    group: Optional[int] = None  # chunk size for grouping
    no_ambiguous: bool = False  # filter 0,O,1,l,I
    min_upper: int = 0
    min_lower: int = 0
    min_digits: int = 0
    min_symbols: int = 0
    upper: bool = False  # force uppercase
    lower: bool = False  # force lowercase
    entropy: bool = False  # print entropy to stderr
    count: int = 1  # number of keys to generate
    alphabet: Optional[str] = None  # required for format="custom"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _compute_random_length(opts: GenerateOptions) -> int:
    if opts.random_length is not None:
        return opts.random_length
    return opts.length - len(opts.prefix) - len(opts.suffix)


def _bytes_for_chars(fmt: str, char_count: int) -> int:
    """Back-calculate byte count for byte-based formats to hit approximately char_count output chars."""
    if fmt == "hex":
        return math.ceil(char_count / 2)
    elif fmt in ("base64", "base64url"):
        return math.ceil(char_count * 3 / 4)
    elif fmt == "base32":
        return math.ceil(char_count * 5 / 8)
    return char_count


def _raw_random(opts: GenerateOptions, n_chars: int) -> str:
    fmt = opts.format
    if fmt == "hex":
        return formats.gen_hex(_bytes_for_chars("hex", n_chars))
    elif fmt == "base64":
        return formats.gen_base64(_bytes_for_chars("base64", n_chars))
    elif fmt == "base64url":
        return formats.gen_base64url(_bytes_for_chars("base64url", n_chars))
    elif fmt == "base32":
        return formats.gen_base32(_bytes_for_chars("base32", n_chars))
    elif fmt == "alphanumeric":
        return formats.gen_alphanumeric(n_chars)
    elif fmt == "uuid4":
        return formats.gen_uuid4()
    elif fmt == "ulid":
        return formats.gen_ulid()
    elif fmt == "url-safe":
        return formats.gen_url_safe(n_chars)
    elif fmt == "custom":
        return formats.gen_custom(n_chars, opts.alphabet)  # type: ignore[arg-type]
    else:
        raise GeneratorError(f"Unknown format: {fmt}")


def _apply_case(s: str, upper: bool, lower: bool) -> str:
    if upper:
        return s.upper()
    if lower:
        return s.lower()
    return s


def _meets_minimums(s: str, opts: GenerateOptions) -> bool:
    if opts.min_upper and sum(1 for c in s if c.isupper()) < opts.min_upper:
        return False
    if opts.min_lower and sum(1 for c in s if c.islower()) < opts.min_lower:
        return False
    if opts.min_digits and sum(1 for c in s if c.isdigit()) < opts.min_digits:
        return False
    if opts.min_symbols and sum(1 for c in s if c in _SYMBOL_CHARS) < opts.min_symbols:
        return False
    return True


def _compute_entropy(opts: GenerateOptions, random_len: int) -> float:
    fmt = opts.format
    if fmt == "uuid4":
        return 122.0
    elif fmt == "ulid":
        return 80.0
    elif fmt == "hex":
        return random_len * 4.0
    elif fmt in ("base64", "base64url"):
        return random_len * 6.0
    elif fmt == "base32":
        return random_len * 5.0
    elif fmt == "alphanumeric":
        return random_len * math.log2(62)
    elif fmt == "url-safe":
        return random_len * math.log2(64)
    elif fmt == "custom":
        unique = len(set(opts.alphabet or ""))
        return random_len * math.log2(unique) if unique > 1 else 0.0
    return 0.0


def _apply_grouping(s: str, group: int, separator: str) -> str:
    chunks = [s[i : i + group] for i in range(0, len(s), group)]
    return separator.join(chunks)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate(opts: GenerateOptions) -> str:
    """Generate a single key string per opts. Raises GeneratorError on failure."""
    validate_options(opts)
    random_len = _compute_random_length(opts)

    # Fixed-length formats: ignore random_len, just return the value
    if opts.format in ("uuid4", "ulid"):
        raw = _raw_random(opts, random_len)
        raw = _apply_case(raw, opts.upper, opts.lower)
        if opts.entropy:
            bits = _compute_entropy(opts, random_len)
            print(f"Entropy: ~{bits:.0f} bits", file=sys.stderr)
        return opts.prefix + raw + opts.suffix

    # All other formats: rejection-sampling loop with 10k cap
    for _ in range(10_000):
        raw = _raw_random(opts, random_len)

        # Trim byte-based encoded output to target char count
        if opts.format in ("hex", "base64", "base64url", "base32"):
            raw = raw[:random_len]
            if len(raw) < random_len:
                continue  # encoded output shorter than needed — retry

        # No-ambiguous filter
        if opts.no_ambiguous:
            raw = "".join(c for c in raw if c not in _AMBIGUOUS)
            if len(raw) < random_len:
                continue

        # Case toggle
        raw = _apply_case(raw, opts.upper, opts.lower)

        # Min-class check
        if not _meets_minimums(raw, opts):
            continue

        # All constraints satisfied — apply grouping and assemble
        if opts.group:
            raw = _apply_grouping(raw, opts.group, opts.separator)

        if opts.entropy:
            bits = _compute_entropy(opts, random_len)
            print(f"Entropy: ~{bits:.0f} bits", file=sys.stderr)

        return opts.prefix + raw + opts.suffix

    raise GeneratorError(
        "Could not satisfy constraints after 10,000 attempts — "
        "try relaxing --min-* requirements or increasing --length"
    )
