"""The baked-state axis (src/axes.ilx): every primary operational object
expands into -down/-degraded/-maintenance/-planned variants, emitted to
svg-states/ and kept out of the draw.io libraries.

These oracles cover what the base-only suite (which iterates the canonical
170) cannot see: that the variants exist, composite a status badge, stay
inside the palette, and — the load-bearing one — that red still means
"down". A -down variant legitimately carries the accent (it composites
the red state-down badge); no other state may introduce it.
"""

import re

import pytest

from build import partition
from iso.registry import all_icons
from iso.render_svg import render
from iso.theme import THEMES

HEX = re.compile(r"#[0-9a-fA-F]{3,8}")

# Base slugs that legitimately carry brand red in their own right (§16);
# their state variants inherit it. Mirrors tests/test_palette.py.
ACCENT_DIM_BASES = {"net-firewall", "net-utm"}


@pytest.fixture(scope="session")
def baked():
    _, variants = partition(all_icons())
    return variants


def _split(slug):
    suffix = slug.rsplit("-", 1)[1]
    return slug[: -len(suffix) - 1], suffix


def _hexes(svg):
    return {h.lower() for h in HEX.findall(svg)}


def test_every_primary_expands_fourfold(baked):
    # Don't hardcode the primary count (it shifts as categories are
    # recast); instead require the axis to be complete and total: every
    # base that has any state variant has all four, and nothing else.
    assert baked, "no baked state variants emitted"
    suffixes = {_split(i.slug)[1] for i in baked}
    assert suffixes == {"down", "degraded", "maintenance", "planned"}
    by_base = {}
    for i in baked:
        by_base.setdefault(_split(i.slug)[0], set()).add(_split(i.slug)[1])
    incomplete = {b: sorted(s) for b, s in by_base.items()
                  if s != {"down", "degraded", "maintenance", "planned"}}
    assert not incomplete, f"primaries missing state variants: {incomplete}"
    assert len(baked) == 4 * len(by_base)


def test_each_variant_composites_a_badge_group(baked):
    # The overlay is emitted as a translated+scaled <g>; a variant that
    # silently dropped its badge would have none.
    for icon in baked:
        svg = render(icon, THEMES["dark"])
        assert "<g transform=" in svg, icon.slug


def test_variants_stay_within_the_palette(baked):
    for theme_name in ("dark", "light"):
        palette = {v.lower() for v in THEMES[theme_name].values()
                   if v.startswith("#")}
        for icon in baked:
            stray = _hexes(render(icon, THEMES[theme_name])) - palette
            assert not stray, f"{icon.slug} ({theme_name}): {stray}"


def test_red_means_down(baked):
    # Two-sided: -down MUST carry accent; every other state MUST NOT
    # introduce it (only a base that already owns red keeps it).
    accent = THEMES["dark"]["accent"].lower()
    for icon in baked:
        base, suffix = _split(icon.slug)
        hexes = _hexes(render(icon, THEMES["dark"]))
        if suffix == "down":
            assert accent in hexes, f"{icon.slug} should carry accent"
        else:
            assert accent not in hexes, f"{icon.slug} carries accent"


def test_accent_dim_is_confined_to_the_flame_firewalls(baked):
    dim = THEMES["dark"]["accent-dim"].lower()
    for icon in baked:
        base, _ = _split(icon.slug)
        hexes = _hexes(render(icon, THEMES["dark"]))
        if base in ACCENT_DIM_BASES:
            assert dim in hexes, f"{icon.slug} should carry accent-dim"
        else:
            assert dim not in hexes, f"{icon.slug} carries accent-dim"
