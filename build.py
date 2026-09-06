#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Emit the pack: dist/svg, dist/svg-light, contact sheets (SVG + PNG).

Deterministic: sorted iteration, fixed float formatting, no timestamps.
PNG rasterization uses resvg (cairosvg needs libcairo, absent on this host);
PNGs are previews only and are not part of the shipped pack.
"""

import argparse
import os
import shutil
import subprocess
import sys

from iso.registry import all_icons
from iso.render_svg import render, viewbox_of
from iso.theme import THEMES

CELL = 150.0
PAD = 40.0
ICON_BOX = 120.0
LABEL_H = 26.0   # strip under each icon for its slug (preview sheets only)

# Baked-state axis suffixes (see src/axes.ilx). A slug is a baked variant
# when it is "<primary>-<suffix>" and <primary> is itself an emitted slug;
# that guards against a real slug that merely ends in one of these words.
STATE_SUFFIXES = ("down", "degraded", "maintenance", "planned")


def _is_state_variant(slug, known):
    return any(slug.endswith("-" + s) and slug[: -len(s) - 1] in known
               for s in STATE_SUFFIXES)


def partition(icons):
    """Split into (base, baked). Base is the canonical library set; baked
    variants are static-export only and never enter a draw.io library."""
    known = {i.slug for i in icons}
    base = [i for i in icons if not _is_state_variant(i.slug, known)]
    baked = [i for i in icons if _is_state_variant(i.slug, known)]
    return base, baked


def _resvg():
    found = shutil.which("resvg") or shutil.which(
        "resvg", path=os.path.expanduser("~/.cargo/bin"))
    return found


def _emit_to(out_dir, icons, dark_sub, light_sub):
    for theme_name, sub in (("dark", dark_sub), ("light", light_sub)):
        d = os.path.join(out_dir, sub)
        os.makedirs(d, exist_ok=True)
        for icon in icons:
            with open(os.path.join(d, icon.filename), "w") as f:
                f.write(render(icon, THEMES[theme_name]))


def write_svgs(out_dir, only=None):
    icons = [i for i in all_icons() if only is None or i.slug == only]
    if only is not None and not icons:
        raise SystemExit(f"unknown slug: {only}")
    if only is not None:
        _emit_to(out_dir, icons, "svg", "svg-light")
        return icons
    base, baked = partition(icons)
    _emit_to(out_dir, base, "svg", "svg-light")
    _emit_to(out_dir, baked, "svg-states", "svg-states-light")
    return base


def _cell(icon, theme, x, y):
    """One icon as a nested <svg>, scaled to fit ICON_BOX, bottom-aligned."""
    minx, miny, w, h = viewbox_of(icon)
    scale = min(ICON_BOX / w, ICON_BOX / h)
    cw, ch = w * scale, h * scale
    ox = x + (CELL - cw) / 2
    oy = y + (CELL - ch)  # bottom-aligned so baselines read across a row
    body = render(icon, theme)
    inner = body.replace(
        f'width="{w:.0f}" height="{h:.0f}"',
        f'x="{ox:.1f}" y="{oy:.1f}" width="{cw:.1f}" height="{ch:.1f}"', 1)
    if inner == body:
        raise AssertionError(f"cell sizing failed for {icon.slug}")
    return inner


def contact_sheet(icons, columns=6):
    """Icons on the dark ground above the same icons on white, each labelled
    with its slug. The label is <text>; that is fine here because a preview
    sheet is a documentation artifact, not a shipped icon (which carry no
    text by the pack's own rule)."""
    row_h = CELL + LABEL_H
    rows = (len(icons) + columns - 1) // columns
    band_h = rows * row_h + 2 * PAD
    width = columns * CELL + 2 * PAD
    cells = []
    bands = (("dark", THEMES["dark"]["bg-canvas"], "#a7a39a"),
             ("light", "#ffffff", "#555555"))
    for band, (theme_name, ground, label_fill) in enumerate(bands):
        y0 = band * band_h
        cells.append(f'<rect y="{y0:.1f}" width="{width:.1f}" '
                     f'height="{band_h:.1f}" fill="{ground}"/>')
        for i, icon in enumerate(icons):
            x = PAD + (i % columns) * CELL
            y = y0 + PAD + (i // columns) * row_h
            cells.append(_cell(icon, THEMES[theme_name], x, y))
            cells.append(
                f'<text x="{x + CELL / 2:.1f}" y="{y + CELL + 15:.1f}" '
                f'font-family="monospace" font-size="8.5" '
                f'text-anchor="middle" fill="{label_fill}">'
                f'{icon.slug}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{width:.0f}" height="{2 * band_h:.0f}">'
            + "".join(cells) + "</svg>")


def write_sheets(out_dir, icons, png=True):
    d = os.path.join(out_dir, "preview")
    # Rebuild the dir from scratch so a --no-png run never ships stale PNGs
    # left by an earlier PNG build; keeps the packaged preview deterministic.
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d, exist_ok=True)
    by_cat = {}
    for icon in icons:
        by_cat.setdefault(icon.category, []).append(icon)
    sheets = {f"sheet-{cat}": members for cat, members in sorted(by_cat.items())}
    sheets["sheet-all"] = icons
    resvg = _resvg() if png else None
    if png and not resvg:
        print("warning: resvg not found; skipping PNG previews",
              file=sys.stderr)
    for name, members in sheets.items():
        svg_path = os.path.join(d, name + ".svg")
        with open(svg_path, "w") as f:
            f.write(contact_sheet(members))
        if resvg:
            subprocess.run([resvg, svg_path,
                            os.path.join(d, name + ".png")], check=True)
    # A second preview, laid out by the inheritance tree rather than by
    # category grid: category -> base families -> icons -> aliases.
    from iso.treeview import tree_sheet
    tree_path = os.path.join(d, "sheet-tree.svg")
    with open(tree_path, "w") as f:
        f.write(tree_sheet(icons, render, viewbox_of, THEMES))
    if resvg:
        subprocess.run([resvg, tree_path,
                        os.path.join(d, "sheet-tree.png")], check=True)


def write_libraries(out_dir, icons):
    from iso.drawio import build_libraries
    for theme_name, sub in (("dark", "drawio"), ("light", "drawio-light")):
        d = os.path.join(out_dir, sub)
        os.makedirs(d, exist_ok=True)
        libs = build_libraries(
            icons, lambda i: render(i, THEMES[theme_name]), theme_name)
        for name in sorted(libs):
            with open(os.path.join(d, name), "w") as f:
                f.write(libs[name])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="dist")
    ap.add_argument("--only", default=None, help="build a single slug")
    ap.add_argument("--no-png", action="store_true")
    args = ap.parse_args()
    icons = write_svgs(args.out, args.only)
    if args.only is None:
        write_libraries(args.out, icons)
        _, baked = partition(all_icons())
        write_sheets(args.out, icons, png=not args.no_png)
        print(f"{len(icons)} base slugs + {len(baked)} baked state variants "
              f"-> {args.out}")
    else:
        write_sheets(args.out, icons, png=not args.no_png)
        print(f"{len(icons)} slug -> {args.out}")


if __name__ == "__main__":
    main()
