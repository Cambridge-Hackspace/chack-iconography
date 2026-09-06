"""Dark and light variants are the same geometry with different greys."""

import re

from iso.theme import THEMES

HEX = re.compile(r"#[0-9a-fA-F]{3,8}")


def test_variants_differ_only_in_colour(built):
    out, icons = built
    for icon in icons:
        dark = (out / "svg" / icon.filename).read_text()
        light = (out / "svg-light" / icon.filename).read_text()
        assert HEX.sub("#", dark) == HEX.sub("#", light), icon.slug


def test_shared_colours_are_byte_identical_across_variants(built):
    out, icons = built
    shared = {THEMES["dark"][t].lower()
              for t in ("accent", "accent-dim", "state-up", "state-degraded",
                        "state-maintenance", "state-primary", "state-purple")}
    for icon in icons:
        dark = {h.lower() for h in HEX.findall(
            (out / "svg" / icon.filename).read_text())}
        light = {h.lower() for h in HEX.findall(
            (out / "svg-light" / icon.filename).read_text())}
        assert dark & shared == light & shared, icon.slug
