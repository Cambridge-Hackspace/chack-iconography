"""The tree preview places every icon under its real inheritance parent.

The oracle that matters here is *placement*: an icon that `extends` a base
must hang under that base in the sheet, not float up to the category root.
`treeview` learns the parent by brace-matching each definition's block; this
test learns it by a deliberately different method — nearest-preceding
top-level header — and asserts the two agree. Agreement is the check; a
brace-matcher bug that dropped an `extends` would drop the icon to its
category root and this test would see the disagreement.
"""

import os
import re
import xml.etree.ElementTree as ET

from build import partition
from iso.registry import all_icons
from iso.render_svg import render, viewbox_of
from iso.theme import THEMES
from iso.treeview import build_forest, tree_sheet

SRC = os.path.join(os.path.dirname(__file__), "..", "src")

_HEADER = re.compile(r'^(?:base|icon) "([a-z0-9-]+)"')
_EXTENDS = re.compile(r'^\s+extends[ =]"([a-z0-9-]+)"')


def _base_icons():
    base, _ = partition(all_icons())
    return base


def _extends_by_nearest_header():
    """slug -> extends-target, attributing each indented `extends` to the
    nearest preceding column-0 `base`/`icon` header. Independent of
    treeview's brace-matcher on purpose."""
    edges = {}
    for fname in sorted(os.listdir(SRC)):
        if not fname.endswith(".ilx"):
            continue
        cur = None
        for line in open(os.path.join(SRC, fname)):
            h = _HEADER.match(line)
            if h:
                cur = h.group(1)
                continue
            e = _EXTENDS.match(line)
            if e and cur and cur not in edges:
                edges[cur] = e.group(1)
    return edges


def _nested_svgs(svg):
    root = ET.fromstring(svg)
    return [el for el in root.iter()
            if el.tag.split("}")[-1] == "svg" and el is not root]


def _labels(svg):
    root = ET.fromstring(svg)
    return [el.text for el in root.iter() if el.tag.split("}")[-1] == "text"]


def test_forest_places_each_icon_under_its_real_parent():
    defs, children, _, _ = build_forest(_base_icons())
    for slug, target in _extends_by_nearest_header().items():
        if target in defs:  # parent is a definition -> child hangs under it
            assert slug in children.get(target, []), \
                f"{slug} extends {target} but is not placed under it"


def test_no_family_has_an_unresolved_category():
    _, _, cats, _ = build_forest(_base_icons())
    assert "cat:?" not in cats, "a base family resolved to no category"


def test_every_base_icon_appears_once_per_band():
    icons = _base_icons()
    nested = _nested_svgs(tree_sheet(icons, render, viewbox_of, THEMES))
    # Two bands (dark over light), one thumbnail per icon per band.
    assert len(nested) == 2 * len(icons)


def test_every_base_icon_is_labelled():
    icons = _base_icons()
    labels = set(_labels(tree_sheet(icons, render, viewbox_of, THEMES)))
    missing = {i.slug for i in icons} - labels
    assert not missing, missing


def test_tree_sheet_is_deterministic():
    icons = _base_icons()
    a = tree_sheet(icons, render, viewbox_of, THEMES)
    b = tree_sheet(icons, render, viewbox_of, THEMES)
    assert a == b
