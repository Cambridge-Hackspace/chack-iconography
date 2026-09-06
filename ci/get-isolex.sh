#!/usr/bin/env bash
# Fetch a pinned, checksum-verified isolex compiler for the pack build.
#
# The pack consumes isolex as a released binary: never vendored, never
# built here. ISOLEX_VERSION and ci/isolex-checksums.txt pin exactly which
# bytes are acceptable (the pin-what-you-download doctrine: we verify
# against a checksum WE record, not merely the sidecar the server serves).
# Prints the resolved binary path on stdout; all diagnostics go to stderr.
#
# Resolution order:
#   1. $ISOLEX_BIN, if set and executable  (explicit override).
#   2. ../isolex/target/release/isolex      (local dev sibling checkout).
#   3. A checksum-verified download of the pinned release.
set -euo pipefail

here=$(cd "$(dirname "$0")/.." && pwd)

if [[ -n "${ISOLEX_BIN:-}" && -x "${ISOLEX_BIN}" ]]; then
    echo "$ISOLEX_BIN"; exit 0
fi
sibling="$here/../isolex/target/release/isolex"
if [[ -x "$sibling" ]]; then
    echo "$sibling"; exit 0
fi

version=$(tr -d '[:space:]' < "$here/ISOLEX_VERSION")

uname_s=$(uname -s); uname_m=$(uname -m)
case "$uname_s/$uname_m" in
    Linux/x86_64)  target="x86_64-unknown-linux-gnu" ;;
    FreeBSD/amd64) target="x86_64-unknown-freebsd" ;;
    *) echo "get-isolex: no pinned target for $uname_s/$uname_m" >&2; exit 1 ;;
esac

artifact="isolex-v${version}-${target}"
want=$(awk -v a="$artifact" '$1!~/^#/ && $2==a {print $1}' \
    "$here/ci/isolex-checksums.txt")
if [[ -z "$want" || "$want" == PENDING* ]]; then
    {
        echo "get-isolex: no pinned sha256 for $artifact."
        echo "  isolex $version is not released yet, or its checksum has"
        echo "  not been recorded. Release isolex (push main and tag"
        echo "  $version so the pipeline publishes binaries), then copy the"
        echo "  published ${artifact}.sha256 value into"
        echo "  ci/isolex-checksums.txt."
    } >&2
    exit 1
fi

cache="${ISOLEX_CACHE:-$here/.isolex}"
mkdir -p "$cache"
bin="$cache/$artifact"
if [[ ! -x "$bin" ]] || ! echo "$want  $bin" | sha256sum -c - >/dev/null 2>&1
then
    url="https://bitbucket.org/axonibyte/isolex/downloads/$artifact"
    curl -sSL --fail-with-body -o "$bin.tmp" "$url"
    echo "$want  $bin.tmp" | sha256sum -c - >/dev/null
    chmod +x "$bin.tmp"
    mv "$bin.tmp" "$bin"
fi
echo "$bin"
