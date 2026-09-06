#!/bin/bash
# Host-execution run verb: stand up draw.io + the Playwright driver as
# containers and run the battery. Owns its exit status (no pipes).
set -euo pipefail

# out/ must mean *this* run, guest-side too (docs/tenants.md).
rm -rf "${REAPER_OUT:?}"/*

DRAWIO_IMG="docker.io/jgraph/drawio@sha256:19d71d91d092e65132ea22b2e1cfcddf9716402a01386fbaae7190cf689adeb0"
DRIVER_IMG="mcr.microsoft.com/playwright/python@sha256:aa81288e738725378becba5b3e06cb0f3a7f012a610e87e8d767a090ea3f740d"

if command -v docker >/dev/null 2>&1; then ENGINE=docker; else ENGINE=podman; fi

NET=chackicons-e2e
$ENGINE rm -f chack-drawio chack-driver >/dev/null 2>&1 || true
$ENGINE network rm "$NET" >/dev/null 2>&1 || true
$ENGINE network create "$NET" >/dev/null

cleanup() {
  $ENGINE logs chack-drawio > "$REAPER_OUT/drawio.log" 2>&1 || true
  $ENGINE rm -f chack-drawio chack-driver >/dev/null 2>&1 || true
  $ENGINE network rm "$NET" >/dev/null 2>&1 || true
}
trap cleanup EXIT

$ENGINE run -d --name chack-drawio --network "$NET" "$DRAWIO_IMG" >/dev/null

# Wait for tomcat to answer before snapshotting pristine.
for i in $(seq 1 60); do
  if $ENGINE run --rm --network "$NET" "$DRIVER_IMG" \
      python -c "import urllib.request,sys; urllib.request.urlopen('http://chack-drawio:8080/', timeout=2); sys.exit(0)" \
      >/dev/null 2>&1; then
    break
  fi
  if [ "$i" -eq 60 ]; then echo "drawio never came up" >&2; exit 1; fi
  sleep 2
done

mkdir -p "$REAPER_STATE/profile" "$REAPER_STATE/documents"

# Tight pristine: the stack is up and untouched. Kept from the first call.
"$REAPER_CONTROL/snapshot" || true

run_driver() {
  # $1: script under e2e/. The caller survives resets because the control
  # dir is mounted through; the driver decides when to use it. The image
  # carries the browsers but (at this digest) not the pip package; the
  # matching version is installed pinned, warm via the pip cache.
  $ENGINE run --rm --name chack-driver --network "$NET" \
    -v "$REAPER_WORK":/work -v "$REAPER_OUT":/out \
    -v "$REAPER_STATE":/state -v "$REAPER_CONTROL":/control \
    -v "$REAPER_CACHE_PIP":/pipcache -e PIP_CACHE_DIR=/pipcache \
    -e DRAWIO_URL=http://chack-drawio:8080 -e PYTHONPATH=/work \
    -w /work "$DRIVER_IMG" bash -c \
    "pip install -q --root-user-action=ignore playwright==1.62.0 && \
     python e2e/$1"
}

run_driver audit.py
run_driver gridcheck.py
run_driver simulate.py
