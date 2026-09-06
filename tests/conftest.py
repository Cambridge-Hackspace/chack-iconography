import pytest

from build import write_svgs


@pytest.fixture(scope="session")
def built(tmp_path_factory):
    """One full SVG build per test session (no sheets, no PNGs)."""
    out = tmp_path_factory.mktemp("dist")
    icons = write_svgs(str(out))
    return out, icons
