# Recycle Group — corporate website

Static site. Source in `pages/` (one file per route, with a small front-matter block), layout in `base.html`, styles in `static/css/main.css`, photography and official logos in `static/src-img/`.

## Build

    python3 build.py                                  # → dist/ (Netlify: root paths, Netlify form)
    BASE=/recycle-group-site OUT=docs FORM=mailto SITE_URL=https://<account>.github.io python3 build.py   # → docs/ (GitHub Pages)

Needs Python 3 with Pillow and Jinja2. The build resizes images, prefixes paths with `BASE`, checks every internal link, and writes sitemap.xml / robots.txt.

## Hosting

GitHub Pages serves `docs/` on `main` (Settings → Pages → Deploy from a branch → main, /docs). Commit the rebuilt `docs/` with every change.

## QA

    python3 -m http.server 8090 --directory dist &
    python3 qa.py        # Playwright: every route × desktop/mobile — no horizontal scroll, no broken images, no console errors, no heading overflow
