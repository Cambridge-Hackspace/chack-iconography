#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Prepare a blind legibility sample: a seeded resample of the pack with
randomised filenames, plus a separate answer key.

The blind pass asks a fresh viewer (or an agent) to name each glyph from
sight alone — so the filename must not give it away. This script copies a
seeded 5% of the base leaves and 2% of the composed-state variants into an
output directory as blind-0001.svg…, and writes answer-key.json mapping
each blind name back to its real slug. Determinism: same seed and same
dist produce the same sample and the same shuffle, so a finding is
replayable and a regression is a diff.

Usage:  uv run e2e/blind_sample.py [--dist dist] [--out out/blind]
        BLIND_SEED overrides the seed (else seeds.json's first seed).
"""

import argparse
import json
import math
import os
import random
import shutil
from pathlib import Path

BASE_FRACTION = 0.05
STATE_FRACTION = 0.02
STATE_SUFFIXES = ("-down", "-degraded", "-maintenance", "-planned")


def _seed():
    env = os.environ.get("BLIND_SEED")
    if env:
        return int(env)
    seeds = json.loads((Path(__file__).parent / "seeds.json").read_text())
    return seeds["seeds"][0]


def _sample(rng, pool, fraction):
    if not pool:
        return []
    k = max(1, math.ceil(len(pool) * fraction))
    return rng.sample(sorted(pool), min(k, len(pool)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist", default="dist")
    ap.add_argument("--out", default="out/blind")
    args = ap.parse_args()

    dist = Path(args.dist)
    base_dir, state_dir = dist / "svg", dist / "svg-states"
    base = [p.name for p in base_dir.glob("iso-*.svg")] \
        if base_dir.is_dir() else []
    state = [p.name for p in state_dir.glob("iso-*.svg")] \
        if state_dir.is_dir() else []
    if not base:
        raise SystemExit(f"no base SVGs under {base_dir} — run the build")

    seed = _seed()
    rng = random.Random(seed)
    picked = [(base_dir, f) for f in _sample(rng, base, BASE_FRACTION)]
    picked += [(state_dir, f) for f in _sample(rng, state, STATE_FRACTION)]
    # shuffle so the ordering leaks neither category nor source directory
    rng.shuffle(picked)

    out = Path(args.out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    key = {}
    for i, (src_dir, fname) in enumerate(picked, 1):
        blind = f"blind-{i:04d}.svg"
        shutil.copyfile(src_dir / fname, out / blind)
        key[blind] = fname[len("iso-"):-len(".svg")]
    (out / "answer-key.json").write_text(
        json.dumps({"seed": seed, "base_pool": len(base),
                    "state_pool": len(state), "answers": key}, indent=2))

    print(f"blind sample: {len(picked)} glyphs "
          f"({len(base)} base pool @ {BASE_FRACTION:.0%}, "
          f"{len(state)} state pool @ {STATE_FRACTION:.0%}), "
          f"seed {seed} -> {out}")


if __name__ == "__main__":
    main()
