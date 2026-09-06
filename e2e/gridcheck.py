#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = ["playwright==1.62.0"]
# ///
"""Grid-snap check against a real draw.io, both interaction paths.

The view transform is solved exactly from reference cells injected at
known graph coordinates, so every cursor target below is expressed in
graph units regardless of zoom or scroll. Two oracles:

- drop-snap: with alignment guides turned OFF (they outrank the grid by
  design — observed locking a drop's edge to a neighbour's edge and to
  the page centre), drag the same sidebar item to cursor targets that
  differ by sub-grid offsets (0, 13, 30, 47 px in graph units). Pure grid
  snap lands every drop within rounding tolerance of a grid multiple on
  both axes, absorbing the offsets.
- move-snap: same, for dragging an on-canvas cell that starts
  deliberately off-grid.

Drags are human-paced: draw.io positions drops from its dragOver
processing, and synthetic full-speed drags starve it (observed as
free-floating landings).

Exit 0 only if both paths snap. The verdict, residues and screenshots go
to $REAPER_OUT.
"""

import base64
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from playwright.sync_api import sync_playwright

import harness as H

GRID = 69
VM_SVG = Path("dist/svg/iso-virt-vm-1x1.svg")
VM_W, VM_H = 85, 96


def b64(text):
    return base64.b64encode(text.encode()).decode()


def cell(cid, x, y, payload):
    return (f'<mxCell id="{cid}" style="shape=image;aspect=fixed;'
            f'imageAspect=0;image=data:image/svg+xml,{payload};" '
            f'vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" '
            f'width="{VM_W}" height="{VM_H}" as="geometry"/></mxCell>')


def geometries(page):
    xml = H.get_diagram_xml(page)
    out = []
    for c in ET.fromstring(xml).findall(".//mxCell[@vertex='1']"):
        g = c.find("mxGeometry")
        out.append((c.get("id"), float(g.get("x", "0")),
                    float(g.get("y", "0"))))
    return out


def rendered_rects(page):
    return page.evaluate(
        "() => [...document.querySelectorAll("
        "'.geDiagramContainer image')].map(im => {"
        " const r = im.getBoundingClientRect();"
        " return [r.x, r.y, r.width, r.height]; })")


def main():
    payload = b64(VM_SVG.read_text())
    report = {}
    failures = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        oracles = H.Oracles(page)
        H.open_editor(page)
        oracles.drain()
        H.load_library(page, "dist/drawio/iso-all.xml")

        # guides outrank the grid when enabled; this check is about the
        # grid, so switch them off through the Format panel
        guides = page.locator(".geFormatContainer").get_by_text(
            "Guides", exact=True)
        guides.click()
        page.wait_for_timeout(300)

        # --- solve the view transform from three reference cells -------
        refs = (cell("ra", 0, 0, payload) + cell("rb", 690, 0, payload)
                + cell("rc", 0, 345, payload))
        H.set_diagram_xml(
            page,
            '<mxGraphModel grid="1" gridSize="69" background="#0b0b0d">'
            '<root><mxCell id="0"/><mxCell id="1" parent="0"/>'
            + refs + "</root></mxGraphModel>")
        rects = rendered_rects(page)
        assert len(rects) == 3, f"expected 3 reference images, got {rects}"
        ra = min(rects, key=lambda r: r[0] + r[1])
        ax, ay, aw = ra[0], ra[1], ra[2]
        bx = max(r[0] for r in rects)
        cy = max(r[1] for r in rects)
        sx = (bx - ax) / 690
        sy = (cy - ay) / 345
        report["view"] = {"scale_x": sx, "scale_y": sy,
                          "origin": [ax, ay], "ref_width_px": aw}
        if abs(sx - sy) > 0.01:
            failures.append(f"anisotropic view scale {sx} vs {sy}")
        s = (sx + sy) / 2

        def screen(gx, gy):
            return ax + gx * s, ay + gy * s

        # --- drop-snap sweep ------------------------------------------
        entries = json.loads(ET.fromstring(
            Path("dist/drawio/iso-all.xml").read_text()).text)
        vm_idx = [e["title"] for e in entries].index("virt-vm")
        offsets = [0, 13, 30, 47]
        landed = []
        for i, d in enumerate(offsets):
            item = H.sidebar_items(page, "iso-all").nth(vm_idx)
            item.scroll_into_view_if_needed()
            # keep every target well inside the canvas, clear of the
            # format panel and of each other's alignment-guide range
            gx, gy = 120 + i * 2 * GRID + d, 550 + (i % 2) * 2 * GRID + d
            px, py = screen(gx, gy)
            H.drag_item_to_canvas_abs(page, item, px, py, paced=True)
            page.wait_for_timeout(250)
            new = [g for g in geometries(page)
                   if g[0] not in ("ra", "rb", "rc")]
            assert len(new) == i + 1, \
                f"drop {i} did not land a new cell: {new}"
            landed.append(new[-1][1:])
        def on_grid(v):
            return min(v % GRID, GRID - v % GRID) <= 2

        residues = [(round(x % GRID, 1), round(y % GRID, 1))
                    for x, y in landed]
        drop_snaps = all(on_grid(x) and on_grid(y) for x, y in landed)
        report["drop_snap"] = {"targets_offset_by": offsets,
                              "landed": landed, "residues": residues,
                              "verdict": drop_snaps}
        if not drop_snaps:
            failures.append(
                f"sidebar drops do not snap with guides off: "
                f"residues {residues} for cursor offsets {offsets}")

        # --- move-snap: shove an off-grid cell ------------------------
        H.set_diagram_xml(
            page,
            '<mxGraphModel grid="1" gridSize="69" background="#0b0b0d">'
            '<root><mxCell id="0"/><mxCell id="1" parent="0"/>'
            + cell("mv", 100, 100, payload) + "</root></mxGraphModel>")
        page.wait_for_timeout(300)
        ex, ey = screen(600, 50)  # deselect on empty canvas first
        page.mouse.click(ex, ey)
        page.wait_for_timeout(400)
        cx0, cy0 = screen(100 + VM_W / 2, 100 + VM_H / 2)
        cx1, cy1 = screen(413 + VM_W / 2, 313 + VM_H / 2)
        H.drag_on_canvas(page, cx0, cy0, cx1, cy1)
        (_, mx, my), = [g for g in geometries(page) if g[0] == "mv"]
        if (mx, my) == (100.0, 100.0):
            failures.append("move drag never engaged: cell did not move")
        move_res = (round(mx % GRID, 1), round(my % GRID, 1))
        move_snaps = on_grid(mx) and on_grid(my)
        report["move_snap"] = {"from": [100, 100], "landed": [mx, my],
                              "residues": move_res, "verdict": move_snaps}
        if not move_snaps:
            failures.append(
                f"moving an off-grid cell landed off-grid at ({mx}, {my})")

        page.screenshot(path=str(H.OUT / "gridcheck.png"))
        tripped = oracles.drain()
        if tripped:
            failures.append(f"cheap oracles tripped: {tripped}")
        browser.close()

    report["failures"] = failures
    H.write_report("gridcheck-report", report, ok=not failures)
    print(json.dumps(report, indent=1))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
