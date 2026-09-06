"""Palette token -> hex maps for both variants, and per-category brand tints.

Themed to Cambridge Hackspace (cambridgehackspace.com). The brand is a
four-circle maker mark in red, blue, gold and green on a light ground. Those
four colours were sampled from the site's own logo and index images on
2026-09-05: red `#c34e4b`, blue `#3d84af`, gold `#d8a300`, green `#89b108`.

Unlike a monochrome hardware pack, chack wears the brand *on the objects*:
each category is coloured by domain -- blue for compute/services, green for
storage/physical, gold for network, red for security -- so a diagram reads
its shape of the world in the brand's own colours. The face shades and the
(coloured) outline of every object are derived from that one hue, top face
lightest, so the isometric shading still reads. People and annotations stay
neutral so the colour means something.

The *exact* alarm red (`accent` `#c34e4b`) stays reserved for "wrong or
hostile" and is governed from source; security bodies wear tints of red,
never the pure alarm hex, so a real fault still pops against them.

Light is the site's own footing and the pack's primary; the dark variant
mirrors it on a charcoal ground.
"""

# ---- brand ---------------------------------------------------------------

BRAND = {
    "red": "#c34e4b",
    "blue": "#3d84af",
    "gold": "#d8a300",
    "green": "#89b108",
}


def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*(max(0, min(255, round(c))) for c in rgb))


def _mix(a, b, t):
    """Blend hex a toward hex b by t in [0,1]."""
    ra, rb = _rgb(a), _rgb(b)
    return _hex(tuple(ra[i] + (rb[i] - ra[i]) * t for i in range(3)))


_WHITE, _BLACK = "#ffffff", "#000000"


def _family(base, light):
    """Four isometric shades from one brand hue: top (lit) lightest, then
    right, then left (shadowed), plus a saturated outline of the same hue."""
    if light:
        return {
            "body-top": _mix(base, _WHITE, 0.70),
            "body-right": _mix(base, _WHITE, 0.52),
            "body-left": _mix(base, _WHITE, 0.34),
            "outline": _mix(base, _BLACK, 0.30),
        }
    return {
        "body-top": _mix(base, _BLACK, 0.26),
        "body-right": _mix(base, _BLACK, 0.42),
        "body-left": _mix(base, _BLACK, 0.55),
        "outline": _mix(base, _WHITE, 0.32),
    }


# Neutral family: warm-grey hardware for people and annotations, where a
# domain colour would be noise. Given explicitly (not derived) so it reads
# as "no domain" rather than a fifth colour.
_NEUTRAL_LIGHT = {
    "body-top": "#e7e6e2",
    "body-right": "#d3d1cb",
    "body-left": "#bfbdb5",
    "outline": "#3a3a38",
}
_NEUTRAL_DARK = {
    "body-top": "#4b4b48",
    "body-right": "#3a3a37",
    "body-left": "#2c2c29",
    "outline": "#6c6c68",
}

# category -> brand hue (or "neutral"). Categories that draw isometric
# bodies get a domain colour; figures (actor) and annotation layers
# (badge/state/legend/chrome) stay neutral so the colour carries meaning.
CATEGORY_HUE = {
    "compute": "blue", "svc": "blue", "k8s": "blue", "virt": "blue",
    "ext": "blue",
    "stor": "green", "facility": "green", "edge": "green",
    "endpoint": "green", "fab": "green",
    "net": "gold", "link": "gold",
    "sec": "red",
    "actor": "neutral", "badge": "neutral", "state": "neutral",
    "legend": "neutral", "chrome": "neutral",
}


def _families(light):
    fams = {hue: _family(base, light) for hue, base in BRAND.items()}
    fams["neutral"] = _NEUTRAL_LIGHT if light else _NEUTRAL_DARK
    return fams


# ---- base palettes (grounds, ink, accent, states, links) -----------------

DARK = {
    "none": "none",
    "bg-canvas": "#1b1c1e",     # neutral charcoal ground
    "bg-zone": "#242629",       # zone/site tiles, one step up
    "bg-zone-alt": "#2e3034",   # nested zone, another step up
    # default (neutral) hardware faces; per-category tints override these
    "body-top": _NEUTRAL_DARK["body-top"],
    "body-right": _NEUTRAL_DARK["body-right"],
    "body-left": _NEUTRAL_DARK["body-left"],
    "outline": _NEUTRAL_DARK["outline"],
    "ink": "#ececee",
    "ink-muted": "#a7a9ad",
    "accent": "#c34e4b",        # CHS brand red -- reserved (see governance)
    "accent-dim": "#8f3634",    # red at rest (unlit/critical-but-planned)
    "virt": "#ececee",          # translucent objects; opacity lives in the IR
    "shadow": "#000000",        # legend-shadow only; 35% alpha in the IR
    # state colours (§10 / §16) -- the brand's non-body colours, semantic
    "state-up": "#89b108",         # CHS green
    "state-degraded": "#d8a300",   # CHS gold
    "state-maintenance": "#3d84af",  # CHS blue
    "state-primary": "#c9a227",    # neutral gold, distinct from degraded
    "state-purple": "#9b6fd6",     # rollback anchor, replication
    # link colours (§9 / §16)
    "link-fibre": "#d8a300",       # CHS gold
    "link-wan": "#3d84af",         # CHS blue
    "link-vpn": "#7a5bc4",
}

LIGHT = dict(
    DARK,
    **{
        "bg-canvas": "#ffffff",
        "bg-zone": "#f4f5f6",
        "bg-zone-alt": "#e8eaec",
        "body-top": _NEUTRAL_LIGHT["body-top"],
        "body-right": _NEUTRAL_LIGHT["body-right"],
        "body-left": _NEUTRAL_LIGHT["body-left"],
        "outline": _NEUTRAL_LIGHT["outline"],
        "ink": "#26282b",
        "ink-muted": "#5c5e62",
        "virt": "#26282b",  # inverts with ink or glyphs vanish on white
    },
)

THEMES = {"dark": DARK, "light": LIGHT}

# Precomputed hue families per variant, for object_theme / palette_hexes.
_FAMILIES = {"dark": _families(False), "light": _families(True)}


def object_theme(theme_name, category):
    """The theme an object of `category` renders with: the base palette with
    its body faces and outline replaced by the category's brand family. A
    category with no mapping keeps the neutral base faces."""
    base = THEMES[theme_name]
    hue = CATEGORY_HUE.get(category)
    if hue is None:
        return base
    return {**base, **_FAMILIES[theme_name][hue]}


def palette_hexes(theme_name):
    """Every hex any object of any category can emit in this variant: the
    base palette plus every category family. The palette-conformance oracle
    reads this so category tints are first-class, not strays."""
    out = {v.lower() for v in THEMES[theme_name].values() if v.startswith("#")}
    for fam in _FAMILIES[theme_name].values():
        out |= {v.lower() for v in fam.values()}
    return out
