"""
Generator engine: GenerateOptions dataclass and generate() function.
generate() is implemented in Plan 03-03; this file defines the public contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


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
