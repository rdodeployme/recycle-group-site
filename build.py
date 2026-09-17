"""Recycle Group corporate site generator.
python3 build.py  →  dist/  (index.html + one folder per page + assets/)
"""
import os, re, shutil, sys, io
from PIL import Image
from jinja2 import Environment, FileSystemLoader

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "static", "src-img")   # source photography + official logos
# Deployment target. GitHub Pages project site => BASE="/recycle-group-site", OUT="docs", FORM="mailto"
BASE = os.environ.get("BASE", "").rstrip("/")
OUT = os.environ.get("OUT", "dist")
FORM = os.environ.get("FORM", "netlify")          # netlify | mailto
DIST = os.path.join(HERE, OUT)
SITE_URL = os.environ.get("SITE_URL", "https://recycle-group-corporate.netlify.app").rstrip("/")

NAV = [
    dict(path="/councils/", label="Councils"),
    dict(path="/industry/", label="Industry", mlabel="Commercial & industry"),
    dict(path="/facilities/", label="Facilities", mlabel="Our facilities"),
    dict(path="/materials/", label="Materials", mlabel="What we recover"),
    dict(path="/businesses/", label="The group"),
    dict(path="/community/", label="Community"),
    dict(path="/about/", label="About"),
]

# Old URLs from the first build -> where they went. Rendered as stub pages
# (GitHub Pages has no redirect engine) plus a Netlify _redirects file.
REDIRECTS = {
    "/facility/": "/facilities/",
    "/where/": "/facilities/",
    "/people/": "/about/",
}

# Group-wide diversion figure. Richard wants a headline percentage; the JUNK
# site says 93% and his review says 95%, so the number is NOT published until
# that is settled. Set DIVERSION to e.g. "95" and it appears in the home proof
# strip, the councils page and the materials page. Nothing else to change.
DIVERSION = None

# images: name -> (source, max width, quality)
IMAGES = {
    # Photography rule (17 Sep 2026): nothing shot on the council-visit / factory-tour
    # day goes on this site. That rules out the whole council-* set and the phone snaps
    # taken alongside it (floor, line, conveyor, crew-walk, granulate, steel-bin,
    # mattress-stack, and the blog stills cut from the same day). Everything below is
    # from the supplied JUNK / Recycle Group photography.

    # Facility and plant
    "sorting-line":   (f"{SRC}/rg-sorting-line.webp", 1600, 74),
    "intake":         (f"{SRC}/rg-intake.webp", 1600, 74),
    "facility-wide":  (f"{SRC}/facility-floor-wide.webp", 1260, 72),
    "mattress-line":  (f"{SRC}/facility-mattress-line.webp", 1260, 72),
    "granulator":     (f"{SRC}/facility-cable-granulator.webp", 1260, 72),
    "nunjara":        (f"{SRC}/rg-nunjara-tile.webp", 918, 74),
    "warehouse-floor":(f"{SRC}/recycle-warehouse-floor.webp", 1071, 74),

    # Collection and crew
    "junk-truck":     (f"{SRC}/junk-household-rubbish-removal-hero.webp", 1200, 66),
    "hard-waste":     (f"{SRC}/junk-hard-waste-collection-2.webp", 1260, 72),
    "fleet":          (f"{SRC}/junk-truck-fleet-numbered.webp", 1260, 72),
    "crew-truck":     (f"{SRC}/junk-general-crew-truck-hero.webp", 1260, 72),
    "industrial":     (f"{SRC}/junk-warehouse-industrial-clearout-hero.webp", 1260, 72),
    "office-carry":   (f"{SRC}/junk-crew-office-carry.webp", 1071, 74),
    "green-waste":    (f"{SRC}/junk-crew-green-waste-load.webp", 1071, 74),
    "volume":         (f"{SRC}/rg-volume.webp", 1600, 72),
    "covered-truck":  (f"{SRC}/rg-covered-truck.webp", 747, 78),

    # Reuse, community and brand tiles
    "aid":            (f"{SRC}/comm-materialaid-delivery.webp", 1100, 66),
    "sorting":        (f"{SRC}/junk-community-sorting-square.webp", 800, 66),
    "donation-bins":  (f"{SRC}/rg-donation-bins.webp", 738, 78),
    "love-junk":      (f"{SRC}/love-junk-card.webp", 1051, 80),
    "love-junk-tile": (f"{SRC}/love-junk-tile.webp", 700, 80),
    "declutter-tile": (f"{SRC}/rg-declutter-tile.webp", 1200, 72),
}
LOGOS = {
    "recycle-group-logo.png": f"{SRC}/recycle-group-logo.png",
    "junk-logo.png":          f"{SRC}/logo-header.png",
    "trash-logo.png":         f"{SRC}/trash-logo.png",
    "tmrc-logo-white.png":    f"{SRC}/tmrc-logo-white.png",
    "recycle-warehouse-logo.png": f"{SRC}/recycle-warehouse-logo.png",
    "declutter-logo.png":     f"{SRC}/declutter-logo.png",
    "rubbish-logo.png":       f"{SRC}/rubbish-logo.png",
    "vogue-vintage-logo.png": f"{SRC}/vogue-vintage-logo.png",
}
VARIANTS = {}   # name -> full width, filled by build_assets
FAVICON = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' fill='#050505'/><text x='16' y='23' font-family='Arial Black,sans-serif' font-size='15' font-weight='900' text-anchor='middle' fill='#00ED00'>RG</text></svg>"""

