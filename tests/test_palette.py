"""Every colour in every emitted SVG is a palette colour, and the brand
red appears exactly where a source `grant` reserves it — asserted from
both sides (no unauthorised red; no dead grant), with an accent budget.

Grants live in the `.ilx` source (`grant "accent" reason="..."`) and are
carried through to the IR, so this test reads them off the compiled
icons rather than a list maintained here — the reservation cannot drift
from the artwork.
"""

import math
import re

from iso.theme import THEMES, palette_hexes

HEX = re.compile(r"#[0-9a-fA-F]{3,8}")


def _hexes(svg_text):
    return {h.lower() for h in HEX.findall(svg_text)}


def _read(out, sub, icon):
    return (out / sub / icon.filename).read_text()


def _granted(icon, color):
    return any(g[0] == color for g in icon.grants)


def test_all_colours_are_palette_colours(built):
    out, icons = built
    for theme_name, sub in (("dark", "svg"), ("light", "svg-light")):
        palette = palette_hexes(theme_name)
        for icon in icons:
            stray = _hexes(_read(out, sub, icon)) - palette
            assert not stray, f"{icon.slug} ({theme_name}): {stray}"


def test_red_is_reserved(built):
    # Two-sided over both themes: a slug carries accent / accent-dim iff it
    # holds the matching grant.
    out, icons = built
    accent = THEMES["dark"]["accent"].lower()
    dim = THEMES["dark"]["accent-dim"].lower()
    for icon in icons:
        want_accent = _granted(icon, "accent")
        want_dim = _granted(icon, "accent-dim")
        for sub in ("svg", "svg-light"):
            hexes = _hexes(_read(out, sub, icon))
            assert (accent in hexes) == want_accent, \
                f"{icon.slug} ({sub}): accent usage != grant"
            assert (dim in hexes) == want_dim, \
                f"{icon.slug} ({sub}): accent-dim usage != grant"


def test_accent_budget(built):
    # Reserved red is scarce by policy: accent grants stay under 2% of the
    # base leaves. (accent-dim, the softer boundary red, is uncapped.)
    _, icons = built
    accent_grants = [i for i in icons if _granted(i, "accent")]
    cap = max(1, math.ceil(0.02 * len(icons)))
    assert len(accent_grants) <= cap, (
        f"{len(accent_grants)} accent grants exceeds 2% of {len(icons)} "
        f"leaves (cap {cap}): {[i.slug for i in accent_grants]}")


def test_grants_only_reserve_red(built):
    # A grant is only meaningful for the reserved colours; a grant for
    # anything else is a mistake in the source.
    _, icons = built
    for icon in icons:
        for g in icon.grants:
            assert g[0] in ("accent", "accent-dim"), \
                f"{icon.slug}: grant for non-reserved colour {g[0]!r}"
            assert len(g) >= 2 and g[1].strip(), \
                f"{icon.slug}: grant {g[0]!r} lacks a reason"
