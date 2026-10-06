"""Screenshot pages of a built folder. usage: shot.py <dir> <outdir> <width> page1 page2 ..."""
import sys, asyncio, http.server, threading, functools, os
from playwright.async_api import async_playwright
d, out, width = sys.argv[1], sys.argv[2], int(sys.argv[3]); pages = sys.argv[4:]
os.makedirs(out, exist_ok=True)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a, **k): pass
handler = functools.partial(Q, directory=d)

srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={"width": width, "height": 900}, device_scale_factor=1)
        pg = await ctx.new_page()
        errs = []
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.on("requestfailed", lambda r: errs.append("FAILED " + r.url))
        for name in pages:
            await pg.goto(f"http://127.0.0.1:{port}/{name}", wait_until="networkidle")
            h = await pg.evaluate("document.documentElement.scrollHeight")
            for y in range(0, h, 600):
                await pg.evaluate(f"window.scrollTo({{top:{y},behavior:'instant'}})"); await pg.wait_for_timeout(120)
            await pg.evaluate("window.scrollTo({top:0,behavior:'instant'})"); await pg.wait_for_timeout(700)
            ow = await pg.evaluate("document.documentElement.scrollWidth")
            await pg.screenshot(path=f"{out}/{name.replace('.html','')}-{width}.png", full_page=True)
            print(name, "scrollWidth", ow, "errors", errs[-5:]); errs.clear()
        await b.close()
asyncio.run(main())
