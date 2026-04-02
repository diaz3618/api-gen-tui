from __future__ import annotations

import typer

from vk.errors import GeneratorError
from vk.output import print_error

# ---------------------------------------------------------------------------
# Character set constants
# ---------------------------------------------------------------------------

_LOWER = "abcdefghijklmnopqrstuvwxyz"
_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_DIGITS = "0123456789"
_ALNUM = _LOWER + _UPPER + _DIGITS
_HEX = "0123456789abcdef"
_SYMS = "!@#$%^&*"


# ---------------------------------------------------------------------------
# HCL builder
# ---------------------------------------------------------------------------


def _build_hcl(length: int, rules: list[tuple[str, int]], comment: str = "") -> str:
    """Build a Vault HCL password policy string.

    Args:
        length: Total password length.
        rules: List of (charset, min_chars) tuples — each becomes a rule "charset" block.
        comment: Optional comment line prepended before 'length' (documents limitations).

    Returns:
        Valid Vault HCL policy string (D-17 format).
    """
    lines: list[str] = []
    if comment:
        lines.append(f"# {comment}")
    lines.append(f"length = {length}")
    for charset, min_chars in rules:
        lines.append('rule "charset" {')
        lines.append(f'  charset = "{charset}"')
        lines.append(f"  min-chars = {min_chars}")
        lines.append("}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Preset definitions (D-15)
# ---------------------------------------------------------------------------

_PRESETS: dict[str, str] = {
    "default": _build_hcl(
        32,
        [(_ALNUM, 1)],
    ),
    "strong": _build_hcl(
        32,
        [(_LOWER, 4), (_UPPER, 4), (_DIGITS, 4), (_SYMS, 2)],
    ),
    "hex": _build_hcl(
        64,
        [(_HEX, 1)],
    ),
    "uuid": _build_hcl(
        36,
        [(_HEX + "-", 1)],
        comment="UUID4 approximation — Vault does not natively enforce UUID4 format",
    ),
    "stripe": _build_hcl(
        32,
        [(_ALNUM, 1)],
        comment="Stripe-style random portion (32 chars); prefix 'sk_live_' added by application",
    ),
}


# ---------------------------------------------------------------------------
# CLI command
# ---------------------------------------------------------------------------


def policy(
    preset: str = typer.Argument(
        ...,
        help="Named generator preset. Valid values: default, strong, hex, uuid, stripe",
    ),
) -> None:
    """Emit a Vault HCL password policy from a generator preset.

    Output goes to stdout (pipe-friendly). Use: vk policy strong > vault-policy.hcl
    """
    if preset not in _PRESETS:
        print_error(
            GeneratorError(
                f"Unknown policy preset: '{preset}'",
                hint=f"Valid presets: {', '.join(_PRESETS)}",
            )
        )
        raise typer.Exit(1)
    # D-16: stdout only, no Rich formatting — HCL must be valid and machine-readable
    typer.echo(_PRESETS[preset])
