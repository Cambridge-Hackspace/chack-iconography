"""Preview laid out by the isolex inheritance tree.

Parses the `.ilx` source forest (parent via `extends`, home via `category`)
and lays it out left-to-right: a category box, the base families that hang
off it as dashed pills, and every concrete icon as a thumbnail beside its
slug. Bases are drawn (dashed) even though they emit nothing, because the
whole point of this sheet is to show the *inheritance*, not just the leaves.

This is a documentation artifact, so it carries text labels — the same
licence the contact sheets take (a shipped icon carries no text; a preview
of them may).
"""

import os
import re

SRC = os.path.join(os.path.dirname(__file__), "..", "src")

ROW, COL, ICON = 48.0, 220.0, 40.0
PADX = 30.0

_DEF = re.compile(r'^(base|icon) "([a-z0-9-]+)"(.*)$')
_EXT = re.compile(r'extends[ =]"([a-z0-9-]+)"')
_CAT = re.compile(r'category "([a-z0-9-]+)"')


def _definitions():
    """name -> {kind, parent, category} for every base/icon in the source.

    Parses by brace-matching the node's own block so an `extends`/`category`
    from a *nested* child cannot be misattributed to its parent.
    """
    defs = {}
    for fname in sorted(os.listdir(SRC)):
        if not fname.endswith(".ilx"):
            continue
        lines = open(os.path.join(SRC, fname)).read().splitlines()
        i = 0
        while i < len(lines):
            m = _DEF.match(lines[i])
            if not m:
                i += 1
                continue
            kind, name, rest = m.groups()
            depth = rest.count("{") - rest.count("}")
            block, j = [rest], i
            while depth > 0 and j + 1 < len(lines):
                j += 1
                block.append(lines[j])
                depth += lines[j].count("{") - lines[j].count("}")
            body = "\n".join(block)
            pm = _EXT.search(body)
            cm = _CAT.search(body)
            defs[name] = dict(kind=kind,
                              parent=pm.group(1) if pm else None,
                              category=cm.group(1) if cm else None)
            i = j + 1
    return defs


def build_forest(icons):
    """(defs, children, cats, category_of) for the inheritance forest.

    A definition hangs off its `extends` parent when that parent is itself a
    definition, otherwise off a synthetic "cat:<category>" root. `icons` is
    the base (non-baked) set, used only to resolve a leaf's home category
    when nothing on its `extends` chain declares one.
    """
    defs = _definitions()
    lookup = {i.slug: i for i in icons}

    # def -> its child definitions, for the descendant category fallback below.
    def_children = {}
    for n, d in defs.items():
        if d["parent"] in defs:
            def_children.setdefault(d["parent"], []).append(n)

    def _chain_category(name):
        seen = set()
        while name and name not in seen:
            seen.add(name)
            c = defs.get(name, {}).get("category")
            if c:
                return c
            name = defs.get(name, {}).get("parent")
        return None

    def category_of(name):
        c = _chain_category(name)
        if c:
            return c
        if name in lookup:  # a concrete icon carries its category in the IR
            return lookup[name].category
        # A category-less base (e.g. `rack-unit`) belongs to whatever its
        # concrete descendants do — borrow from the first one, breadth-first,
        # so the whole family roots under one category box rather than "?".
        queue, seen = list(def_children.get(name, [])), set()
        while queue:
            k = queue.pop(0)
            if k in seen:
                continue
            seen.add(k)
            if k in lookup:
                return lookup[k].category
            cc = _chain_category(k)
            if cc:
                return cc
            queue.extend(def_children.get(k, []))
        return "?"

    children = {}
    for n, d in defs.items():
        parent = d["parent"] if d["parent"] in defs else "cat:" + category_of(n)
        children.setdefault(parent, []).append(n)
    cats = sorted({"cat:" + category_of(n) for n in defs})
    for c in cats:
        children.setdefault(c, [])
    for k in children:
        children[k].sort()
    return defs, children, cats, category_of


