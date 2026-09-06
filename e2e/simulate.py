#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = ["playwright==1.62.0"]
# ///
"""Tier 9: seed-driven simulated users against a real draw.io.

Two actors take turns on their own documents for a configurable number of
actions drawn from a weighted pool by a seeded PRNG; a shadow model
(e2e/model.py) records what should be true and is diffed against the saved
diagram at checkpoints and at the end. Nemesis classes live in the same
pool, so faults land on accumulated history. On failure the run shrinks:
prefix bisect first, then action-kind removal, with state rolled back via
$REAPER_CONTROL/reset between replays; strong/weak reproduction is stated
in the report.

What this deliberately does not prove: interactive resize distortion
(aspect=fixed is instead asserted statically on every payload the canvas
holds), absolute grid positions during the seeded run (guides and page-centre
magnetism legitimately outrank the grid; e2e/gridcheck.py asserts pure
grid snap with guides off),
duplicate/paste offsets (excluded from the pool), and multi-user
concurrency (draw.io local mode has none; the actors own separate
documents).

Replay: seeds and action count come from e2e/seeds.json or the SEED /
ACTIONS environment; the trace of every run streams to $REAPER_OUT before
any assertion can end the process.
"""

import base64
import json
import os
import random
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from playwright.sync_api import sync_playwright

import harness as H
import model as M

sys.path.insert(0, "/work")
from iso.theme import THEMES                # noqa: E402

GRID = 69
LIB = Path("dist/drawio/iso-all.xml")
CONTROL = Path(os.environ.get("REAPER_CONTROL", "/control"))

# The run phase tests the BUILT artifacts, not a recompile: each icon's
# shipped SVG is pulled straight out of the library's base64 payloads, so
# the battery needs neither the registry nor the isolex compiler at run
# time — it exercises exactly the bytes the pack will ship.
_ENTRIES = json.loads(ET.fromstring(LIB.read_text()).text)
_IMG = re.compile(r"image=data:image/svg\+xml,([A-Za-z0-9+/=]+);")
SVG_OF = {}
for _e in _ENTRIES:
    # icons are vertices; the link-blocked edge also carries an svg badge
    # payload but is not an icon, so exclude edge entries.
    if 'edge="1"' in _e["xml"]:
        continue
    _m = _IMG.search(_e["xml"])
    if _m:
        SVG_OF[_e["title"]] = base64.b64decode(_m.group(1)).decode()
DIST_HASHES = {M.payload_hash(s): s for s in SVG_OF.values()}
# draw.io's SVG export writes its own `light-dark(bg, #e4e4e6)` fallback
# into the root style attribute — present in an empty-canvas export, so
# app chrome by construction (probed on 31.4.2), not pack pixels.
APP_EXPORT_CHROME = {"#e4e4e6"}
PALETTE = ({v for v in THEMES["dark"].values() if v.startswith("#")}
           | {"#ffffff", "#000000"} | APP_EXPORT_CHROME)


