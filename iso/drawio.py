"""draw.io mxlibrary emitter.

Object icons become image entries with the SVG base64-embedded in the style
(draw.io's own `image=data:image/svg+xml,<base64>` convention — no
";base64" marker, since ";" would split the style string) and aspect=fixed.

Zones (§8) are native draw.io shapes with alpha fills, not raster images,
so they tint whatever sits behind them (handoff decision 2). Links (§9) are
edge-style presets in iso-links.xml.
"""

import base64
import json

from iso.theme import THEMES

# grid unit: the isometric tile width at S=40 (documented in the README)
TILE_W = 69.28


def _entry_xml(style, w, h, extra_cells=""):
    return (
        '<mxGraphModel><root>'
        '<mxCell id="0"/><mxCell id="1" parent="0"/>'
        f'<mxCell id="2" value="" style="{style}" vertex="1" parent="1">'
        f'<mxGeometry width="{w}" height="{h}" as="geometry"/></mxCell>'
        f'{extra_cells}'
        '</root></mxGraphModel>'
    )


def icon_entry(icon, svg_text):
    b64 = base64.b64encode(svg_text.encode()).decode()
    minx, miny, w, h = _viewbox_dims(svg_text)
    style = ("shape=image;verticalLabelPosition=bottom;verticalAlign=top;"
             "html=1;aspect=fixed;imageAspect=0;"
             f"image=data:image/svg+xml,{b64};")
    return {
        "xml": _entry_xml(style, round(w), round(h)),
        "w": round(w),
        "h": round(h),
        "title": icon.slug,
        "aspect": "fixed",
    }


def _viewbox_dims(svg_text):
    vb = svg_text.split('viewBox="', 1)[1].split('"', 1)[0]
    return tuple(float(v) for v in vb.split())


# --- §8 zones: name -> style parts (theme tokens resolved at emit time) ---

def zone_defs(theme):
    zone = theme["bg-zone"]
    alt = theme["bg-zone-alt"]
    outline = theme["outline"]
    base = "shape=isoRectangle;html=1;labelPosition=center;verticalAlign=top;"

    def z(fill, stroke, w=3, extra=""):
        return (f"{base}fillColor={fill};strokeColor={stroke};"
                f"strokeWidth={w};{extra}")

    return {
        "zone-site": (z(zone, outline, 3), 6, 4),
        "zone-rack-row": (z(zone, outline, 2), 8, 2),
        "zone-vlan": (z(zone, theme["link-wan"], 2, "dashed=1;"), 4, 3),
        "zone-subnet": (z(zone, theme["ink-muted"], 2), 4, 3),
        "zone-dmz": (z(zone, theme["state-degraded"], 3,
                       "dashed=1;dashPattern=12 4;"), 4, 3),
        "zone-trust-high": (z(zone, theme["state-up"], 2), 4, 3),
        # accent-dim, not accent: a trust boundary is a fact, not an alarm
        "zone-trust-low": (z(zone, theme["accent-dim"], 2), 4, 3),
        "zone-management": (z(alt, outline, 2, "dashed=1;dashPattern=2 4;"),
                            4, 3),
        "zone-cluster": ("shape=isoCube;html=1;"
                         f"fillColor={theme['ink']};opacity=12;"
                         f"strokeColor={outline};strokeWidth=2;", 4, 4),
        "zone-vpc": (z(alt, theme["link-wan"], 2, "dashPattern=1 3;dashed=1;"),
                     5, 4),
        "zone-availability-zone": (z(zone, outline, 2,
                                     "dashed=1;dashPattern=16 6;"), 5, 4),
        "zone-tenant": (z(alt, theme["ink-muted"], 2), 4, 3),
        "zone-air-gap": (z(zone, outline, 3, "dashed=1;dashPattern=4 12;"),
                         4, 3),
    }


def zone_entry(name, style, tiles_w, tiles_h):
    w = round(TILE_W * tiles_w)
    h = round(TILE_W * tiles_h / 2)
    return {"xml": _entry_xml(style, w, h), "w": w, "h": h, "title": name}


# --- §9 links: name -> draw.io edge style (theme tokens at emit time) ---

