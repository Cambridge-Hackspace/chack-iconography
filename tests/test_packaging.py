"""The Downloads packaging publishes both preview sheets.

The tree sheet was built and tarballed from the start but not published as a
direct download -- so the Downloads page showed only the grid. This guards
the corrected contract: ci/package.sh copies both the tree and the grid into
upload/ as standalone previews, so neither can quietly drop back out.

Parsed textually (no bash invoked, no dist/ build), so it holds wherever
pytest runs. It checks the packaging *intent*, not a live run -- the CI
build step is where the artifacts are actually produced.
"""

import os
import re

PACKAGE_SH = os.path.join(os.path.dirname(__file__), "..", "ci", "package.sh")

# Each published preview: (source sheet in dist/preview, upload filename stem).
PUBLISHED_PREVIEWS = (
    ("sheet-tree.svg", "preview-tree"),   # inheritance structure
    ("sheet-all.svg", "preview"),         # flat labelled catalogue
)


def _text():
    with open(PACKAGE_SH) as f:
        return f.read()


def test_both_preview_sheets_are_published():
    text = _text()
    for source, stem in PUBLISHED_PREVIEWS:
        # a cp of dist/preview/<source> into an upload/...<stem>...svg name
        pattern = (rf'cp\s+\S*dist/preview/{re.escape(source)}\s+'
                   rf'"?\S*upload/\S*{re.escape(stem)}\S*\.svg')
        assert re.search(pattern, text), \
            f"package.sh does not publish {source} as an upload/{stem} preview"


def test_preview_stems_are_distinct():
    # The two previews must not collide on the same upload filename, or one
    # would overwrite the other. `preview` is a substring of `preview-tree`,
    # so compare the actual destination expressions, not the stems.
    text = _text()
    dests = re.findall(r'cp\s+\S*dist/preview/\S+\s+("?\S*upload/\S+\.svg"?)',
                       text)
    assert len(set(dests)) == len(dests), f"preview uploads collide: {dests}"
    assert len(dests) >= 2, "expected at least two published preview sheets"
