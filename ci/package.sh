#!/bin/bash
# Package dist/ for the Downloads page. What a person grabs:
#   - the tbz2: everything (glyphs in both themes, baked state variants,
#     every draw.io library, and the contact sheets under preview/);
#   - iso-core.xml: the curated starter palette (common icons + presets);
#   - two standalone preview sheets, so you can eyeball what's inside before
#     downloading the tarball: the tree (every icon by its inheritance --
#     which leaves share a base) and the grid (every icon labelled, a flat
#     catalogue). Both also live in the tarball's preview/.
# iso-all.xml (every icon) lives in the tarball; a Downloads page full of
# per-category XMLs, or one enormous all-library, was noise.
set -euo pipefail

# VERSION is set by the release workflow from the git tag; `dev` locally.
VER="${VERSION:-dev}"
NAME="chack-iconography"

rm -rf upload
mkdir -p upload

tar -cjf "upload/${NAME}-${VER}.tbz2" -C dist \
  svg svg-light svg-states svg-states-light drawio drawio-light preview

cp dist/drawio/iso-core.xml "upload/iso-core-${VER}.xml"
cp dist/preview/sheet-tree.svg "upload/${NAME}-preview-tree-${VER}.svg"
cp dist/preview/sheet-all.svg "upload/${NAME}-preview-${VER}.svg"

ls -l upload
