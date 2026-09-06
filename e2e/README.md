# The reaper battery

Runs the pack against a real, digest-pinned draw.io in a disposable guest.
`reaper up` once, then `reaper test` for the loop. Everything lands in
`out/`: JSON reports, per-library screenshots, simulation traces.

- `run.sh` — host-execution run verb: draw.io container + Playwright
  driver container on a private network; snapshots pristine after
  stack-up.
- `audit.py` — Tier A: loads every library through the real UI and asserts
  the rendered sidebar count equals the file's entry count (draw.io drops
  malformed entries *silently*), that every preview painted its embedded
  image, and that dragging produces a canvas image; screenshots each
  palette as human evidence; checks a composed canvas on both grounds;
  console errors / page errors / failed requests are collected the whole
  time and must be empty.
- `simulate.py` — Tier 9: seeded actors over accumulated history with a
  shadow model (`model.py`), nemesis action classes, and a shrinker.
  Fixed seeds in `seeds.json`; hunts via `SEED=`/`ACTIONS=`. Its
  invariant checker is self-tested stackless in
  `tests/test_e2e_oracles.py`.

Workstation tiers stay on the workstation (`make test`); nothing moved in
here because sessions exist.
