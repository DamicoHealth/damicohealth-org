"""Turn the original photos into web-sized WebP files.
Usage: python3 tools/images.py <folder with originals> src/assets/img
Each entry: id -> (source file, crop as (left, top, right, bottom) fractions or None)."""
import sys, os, json
from PIL import Image, ImageOps
Image.MAX_IMAGE_PIXELS = None
SRC, OUT = sys.argv[1], sys.argv[2]
WIDTHS = [480, 960, 1600, 2400]
PHOTOS = {
    "consultation":   ("E.jpg", None),
    "erhardt-path":   ("E-1.jpg", None),
    "team-four":      ("IC-2.jpg", None),
    "team-backs":     ("IC-1.jpg", None),
    "team-two":       ("Icon-3.jpg", None),
    "intake-notes":   ("Icon-4.jpg", None),
    "team-three":     ("Icon-6.jpg", None),
    "clinic-baby":    ("Icon-7.jpg", None),
    "pharmacy-team":  ("Pharma.jpg", None),
    "ultrasound":     ("Rad-1.jpg", None),
    "erhardt-desk":   ("Rad-2.jpg", None),
    "road":           ("U-22.jpg", (0, 0.22, 0.86, 0.86)),
    "lab":            ("U-39.jpg", None),
    "mural":          ("U-5.jpg", None),
    "pharmacy-room":  ("U-57.jpg", None),
    "emr-intake":     ("EMR-1.jpg", None),
    "motorbike":      ("J.jpg", None),
    "gloria":         ("HS-3.jpg", None),
    "erhardt":        ("HS-4.jpg", None),
    "desk-pair":      ("U-41.jpg", None),
}
manifest = {}
for pid, (fn, crop) in PHOTOS.items():
    im = ImageOps.exif_transpose(Image.open(os.path.join(SRC, fn))).convert("RGB")
    if crop:
        w, h = im.size
        im = im.crop((int(crop[0]*w), int(crop[1]*h), int(crop[2]*w), int(crop[3]*h)))
    w, h = im.size
    made = []
    for tw in WIDTHS:
        if tw > w and made: break
        tw2 = min(tw, w)
        r = im.resize((tw2, round(h*tw2/w)), Image.LANCZOS)
        r.save(os.path.join(OUT, f"{pid}-{tw2}.webp"), "WEBP", quality=76, method=6)
        made.append(tw2)
    manifest[pid] = {"w": w, "h": h, "widths": made}
    print(pid, w, h, made)
# social share image
im = ImageOps.exif_transpose(Image.open(os.path.join(SRC, "IC-2.jpg"))).convert("RGB")
im = ImageOps.fit(im, (1200, 630), Image.LANCZOS, centering=(0.5, 0.45))
im.save(os.path.join(OUT, "share.jpg"), quality=84, optimize=True)
json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=1)
