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
    dict(path="/businesses/", label="Businesses"),
    dict(path="/how-it-works/", label="How it works"),
    dict(path="/facility/", label="Facility", mlabel="The facility"),
    dict(path="/materials/", label="Materials", mlabel="Material streams"),
    dict(path="/community/", label="Community"),
    dict(path="/people/", label="People"),
    dict(path="/where/", label="Where", mlabel="Where we operate"),
]

# images: name -> (source, max width, quality)
IMAGES = {
    "hero-mattress":  (f"{SRC}/blog-facility-hero-mattress-floor.webp", 1600, 74),
    "sorting-line":   (f"{SRC}/council-visit-hero.webp", 1600, 66),
    "floor":          (f"{SRC}/floor.webp", 1600, 66),
    "line":           (f"{SRC}/line.webp", 1200, 66),
    "steel":          (f"{SRC}/blog-cheaper-hero-spring-steel.webp", 1100, 66),
    "poly-machine":   (f"{SRC}/council-eps-machine.webp", 800, 66),
    "poly-out":       (f"{SRC}/council-eps-output.webp", 700, 66),
    "poly-ctn":       (f"{SRC}/council-eps-container.webp", 700, 66),
    "cable":          (f"{SRC}/council-cable-group.webp", 700, 66),
    "granulate":      (f"{SRC}/granulate.webp", 700, 64),
    "sep":            (f"{SRC}/blog-loop-hero-separation-table.webp", 1100, 66),
    "aid":            (f"{SRC}/comm-materialaid-delivery.webp", 1100, 66),
    "sorting":        (f"{SRC}/junk-community-sorting-square.webp", 800, 66),
    "junk-truck":     (f"{SRC}/junk-household-rubbish-removal-hero.webp", 1200, 66),
    "talking":        (f"{SRC}/council-visit-talking.webp", 800, 66),
    "mattress-stack": (f"{SRC}/mattress-stack.webp", 800, 66),
    "steel-bin":      (f"{SRC}/steel-bin.webp", 900, 66),
    "crew-walk":      (f"{SRC}/crew-walk.webp", 800, 66),
    "conveyor":       (f"{SRC}/conveyor.webp", 800, 66),
    "mattress-steel": (f"{SRC}/council-mattress-steel.webp", 800, 66),
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
    Image.open(IMAGES["hero-mattress"][0]).convert("RGB").resize((1200, 630)).save(f"{out}/img/og.jpg", "JPEG", quality=80)
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
        body = env.from_string(body).render(form=FORM, **meta)
        html = base.render(nav=NAV, path=path, site_url=SITE_URL, base=BASE, body=body,
                           title=meta["title"], description=meta["description"],
                           mbar=meta.get("mbar", "yes") != "no")
        html = responsive_images(html)
        if BASE:
            html = re.sub(r'((?:href|src|action|srcset)=")/(?!/)', rf'\1{BASE}/', html)
            html = html.replace(", /assets/img/", f", {BASE}/assets/img/")
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

def check_links(pages):
    bad = []
    for root, _, files in os.walk(DIST):
        for f in files:
            if not f.endswith(".html"): continue
            html = open(os.path.join(root, f), encoding="utf-8").read()
            for href in re.findall(r'(?:href|src)="(/[^"#?]*)', html):
                if BASE and not href.startswith(BASE + "/") and href != BASE: bad.append((f"{root}/{f}", href + " (missing BASE)")); continue
                target = os.path.join(DIST, href[len(BASE):].strip("/"))
                if not (os.path.exists(target) or os.path.exists(os.path.join(target, "index.html"))):
                    bad.append((f"{root}/{f}", href))
    return bad

if __name__ == "__main__":
    if os.path.isdir(DIST): shutil.rmtree(DIST)
    os.makedirs(DIST)
    build_assets()
    pages = build_pages()
    open(f"{DIST}/sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{SITE_URL}{BASE}{p}</loc></url>\n" for p in pages if p != "/thanks/") + "</urlset>\n")
    open(f"{DIST}/robots.txt", "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}{BASE}/sitemap.xml\n")
    if FORM == "netlify": open(f"{DIST}/_redirects", "w").write("/index.html / 301\n")
    else: open(f"{DIST}/.nojekyll", "w").write("")
    bad = check_links(pages)
    total = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(DIST) for f in fs)
    print("pages:", ", ".join(pages))
    print("dist:", round(total / 1e6, 2), "MB")
    if bad:
        print("BROKEN LINKS:"); [print("  ", b) for b in bad]; sys.exit(1)
