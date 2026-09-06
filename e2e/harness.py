"""Shared Playwright harness for the draw.io battery.

Cheap oracles ride every page (testing-methodology: nothing escapes the
cheap checks): console errors, page errors, and failed requests are
collected continuously and asserted empty at checkpoint time.
"""

import json
import os
import time
import urllib.parse
from pathlib import Path

DRAWIO_URL = os.environ.get("DRAWIO_URL", "http://localhost:8080")
OUT = Path(os.environ.get("REAPER_OUT", "/out"))
STATE = Path(os.environ.get("REAPER_STATE", "/state"))

EMPTY_XML = ('<mxGraphModel dx="800" dy="600" grid="1" gridSize="69" '
             'background="#0b0b0d"><root><mxCell id="0"/>'
             '<mxCell id="1" parent="0"/></root></mxGraphModel>')


class Oracles:
    """Continuous cheap checks. `drain` returns and clears what tripped."""

    IGNORE_SUBSTRINGS = (
        "favicon",           # tomcat has none; not the pack's defect
        # the app fetches <origin>/null once at startup and again on some
        # of its own UI paths. Evidence it is not pack-attributable: it
        # fires on a bare editor with zero pack content, and Tier A ran
        # every library load, preview render and drag with zero
        # occurrences. Only this exact resource is ignored.
        "/null:0]",
    )

    def __init__(self, page):
        self.console_errors = []
        self.page_errors = []
        self.failed_requests = []
        page.on("console", self._on_console)
        page.on("pageerror", lambda e: self.page_errors.append(str(e)))
        page.on("requestfailed", self._on_requestfailed)

    def _ignored(self, text):
        return any(s in text for s in self.IGNORE_SUBSTRINGS)

    def _on_console(self, msg):
        if msg.type != "error":
            return
        loc = msg.location or {}
        formatted = (f"{msg.text} "
                     f"[{loc.get('url', '?')}:{loc.get('lineNumber')}]")
        # match against the formatted line: the URL under test lives in
        # msg.location, not msg.text (the /null filter silently never
        # fired when this checked msg.text alone)
        if not self._ignored(formatted):
            self.console_errors.append(formatted)

    def _on_requestfailed(self, req):
        if not self._ignored(req.url):
            self.failed_requests.append(f"{req.url} ({req.failure})")

    def drain(self):
        tripped = {
            "console_errors": self.console_errors[:],
            "page_errors": self.page_errors[:],
            "failed_requests": self.failed_requests[:],
        }
        self.console_errors.clear()
        self.page_errors.clear()
        self.failed_requests.clear()
        return {k: v for k, v in tripped.items() if v}


def open_editor(page, background="#0b0b0d"):
    """Open draw.io on a blank local diagram, no storage dialogs."""
    xml = EMPTY_XML.replace('background="#0b0b0d"',
                            f'background="{background}"')
    url = (f"{DRAWIO_URL}/?splash=0&local=1&lang=en"
           f"#R{urllib.parse.quote(xml)}")
    page.goto(url)
    page.wait_for_selector(".geMenubarContainer", timeout=30000)
    page.wait_for_selector(".geDiagramContainer svg", timeout=30000)


def _click_menu(page, top, *items):
    page.click(f".geMenubarContainer >> text='{top}'")
    for label in items:
        item = page.locator(".mxPopupMenuItem", has_text=label).first
        item.wait_for(state="visible", timeout=5000)
        item.hover()
        item.click()


def load_library(page, path):
    """File > Open Library... through the real chooser."""
    with page.expect_file_chooser(timeout=10000) as fc:
        _click_menu(page, "File", "Open Library from", "Device...")
    fc.value.set_files(path)
    name = Path(path).stem
    title = page.locator(".geTitle", has_text=name).first
    title.wait_for(state="visible", timeout=15000)
    return title


