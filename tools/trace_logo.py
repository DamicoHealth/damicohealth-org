"""Trace the paw mark and wordmark PNGs into SVG paths. Run once; output is committed."""
import sys, numpy as np, potrace
from PIL import Image
SRC = sys.argv[1]; OUT = sys.argv[2]

def alpha_mask(path, scale=None):
    im = Image.open(path).convert("RGBA")
    if scale: im = im.resize((int(im.width*scale), int(im.height*scale)), Image.LANCZOS)
    arr = np.array(im).astype(int)
    # artwork is flat orange on a white or transparent ground: keep opaque, saturated pixels
    a = (arr[:, :, 3] > 128) & ((arr[:, :, 0] - arr[:, :, 2]) > 70)
    return a

def bbox(a):
    ys, xs = np.where(a)
    return xs.min(), ys.min(), xs.max()+1, ys.max()+1

def trace(a):
    bm = potrace.Bitmap(~a)  # the library expects dark artwork on a light ground
    pl = bm.trace(turdsize=8, alphamax=1.0, opticurve=True, opttolerance=0.3)
    d = []
    for curve in pl:
        s = curve.start_point
        d.append(f"M{s.x:.1f} {s.y:.1f}")
        for seg in curve.segments:
            if seg.is_corner:
                d.append(f"L{seg.c.x:.1f} {seg.c.y:.1f}L{seg.end_point.x:.1f} {seg.end_point.y:.1f}")
            else:
                d.append(f"C{seg.c1.x:.1f} {seg.c1.y:.1f} {seg.c2.x:.1f} {seg.c2.y:.1f} {seg.end_point.x:.1f} {seg.end_point.y:.1f}")
        d.append("Z")
    return "".join(d)

# Paw: top block of the stacked logo (paw sits above the wordmark, separated by empty rows)
a = alpha_mask(f"{SRC}/DH1GPNG.png")
rows = a.any(axis=1)
ys = np.where(rows)[0]
gaps = np.where(np.diff(ys) > 20)[0]
paw_bottom = ys[gaps[0]] + 1
paw = a[:paw_bottom]
x0, y0, x1, y1 = bbox(paw)
paw = paw[y0:y1, x0:x1]
paw_d = trace(paw); ph, pw = paw.shape

w = alpha_mask(f"{SRC}/DH.png")
x0, y0, x1, y1 = bbox(w)
w = w[y0:y1, x0:x1]
word_d = trace(w); wh, ww = w.shape
print("paw", pw, ph, "word", ww, wh, len(paw_d), len(word_d))

open(f"{OUT}/paw.svg", "w").write(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {pw} {ph}"><path fill="#F68630" fill-rule="evenodd" d="{paw_d}"/></svg>')

def lockup(word_fill, name):
    # paw at left, wordmark to the right, vertically centred; unit = paw height
    H = ph; gap = pw * 0.28
    ws = (H * 0.40) / wh           # wordmark cap height = 40% of paw height
    wy = (H - wh * ws) / 2
    W = pw + gap + ww * ws
    open(f"{OUT}/{name}", "w").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H}" role="img" aria-label="Damico Health">'
        f'<path fill="#F68630" fill-rule="evenodd" d="{paw_d}"/>'
        f'<g transform="translate({pw+gap:.1f} {wy:.1f}) scale({ws:.4f})"><path fill="{word_fill}" fill-rule="evenodd" d="{word_d}"/></g></svg>')
lockup("#F68630", "logo.svg")
lockup("#FFFFFF", "logo-light.svg")
lockup("#16233F", "logo-ink.svg")