def build_assets():
    out = os.path.join(DIST, "assets")
    os.makedirs(f"{out}/img", exist_ok=True)
    shutil.copytree(f"{HERE}/static/fonts", f"{out}/fonts", dirs_exist_ok=True)
    os.makedirs(f"{out}/css", exist_ok=True)
    css = open(f"{HERE}/static/css/main.css", encoding="utf-8").read().replace("url(/assets/", f"url({BASE}/assets/")
    open(f"{out}/css/main.css", "w", encoding="utf-8").write(css)
    for name, (p, w, q) in IMAGES.items():
        im = Image.open(p).convert("RGB")
        if im.width > w: im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        im.save(f"{out}/img/{name}.webp", "WEBP", quality=q, method=6)
        if im.width > 720:   # phone variant for srcset
            VARIANTS[name] = im.width
            sm = im.resize((720, round(im.height * 720 / im.width)), Image.LANCZOS)
            sm.save(f"{out}/img/{name}-720.webp", "WEBP", quality=q, method=6)
    for name, p in LOGOS.items():
        im = Image.open(p).convert("RGBA")
        if im.width > 900: im = im.resize((900, round(im.height * 900 / im.width)), Image.LANCZOS)
        im.save(f"{out}/img/{name}", "PNG", optimize=True)
    # og image = hero
    _og = Image.open(IMAGES["sorting-line"][0]).convert("RGB")
    _ow = min(_og.width, round(_og.height * 1200 / 630))
    _oh = round(_ow * 630 / 1200)
    _og = _og.crop(((_og.width - _ow) // 2, (_og.height - _oh) // 2,
                    (_og.width + _ow) // 2, (_og.height + _oh) // 2))
    _og.resize((1200, 630), Image.LANCZOS).save(f"{out}/img/og.jpg", "JPEG", quality=82)
    open(f"{out}/img/favicon.svg", "w").write(FAVICON)

def build_pages():
    env = Environment(loader=FileSystemLoader(HERE), autoescape=False)
    base = env.get_template("base.html")
    pages = []
    for fn in sorted(os.listdir(f"{HERE}/pages")):
        if not fn.endswith(".html"): continue
        raw = open(f"{HERE}/pages/{fn}", encoding="utf-8").read()
        # front matter: lines "key: value" until a blank line
        head, body = raw.split("\n---\n", 1)
        meta = dict(l.split(":", 1) for l in head.strip().splitlines())
        meta = {k.strip(): v.strip() for k, v in meta.items()}
        path = meta["path"]
        body = env.from_string(body).render(form=FORM, diversion=DIVERSION, base=BASE, **meta)
        html = base.render(nav=NAV, path=path, site_url=SITE_URL, base=BASE, body=body,
                           title=meta["title"], description=meta["description"],
                           mbar=meta.get("mbar", "yes") != "no")
        html = responsive_images(html)
        if BASE:
            html = re.sub(r'((?:href|src|action|srcset)=")/(?!/)', rf'\1{BASE}/', html)
            html = html.replace(", /assets/img/", f", {BASE}/assets/img/")
            html = html.replace("url(/assets/", f"url({BASE}/assets/")
        outdir = DIST if path == "/" else os.path.join(DIST, path.strip("/"))
        os.makedirs(outdir, exist_ok=True)
        open(os.path.join(outdir, "index.html"), "w", encoding="utf-8").write(html)
        pages.append(path)
    return pages

def responsive_images(html):
    """Add srcset/sizes for photos that have a phone variant, and async image decoding."""
    def fix(m):
        tag = m.group(0); name = m.group(1)
        if name in VARIANTS:
            full_w = VARIANTS[name]
            sizes = "100vw" if 'fetchpriority="high"' in tag else "(max-width:760px) 100vw, (max-width:1240px) 50vw, 620px"
            tag = tag.replace(f'src="/assets/img/{name}.webp"', f'src="/assets/img/{name}.webp" srcset="/assets/img/{name}-720.webp 720w, /assets/img/{name}.webp {full_w}w" sizes="{sizes}"')
        if "decoding=" not in tag: tag = tag[:-1] + ' decoding="async">'
        return tag
    return re.sub(r'<img [^>]*src="/assets/img/([\w-]+)\.webp"[^>]*>', fix, html)

def prune_images():
    """Drop any built image no page references, so the repo carries only what it uses."""
    used = set()
    for root, _, files in os.walk(DIST):
        for f in files:
            if f.endswith(".html"):
                used |= set(re.findall(r"/assets/img/([\w.-]+)", open(os.path.join(root, f), encoding="utf-8").read()))
    for p in os.listdir(os.path.join(DIST, "assets", "img")):
        if p not in used and p != "og.jpg":
            os.remove(os.path.join(DIST, "assets", "img", p))

def check_links(pages):
    bad = []
    for root, _, files in os.walk(DIST):
        for f in files:
            if not f.endswith(".html"): continue
            html = open(os.path.join(root, f), encoding="utf-8").read()
            refs = re.findall(r'(?:href|src)="(/[^"#?]*)', html) + re.findall(r'url\((/[^)]*)\)', html)
            for href in refs:
                if BASE and not href.startswith(BASE + "/") and href != BASE: bad.append((f"{root}/{f}", href + " (missing BASE)")); continue
                target = os.path.join(DIST, href[len(BASE):].strip("/"))
                if not (os.path.exists(target) or os.path.exists(os.path.join(target, "index.html"))):
                    bad.append((f"{root}/{f}", href))
    return bad

REDIRECT_STUB = """<!DOCTYPE html>
<html lang="en-AU"><head><meta charset="utf-8">
<title>Moved — Recycle Group</title>
<link rel="canonical" href="{site}{base}{to}">
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={base}{to}">
<script>location.replace("{base}{to}" + location.hash);</script>
</head><body style="font-family:system-ui;padding:40px">
<p>This page moved. <a href="{base}{to}">Continue to {to}</a>.</p>
</body></html>
"""

def build_redirects():
    for old, new in REDIRECTS.items():
        d = os.path.join(DIST, old.strip("/"))
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(
            REDIRECT_STUB.format(site=SITE_URL, base=BASE, to=new))

if __name__ == "__main__":
    if os.path.isdir(DIST): shutil.rmtree(DIST)
    os.makedirs(DIST)
    build_assets()
    pages = build_pages()
    open(f"{DIST}/sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{SITE_URL}{BASE}{p}</loc></url>\n" for p in pages if p != "/thanks/") + "</urlset>\n")
    open(f"{DIST}/robots.txt", "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}{BASE}/sitemap.xml\n")
    build_redirects()
    if FORM == "netlify":
        open(f"{DIST}/_redirects", "w").write("/index.html / 301\n" + "".join(
            f"{o} {n} 301\n" for o, n in REDIRECTS.items()))
    else: open(f"{DIST}/.nojekyll", "w").write("")
    prune_images()
    bad = [x for x in check_links(pages) if not any(x[1].endswith(o) for o in REDIRECTS)]
    total = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(DIST) for f in fs)
    print("pages:", ", ".join(pages))
    print("dist:", round(total / 1e6, 2), "MB")
    if bad:
        print("BROKEN LINKS:"); [print("  ", b) for b in bad]; sys.exit(1)
