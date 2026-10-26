# Visual QA loop: YellowForce vs Vantra

Goal: our pages look almost identical to Vantra when viewed side by side. Same capture method on both sides,
same names, then composites you can read slice by slice.

All commands run from the site folder:

```sh
cd /Users/axelcassou/life/yellowforce/website
PY=../.venv/bin/python          # Python 3.12 with Playwright 1.64.1 + headless Chromium 156
```

Network or a local server needs the Bash sandbox off (capturing Vantra live, or binding port 8787).

## 1. Build and serve ours on 8787

```sh
python3 build.py                                            # renders src/ into docs/
python3 -m http.server 8787 --bind 127.0.0.1 -d docs        # keep running (background it)
```

Check it answers: `curl -sI http://127.0.0.1:8787/ | head -1`.

**Safari / WebKit previews:** the production CSP has `upgrade-insecure-requests`, so WebKit rewrites every asset URL
on `http://127.0.0.1` to `https://` and the page never loads (TLS errors, `html.ready` never set). Chromium and
Firefox exempt localhost. For WebKit, build with `python3 build.py --dev --out .out/NAME` (never deploy that build)
or serve over HTTPS: `qa/test/functional/serve_https.py` serves `docs/` on https://127.0.0.1:8788 (404.html for
missing paths). The live https site is not affected.

## 2. Capture ours (whole standard set, about 2 minutes)

```sh
$PY tools/shoot.py --preset ours qa/ours                    # pages + states, 1440 and 390
$PY tools/shoot.py --preset ours qa/ours --only home,about  # just some names
```

Every capture prints one status line and a reveal audit. `audit: ok` means nothing visible-sized was left at
opacity < 0.1 or `visibility: hidden` after the scroll-through. Closed FAQ answers and hover-only images are
expected to show up in the audit (Vantra has 5 FAQ answers and 3 hover images on home).

Page names and the paths they map to (defined in `tools/shoot.py`, PAGES / OURS_EXTRA / STATES):

| name | Vantra | ours |
|---|---|---|
| home | `/` | `/` |
| about | `/about-us` | `/about/` |
| work | `/work` | `/services/` |
| coverage | (compared with `work`) | `/coverage/` |
| case | `/work/meridian` | `/coverage/network/` |
| journal | `/journal` | `/insights/` |
| note | `/journal/why-we-price-in-outcomes` | `/insights/ai-swarms/` |
| contact | `/contact-us` | `/contact/` |
| 404 | `/404` | `/404.html` |
| home-menu | click menu button | click `[data-qa=menu-toggle]` |
| home-faq | click first FAQ question, crop FAQ section | click `[data-qa=faq-toggle]` (first), crop `[data-qa=faq]` |
| home-hover | hover first button in the closing CTA band, before/after crops + frame strip | hover `[data-qa=button]` (first) |

**Hooks our markup needs for the state shots** (fallbacks exist, but these make them exact):
`data-qa="menu-toggle"` on the nav menu button, `data-qa="faq"` on the home FAQ section,
`data-qa="faq-toggle"` on each FAQ question button, `data-qa="button"` on the first primary button of the
home closing CTA band (Vantra's hover reference is "Start a project" in that band).

## 3. Make the side-by-sides

```sh
$PY tools/sidebyside.py --pairs qa/ref qa/ours qa/compare --slice 900 --diff
```

Output in `qa/compare/`:
- `NAME-WIDTH-full.png` whole page, Vantra left, ours right, diff third
- `NAME-WIDTH-full-sliceNN.png` the same in 900 px bands: read these one by one with the Read tool
- `home-WIDTH-menu.png`, `home-WIDTH-faq.png`, `home-WIDTH-faq-el.png`, `home-WIDTH-hover-el.png`,
  `home-WIDTH-hover-el-before.png`, `home-WIDTH-hover-frames.png` for the states

The printed "mean diff" (0 to 255) is only a rough trend number between runs of the same page: copy and images
differ on purpose, so read the slices, do not chase the number. Hatched grey = that page has ended.
Drop `--diff` for lighter files; add `--no-full` to skip the tall full composites.

## Single page, fast iteration

```sh
$PY tools/shoot.py http://127.0.0.1:8787/about/ qa/ours --name about --widths 1440
$PY tools/sidebyside.py qa/ref/about-1440-full.png qa/ours/about-1440-full.png qa/compare/about-1440-full.png --slice 900
```

Element or state shots on any page:

```sh
$PY tools/shoot.py http://127.0.0.1:8787/ qa/ours --name home --widths 1440 --selector "[data-qa=faq]"
$PY tools/shoot.py http://127.0.0.1:8787/ qa/ours --name home --state menu --click "[data-qa=menu-toggle]"
$PY tools/shoot.py http://127.0.0.1:8787/ qa/ours --name home --state hover --hover "[data-qa=button]" \
    --selector "[data-qa=button]" --el-before --frames 0,80,160,240,360,600
```

`--click` and `--hover` can be repeated and run in the order given. A selector may list fallbacks:
`"[data-qa=x] || .nav button"` (first that matches wins). Playwright `>> nth=N` picks the Nth match.

## How captures are made (identical on both sides)

- Viewport 1440x900 or 390x844 (any width < 768 uses height 844), deviceScaleFactor 1, scrollbars hidden.
  `--mobile` adds touch-phone emulation; the references were shot without it, so use it on both sides or neither.
- Load, network idle (max 10 s), `document.fonts.ready`, 1 s wait.
- CSS hides the Webflow template bar (`.ctm-box`, the "Customize / Figma / Help / Buy Now" box) and
  `.w-webflow-badge`. Nothing else is injected.
- Scroll to the bottom with real mouse-wheel events in half-viewport steps (drives Lenis and fires every
  ScrollTrigger reveal and lazy image), wait, back to the top, wait for tweens and images.
- Scroll-scrubbed animations (the statement character fill) are set to finished: every GSAP ScrollTrigger
  with `scrub` is disabled at progress 1. This needs `window.ScrollTrigger`, which the UMD build in
  `assets/js/vendor/` exposes. The status line shows `scrub-finished=N` (Vantra home: 1; -1 means
  ScrollTrigger was not found on the page). `--keep-scrub` turns this off.
- Full page via capture-beyond-viewport, so the fixed nav appears once at the top. Pages over 16000 px are shot
  in 4000 px clips and stitched (checked pixel-identical to a single capture).
- Slices are crops of the full page every 900 px, so `sliceNN` lines up with the side-by-side slices.

## References (`qa/ref/`)

Captured 2026-10-25 from https://vantra-studio.webflow.io/ (live template preview), 1440 and 390, 134 files,
56 MB: the 8 pages above (`-full` + `-sliceNN`), plus `home-*-menu`, `home-*-faq(-el)`,
`home-*-hover(-el, -el-before, -frames)`. Checked: every section revealed, statement filled, template bar hidden.
The live `/404` answers HTTP 200 but shows the 404 design. Refresh them (only if Vantra changes):

```sh
$PY tools/shoot.py --preset vantra qa/ref --jobs 4
```