class Actor:
    def __init__(self, browser, name, trace):
        self.name = name
        self.page = browser.new_page()
        self.oracles = H.Oracles(self.page)
        self.model = M.ShadowModel(grid=GRID)
        self.trace = trace
        self.entries = None   # slug list, sidebar order
        H.open_editor(self.page)
        self.baseline_noise = self.oracles.drain()  # app-only, pre-pack
        self._load_library()
        self.drops = 0

    def _load_library(self):
        H.load_library(self.page, str(LIB))
        entries = json.loads(ET.fromstring(LIB.read_text()).text)
        self.entries = [e["title"] for e in entries]

    def _droppable(self):
        return [i for i, t in enumerate(self.entries) if t in SVG_OF]

    def _edge_indices(self):
        return [i for i, t in enumerate(self.entries)
                if t.startswith("link-") and t not in SVG_OF]

    def items(self):
        return H.sidebar_items(self.page, "iso-all")

    def sync_check(self):
        xml = H.get_diagram_xml(self.page)
        return M.check(self.model, xml, DIST_HASHES)

    # --- actions -------------------------------------------------------

    def act_drop(self, rng):
        idx = rng.choice(self._droppable())
        slot = self.drops % 36
        x, y = 140 + (slot % 6) * 160, 110 + (slot // 6) * 115
        item = self.items().nth(idx)
        item.scroll_into_view_if_needed()
        H.drag_item_to_canvas(self.page, item, x, y)
        self.model.drop(SVG_OF[self.entries[idx]])
        self.drops += 1

    def act_connect(self, rng):
        edges = self._edge_indices()
        idx = rng.choice(edges)
        entries = json.loads(ET.fromstring(LIB.read_text()).text)
        style = ET.fromstring(entries[idx]["xml"]).find(
            ".//mxCell[@edge='1']").get("style")
        item = self.items().nth(idx)
        item.scroll_into_view_if_needed()
        H.drag_item_to_canvas(self.page, item,
                              260 + (self.drops % 4) * 180, 800)
        self.model.connect(style)
        # the blocked preset carries its midpoint badge as a child cell
        if entries[idx]["title"] == "link-blocked":
            self.model.drop(SVG_OF["state-down"])

    def act_checkpoint(self, rng):
        v = self.sync_check()
        assert not v, f"{self.name} checkpoint: {v}"

    def act_save_reload(self, rng):
        xml_before = H.get_diagram_xml(self.page)
        H.open_editor(self.page)  # abandon-and-reopen with explicit state
        self.baseline_noise = self.oracles.drain()  # app startup noise
        H.set_diagram_xml(self.page, xml_before)
        v = self.sync_check()
        assert not v, f"{self.name} save/reload: {v}"

    def act_export_svg(self, rng):
        with self.page.expect_download(timeout=20000) as dl:
            H._click_menu(self.page, "File", "Export as", "SVG...")
            dialog = self.page.locator(".geDialog").last
            dialog.get_by_role("button", name="Export").click()
            # a filename dialog follows; OK triggers the download
            save = self.page.locator(".geDialog").last
            save.get_by_role("button", name="OK").click()
        svg = Path(dl.value.path()).read_text()
        v = M.check_export_palette(svg, PALETTE)
        assert not v, f"{self.name} export: {v}"

    # --- nemesis -------------------------------------------------------

    def nemesis_close_library(self, rng):
        before = H.canvas_icon_count(self.page)
        title = self.page.locator(".geTitle", has_text="iso-all").first
        title.hover()
        closer = title.locator("img").last
        if closer.count():
            closer.click()
        after = H.canvas_icon_count(self.page)
        assert after == before, "closing the library disturbed the canvas"
        self._load_library()

    def nemesis_corrupt_xml(self, rng):
        good = H.get_diagram_xml(self.page)
        try:
            H.set_diagram_xml(self.page, good[: len(good) // 2])  # truncated
        except Exception:
            pass  # a refusal that keeps the dialog is one coherent outcome
        for _ in range(3):
            if not self.page.locator(".geDialog").count():
                break
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(300)
        v = self.sync_check()
        if v:  # a refusal that kept the old state is the coherent outcome;
            # anything else is not
            H.set_diagram_xml(self.page, good)
            v2 = self.sync_check()
            assert not v2, f"{self.name} corrupt-xml wrecked state: {v2}"

    def nemesis_undo_storm(self, rng):
        canvas = self.page.locator(".geDiagramContainer").first.bounding_box()
        self.page.mouse.click(canvas["x"] + 1050, canvas["y"] + 650)
        k = rng.randint(2, 5)
        for _ in range(k):
            self.page.keyboard.press("Control+z")
        for _ in range(k):
            self.page.keyboard.press("Control+Shift+z")
        self.page.wait_for_timeout(200)
        v = self.sync_check()
        assert not v, f"{self.name} undo-storm ({k}): {v}"

    def nemesis_double_drop(self, rng):
        # Drop the same sidebar item twice; the census must then show two.
        # Confirm each drag actually created a model cell before counting
        # it: a copy fired before draw.io settled the previous drop, or
        # dropped where prior session content sat, otherwise silently
        # produces no cell. Re-grab the item, settle, and shift down until
        # it lands on its own — this exercises the double-drop, not the
        # app's drag timing.
        idx = rng.choice(self._droppable())
        for k in range(2):
            before = H.canvas_icon_count(self.page)
            for attempt in range(6):
                item = self.items().nth(idx)
                item.scroll_into_view_if_needed()
                H.drag_item_to_canvas(self.page, item,
                                      1050, 150 + k * 200 + attempt * 70)
                self.page.wait_for_timeout(200)
                if H.canvas_icon_count(self.page) == before + 1:
                    break
            self.model.drop(SVG_OF[self.entries[idx]])
        v = self.sync_check()
        assert not v, f"{self.name} double-drop: {v}"

    def nemesis_abandon(self, rng):
        # walk away mid-edit: reload the app over unsaved changes, then
        # re-impose a known state. Coherent = no crash, definite state.
        H.open_editor(self.page)
        self.baseline_noise = self.oracles.drain()  # app startup noise
        xml_cells = "".join(
            f'<mxCell id="c{i}" style="shape=image;aspect=fixed;imageAspect=0;'
            f'image=data:image/svg+xml,{_b64(SVG_OF[slug])};" vertex="1" '
            f'parent="1"><mxGeometry x="{GRID * (2 + i)}" y="{GRID * 2}" '
            f'width="90" height="60" as="geometry"/></mxCell>'
            for i, slug in enumerate(_census_slugs(self.model)))
        H.set_diagram_xml(
            self.page,
            '<mxGraphModel grid="1" gridSize="69" background="#0b0b0d">'
            '<root><mxCell id="0"/><mxCell id="1" parent="0"/>'
            + xml_cells + "</root></mxGraphModel>")
        self.model.edges.clear()  # the reimposed state carries no edges
        v = self.sync_check()
        assert not v, f"{self.name} abandonment: {v}"


def _b64(svg):
    import base64
    return base64.b64encode(svg.encode()).decode()


def _census_slugs(model):
    by_hash = {M.payload_hash(s): slug for slug, s in SVG_OF.items()}
    out = []
    for h, n in sorted(model.icons.items()):
        out += [by_hash[h]] * n
    return out


ACTIONS = [
    ("drop", Actor.act_drop, 8),
    ("connect", Actor.act_connect, 3),
    ("checkpoint", Actor.act_checkpoint, 2),
    ("save-reload", Actor.act_save_reload, 1),
    ("export-svg", Actor.act_export_svg, 1),
    ("nemesis-close-library", Actor.nemesis_close_library, 1),
    ("nemesis-corrupt-xml", Actor.nemesis_corrupt_xml, 1),
    ("nemesis-undo-storm", Actor.nemesis_undo_storm, 1),
    ("nemesis-double-drop", Actor.nemesis_double_drop, 1),
    ("nemesis-abandon", Actor.nemesis_abandon, 1),
]


def plan(seed, n_actions, kinds=None):
    rng = random.Random(seed)
    pool = [(name, fn) for name, fn, w in ACTIONS
            if kinds is None or name in kinds for _ in range(w)]
    return [(rng.randrange(2), *rng.choice(pool)) for _ in range(n_actions)]


def run_once(seed, n_actions, kinds=None, tag="run"):
    trace_path = H.OUT / f"sim-trace-{tag}-{seed}.jsonl"
    steps = plan(seed, n_actions, kinds)
    rng = random.Random(seed + 1)  # action parameters, replayable too
    with sync_playwright() as pw, open(trace_path, "w", buffering=1) as tr:
        browser = pw.chromium.launch_persistent_context(
            user_data_dir=str(H.STATE / "profile"),
            accept_downloads=True,
            viewport={"width": 1600, "height": 1000})
        actors = [Actor(browser, f"actor{k}", tr) for k in (0, 1)]
        try:
            for i, (who, name, fn) in enumerate(steps):
                tr.write(json.dumps({"i": i, "actor": who,
                                     "action": name}) + "\n")
                fn(actors[who], rng)
            for a in actors:
                v = a.sync_check()
                assert not v, f"{a.name} final: {v}"
                tripped = a.oracles.drain()
                assert not tripped, f"{a.name} cheap oracles: {tripped}"
        finally:
            browser.close()


def reset_state():
    """Between-seed isolation. NOT $REAPER_CONTROL/reset: that stops the
    stack's containers (only the caller survives — its contract), which
    takes draw.io down mid-battery; found live on the first full run.
    Pristine state is the empty post-stack-up dirs, so wiping their
    contents is the same rollback; the ZFS reset still runs where it
    belongs, in `reaper test`'s own loop between runs."""
    import shutil
    for sub in ("profile", "documents"):
        d = H.STATE / sub
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True, exist_ok=True)


def shrink(seed, n_actions):
    """Smallest failing prefix, then drop action kinds. Reproduction on a
    reset stack is the strong signal; failure to reproduce is weak."""

    attempts = []

    def fails(n, kinds=None, tag="shrink"):
        reset_state()
        try:
            run_once(seed, n, kinds, tag=tag)
            return False
        except Exception as e:
            attempts.append({"n": n,
                             "kinds": sorted(kinds) if kinds else None,
                             "error": str(e)[:300]})
            return True

    lo, hi = 1, n_actions  # invariant: hi fails (or did, on first run)
    if not fails(hi):
        return {"reproduced": False, "attempts": attempts,
                "note": "weak signal: full-length replay on reset state "
                        "passed; original failure rode accumulated state"}
    while lo < hi:
        mid = (lo + hi) // 2
        if fails(mid):
            hi = mid
        else:
            lo = mid + 1
    prefix = hi
    kinds = {name for _, name, _ in plan(seed, prefix)}
    for kind in sorted(kinds):
        if len(kinds) > 1 and fails(prefix, kinds - {kind}):
            kinds = kinds - {kind}
    return {"reproduced": True, "prefix": prefix,
            "kinds": sorted(kinds), "attempts": attempts}


def main():
    cfg = json.loads(Path("e2e/seeds.json").read_text())
    seeds = ([int(os.environ["SEED"])] if os.environ.get("SEED")
             else cfg["seeds"])
    n_actions = int(os.environ.get("ACTIONS", cfg["actions"]))
    report = {"seeds": {}}
    failed = False
    for seed in seeds:
        reset_state()
        try:
            run_once(seed, n_actions, tag="run")
            report["seeds"][seed] = {"ok": True}
            print(f"seed {seed}: ok ({n_actions} actions)")
        except Exception as e:
            failed = True
            print(f"seed {seed}: FAILED: {e}", file=sys.stderr)
            report["seeds"][seed] = {"ok": False, "error": str(e),
                                     "shrink": shrink(seed, n_actions)}
    H.write_report("simulate-report", report, ok=not failed)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
