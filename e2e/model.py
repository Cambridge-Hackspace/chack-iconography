"""Tier 9 shadow model and invariants. Pure stdlib — no Playwright — so
the workstation suite can self-test the oracle without any stack
(testing-methodology §11: an invariant that never fires is
indistinguishable from a passing suite).

The model is deliberately partial: it tracks per-icon payload hashes,
counts, aspect flags and edge styles — the things the pack's guarantees
are about — and nothing else.
"""

import base64
import hashlib
import re
import xml.etree.ElementTree as ET
from collections import Counter


def payload_hash(svg_text):
    return hashlib.sha256(svg_text.encode()).hexdigest()[:16]


class ShadowModel:
    def __init__(self, grid=69):
        self.grid = grid
        self.icons = Counter()   # payload hash -> expected count on canvas
        self.edges = Counter()   # frozenset of style tokens -> count

    def drop(self, svg_text):
        self.icons[payload_hash(svg_text)] += 1

    def remove(self, svg_text):
        h = payload_hash(svg_text)
        self.icons[h] -= 1
        if self.icons[h] <= 0:
            del self.icons[h]

    def connect(self, style):
        self.edges[_style_key(style)] += 1


def _style_key(style):
    return frozenset(t for t in style.split(";")
                     if t and not t.startswith("image="))


def _cells(xml_text):
    root = ET.fromstring(xml_text)
    return root.findall(".//mxCell")


def check(model, xml_text, dist_svgs=None):
    """Diff the shadow model against a saved diagram. Returns violations
    as strings; empty means coherent. dist_svgs: optional {hash: svg_text}
    of legitimate payloads for byte-fidelity checking."""
    violations = []
    seen_icons = Counter()
    seen_edges = Counter()

    for cell in _cells(xml_text):
        style = cell.get("style") or ""
        if cell.get("edge") == "1":
            seen_edges[_style_key(style)] += 1
            continue
        m = re.search(r"image=data:image/svg\+xml,([A-Za-z0-9+/=]+)", style)
        if not m:
            continue
        try:
            svg = base64.b64decode(m.group(1), validate=True).decode()
        except Exception as e:
            violations.append(f"undecodable image payload: {e}")
            continue
        h = payload_hash(svg)
        seen_icons[h] += 1
        if "aspect=fixed" not in style:
            violations.append(f"icon {h} lost aspect=fixed")
        if dist_svgs is not None and h not in dist_svgs:
            violations.append(f"icon payload {h} is not a pack SVG "
                              f"byte-for-byte (re-encoded in transit?)")
        # Absolute grid position is deliberately not an invariant: draw.io
        # snaps its drop *reference point*, not the geometry corner (found
        # live — corners land off-grid by half-extents by design). The
        # pack's real claim, that footprints tile under snap, is relative
        # alignment, and Tier A asserts it directly.

    if seen_icons != model.icons:
        violations.append(
            f"icon census mismatch: model {dict(model.icons)} "
            f"vs canvas {dict(seen_icons)}")
    if seen_edges != model.edges:
        violations.append(
            f"edge census mismatch: model has {sum(model.edges.values())} "
            f"edge(s), canvas {sum(seen_edges.values())}, or styles differ")
    return violations


def check_export_palette(svg_text, palette_hexes):
    """Exported SVG must contain only pack colours — the red-reservation
    rule re-checked after draw.io's own re-encoding."""
    found = {h.lower() for h in re.findall(r"#[0-9a-fA-F]{6}", svg_text)}
    stray = found - {h.lower() for h in palette_hexes}
    return [f"exported SVG contains non-palette colours: {sorted(stray)}"] \
        if stray else []
