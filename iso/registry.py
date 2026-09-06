"""The slug registry: icons come from `isolex compile <lexicon> --ir`.

The Isolex source tree under `src/` is the single, human-readable source
of truth. This module runs the compiler once per process and adapts its
shape-IR JSON into the `IconDef` objects the renderer, the draw.io
emitter, and the build script consume. There are no Python icon builders
any more; a definition is inspected by opening its `.ilx` file.

The compiler binary is located via `$ISOLEX_BIN`, else a sibling
`../isolex/target/release/isolex` checkout. CI and the reaper tenant set
`$ISOLEX_BIN` to a version-pinned, checksum-verified download.
"""

import json
import os
import subprocess
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

# Categories whose objects sit on tiles and carry a footprint in the name.
FOOTPRINT_CATEGORIES = {"compute", "virt", "svc", "net", "stor", "ext"}

ROOT = Path(__file__).parent.parent
LEXICON = ROOT / "src"


@dataclass(frozen=True)
class IconDef:
    slug: str
    category: str
    viewbox: tuple          # (minx, miny, w, h), from the compiler
    shapes: tuple           # resolved shape-IR primitives (dicts)
    footprint: tuple | None = None   # (w, d, h) tile units, or None
    canvas: tuple | None = None      # (w, h) px for flat icons, or None
    describe: tuple = ()             # documentation lines
    grants: tuple = field(default=())  # declared colour grants

    @property
    def filename(self) -> str:
        base = f"iso-{self.slug}"
        if self.category in FOOTPRINT_CATEGORIES:
            w, d, _ = self.footprint
            base += f"-{int(w)}x{int(d)}"
        return base + ".svg"


def isolex_bin() -> str:
    env = os.environ.get("ISOLEX_BIN")
    if env:
        return env
    sibling = ROOT.parent / "isolex/target/release/isolex"
    if sibling.exists():
        return str(sibling)
    raise SystemExit(
        "no isolex binary: set $ISOLEX_BIN or build the sibling checkout "
        "(cd ../isolex && cargo build --release)")


@lru_cache(maxsize=None)
def _compile(lexicon: str) -> tuple:
    out = subprocess.run(
        [isolex_bin(), "compile", lexicon, "--ir", "-"],
        capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"isolex compile failed:\n{out.stderr}")
    doc = json.loads(out.stdout)
    icons = []
    for i in doc["icons"]:
        icons.append(IconDef(
            slug=i["name"],
            category=i["category"],
            viewbox=tuple(i["viewbox"]),
            shapes=tuple(i["shapes"]),
            footprint=tuple(i["footprint"]) if i.get("footprint") else None,
            canvas=tuple(i["canvas"]) if i.get("canvas") else None,
            describe=tuple(i.get("describe") or ()),
            grants=tuple(tuple(g) if isinstance(g, (list, tuple)) else (g,)
                         for g in i.get("grants") or ()),
        ))
    return tuple(sorted(icons, key=lambda d: d.slug))


def all_icons() -> list[IconDef]:
    return list(_compile(str(LEXICON)))


@lru_cache(maxsize=None)
def _index(lexicon: str) -> dict:
    return {d.slug: d for d in _compile(lexicon)}


def by_slug(slug: str) -> IconDef:
    return _index(str(LEXICON))[slug]
