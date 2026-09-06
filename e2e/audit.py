#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = ["playwright==1.62.0"]
# ///
"""Tier A: deterministic library audit against a real draw.io.

Per library: load through the real UI, assert the rendered sidebar count
equals the file's entry count (draw.io drops malformed entries silently —
the defect class no schema test can see), verify every preview actually
rendered its embedded image, drag the first entry onto the canvas, and
screenshot the palette as Tier-11 human evidence. Then drop one icon per
category on dark and light grounds and screenshot both.

Exit status is the verdict; the JSON report carries the detail.
"""

import base64
import json
import math
import os
import random
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from playwright.sync_api import sync_playwright

import harness as H

LIBS = sorted(Path("dist/drawio").glob("iso-*.xml"))
SCREENS = H.OUT / "screens"

# Preview-paint bbox checks are the per-item cost that does not scale to
# thousands of icons. Sidebar-count and zero-console stay exhaustive
# (cheap, and the defect class no schema test can see); paint is sampled
# at 10% per library, seeded and logged, with full depth opt-in via
# AUDIT_FULL_PAINT. The seed comes from AUDIT_SEED, else seeds.json.
PAINT_SAMPLE = 0.10


def _paint_seed():
    env = os.environ.get("AUDIT_SEED")
    if env:
        return int(env)
    return json.loads((Path(__file__).parent / "seeds.json")
                      .read_text())["seeds"][0]


def file_entries(path):
    root = ET.fromstring(path.read_text())
    return json.loads(root.text)


def main():
    assert LIBS, "dist/drawio is empty — did the build verb run?"
    failures = []
    seed = _paint_seed()
    rng = random.Random(seed)
    full_paint = bool(os.environ.get("AUDIT_FULL_PAINT"))
    report = {"libraries": {}, "paint_sample_seed": seed,
              "paint_full": full_paint}
    print(f"tier A: paint sampling {'FULL' if full_paint else '10%'} "
          f"(seed {seed})", file=sys.stderr)
    SCREENS.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch_persistent_context(
            user_data_dir=str(H.STATE / "profile"),
            viewport={"width": 1600, "height": 1000})
        page = browser.pages[0] if browser.pages else browser.new_page()
        oracles = H.Oracles(page)
        H.open_editor(page)
        # Baseline: whatever the bare app emits before the pack is ever
        # loaded is the app's own noise (observed: one 404 for /null at
        # startup). Recorded, not asserted; everything after first pack
        # contact still fails the audit.
        report["app_baseline_noise"] = oracles.drain()

        for lib in LIBS:
            name = lib.stem
            entries = file_entries(lib)
            try:
                H.load_library(page, str(lib))
                items = H.sidebar_items(page, name)
                rendered = items.count()
            except Exception:
                page.screenshot(path=str(SCREENS / f"FAIL-{name}.png"))
                (H.OUT / f"FAIL-{name}.html").write_text(page.content())
                raise
            lib_report = {"file_entries": len(entries),
                          "sidebar_rendered": rendered}
            if rendered != len(entries):
                failures.append(
                    f"{name}: sidebar shows {rendered} of "
                    f"{len(entries)} entries — draw.io dropped some")

            # image-bearing previews must have painted their bitmap. This
            # getBBox pass is the cost that does not scale, so sample 10%
            # (seeded) unless AUDIT_FULL_PAINT asks for every item.
            if os.environ.get("AUDIT_FULL_PAINT"):
                checked = list(range(rendered))
            else:
                k = max(1, math.ceil(rendered * PAINT_SAMPLE))
                checked = sorted(rng.sample(range(rendered),
                                            min(k, rendered))) if rendered \
                    else []
            unpainted = items.evaluate_all(
                "(els, idx) => idx.flatMap(i => {"
                "  const imgs = els[i].querySelectorAll('image');"
                "  return [...imgs].some(im =>"
                "    im.getBBox().width === 0) ? [i] : []; })",
                checked)
            if unpainted:
                failures.append(f"{name}: unpainted previews at {unpainted}")
            lib_report["paint_checked"] = checked
            lib_report["unpainted_previews"] = unpainted

            if not name.endswith("-links") and rendered:
                slot = len(report["libraries"])
                before = H.canvas_icon_count(page)
                H.drag_item_to_canvas(page, items.first,
                                      160 + (slot % 5) * 150,
                                      160 + (slot // 5) * 150)
                after = H.canvas_icon_count(page)
                is_image_lib = "image=" in json.dumps(entries[0])
                if is_image_lib and after != before + 1:
                    failures.append(
                        f"{name}: drag added {after - before} images")
                lib_report["drag_added_image"] = after - before

            if rendered:
                items.first.scroll_into_view_if_needed()
                sidebar = H.sidebar_container(page, name)
                sidebar.screenshot(path=str(SCREENS / f"{name}.png"))
            else:
                page.screenshot(path=str(SCREENS / f"FAIL-{name}.png"))
                (H.OUT / f"FAIL-{name}.html").write_text(page.content())
            report["libraries"][name] = lib_report

        # ground checks: the composed canvas on both grounds
        page.screenshot(path=str(SCREENS / "canvas-dark.png"))
        xml = H.get_diagram_xml(page)
        H.set_diagram_xml(page, re.sub(r'background="[^"]*"',
                                       'background="#ffffff"', xml))
        page.screenshot(path=str(SCREENS / "canvas-light.png"))

        tripped = oracles.drain()
        if tripped:
            failures.append(f"cheap oracles tripped: {tripped}")
        report["cheap_oracles"] = tripped

        browser.close()

    report["failures"] = failures
    H.write_report("audit-report", report, ok=not failures)
    if failures:
        print("TIER A FAILED:", *failures, sep="\n  ", file=sys.stderr)
        return 1
    print(f"tier A ok: {len(report['libraries'])} libraries audited")
    return 0


if __name__ == "__main__":
    sys.exit(main())
