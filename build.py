#!/usr/bin/env python3
"""Builds damicohealth.org from src/ into dist/ (the live site) and preview/ (review copy).

    python3 build.py

Pages live in src/pages/*.html: a few "key: value" lines, a line with ---, then the page's HTML.
Shared pieces live in src/layout.html and src/partials/. No dependencies beyond Python 3.
"""
import json, re, shutil, sys, html
from pathlib import Path
from datetime import date

ROOT = Path(__file__).parent
SRC = ROOT / "src"
SITE_URL = "https://damicohealth.org"
MANIFEST = json.loads((SRC / "assets/img/manifest.json").read_text())

FONT_LINKS = {
    # live site serves its own font files; the review copy loads the same faces from Google Fonts
    "dist": '<link rel="preload" href="assets/fonts/gabarito-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>\n'
            '<link rel="preload" href="assets/fonts/atkinson-hyperlegible-next-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>\n'
            '<link rel="stylesheet" href="assets/css/fonts.css">',
    "preview": '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible+Next:ital,wght@0,400..700;1,400..700&family=Gabarito:wght@500..800&display=swap">',
}

def attrs(s):
    return dict(re.findall(r'(\w[\w-]*)="([^"]*)"', s))

def photo(m):
    a = attrs(m.group(1))
    pid = a["id"]; info = MANIFEST[pid]
    widths = info["widths"]
    if "max" in a: widths = [w for w in widths if w <= int(a["max"])] or widths[:1]
    srcset = ", ".join(f"assets/img/{pid}-{w}.webp {w}w" for w in widths)
    default = widths[min(1, len(widths) - 1)]
    cls = f' class="{a["class"]}"' if a.get("class") else ""
    style = f' style="object-position:{a["pos"]}"' if a.get("pos") else ""
    eager = a.get("loading") == "eager"
    load = ' fetchpriority="high"' if eager else ' loading="lazy"'
    return (f'<img src="assets/img/{pid}-{default}.webp" srcset="{srcset}" sizes="{a.get("sizes", "100vw")}" '
            f'width="{info["w"]}" height="{info["h"]}" alt="{a.get("alt", "")}"{cls}{style}{load} decoding="async">')

def dots(m):
    a = attrs(m.group(1))
    cls = f' class="{a["class"]}"' if a.get("class") else ""
    return f"<i{cls}></i>" * int(a["n"])

def render(text, ctx, depth=0):
    def inc(m):
        return render((SRC / "partials" / f"{m.group(1)}.html").read_text(), ctx, depth + 1)
    text = re.sub(r"\{\{include (\S+?)\}\}", inc, text)
    text = re.sub(r"\{\{photo (.+?)\}\}", photo, text)
    text = re.sub(r"\{\{dots (.+?)\}\}", dots, text)
    def var(m):
        k = m.group(1)
        if k not in ctx: sys.exit(f"Unknown placeholder {{{{{k}}}}}")
        return str(ctx[k])
    return re.sub(r"\{\{(\w+)\}\}", var, text)

def load_page(path):
    head, body = path.read_text().split("\n---\n", 1)
    meta = dict(line.split(":", 1) for line in head.strip().splitlines())
    return {k.strip(): v.strip() for k, v in meta.items()}, body

def build(target):
    out = ROOT / target
    if out.exists(): shutil.rmtree(out)
    shutil.copytree(SRC / "assets", out / "assets", ignore=shutil.ignore_patterns("manifest.json", "fonts" if target == "preview" else "__none__", "fonts.css" if target == "preview" else "__none__"))
    layout = (SRC / "layout.html").read_text()
    urls = []
    for path in sorted((SRC / "pages").glob("*.html")):
        meta, body = load_page(path)
        slug = path.stem
        is_home = slug == "index"
        ctx = {
            "home": "index.html" if target == "preview" else "./",
            "year": date.today().year,
            "fonts": FONT_LINKS[target],
            "title": "Damico Health Site Preview" if (target == "preview" and is_home) else meta["title"],
            "description": html.escape(meta["description"], quote=True),
            "canonical": SITE_URL + ("/" if is_home else f"/{slug}"),
            "share_image": SITE_URL + "/assets/img/share.jpg",
            "robots": '<meta name="robots" content="noindex">' if meta.get("index") == "no" or target == "preview" else "",
            "body_class": meta.get("class", ""),
        }
        for key in ("about", "work", "emr", "team", "contact", "donate"):
            ctx[f"nav_{key}"] = ' aria-current="page"' if meta.get("nav") == key else ""
        ctx["content"] = render(body, ctx)
        page = render(layout, ctx)
        if slug == "404" and target == "dist":
            page = page.replace("<head>", '<head>\n<base href="/">', 1)  # a 404 can be served from any path
        if chr(0x2014) in page: sys.exit(f"Em dash found in {slug}")
        if target == "preview" and is_home:
            # the review host wraps the home page in its own <html>/<head>/<body>
            head = re.search(r"<head>(.*?)</head>", page, re.S).group(1)
            head = re.sub(r'<meta (charset|name="viewport")[^>]*>\n?', "", head)
            body_html = re.search(r"<body[^>]*>(.*?)</body>", page, re.S).group(1)
            page = head.strip() + "\n" + body_html.strip() + "\n"
        (out / f"{slug}.html").write_text(page)
        if meta.get("index") != "no": urls.append(ctx["canonical"])
    if target == "dist":
        (out / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
        (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
        (out / ".nojekyll").write_text("")
        for extra in (SRC / "static").glob("*") if (SRC / "static").exists() else []:
            shutil.copy(extra, out / extra.name)
    print(f"{target}: {len(list(out.glob('*.html')))} pages")

if __name__ == "__main__":
    for t in ("dist", "preview"):
        build(t)
