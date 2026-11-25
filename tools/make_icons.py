"""Draws the browser-tab icon (favicon.svg) and the home-screen icon (touch-icon.png):
the letters DH in the site's display face on a navy rounded square.
Run from the repository root:  python3 tools/make_icons.py"""
import io
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "src/assets/img"
NAVY, ORANGE = "#16233F", "#F68630"
S = 1400                      # canvas size for the SVG
TEXT = "DH"

font = TTFont(IMG.parent / "fonts/gabarito-latin-wght-normal.woff2")
font.flavor = None
font = instantiateVariableFont(font, {"wght": 800})
upm = font["head"].unitsPerEm
cmap = font.getBestCmap()
glyphs = font.getGlyphSet()
hmtx = font["hmtx"]

# glyph outlines as SVG paths, laid out left to right in font units
paths, x = [], 0
for ch in TEXT:
    name = cmap[ord(ch)]
    pen = SVGPathPen(glyphs)
    glyphs[name].draw(pen)
    paths.append((pen.getCommands(), x))
    x += hmtx[name][0]
bp = BoundsPen(glyphs)
for ch in TEXT:
    glyphs[cmap[ord(ch)]].draw(bp)
# tight ink bounds across the run
xmin, ymin, xmax, ymax = None, None, None, None
for ch, (_, dx) in zip(TEXT, paths):
    b = BoundsPen(glyphs); glyphs[cmap[ord(ch)]].draw(b)
    bx0, by0, bx1, by1 = b.bounds
    bx0 += dx; bx1 += dx
    xmin = bx0 if xmin is None else min(xmin, bx0); xmax = bx1 if xmax is None else max(xmax, bx1)
    ymin = by0 if ymin is None else min(ymin, by0); ymax = by1 if ymax is None else max(ymax, by1)
ink_w, ink_h = xmax - xmin, ymax - ymin
scale = (S * 0.68) / ink_w           # letters span 68% of the square
tx = (S - ink_w * scale) / 2 - xmin * scale
ty = (S + ink_h * scale) / 2 + ymin * scale   # baseline position after the y flip
group = "".join(f'<path transform="translate({dx} 0)" d="{d}"/>' for d, dx in paths)
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}">'
       f'<rect width="{S}" height="{S}" rx="{S * 0.22:.0f}" fill="{NAVY}"/>'
       f'<g fill="{ORANGE}" transform="translate({tx:.1f} {ty:.1f}) scale({scale:.5f} {-scale:.5f})">{group}</g></svg>')
(IMG / "favicon.svg").write_text(svg)

# PNG for the home-screen icon, drawn with the same face
buf = io.BytesIO(); font.save(buf); buf.seek(0)
P = 720
im = Image.new("RGBA", (P, P), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
d.rounded_rectangle((0, 0, P - 1, P - 1), radius=int(P * 0.22), fill=NAVY)
f = ImageFont.truetype(buf, size=int(P * 0.68 * upm / ink_w))
l, t, r, b = d.textbbox((0, 0), TEXT, font=f)
d.text(((P - (r - l)) / 2 - l, (P - (b - t)) / 2 - t), TEXT, font=f, fill=ORANGE)
im.resize((180, 180), Image.LANCZOS).save(IMG / "touch-icon.png")
print("wrote favicon.svg and touch-icon.png")
