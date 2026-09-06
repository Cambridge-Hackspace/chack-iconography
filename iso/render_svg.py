"""IR x theme -> SVG text. The only place tokens become hex."""

from iso.registry import IconDef

def _F(v):
    # one fixed coordinate format, for byte determinism. Negative zero is
    # canonicalised away: -0.00 and 0.00 are the same coordinate, and which
    # one a platform's libm produces for a value like cos(3*pi/2) is noise.
    s = f"{v:.2f}"
    return "0.00" if s == "-0.00" else s


def _paint(shape, theme):
    fill = theme[shape["fill"]]
    stroke = theme[shape["stroke"]]
    parts = [f'fill="{fill}"']
    if shape.get("fill_opacity", 1.0) != 1.0:
        parts.append(f'fill-opacity="{_F(shape["fill_opacity"])}"')
    if stroke != "none":
        parts.append(f'stroke="{stroke}"')
        parts.append(f'stroke-width="{_F(shape["stroke_width"])}"')
        parts.append('stroke-linejoin="round" stroke-linecap="round"')
    if shape.get("dash"):
        parts.append(f'stroke-dasharray="{shape["dash"]}"')
    return " ".join(parts)


def _emit(shape, theme):
    k = shape["kind"]
    if k == "group":
        # A group carries no paint of its own; its children do.
        inner = "".join(_emit(c, theme) for c in shape["shapes"])
        return (f'<g transform="translate({_F(shape["tx"])},'
                f'{_F(shape["ty"])}) scale({_F(shape["scale"])})">'
                f"{inner}</g>")
    paint = _paint(shape, theme)
    if k == "polygon":
        pts = " ".join(f"{_F(x)},{_F(y)}" for x, y in shape["points"])
        return f'<polygon points="{pts}" {paint}/>'
    if k == "path":
        return f'<path d="{shape["d"]}" {paint}/>'
    if k == "ellipse":
        return (f'<ellipse cx="{_F(shape["cx"])}" cy="{_F(shape["cy"])}" '
                f'rx="{_F(shape["rx"])}" ry="{_F(shape["ry"])}" {paint}/>')
    if k == "circle":
        return (f'<circle cx="{_F(shape["cx"])}" cy="{_F(shape["cy"])}" '
                f'r="{_F(shape["r"])}" {paint}/>')
    if k == "rect":
        rx = f' rx="{_F(shape["rx"])}"' if shape.get("rx") else ""
        return (f'<rect x="{_F(shape["x"])}" y="{_F(shape["y"])}" '
                f'width="{_F(shape["w"])}" height="{_F(shape["h"])}"'
                f'{rx} {paint}/>')
    raise ValueError(f"unknown IR kind {k}")


def viewbox_of(icon: IconDef):
    return icon.viewbox


def render(icon: IconDef, theme: dict) -> str:
    """Render one compiled icon. Its shape-IR primitives share _emit's
    vocabulary by design, and its viewBox comes from the compiler."""
    minx, miny, w, h = icon.viewbox
    body = "".join(_emit(s, theme) for s in icon.shapes)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{minx:.2f} {miny:.2f} {w:.2f} {h:.2f}" '
        f'width="{w:.0f}" height="{h:.0f}">{body}</svg>'
    )
