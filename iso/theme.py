"""Palette token -> hex maps for both variants.

Themed to Cambridge Hackspace (cambridgehackspace.com). The brand is a
four-circle maker mark in red, blue, gold and green on a light ground, with
`#333` structural rules from the site CSS. The four brand colours were
sampled from the site's own logo and index images on 2026-09-05:
red `#c34e4b`, blue `#3d84af`, gold `#d8a300`, green `#89b108`.

The pack ships light-forward (the site's own footing) but keeps a dark
variant: light overrides only the greys, ink and `virt`; accent, accent-dim
and every state/link colour are shared between variants (dictionary §16).

Red (`accent`/`accent-dim`) is reserved for "something is wrong or hostile"
and is governed by source `grant`s -- so the brand red is never spent on
decoration. The other three brand colours carry the neutral state/link
semantics (green = up, gold = fibre/degraded, blue = WAN/maintenance).
"""

DARK = {
    "none": "none",
    "bg-canvas": "#1b1c1e",     # neutral charcoal ground
    "bg-zone": "#242629",       # zone/site tiles, one step up
    "bg-zone-alt": "#2e3034",   # nested zone, another step up
    "body-top": "#4b4d51",
    "body-right": "#3a3c40",
    "body-left": "#2c2e32",
    "outline": "#6b6d72",
    "ink": "#ececee",
    "ink-muted": "#a7a9ad",
    "accent": "#c34e4b",        # CHS brand red -- reserved (see governance)
    "accent-dim": "#8f3634",    # red at rest (unlit/critical-but-planned)
    "virt": "#ececee",          # translucent objects; opacity lives in the IR
    "shadow": "#000000",        # legend-shadow only; 35% alpha in the IR
    # state colours (§10 / §16) -- identical in both variants
    "state-up": "#89b108",         # CHS green
    "state-degraded": "#d8a300",   # CHS gold
    "state-maintenance": "#3d84af",  # CHS blue
    "state-primary": "#c9a227",    # neutral gold, distinct from degraded
    "state-purple": "#9b6fd6",     # rollback anchor, replication
    # link colours (§9 / §16) -- identical in both variants
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
        "body-top": "#e4e6e8",
        "body-right": "#d2d4d7",
        "body-left": "#c0c2c6",
        "outline": "#333333",   # CHS structural grey (site CSS)
        "ink": "#26282b",
        "ink-muted": "#5c5e62",
        "virt": "#26282b",  # inverts with ink or glyphs vanish on white (POC finding)
    },
)

THEMES = {"dark": DARK, "light": LIGHT}
