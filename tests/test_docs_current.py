"""The lexicon reference is generated, not hand-written: `isolex docs`
over the `src/` tree is the source of truth, and the committed
`docs/lexicon-reference.md` must match it byte-for-byte.

This inverts the old dictionary<->registry bijection. The `.ilx` files
are now authoritative and directly human-readable; this test catches a
definition edited without regenerating the reference (run `make docs`).
"""

import subprocess
from pathlib import Path

from iso.registry import LEXICON, isolex_bin

REFERENCE = Path(__file__).parent.parent / "docs/lexicon-reference.md"


def test_lexicon_reference_is_current():
    out = subprocess.run(
        [isolex_bin(), "docs", str(LEXICON)],
        capture_output=True, text=True)
    assert out.returncode == 0, f"isolex docs failed:\n{out.stderr}"
    committed = REFERENCE.read_text()
    assert out.stdout == committed, (
        "docs/lexicon-reference.md is stale; regenerate with `make docs`")
