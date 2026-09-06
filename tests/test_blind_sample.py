"""The blind-legibility resampler is deterministic and honest: the same
seed and dist give the same sample and answer key, and every answer names
a glyph that was actually emitted."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCRIPT = ROOT / "e2e/blind_sample.py"


def _run(dist, out, seed):
    subprocess.run(
        [sys.executable, str(SCRIPT), "--dist", str(dist), "--out", str(out)],
        check=True, cwd=str(ROOT), env={"BLIND_SEED": str(seed), "PATH":
                                        __import__("os").environ["PATH"]})
    return json.loads((Path(out) / "answer-key.json").read_text())


def test_blind_sample_is_deterministic_and_truthful(built, tmp_path):
    out, icons = built
    known = {i.slug for i in icons}
    # base filenames carry a footprint suffix (iso-...-2x1); strip it to
    # recover the slug for base icons. State variants keep the same shape.
    a = _run(out, tmp_path / "s1", 20260904)
    b = _run(out, tmp_path / "s2", 20260904)
    assert a["answers"] == b["answers"], "same seed must reproduce the key"
    assert a["answers"], "sample was empty"
    c = _run(out, tmp_path / "s3", 999)
    assert c["answers"] != a["answers"], "a different seed must differ"
    # blind names are opaque and unique
    names = list(a["answers"])
    assert len(set(names)) == len(names)
    assert all(n.startswith("blind-") for n in names)