def sidebar_container(page, lib_name):
    """The palette block for a loaded library. DOM (probed on 31.4.2):
    .geTitle, then a classless wrapper div holding .geSidebar > a.geItem."""
    return page.locator(
        f"xpath=//*[contains(@class,'geTitle') and "
        f"normalize-space(.)='{lib_name}']"
        f"/following-sibling::div[1]")


def sidebar_items(page, lib_name):
    """The palette entries of a loaded library, as a locator."""
    return page.locator(
        f"xpath=//*[contains(@class,'geTitle') and "
        f"normalize-space(.)='{lib_name}']"
        f"/following-sibling::div[1]//a[contains(@class,'geItem')]")


def canvas_icon_count(page):
    """Count image cells in the authoritative model (the DOM also holds
    draw.io's own <image> chrome — hover arrows, previews — so counting
    rendered elements over-reports; found by Tier A)."""
    return get_diagram_xml(page).count("image=data:")


def drag_item_to_canvas_abs(page, item, px, py, paced=False):
    """Drag a sidebar item to an absolute viewport point (for callers
    that solved the view transform and work in graph coordinates).
    paced=True moves in human-speed increments so the app's dragOver
    logic runs between events."""
    box = item.bounding_box()
    sx = box["x"] + box["width"] / 2
    sy = box["y"] + box["height"] / 2
    page.mouse.move(sx, sy)
    page.mouse.down()
    if paced:
        n = 24
        for k in range(1, n + 1):
            page.mouse.move(sx + (px - sx) * k / n,
                            sy + (py - sy) * k / n)
            page.wait_for_timeout(25)
    else:
        page.mouse.move(px, py, steps=8)
    page.wait_for_timeout(150)
    page.mouse.move(px, py)
    page.wait_for_timeout(60)
    page.mouse.up()


def drag_on_canvas(page, x0, y0, x1, y1):
    """Human-paced drag of something already on the canvas."""
    page.mouse.move(x0, y0)
    page.wait_for_timeout(150)
    page.mouse.down()
    page.wait_for_timeout(150)
    n = 24
    for k in range(1, n + 1):
        page.mouse.move(x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n)
        page.wait_for_timeout(25)
    page.wait_for_timeout(150)
    page.mouse.up()
    page.wait_for_timeout(250)


def drag_item_to_canvas(page, item, x=400, y=300):
    box = item.bounding_box()
    canvas = page.locator(".geDiagramContainer").first.bounding_box()
    page.mouse.move(box["x"] + box["width"] / 2,
                    box["y"] + box["height"] / 2)
    page.mouse.down()
    page.mouse.move(canvas["x"] + x, canvas["y"] + y, steps=8)
    # draw.io positions the drop at the last mousemove it has *processed*;
    # releasing immediately lands the shape mid-flight (observed: drops
    # short of the target with per-drop jitter). Settle, reaffirm, release.
    page.wait_for_timeout(150)
    page.mouse.move(canvas["x"] + x, canvas["y"] + y)
    page.wait_for_timeout(60)
    page.mouse.up()


def set_diagram_xml(page, xml):
    """Extras > Edit Diagram... — also the door Tier B's nemesis uses."""
    _click_menu(page, "Extras", "Edit Diagram...")
    dialog = page.locator(".geDialog").last
    ta = dialog.locator("textarea").first
    ta.wait_for(state="visible", timeout=5000)
    ta.fill(xml)
    dialog.get_by_role("button", name="Apply").click()
    page.wait_for_timeout(300)


def get_diagram_xml(page):
    _click_menu(page, "Extras", "Edit Diagram...")
    dialog = page.locator(".geDialog").last
    ta = dialog.locator("textarea").first
    ta.wait_for(state="visible", timeout=5000)
    xml = ta.input_value()
    dialog.get_by_role("button", name="Cancel").click()
    page.wait_for_timeout(200)
    return xml


def write_report(name, report, ok):
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / f"{name}.json", "w") as f:
        json.dump({"ok": ok, "generated": time.strftime("%F %T"),
                   **report}, f, indent=1)
