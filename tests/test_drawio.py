"""draw.io libraries: parse, decode, and round-trip against the dist SVGs."""

import base64
import json
import re
import xml.etree.ElementTree as ET

import pytest

from build import partition
from iso.drawio import build_libraries, edge_defs, zone_defs
from iso.registry import all_icons
from iso.render_svg import render
from iso.theme import THEMES


@pytest.fixture(scope="session")
def libs():
    # Libraries carry the canonical (base) icons only; baked-state variants
    # are static-export SVGs and are excluded by design.
    icons, _ = partition(all_icons())
    return icons, build_libraries(
        icons, lambda i: render(i, THEMES["dark"]), "dark")


def _entries(xml_text):
    root = ET.fromstring(xml_text)
    assert root.tag == "mxlibrary"
    return json.loads(root.text)


def test_every_library_parses_and_counts_match(libs):
    icons, built = libs
    by_cat = {}
    for i in icons:
        by_cat.setdefault(i.category, []).append(i)
    for cat, members in by_cat.items():
        entries = _entries(built[f"iso-{cat}.xml"])
        assert len(entries) == len(members), cat
    assert len(_entries(built["iso-zone.xml"])) == len(
        zone_defs(THEMES["dark"]))
    assert len(_entries(built["iso-links.xml"])) == len(
        edge_defs(THEMES["dark"]))
    total = len(icons) + len(zone_defs(THEMES["dark"])) + len(
        edge_defs(THEMES["dark"]))
    assert len(_entries(built["iso-all.xml"])) == total


def test_iso_core_is_the_curated_palette(libs):
    from iso.drawio import core_slugs
    icons, built = libs
    core = core_slugs()
    known = {i.slug for i in icons}
    # every core slug is a real base icon (no rot / typos)
    assert all(s in known for s in core), \
        [s for s in core if s not in known]
    # core is a strict, smaller subset of the full set
    assert len(core) < len(icons), (len(core), len(icons))
    entries = _entries(built["iso-core.xml"])
    expected = len(core) + len(zone_defs(THEMES["dark"])) + len(
        edge_defs(THEMES["dark"]))
    assert len(entries) == expected, (len(entries), expected)
    # iso-all carries strictly more than core
    assert len(_entries(built["iso-all.xml"])) > len(entries)


def test_image_payloads_round_trip_to_dist_svgs(libs):
    icons, built = libs
    by_slug = {i.slug: i for i in icons}
    entries = _entries(built["iso-all.xml"])
    checked = 0
    for e in entries:
        m = re.search(r"image=data:image/svg\+xml,([A-Za-z0-9+/=]+);",
                      e["xml"])
        if not m or e["title"] not in by_slug:
            continue
        decoded = base64.b64decode(m.group(1)).decode()
        expected = render(by_slug[e["title"]], THEMES["dark"])
        assert decoded == expected, e["title"]
        checked += 1
    assert checked == len(icons)


def test_every_entry_model_parses_and_images_are_aspect_fixed(libs):
    _, built = libs
    for name, xml_text in built.items():
        for e in _entries(xml_text):
            model = ET.fromstring(e["xml"])
            cells = model.findall(".//mxCell[@style]")
            assert cells, f"{name}:{e['title']}"
            for c in cells:
                style = c.get("style")
                if "image=" in style:
                    assert "aspect=fixed" in style, f"{name}:{e['title']}"


def test_edge_presets_are_edges_with_valid_styles(libs):
    _, built = libs
    for e in _entries(built["iso-links.xml"]):
        model = ET.fromstring(e["xml"])
        edge = model.find(".//mxCell[@edge='1']")
        assert edge is not None, e["title"]
        for kv in filter(None, edge.get("style").split(";")):
            assert re.fullmatch(r"[A-Za-z]+=[^;]*|[A-Za-z]+", kv), \
                f"{e['title']}: {kv}"


def test_zone_fills_are_theme_colours_with_alpha_semantics(libs):
    _, built = libs
    palette = {v.lower() for v in THEMES["dark"].values()
               if v.startswith("#")}
    for e in _entries(built["iso-zone.xml"]):
        model = ET.fromstring(e["xml"])
        style = model.find(".//mxCell[@style]").get("style")
        for key in ("fillColor", "strokeColor"):
            m = re.search(rf"{key}=(#[0-9a-fA-F]{{6}})", style)
            assert m, f"{e['title']}: {key}"
            assert m.group(1).lower() in palette, f"{e['title']}: {key}"


def test_cells_never_nest_inside_cells(libs):
    # draw.io's codec rejects an mxCell element inside another mxCell —
    # silently in the sidebar, loudly on the console. Found live by Tier A
    # on the link-blocked badge; children belong at root level with a
    # parent attribute.
    _, built = libs
    for name, xml_text in built.items():
        for e in _entries(xml_text):
            model = ET.fromstring(e["xml"])
            for cell in model.iter("mxCell"):
                assert cell.find("mxCell") is None, f"{name}:{e['title']}"
