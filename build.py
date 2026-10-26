#!/usr/bin/env python3
"""YellowForce static site builder (stdlib only).

    python3 build.py            production build into docs/
    python3 build.py --dev      same, but without the CSP upgrade-insecure-requests directive
                                (so http://127.0.0.1 previews load assets in Safari); never deploy a --dev build
    python3 build.py --out .out/NAME [--dev]   build somewhere else (previews); unknown flags are an error

Pages: src/pages/**/*.html. Each starts with a front-matter block:

    ---
    title: Services
    description: One sentence for search and link previews.
    bodyclass: page-services
    path: /services/                         (optional, derived from the file name)
    og: /assets/img/og.png                   (optional)
    ogtype: website                          (optional, "article" for insight posts)
    css: /assets/css/pages/services.css      (optional, comma separated)
    layout: default                          (optional: default | bare)
    sitemap: true                            (optional)
    ---
    <section>...</section>

Directives inside pages and partials:
    <!-- include:NAME -->            src/partials/NAME.html (nested includes allowed)
    <!-- inline:assets/logo/mark.svg -->   inline an SVG file (decorative: aria-hidden)
    {{key}}                           front-matter value (also: site_url, canonical, year, email)
    <img src="/assets/img/gen/x.webp" data-variants sizes="50vw" alt="">
                                      expands srcset from x-800.webp, x-1600.webp, x.webp (only files that exist),
                                      adds loading="lazy" decoding="async" unless loading is set
    data-nav-path="/services/"        on a nav link: build adds is-current + aria-current="page" on the
                                      current page, is-section on its ancestors

Output: pretty URLs. services.html -> docs/services/index.html, coverage/network.html ->
docs/coverage/network/index.html, index.html -> docs/index.html, 404.html -> docs/404.html.
Copies assets/ -> docs/assets/ and static/ -> docs/ (dotfiles included), writes docs/sitemap.xml.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
PAGES = SRC / "pages"
PARTIALS = SRC / "partials"
ASSETS = ROOT / "assets"
STATIC = ROOT / "static"
OUT = ROOT / "docs"  # --out DIR builds somewhere else (parallel agents each preview their own copy); see main()

SITE_URL = "https://yellow-force.com"
EMAIL = "info@yellow-force.com"
DEFAULTS = {
    "title": "YellowForce",
    "description": "YellowForce runs your entire cybersecurity, A to Z. AI agents and cyber experts defend every domain, 24/7.",
    "bodyclass": "",
    "og": "/assets/img/og.png",
    "ogtype": "website",
    "css": "",
    "layout": "default",
    "sitemap": "true",
}

CSP_PROD = ("default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; "
            "font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'none'; "
            "upgrade-insecure-requests")
CSP_DEV = CSP_PROD.replace("; upgrade-insecure-requests", "")

LAYOUT = """<!doctype html>
<html lang="en">
<head>
<!-- include:head -->
</head>
<body class="{{bodyclass}}">
<a class="skip-link" href="#main">Skip to content</a>
<!-- include:nav -->
<main id="main" class="main" tabindex="-1">
{{__content__}}
</main>
<!-- include:footer -->
<!-- include:toast -->
</body>
</html>
"""

BANNED = [
    (r"—", "em dash"),
    (r"mailto:", "mailto link (use a data-copy-email button)"),
    (r"\bplatform\b", "'platform'"),
    (r"\bSaaS\b", "'SaaS'"),
    (r"\bsign[ -]?up\b", "'sign up'"),
    (r"\bfree trial\b", "'free trial'"),
    (r"\bdashboard\b", "'dashboard'"),
    (r"\blog ?in\b", "'log in'"),
    (r"\bPalantir\b", "'Palantir'"),
    (r"\bontology\b", "'ontology'"),
    (r"\bdesign partners?\b", "'design partner'"),
    (r"\bQ[1-4] 20\d\d\b", "quarter date"),
    (r"\bpilot\b", "'pilot'"),
    (r"\b\d+ (days|weeks)\b", "slow timeline"),
    (r"\btrusted by\b", "'trusted by'"),
]

warnings: list[str] = []


def warn(msg: str) -> None:
    warnings.append(msg)


def parse_front_matter(text: str, name: str) -> tuple[dict, str]:
    meta: dict = {}
    m = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        warn(f"{name}: no front matter")
        return meta, text
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            warn(f"{name}: bad front-matter line {line!r}")
            continue
        k, v = line.split(":", 1)
        meta[k.strip().lower()] = v.strip()
    return meta, text[m.end():]


def page_path(rel: Path) -> str:
    """src/pages relative file -> URL path."""
    parts = list(rel.with_suffix("").parts)
    if parts == ["404"]:
        return "/404.html"
    if parts[-1] == "index":
        parts = parts[:-1]
    return "/" + "/".join(parts) + ("/" if parts else "")


def out_file(url_path: str) -> Path:
    if url_path.endswith(".html"):
        return OUT / url_path.lstrip("/")
    return OUT / url_path.lstrip("/") / "index.html"


def read_partial(name: str) -> str:
    p = PARTIALS / f"{name}.html"
    if not p.exists():
        warn(f"missing partial: {name}")
        return f"<!-- missing partial {name} -->"
    return p.read_text(encoding="utf-8")


def expand_includes(text: str, depth: int = 0) -> str:
    if depth > 8:
        warn("include depth exceeded")
        return text

    def rep(m: re.Match) -> str:
        return expand_includes(read_partial(m.group(1).strip()), depth + 1)

    return re.sub(r"<!--\s*include:\s*([\w\-/]+)\s*-->", rep, text)


def expand_inline_svg(text: str) -> str:
    def rep(m: re.Match) -> str:
        rel = m.group(1).strip().lstrip("/")
        p = ROOT / rel
        if not p.exists():
            warn(f"inline svg not found: {rel}")
            return ""
        svg = p.read_text(encoding="utf-8")
        svg = re.sub(r"<\?xml.*?\?>", "", svg, flags=re.S)
        svg = re.sub(r"<!DOCTYPE.*?>", "", svg, flags=re.S | re.I)
        svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
        svg = svg.strip()

        def fix_root(sm: re.Match) -> str:
            tag = sm.group(0)
            tag = re.sub(r'\s(role|aria-label|aria-labelledby|width|height)="[^"]*"', "", tag)
            return tag[:-1] + ' aria-hidden="true" focusable="false">'

        return re.sub(r"<svg\b[^>]*>", fix_root, svg, count=1)

    return re.sub(r"<!--\s*inline:\s*([^\s]+)\s*-->", rep, text)


def fill_vars(text: str, ctx: dict, name: str) -> str:
    def rep(m: re.Match) -> str:
        key = m.group(1).strip()
        if key in ctx:
            return str(ctx[key])
        warn(f"{name}: unknown variable {{{{{key}}}}}")
        return ""

    return re.sub(r"\{\{\s*([\w\-]+)\s*\}\}", rep, text)


def expand_images(text: str, name: str) -> str:
    def rep(m: re.Match) -> str:
        tag = m.group(0)
        src_m = re.search(r'\ssrc="([^"]+)"', tag)
        if not src_m:
            return tag.replace(" data-variants", "")
        src = src_m.group(1)
        stem, ext = src.rsplit(".", 1)
        cands = [(f"{stem}-800.{ext}", 800), (f"{stem}-1600.{ext}", 1600), (src, 2400)]
        found = [(u, w) for (u, w) in cands if (ROOT / u.lstrip("/")).exists()]
        new = tag.replace(" data-variants", "")
        if found:
            srcset = ", ".join(f"{u} {w}w" for u, w in found)
            mid = next((u for u, w in found if w == 1600), found[-1][0])
            new = new.replace(f'src="{src}"', f'src="{mid}" srcset="{srcset}"', 1)
        else:
            warn(f"{name}: image not found yet: {src}")
        if " sizes=" not in new:
            new = new.replace("<img", '<img sizes="100vw"', 1)
        if " loading=" not in new:
            new = new.replace("<img", '<img loading="lazy"', 1)
        if " decoding=" not in new:
            new = new.replace("<img", '<img decoding="async"', 1)
        return new

    return re.sub(r"<img\b[^>]*\sdata-variants\b[^>]*>", rep, text)


def mark_nav(text: str, current: str) -> str:
    def rep(m: re.Match) -> str:
        tag = m.group(0)
        target = m.group(2)
        cls = ""
        extra = ""
        if target == current:
            cls = "is-current"
            extra = ' aria-current="page"'
        elif target != "/" and current.startswith(target):
            cls = "is-section"
        if not cls:
            return tag
        if re.search(r'\sclass="', tag):
            tag = re.sub(r'\sclass="([^"]*)"', lambda c: f' class="{c.group(1)} {cls}"', tag, count=1)
        else:
            tag = tag[:-1] + f' class="{cls}">'
        return tag[:-1] + extra + ">"

    return re.sub(r'<(a|button)\b[^>]*\sdata-nav-path="([^"]*)"[^>]*>', rep, text)


def space_brackets(text: str) -> str:
    """Bracket labels "( 24/7 )" get wide inner spacing (4 no-break spaces) in visible text only."""
    out = []
    skip = False
    for part in re.split(r"(<[^>]+>)", text):
        if part.startswith("<"):
            tag = part[1:].split()[0].lower().rstrip(">") if len(part) > 1 else ""
            if tag in ("script", "style", "title", "textarea"):
                skip = True
            elif tag in ("/script", "/style", "/title", "/textarea"):
                skip = False
            out.append(part)
        elif skip:
            out.append(part)
        else:
            out.append(re.sub(r"\( ([^()<>\n]{1,48}?) \)", "(\u00a0\u00a0\u00a0\u00a0\\1\u00a0\u00a0\u00a0\u00a0)", part))
    return "".join(out)


def css_links(css: str) -> str:
    out = []
    for href in [c.strip() for c in css.split(",") if c.strip()]:
        out.append(f'<link rel="stylesheet" href="{html.escape(href)}">')
    return "\n".join(out)


def lint(text: str, name: str) -> None:
    visible = re.sub(r"<script\b.*?</script>", "", text, flags=re.S)
    visible = re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>', "", visible)
    visible = re.sub(r"<svg\b.*?</svg>", "", visible, flags=re.S)
    for pat, label in BANNED:
        for m in re.finditer(pat, visible, flags=re.I if label != "'SaaS'" else 0):
            s = max(0, m.start() - 40)
            snippet = re.sub(r"\s+", " ", visible[s:m.end() + 40])
            warn(f"{name}: {label}: ...{snippet}...")
            break


def build_page(src: Path, dev: bool) -> tuple[str, Path, dict]:
    rel = src.relative_to(PAGES)
    name = str(rel)
    meta, body = parse_front_matter(src.read_text(encoding="utf-8"), name)
    ctx = dict(DEFAULTS)
    ctx.update(meta)
    url_path = ctx.get("path") or page_path(rel)
    ctx["path"] = url_path
    title = ctx["title"]
    if "YellowForce" not in title:
        title = f"{title} | YellowForce"
    ctx["page_title"] = html.escape(title, quote=False)
    ctx["title_attr"] = html.escape(title)
    ctx["description_attr"] = html.escape(ctx["description"])
    ctx["canonical"] = SITE_URL + ("/404.html" if url_path == "/404.html" else url_path)
    og = ctx["og"]
    ctx["og_image"] = og if og.startswith("http") else SITE_URL + og
    ctx["site_url"] = SITE_URL
    ctx["email"] = EMAIL
    ctx["year"] = str(_dt.date.today().year)
    ctx["csp"] = CSP_DEV if dev else CSP_PROD
    ctx["extra_css"] = css_links(ctx.get("css", ""))
    ctx["robots"] = "noindex" if url_path == "/404.html" or ctx.get("sitemap", "true").lower() == "false" else "index, follow"

    if ctx.get("layout", "default") == "bare":
        doc = body
    else:
        doc = LAYOUT.replace("{{__content__}}", body)
    doc = expand_includes(doc)
    doc = fill_vars(doc, ctx, name)
    doc = expand_inline_svg(doc)
    doc = expand_images(doc, name)
    doc = mark_nav(doc, url_path)
    doc = space_brackets(doc)
    lint(doc, name)
    return url_path, out_file(url_path), ctx | {"html": doc}


def check_links(pages: dict[str, str]) -> None:
    missing: dict[str, set[str]] = {}
    for url, doc in pages.items():
        refs = [m.group(1) for m in re.finditer(r'\s(?:href|src)="(/[^"#?]*)', doc)]
        for m in re.finditer(r'\ssrcset="([^"]+)"', doc):
            refs += [part.strip().split(" ")[0] for part in m.group(1).split(",")]
        for ref in refs:
            if not ref.startswith("/") or ref.startswith("//"):
                continue
            target = OUT / ref.lstrip("/")
            if ref.endswith("/"):
                target = target / "index.html"
            if not target.exists():
                missing.setdefault(ref, set()).add(url)
    for ref in sorted(missing):
        pages_using = sorted(missing[ref])
        shown = ", ".join(pages_using[:4]) + (f" +{len(pages_using) - 4}" if len(pages_using) > 4 else "")
        warn(f"missing target {ref} (linked from {shown})")


def last_changed(src: Path) -> str:
    """Date the page source last changed: its last git commit if the file is unmodified, else its mtime."""
    try:
        dirty = subprocess.run(["git", "status", "--porcelain", "--", str(src)], cwd=ROOT,
                               capture_output=True, text=True, timeout=10).stdout.strip()
        if not dirty:
            d = subprocess.run(["git", "log", "-1", "--format=%cs", "--", str(src)], cwd=ROOT,
                               capture_output=True, text=True, timeout=10).stdout.strip()
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
                return d
    except (OSError, subprocess.SubprocessError):
        pass
    return _dt.date.fromtimestamp(src.stat().st_mtime).isoformat()


def write_sitemap(entries: dict[str, str]) -> None:
    """entries: URL path -> lastmod date of its source page (not the build date, which Google ignores)."""
    rows = "\n".join(
        f"  <url><loc>{SITE_URL}{p}</loc><lastmod>{entries[p]}</lastmod></url>" for p in sorted(entries, key=lambda p: (p != "/", p))
    )
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + rows + "\n</urlset>\n",
        encoding="utf-8",
    )


def strip_css_comments(root: Path) -> None:
    """Published CSS carries no comments (they are build notes). Vendor files keep theirs."""
    for css in root.rglob("*.css"):
        text = css.read_text(encoding="utf-8")
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
        text = re.sub(r"[ \t]+$", "", text, flags=re.M)
        text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
        css.write_text(text, encoding="utf-8")


def refresh_security_txt() -> None:
    """RFC 9116: Expires must stay under a year out, so it is rewritten on every build (build date + 180 days)."""
    p = OUT / ".well-known" / "security.txt"
    if not p.exists():
        return
    exp = (_dt.datetime.now(_dt.timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
           + _dt.timedelta(days=180)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    text = p.read_text(encoding="utf-8")
    if not re.search(r"^Expires:", text, flags=re.M):
        warn("security.txt has no Expires line")
        return
    p.write_text(re.sub(r"^Expires:.*$", f"Expires: {exp}", text, flags=re.M), encoding="utf-8")


def main() -> int:
    global OUT
    ap = argparse.ArgumentParser(description="Build the YellowForce site (src/ -> docs/).")
    ap.add_argument("--dev", action="store_true", help="drop upgrade-insecure-requests from the CSP (local previews only)")
    ap.add_argument("--out", metavar="DIR", help="build into DIR instead of docs/")
    args = ap.parse_args()  # unknown flags (even --help typos) stop here instead of building into docs/
    dev = args.dev
    if args.out:
        OUT = Path(args.out).resolve()
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    if ASSETS.exists():
        # build notes (*.md, VERSIONS.txt) stay private; licence files (fonts/OFL.txt) are published
        shutil.copytree(ASSETS, OUT / "assets", ignore=shutil.ignore_patterns(
            ".DS_Store", "*.psd", "_src", "*.tmp", "*.md", "VERSIONS.txt"))
        strip_css_comments(OUT / "assets" / "css")
    if STATIC.exists():
        shutil.copytree(STATIC, OUT, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".DS_Store"))
        refresh_security_txt()

    built: dict[str, str] = {}
    sitemap: dict[str, str] = {}
    for src in sorted(PAGES.rglob("*.html")):
        if any(part.startswith("_") for part in src.relative_to(PAGES).parts):
            continue
        url, dest, ctx = build_page(src, dev)
        if url in built:
            warn(f"duplicate output path {url} from {src}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(ctx["html"], encoding="utf-8")
        built[url] = ctx["html"]
        if url != "/404.html" and ctx.get("sitemap", "true").lower() != "false":
            sitemap[url] = last_changed(src)
    write_sitemap(sitemap)
    check_links(built)

    print(f"built {len(built)} page(s) into {OUT.relative_to(ROOT)}/" + (" [dev CSP]" if dev else ""))
    for u in sorted(built):
        print(f"  {u}")
    if warnings:
        print(f"\n{len(warnings)} warning(s):")
        for w in warnings:
            print(f"  - {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
