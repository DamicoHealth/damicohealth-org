# damicohealth.org

Source for the Damico Health website. Plain HTML, CSS and a little JavaScript, assembled by one Python script.

## Layout

- `src/pages/` one file per page. A few `key: value` lines, a `---` line, then the page's HTML.
- `src/layout.html` header, navigation and footer shared by every page.
- `src/partials/` pieces reused across pages (program list, donation ledger, signup form, donate band).
- `src/assets/` styles, script, fonts, logo files and web-sized photos.
- `src/static/` files copied to the site as they are (the redirect from the old `/about-1` address).
- `tools/images.py` turns original photos into the web-sized files in `src/assets/img/`.
- `tools/trace_logo.py` produced the vector logo files from the original PNG artwork.

## Build

    python3 build.py

Writes the live site to `dist/` and a review copy to `preview/`. Pushing to `main` builds and publishes `dist/` through GitHub Pages.

## Adding a photo

Add the original to the photo folder, add a line to `PHOTOS` in `tools/images.py`, run it, then place it in a page with
`{{photo id="name" alt="What the photo shows" sizes="(min-width: 900px) 50vw, 100vw"}}`.

## Email signup

The signup forms post to the address in their `data-endpoint` attribute (`src/partials/signup.html` and `signup-page.html`). It is empty until a mailing-list provider is chosen.
