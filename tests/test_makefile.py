"""The Makefile keeps its public contract.

README sends developers to `make bootstrap/build/test/dist`; those targets,
and the VERSION the dist tarball is named from, must exist. This is the
guard the 0.4.1 "bump" needed: that commit emptied the Makefile and nothing
noticed, because neither CI nor reaper drives the file -- but every gate
runs pytest, so a check here fails everywhere a wipe or a dropped target
would otherwise slip through.

Parsed textually on purpose: no `make` binary is invoked, so the test holds
in the CI container (astral/uv, no build-essential) exactly as it does on a
workstation.
"""

import os
import re

MAKEFILE = os.path.join(os.path.dirname(__file__), "..", "Makefile")

# The contract README promises plus the housekeeping targets that round it
# out. Renaming one is a deliberate change to this list, not a silent drop.
REQUIRED_TARGETS = ("bootstrap", "build", "docs", "test", "dist", "clean")


def _text():
    with open(MAKEFILE) as f:
        return f.read()


def test_makefile_is_not_empty():
    assert _text().strip(), "Makefile is empty"


def test_required_targets_are_defined():
    text = _text()
    missing = [t for t in REQUIRED_TARGETS
               if not re.search(rf'^{t}:', text, re.M)]
    assert not missing, f"Makefile is missing target rules: {missing}"


def test_version_is_declared():
    assert re.search(r'^VERSION\s*=\s*\d+\.\d+\.\d+\s*$', _text(), re.M), \
        "Makefile has no `VERSION = X.Y.Z` line"


def test_phony_targets_all_have_rules():
    """Every target named on a `.PHONY:` line must actually be defined -- a
    declared-but-undefined phony is the shape a partial wipe leaves behind."""
    text = _text()
    phony = re.findall(r'^\.PHONY:\s*(.+)$', text, re.M)
    declared = {t for line in phony for t in line.split()}
    assert declared, "no .PHONY targets declared"
    undefined = [t for t in sorted(declared)
                 if not re.search(rf'^{re.escape(t)}:', text, re.M)]
    assert not undefined, f".PHONY names with no rule: {undefined}"
