"""Footprint baselines land at one fixed offset from the frame bottom, so
icons align on the draw.io grid. The projection is duplicated here on
purpose: the doc rule is the source, not the renderer's own helper.
"""

import math
import xml.etree.ElementTree as ET

S = 40.0
PAD = 8.0


def test_baseline_offset_is_constant(built):
    out, icons = built
    for icon in icons:
        if not icon.footprint:
            continue
        fp_w, fp_d, _ = icon.footprint
        base_y = (fp_w + fp_d) * 0.5 * S  # lowest corner: (fp_w, fp_d, 0)
        root = ET.fromstring((out / "svg" / icon.filename).read_text())
        miny_h = root.get("viewBox").split()
        bottom = float(miny_h[1]) + float(miny_h[3])
        assert math.isclose(bottom - base_y, PAD, abs_tol=0.11), icon.slug
