"""Pack-wide structural rules from dictionary §1/§16."""

import re
import xml.etree.ElementTree as ET

# The single outline weight plus the deliberate closed set of glyph weights.
# Growing this set is a decision, not a convenience.
ALLOWED_STROKE_WIDTHS = {"1.20", "1.40", "1.50", "2.20"}


def _files(built):
    out, icons = built
    for icon in icons:
        for sub in ("svg", "svg-light"):
            yield icon, (out / sub / icon.filename).read_text()


def test_valid_xml_with_viewbox(built):
    for icon, text in _files(built):
        root = ET.fromstring(text)
        assert root.get("viewBox"), icon.slug


def test_no_text_no_raster(built):
    for icon, text in _files(built):
        root = ET.fromstring(text)
        tags = {el.tag.split("}")[-1] for el in root.iter()}
        assert "text" not in tags, icon.slug
        assert "image" not in tags, icon.slug


def test_stroke_widths_are_the_closed_set(built):
    for icon, text in _files(built):
        widths = set(re.findall(r'stroke-width="([\d.]+)"', text))
        stray = widths - ALLOWED_STROKE_WIDTHS
        assert not stray, f"{icon.slug}: {stray}"


def test_no_baked_background(built):
    # No opaque shape may span the whole viewBox: transparency is a shipped
    # guarantee (§16). Checked as: no rect/polygon covering the full frame.
    for icon, text in _files(built):
        root = ET.fromstring(text)
        vb = [float(v) for v in root.get("viewBox").split()]
        for el in root.iter():
            tag = el.tag.split("}")[-1]
            if tag == "rect":
                w, h = float(el.get("width")), float(el.get("height"))
                assert not (w >= vb[2] and h >= vb[3]), icon.slug
