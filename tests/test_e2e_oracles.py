"""Self-test of the Tier 9 invariant checker, without any stack.

Each doctored input is modelled on a real defect class the tier exists to
catch; each must make the checker complain, and the clean baseline must
not. This is what makes the expensive tier mean anything.
"""

import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "e2e"))

import model as M  # noqa: E402

SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 9 9"></svg>'
B64 = base64.b64encode(SVG.encode()).decode()


def _diagram(cells):
    return ('<mxGraphModel><root><mxCell id="0"/><mxCell id="1" '
            'parent="0"/>' + cells + "</root></mxGraphModel>")


def _icon_cell(b64=B64, aspect="aspect=fixed;", x=69, y=138, cid="2"):
    return (f'<mxCell id="{cid}" style="shape=image;{aspect}'
            f'image=data:image/svg+xml,{b64};" vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="90" height="60" '
            f'as="geometry"/></mxCell>')


def _model_with_drop():
    m = M.ShadowModel(grid=69)
    m.drop(SVG)
    return m


def test_clean_baseline_is_coherent():
    v = M.check(_model_with_drop(), _diagram(_icon_cell()),
                {M.payload_hash(SVG): SVG})
    assert v == []


def test_detects_dropped_cell():
    v = M.check(_model_with_drop(), _diagram(""))
    assert any("census mismatch" in x for x in v)


def test_detects_stripped_aspect_fixed():
    v = M.check(_model_with_drop(), _diagram(_icon_cell(aspect="")))
    assert any("aspect=fixed" in x for x in v)


def test_detects_reencoded_payload():
    tweaked = base64.b64encode((SVG + " ").encode()).decode()
    v = M.check(_model_with_drop(), _diagram(_icon_cell(b64=tweaked)),
                {M.payload_hash(SVG): SVG})
    assert any("byte-for-byte" in x for x in v)


def test_detects_phantom_extra_cell():
    v = M.check(_model_with_drop(),
                _diagram(_icon_cell() + _icon_cell(cid="3")))
    assert any("census mismatch" in x for x in v)


def test_detects_lost_edge():
    m = _model_with_drop()
    m.connect("edgeStyle=none;strokeColor=#a8a6a0;")
    v = M.check(m, _diagram(_icon_cell()))
    assert any("edge census" in x for x in v)


def test_export_palette_catches_stray_colour():
    ok = M.check_export_palette("<svg fill=\"#b32020\"/>", {"#b32020"})
    assert ok == []
    bad = M.check_export_palette("<svg fill=\"#ff00ff\"/>", {"#b32020"})
    assert bad and "ff00ff" in bad[0]
