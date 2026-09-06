"""Two builds are byte-identical: rebuild-and-diff is a meaningful check.

Covers every emitted directory — the canonical svg/ set and the baked
svg-states/ set — by walking the trees, so a nondeterministic baked
variant cannot slip past a base-only loop.
"""

import filecmp
import os

from build import write_svgs


def _tree(root):
    out = {}
    for dirpath, _, files in os.walk(root):
        for f in files:
            full = os.path.join(dirpath, f)
            out[os.path.relpath(full, root)] = full
    return out


def test_double_build_is_byte_identical(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    write_svgs(str(a))
    write_svgs(str(b))
    ta, tb = _tree(a), _tree(b)
    assert set(ta) == set(tb), "the two builds emit different file sets"
    assert ta, "no SVGs were emitted"
    for rel, fa in ta.items():
        assert filecmp.cmp(fa, tb[rel], shallow=False), rel