def edge_defs(theme):
    muted = theme["ink-muted"]
    e = "edgeStyle=none;html=1;rounded=0;endArrow=none;"

    def s(color, width, extra=""):
        return f"{e}strokeColor={color};strokeWidth={width};{extra}"

    return {
        "link-copper": s(muted, 2),
        "link-copper-10g": s(muted, 3.5),
        "link-fibre": s(theme["link-fibre"], 2),
        "link-fibre-100g": s(theme["link-fibre"], 3.5),
        "link-wireless": s(muted, 2, "dashed=1;dashPattern=1 4;"),
        "link-wan": s(theme["link-wan"], 3),
        "link-internet-uplink": s(theme["link-wan"], 2,
                                  "endArrow=classic;"),
        "link-vpn-tunnel": s(theme["link-vpn"], 2,
                             "shape=link;dashed=1;"),
        "link-lag-trunk": s(muted, 2, "shape=link;"),
        "link-replication": s(theme["state-purple"], 2,
                              "dashed=1;dashPattern=2 3;endArrow=classic;"),
        "link-heartbeat": s(theme["accent"], 2,
                            "dashed=1;dashPattern=1 3;"
                            "startArrow=classic;endArrow=classic;"),
        "link-management-oob": s(theme["outline"], 2,
                                 "dashed=1;dashPattern=8 3 1 3;"),
        "link-serial-console": s(theme["outline"], 1,
                                 "dashed=1;dashPattern=8 3 1 3;"),
        "link-virtual": s(theme["ink"], 1, "opacity=40;"),
        "link-redundant": s(muted, 2, "shape=link;"),
        "link-planned": s(muted, 2, "dashed=1;opacity=50;"),
        "link-blocked": s(muted, 2, "dashed=1;"),
        # Wave 2 connection presets (paired with the net-* tunnel/routing
        # tiles): the encapsulated path, the label-switched path, and the
        # two routing-adjacency kinds. Secure tunnels reuse link-vpn-tunnel.
        "link-gre-tunnel": s(theme["link-vpn"], 2, "shape=link;"),
        "link-mpls-lsp": s(theme["state-purple"], 2,
                           "shape=link;endArrow=classic;"),
        "link-bgp-peering": s(theme["link-wan"], 2,
                              "startArrow=classic;endArrow=classic;"),
        "link-igp-adjacency": s(muted, 2, "dashed=1;dashPattern=4 2;"),
    }


def edge_entry(name, style, blocked_badge_b64=None):
    extra = ""
    if blocked_badge_b64:
        # the red X badge rides the midpoint: a root-level sibling cell
        # whose parent is the edge. Cells never nest inside each other in
        # mxGraphModel XML — draw.io's codec rejects that, silently in the
        # sidebar and loudly on the console (found live by Tier A).
        extra = (
            '<mxCell id="3" value="" style="shape=image;html=1;aspect=fixed;'
            f'imageAspect=0;image=data:image/svg+xml,{blocked_badge_b64};" '
            'vertex="1" connectable="0" parent="2">'
            '<mxGeometry width="24" height="24" relative="1" as="geometry">'
            '<mxPoint x="-12" y="-12" as="offset"/></mxGeometry></mxCell>'
        )
    xml = (
        '<mxGraphModel><root>'
        '<mxCell id="0"/><mxCell id="1" parent="0"/>'
        f'<mxCell id="2" value="" style="{style}" edge="1" parent="1">'
        '<mxGeometry relative="1" as="geometry">'
        '<mxPoint x="0" y="52" as="sourcePoint"/>'
        '<mxPoint x="104" y="0" as="targetPoint"/></mxGeometry></mxCell>'
        f'{extra}'
        '</root></mxGraphModel>'
    )
    return {"xml": xml, "w": 104, "h": 52, "title": name}


def library_xml(entries):
    # draw.io JSON.parses the element's text content, so the JSON must be
    # XML-escaped here and is unescaped by any conforming XML parser.
    from xml.sax.saxutils import escape
    payload = escape(json.dumps(entries, separators=(",", ":")))
    return "<mxlibrary>" + payload + "</mxlibrary>"


def core_slugs():
    """The curated iso-core palette, read from iso/iso-core.txt."""
    import os
    path = os.path.join(os.path.dirname(__file__), "iso-core.txt")
    out = []
    for line in open(path):
        s = line.strip()
        if s and not s.startswith("#"):
            out.append(s)
    return out


def build_libraries(icons, svg_of, theme_name="dark"):
    """Return {filename: xml}. svg_of(icon) -> rendered SVG text.

    Per-category libraries plus two aggregates: iso-all.xml (everything,
    for the tarball) and iso-core.xml (the curated starter palette, the
    Downloads page's one direct-grab file)."""
    theme = THEMES[theme_name]
    by_slug_icon = {i.slug: i for i in icons}
    by_cat = {}
    for icon in icons:
        by_cat.setdefault(icon.category, []).append(icon)

    libs = {}
    all_entries = []
    entry_of = {}
    for cat in sorted(by_cat):
        entries = [icon_entry(i, svg_of(i)) for i in by_cat[cat]]
        for i, e in zip(by_cat[cat], entries):
            entry_of[i.slug] = e
        libs[f"iso-{cat}.xml"] = library_xml(entries)
        all_entries += entries

    zone_entries = [zone_entry(n, st, w, h)
                    for n, (st, w, h) in sorted(zone_defs(theme).items())]
    libs["iso-zone.xml"] = library_xml(zone_entries)
    all_entries += zone_entries

    from iso.registry import by_slug
    badge_b64 = base64.b64encode(
        svg_of(by_slug("state-down")).encode()).decode()
    edge_entries = [
        edge_entry(n, st, badge_b64 if n == "link-blocked" else None)
        for n, st in sorted(edge_defs(theme).items())]
    libs["iso-links.xml"] = library_xml(edge_entries)

    libs["iso-all.xml"] = library_xml(all_entries + edge_entries)

    core = core_slugs()
    missing = [s for s in core if s not in by_slug_icon]
    if missing:
        raise ValueError(f"iso-core.txt names unknown slugs: {missing}")
    core_entries = [entry_of[s] for s in core]
    libs["iso-core.xml"] = library_xml(
        core_entries + zone_entries + edge_entries)
    return libs