def tree_sheet(icons, render, viewbox_of, themes):
    """SVG of the inheritance forest: dark band over light, matching the
    contact sheets. `icons` is the base (non-baked) set."""
    _, children, cats, _ = build_forest(icons)
    lookup = {i.slug: i for i in icons}

    ypos, xdep = {}, {}
    counter = [0]

    def layout(node, depth):
        kids = children.get(node, [])
        if not kids:
            y = counter[0] * ROW + ROW / 2
            counter[0] += 1
        else:
            ys = [layout(k, depth + 1) for k in kids]
            y = (ys[0] + ys[-1]) / 2
        ypos[node], xdep[node] = y, depth
        return y

    for c in cats:
        layout(c, 0)

    maxdepth = max(xdep.values())
    width = PADX + (maxdepth + 1) * COL + 60
    band_h = counter[0] * ROW + 30

    def xof(node):
        return PADX + xdep[node] * COL

    def node_svg(name, y0, theme, fill):
        x, y = xof(name), y0 + ypos[name]
        if name.startswith("cat:"):
            t = name[4:]
            return (f'<rect x="{x:.1f}" y="{y - 9:.1f}" width="90" height="18" '
                    f'rx="4" fill="none" stroke="{fill}"/>'
                    f'<text x="{x + 45:.1f}" y="{y + 3.5:.1f}" '
                    f'font-family="monospace" font-size="11" text-anchor="middle" '
                    f'fill="{fill}">{t}</text>')
        if name not in lookup:  # a base: abstract, emits nothing
            w = 10 + len(name) * 6.4
            return (f'<rect x="{x:.1f}" y="{y - 8:.1f}" width="{w:.1f}" '
                    f'height="16" rx="8" fill="none" stroke="{fill}" '
                    f'stroke-dasharray="2 2" opacity="0.8"/>'
                    f'<text x="{x + 6:.1f}" y="{y + 3:.1f}" font-family="monospace" '
                    f'font-size="9" fill="{fill}" opacity="0.85">{name}</text>')
        icon = lookup[name]
        _, _, w, h = viewbox_of(icon)
        s = min(ICON / w, ICON / h)
        cw, ch = w * s, h * s
        body = render(icon, theme).replace(
            f'width="{w:.0f}" height="{h:.0f}"',
            f'x="{x:.1f}" y="{y - ch / 2:.1f}" width="{cw:.1f}" height="{ch:.1f}"',
            1)
        return (body + f'<text x="{x + ICON + 5:.1f}" y="{y + 3:.1f}" '
                f'font-family="monospace" font-size="9" fill="{fill}">{name}</text>')

    def edges_svg(y0, fill):
        out = []
        for parent, kids in children.items():
            if parent not in ypos:
                continue
            if parent.startswith("cat:"):
                px = xof(parent) + 92
            elif parent not in lookup:
                px = xof(parent) + 10 + len(parent) * 6.4
            else:
                px = xof(parent) + ICON
            py = y0 + ypos[parent]
            midx = px + 10
            for k in kids:
                kx, ky = xof(k), y0 + ypos[k]
                out.append(f'<path d="M{px:.1f},{py:.1f} H{midx:.1f} V{ky:.1f} '
                           f'H{kx - 3:.1f}" fill="none" stroke="{fill}" '
                           f'stroke-width="0.8" opacity="0.45"/>')
        return "".join(out)

    def band(theme_name, ground, fill, y0):
        parts = [f'<rect y="{y0:.1f}" width="{width:.1f}" '
                 f'height="{band_h:.1f}" fill="{ground}"/>']
        parts.append(edges_svg(y0, fill))
        theme = themes[theme_name]
        for name in ypos:
            parts.append(node_svg(name, y0, theme, fill))
        return "".join(parts)

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" '
            f'height="{2 * band_h:.0f}">'
            + band("dark", themes["dark"]["bg-canvas"], "#b0ada4", 0)
            + band("light", "#ffffff", "#555555", band_h) + "</svg>")
