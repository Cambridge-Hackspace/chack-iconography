# chack-iconography

Cambridge Hackspace's isometric network-topology icon pack for draw.io:
several hundred true-vector SVG icons across ~20 categories, compiled
deterministically from an [isolex](https://bitbucket.org/axonibyte/isolex)
lexicon under [`src/`](src) (the human-readable source of truth — each icon
is a declarative `.ilx` definition with prototype inheritance).

Themed to cambridgehackspace.com: the four brand colours — red `#c34e4b`,
blue `#3d84af`, gold `#d8a300`, green `#89b108` — over a light ground with
`#333` structural rules, plus a dark variant. The brand red is reserved for
"something is wrong or hostile" and is governed from source; a healthy
diagram contains no red.

## Building

isolex is the compiler and is never vendored: `ci/get-isolex.sh` resolves a
pinned, checksum-verified release binary (or a local sibling checkout), and
the Python here turns its shape-IR into themed SVG and draw.io libraries.

```sh
make bootstrap   # uv-managed venv + resvg (PNG previews only)
make build       # dist/: svg/, svg-light/, drawio/, drawio-light/, preview/
make test        # the full oracle suite
make dist        # versioned tarball of the pack
```

The build is byte-deterministic: same source, same bytes, on any machine.
`dist/` is a build product and is not committed; rebuild it or take a
release tarball from the GitHub Releases page.

Iterate on one icon with `uv run python build.py --only <slug>`.

## Using the pack in draw.io

1. File → Open Library… → `dist/drawio/iso-all.xml` (or a per-category
   library; `iso-links.xml` holds the edge presets, and the per-category
   `iso-link.xml` holds the connector end-cap icons).
2. Set the page background to `#1b1c1e` (`dist/drawio-light/` on white for
   print).
3. Enable the grid at **69 px** — the isometric tile width — and turn on
   snap. Footprints then align: a 1×1 endpoint occupies one tile, a 2×1
   server two.
4. Zones are resizable native shapes with alpha fills, so they tint what
   sits behind them; badge icons (wrench, compass, person…) drop onto zone
   corners for the decorated variants.
5. Labels are draw.io text, never pixels: hostnames in Jost, IPs and VLAN
   tags in IBM Plex Mono, per the dictionary's typography section.

## Layout

- `src/` — the isolex lexicon: every icon as a `.ilx` definition. The
  source of truth.
- `iso/` — theme dicts, the IR→SVG renderer, the draw.io emitter, and the
  loader over `isolex compile --ir`. Colours exist as palette tokens until
  the renderer resolves them, which is what guarantees the dark and light
  variants are structurally identical.
- `build.py` — orchestration (SVG, libraries, contact + tree previews).
- `tests/` — the oracle portfolio: palette conformance, red reservation,
  structure rules, variant identity, determinism, library round-trips,
  tree/preview placement, Makefile and packaging guards.
- `e2e/` — the reaper tenant battery: a real draw.io driven by Playwright.
  See `.reaper.toml`.
- `.github/workflows/` — CI (test on every push/PR, build on `main`) and
  Release (test, build, and publish the pack to GitHub Releases on a tag).
