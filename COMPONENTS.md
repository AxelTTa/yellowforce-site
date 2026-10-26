# YellowForce components (for page builders)

Read BRIEF.md first. This file tells you which classes and attributes exist so you can build a page without reading the CSS.
Source: `assets/css/tokens.css`, `base.css`, `components.css`, `assets/js/main.js`, `assets/js/streaks.js`.
Own markup only. Never paste Vantra HTML, class names or SVGs.

## 1. Build, pages, partials

- Build: `python3 build.py` (production) or `tools/serve.sh` (build + http://127.0.0.1:8787/). `python3 build.py --dev` drops `upgrade-insecure-requests` from the CSP: needed to preview in Safari/WebKit over http://127.0.0.1 (Chromium and Firefox exempt localhost). Previews: `python3 build.py --out .out/NAME`. Unknown flags are an error.
- The build prints warnings: missing images/pages, unknown `{{vars}}`, and copy-rule hits (em dash, `mailto:`, "platform", "SaaS", "pilot", "N days/weeks", quarter dates, "trusted by"...). Fix copy-rule hits. "Dashboard" is allowed (Oct 26): only as the private client dashboard, never as the product.
- A page is `src/pages/<name>.html` = front matter + the content of `<main>`. Layout (head, skip link, nav, main, footer, toast) is added for you.

```
---
title: Services | YellowForce fully managed cybersecurity   (" | YellowForce" is appended if the name is missing)
description: One sentence.
bodyclass: page-services
css: /assets/css/pages/services.css     (optional, comma separated)
ogtype: article                         (optional, insight posts)
og: /assets/img/og.png                  (optional)
path: /services/                        (optional, derived from file name)
layout: bare                            (optional, you write the whole document)
sitemap: false                          (optional)
---
<section class="block gutter">...</section>
<!-- include:cta -->                     (closing CTA band; must be the LAST thing in the page so the footer overlaps it)
```

- URLs: `services.html` -> `/services/`, `coverage/network.html` -> `/coverage/network/`, `404.html` -> `/404.html`. Files or folders starting with `_` are skipped.
- Directives: `<!-- include:NAME -->` (src/partials), `<!-- inline:assets/logo/mark.svg -->` (inline SVG, decorative), `{{email}}`, `{{site_url}}`, `{{canonical}}`, `{{year}}`, any front-matter key.
- Always root-relative URLs: `/assets/...`, `/coverage/`.
- Partials (shared-ui lane owns them): `head`, `nav`, `cta`, `footer`, `toast`, `logo`, `logo-mark`, `logo-word`.
- Nav bar (`nav.html`, Axel's pick Oct 26, `qa/nav/JUDGE.md`): one compact centered bar. `.topbar` (fixed) > `.pill` (hugs its content; full width under 768) > `.pill__bar` (navy 96% glass, 8% edge, top highlight): `.pill__brand` (the `logo` lockup, links home; the mark's two layers part on hover) + `.pill__links` (Services, Coverage, About, Insights; 768px up) + `.pill__actions` (`.pill__talk` = the site's `btn btn--light` to /contact/, its chip turns amber on hover; `.pill__toggle` = a square 4-dot icon button, no tile at rest, the dots turn amber and rotate when open). Current page: the build adds `is-current`/`is-section` + `aria-current` from `data-nav-path`; the bar shows a 4px amber square under that link. Type floor 13px in the bar. Under 768: lockup, Talk to us and the square (480-767 the bar still hugs them and the menu opens at its width; phones under 480: across the gutters, menu full width). Under 360px: Talk to us leaves the bar, the square becomes "Menu" (rolls to "Close") and the white button sits at the bottom of the menu (`.pill__cta`).
- Menu card (`.pill__drawer`): opaque navy (`--nav-solid`, the bar's navy without the 96% glass, so nothing shows through on phones), its own card under the right end of the bar (under 768: exactly under the bar, at its width), over a flat navy dim (`.topbar__scrim`, no backdrop blur: cheaper on weak machines). Type floor 14px (15px on phones). Rows `.pill__row > .pill__label + .pill__note + .pill__icon`; Services and Coverage rows open submenus (`.pill__sub > .pill__sublink`). Rows the bar already shows (`li.pill__item--bar`: Home, About, Insights) are hidden from 768px up. The current-page square and the live Under attack dot are `::before` markers hung in the row's left padding (`--row-x`), so every label starts on one edge. Row labels are Instrument Sans **600**; arrow and copy icons are scaled 1.22. Keyboard: Enter opens and focuses the first visible row, Tab stays inside, Esc closes and returns focus to the button. The bar stays fixed and visible while scrolling (it does not hide over the FAQ).
- Logo: `<!-- include:logo -->` = the full lockup (inline SVG mark + live-text wordmark "**Yellow**Force" in our Inter, `.logo > .logo__mark + .logo__word > .logo__yellow + .logo__force`). `<!-- include:logo-mark -->` = the mark only (`.logo__mark`, inlines `assets/logo/mark.svg`). `<!-- include:logo-word -->` = the wordmark only (`.logo__word`; `logo` uses it, so it is defined once). Never put the wordmark in an `<img>` (SVG text cannot load our font). Colors come from tokens, so the same markup works everywhere: on paper amber front + navy back, "Yellow" navy, "Force" slate; inside `.on-dark` and the nav bar the back turns white, "Yellow" white, "Force" slate-light. Size it with `font-size` on the parent (the mark is 3.17em wide). After a mark swap run `../.venv/bin/python tools/make_icons.py` (favicons, manifest icons, OG image).
- Bracket labels: write `( 24/7 )` with single spaces; the build widens the inner spacing automatically.

## 2. Images

```html
<div class="shot shot--16x9 media"><img src="/assets/img/gen/hero.webp" data-variants sizes="(max-width: 767px) 100vw, 50vw" alt=""></div>
```
- `data-variants`: build adds `srcset` from `NAME-800.webp`, `NAME-1200.webp`, `NAME-1600.webp`, `NAME.webp` (only files that exist), `loading="lazy"`, `decoding="async"`. Add `loading="eager" fetchpriority="high"` for the first image on a page (only the first-screen ones: two on Services, one elsewhere); the build preloads the first `fetchpriority="high"` image from `<head>` (same srcset/sizes). The 1200 files are for DPR 3 phones (1170 px): after adding or regrading an image run `../.venv/bin/python tools/make_1200.py`.
- Every image container gets class `media`: dark amber gradient fallback + the img fills it (`object-fit: cover`). A missing/broken file keeps the gradient.
- Ratios: `.shot--16x9 --21x9 --4x3 --3x2 --4x5 --1x1`, `.shot` = radius 16px, `.shot--hover` = scale 1.05 on hover.
- Decorative images: `alt=""` and `aria-hidden="true"` on the container.

## 3. Layout and type

| Class | Use |
|---|---|
| `.block` | section vertical padding 6em (`.block--top-0`, `.block--bottom-0`, `.block--about` 10.5em bottom, `.block--clip` overflow clip, needed around carousels: clip, not hidden, so keyboard focus can never scroll the section sideways) |
| `.gutter` | side padding 3em (1.25em <= 991) |
| `.frame` | max 1920 container |
| `.stack` | column gap 5em (header to content). `.stack--m` 3em, `.stack--s` 1.5em |
| `.grid-12` + `.span-4/6/12` | 12 col grid, 1.5em gutter |
| `.on-dark` | flips text/line/logo tokens for navy surfaces (text paper, meta slate-light, focus ring amber) |
| `.t-h0` `.t-h1` ... `.t-h6`, `h1-h6` | Inter display headings (h0 8.75em/700) |
| `.t-statement` | 2.875em statement paragraph |
| `.t-lead` (`--s`) | 2em intro text next to an h2 |
| `.t-body-l` | 1.25em/500 quote-like text; `.t-body-m` 1.25em paragraph; `.t-muted` |
| `.t-label` (`--xs`, `--strong`) | small uppercase meta / bracket label |
| `.sr-only`, `.dot` (`--live` pulse, `--ring` for paper), `.icon` (1em svg) |

Headings: 2 to 5 words, end with a period, two lines with `<br>`: `<h2 data-reveal="lines">What<br>we do.</h2>`.

## 4. Components

**Section header**
```html
<div class="head">
  <h2 class="head__title" data-reveal="lines">Every domain,<br>covered.</h2>
  <div class="head__meta" data-reveal="fade"><span>( 10 / 10 domains )</span><span>Watched 24/7</span></div>
</div>
```
Variants: `.head--center` (label `<p class="t-label">` above an h1/h2), `.head--split` (h2 left + `<p class="head__text t-lead">` right).
On phones the meta stays on the right of the two-line title, same row, like the reference (it wraps its own lines; keep both meta lines short, about 30 characters max).

**Buttons** (text roll + arrow chip). Variants: `btn--dark` (default), `btn--light` (on dark/photo), `btn--ghost` (on paper), `btn--glass` (on dark), `btn--block`. Row: `.btn-row` (`--center`).
```html
<a class="btn btn--dark" href="/contact/">
  <span class="btn__roll"><span class="btn__line">Talk to us</span><span class="btn__line" aria-hidden="true">Talk to us</span></span>
  <span class="btn__chip" aria-hidden="true"><svg class="btn__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M7 17 17 7M9 7h8v8"/></svg><svg class="btn__icon" ...same...></svg></span>
</a>
```
Copy-email button: a `<button type="button" data-copy-email>` (use `data-copy-email="urgent"` for the Under attack toast line). Chip: two copy icons + a third `btn__icon btn__icon--done` check icon (shown after copying). Second roll line may read the address. Exact markup: FAQ "under attack" item in `src/pages/index.html`. JS adds `.is-copied` to any copy button for 2.4s.

**Copy email (text style)**: `<button class="mail" type="button" data-copy-email aria-label="Copy email address info@yellow-force.com"><span data-email-text>info@yellow-force.com</span><svg class="icon">copy</svg></button>`. Big contact version: add `mail--xl`. The Contact page's big address is `.ct-big__addr` (contact.css): one line at every width (`white-space: nowrap`, size capped to its column with container units), never broken at its hyphen. Never `mailto:`, never a form. The toast lives in the layout; JS falls back to selecting `[data-email-text]` if the clipboard is blocked.

**Image cards 2x2** `.tiles > .tiles__cell > a.tile` with `.tile__media.media > img`, `.tile__glass > .tile__row (.tile__name + .tile__meta > span x2) + .tile__reveal > .tile__reveal-inner > .tile__line + .tile__more`. Add `data-reveal="stagger"` on `.tiles`.
One look on Home, Services and Coverage (all in components.css, no page overrides needed): at rest a light frosted panel at least 50% wide x 4em, name (Inter display, 1.75em, 500, one line, like the reference) with the two meta lines stacked right next to it; hover/focus grows it to the full card width x 8em and opens the line + link. Keep names short (one to three words) so the rest panel stays near half the card. On phones the line and link stay hidden (the whole card is the link), like the reference.

**Coverage table** `ul.ledger[data-reveal=stagger][data-bars] > li > a.ledger__row` with `h3.ledger__name`, `.ledger__tag`, `.ledger__gauge > .ledger__gauge-meta (2 spans) + .ledger__track > .ledger__fill`, `.ledger__end`. Bars fill on scroll over a navy-11 track, one row after the other (1.2s, .16s stagger), then each bar gets a slow light pass (`.is-live`, 6s loop, offset per row) so the rows read as live; reduced motion shows the full bars with no pass. `--fill` sets a partial width, e.g. `style="--fill: 60%"` on `.ledger__fill`. Home keeps every bar full (the honest value: every domain is watched).
`.ledger--compact` (Home, 3 rows like the reference; keep each tag to one line at 1440, about 30 characters): on phones each row is one line, name left and gauge (meta over the bar) right; tag and end label drop out. Without it, rows stack (name/end, tag/gauge) on phones.

**Carousel** (practices, reasons, any card row)
```html
<section class="block gutter block--clip"> ...
<div class="carousel" data-carousel role="region" aria-roledescription="carousel" aria-label="Six practices">
  <div class="carousel__viewport" data-carousel-viewport tabindex="0" role="group" aria-label="Six practices. Use the arrow keys to move.">
    <ul class="carousel__track" data-carousel-track data-reveal="stagger"><li class="carousel__slide">CARD</li>...</ul>
  </div>
  <button class="carousel__btn carousel__btn--prev" type="button" data-carousel-prev aria-label="Previous"><span class="carousel__arrow">svg</span></button>
  <button class="carousel__btn carousel__btn--next" type="button" data-carousel-next aria-label="Next"><span class="carousel__arrow">svg</span></button>
</div>
```
Slide width 28em (`.carousel--narrow` 23.9em), same on phones (298px at 390: the next card peeks under the paper fade, the arrow chip sits over the gap, like the reference). Buttons, drag/swipe, arrow keys; wraps at the ends. Tabbing onto a slide's link moves the carousel to it. The viewport never selects text on drag. Slides stay plain list items (no role on the `<li>`).
Cards: `.practice` (`.practice__num`, `svg.glyph.practice__glyph`, `.practice__body > .practice__title + .practice__text`; can be an `<a>`; the text reserves two lines so titles align, keep it to two lines at 1440, about 60 characters), `.reason` (`.reason__who > .reason__icon + .reason__id > .reason__title + .reason__meta`, `.reason__text`; odd slides flip automatically), `.reason--feature on-dark` (`.reason__score > .reason__figure(24<small>/7</small>) + .reason__figure-text`, `.reason__crew > .reason__stack > .reason__chip` x4 + `.reason__crew-label`). Chips are 32px overlapping circles in the reference's avatar slot, never faces. Home uses three close crops of our light imagery, each a bright amber point so the row reads as one set: `--img --burst` (`gen/about-2-320.webp`), `--img --swarm` (`gen/threat-swarm-320.webp`), `--img --trail` (`gen/status-320.webp`), then `--paper` (put `<!-- include:logo-mark -->` inside). The label is two short uppercase lines with a `<br>` ("AI and experts / on watch now"); it never wraps further. An `--img` chip is `<span class="reason__chip reason__chip--img reason__chip--burst media"><img src="...-320.webp" alt="" loading="lazy" decoding="async"></span>` (320 px file, zoomed crop, object-position per modifier). `--live` (`<span class="dot dot--live">`), `--amber` / `--slate` (solid chip with a navy glyph) remain for other pages.
Pixel glyphs: inline SVG, 30px cells on a 180 grid, `<rect width="24" height="24" rx="5">` LED blocks, `fill: currentColor` via `.glyph`. Examples in `src/pages/index.html`.

**Reel** (live canvas)
```html
<div class="reel on-dark" data-streaks-scope data-reveal="frame">
  <canvas class="reel__canvas" data-streaks="reel" aria-hidden="true"></canvas>
  <div class="reel__island"><span class="reel__dot"></span><span class="reel__items"><span class="reel__label">YellowForce reel</span><span class="reel__time" data-clock>Live</span></span><span class="reel__sep"></span>
    <button class="reel__toggle" type="button" data-streaks-toggle aria-pressed="false" aria-label="Pause reel">pause svg.is-pause + play svg.is-play</button></div>
</div>
```
`data-streaks="reel"` is crisp vector light (Axel, Oct 26: the long exposure "gives the illusion that it's blurry"): a swarm of thin amber tracers with white-hot heads rushes a shield arc; a bracket arms over the zone a swarm is about to hit, each tracer stops at the line, its tail drains into the point, the arc flashes white (small ring, glint, a few sparks) and it dies. Every moving line is a hard-edged stroke 1 to 2 device px, no blur, no per-frame pixel work. The shield is static: its hairline, inner arcs and instrument ticks are an SVG (`.reel__shield`, built by streaks.js once per resize, one device px hairlines) and its rim light and navy lift are CSS radial gradients on `.reel` driven by `--shield-x/-y/-r/-ax/-ay` (set by streaks.js; the fallbacks keep a navy frame without JS). Wide frames: threats come from the left, the arc sits at about 66% of the width; tall frames (phones, tablets in portrait): they fall from the top onto a horizon arc at about 58% of the height. The live canvas is cropped to just past the arc. Frame height 80vh (max 960px) at every width, 80svh on phones, like the reference. Perf numbers and captures: `qa/anim/PERF.md`.
`data-streaks="hero"` (alias `accent`) = transparent layer over the home hero image (`<canvas class="hero__streaks">`, `mix-blend-mode: screen`): crisp sparks fly along the image's own spark streaks (a direction grid measured from `gen/hero.webp`, `HERO_FLOW` in streaks.js) into its arc of light and wink out there, and fine tracers ride the arc's outer fibres. It is tied to that image's geometry: a new hero image needs a new ridge (`HERO_RIDGE`) and flow grid. The headline zone (bottom left; bottom on phones) stays clean. Runs continuously (Axel, Oct 26). `data-streaks="pinch"` = the 404 layer over `gen/threat-breach.webp` (tracers converge into the pinch and stop there, faded over the copy; the pinch position is read through the image's real CSS transform). main.js loads streaks.js only on pages with a canvas and starts each canvas lazily: first-screen ones right after first paint, the reel in idle time about two screens before it scrolls in; a canvas stays `visibility: hidden` until its engine has sized it (`.is-on`, no layout shift). Engine rules for all three: DPR capped at 2 (1.5 on weak devices), quality steps down by itself when frames run long (DPR, density, then 30 fps), pauses offscreen, in hidden tabs and on the reel toggle; reduced motion draws one static frame. The reel toggle keeps the fixed name "Pause reel"; `aria-pressed` carries the state. Optional `data-seed="7"` changes the layout. `[data-clock]` shows live San Francisco time.

**FAQ** `.faq` (12-col: `.faq__head` left, `.faq__list[data-faq]` right) > `.faq__item > h3.faq__h > button.faq__q#id[aria-expanded][aria-controls] (span + .faq__icon)` and `div.faq__a#id[role=region][aria-labelledby] > .faq__a-inner > p`. Answers are open without JS. Add `is-open` on an item to start it open. The question text must be the button's first `<span>` (it carries the 1.375em display size; the button keeps the base size so rows are 2em of the base, about 85px at 1440). No rule above the first row, a hairline under every row. Keep it to 5 or 6 questions (Home has 6, "Is this software?" first and "We’re under attack right now." last).

**Insights** `.notes` (2 cols, `.notes--3`) > `a.note` (`.note__media.media > img`, `.note__scrim`, `.note__body > .note__meta (spans) + .note__title`, `.note__more` arrow chip). Index list: `ul.index > li > a.index__row` (`.index__content > .index__label + .index__title`, `.index__meta > .index__peek.media > img` hover preview + `.index__date` + `svg.icon.index__arrow`). `.notes + .index` spacing is automatic. `.notes__foot` for a button below. Card titles keep the h4 size on phones (two lines, max 13em).

**Hero (home)** `.hero.on-dark > .hero__media.media > img` + optional `canvas.hero__streaks[data-streaks=hero]` + `.hero__inner.gutter > .hero__row.frame > .hero__copy (p.hero__label.t-label + h1.hero__title.t-h0) + button.status`. `.hero__title` uses line-height 1.02 (not .9): at .9 the "g" of "Fight" overlaps the "W" below; 1.02 leaves .03 to .04em at every width.
Status card = the "Under attack?" copy-email button: `<button class="status" type="button" data-copy-email="urgent" aria-label="...">` > `.status__body > .status__label (.dot--live + "Under attack?") + .status__main > .status__text + .status__mail ([data-email-text] address + svg.status__icon copy + svg.status__icon.status__icon--done check)`, then `.status__thumb.media > img` (a real photo, not a graphic: `photo/insight-2`, a lit hand on a keyboard, lifted with `brightness(1.18)` so the thumb is the brightest point of the card like the reference). Dark frosted chip a step above the hero's navy-deep (`rgba(20, 32, 60, .5)` + blur 12px + a paper-07 hairline), like the reference's chip, so the photo thumb is the brightest point; hides <= 767 like the reference.

**Inner page heroes**
- `.page-head` (centered, 12em top padding): `p.t-label` + `h1.page-head__title` + `p.page-head__text`. `.page-head--left` variant.
- `.cover.on-dark` (inset dark card like the home hero, 960px max): `.cover__media.media > img` (scrim added), optional `canvas.cover__streaks[data-streaks=pinch]` (404 only: it is tied to that image), `.cover__inner` (`--bottom` variant) > `p.t-label.cover__label`, `h1.cover__title`, `p.cover__text`, `.btn-row`. `.cover--full` (full height, 20px radius), `.cover--short` (80vh). Use for About hero, domain pages, 404.

**Closing CTA band**: `<!-- include:cta -->` (copy from copy.md, Talk to us + How we work + copy-email line). Not on Contact, Privacy, Security, 404. Title in sentence case ("We’ll take it / from here."), like the reference band. Full screen band (100vh, 100svh on phones) with the content block centered; on phones (<= 479) the title is `min(h0, 16.5vw)` (64px at 390) and two lines down to 320px. On phones (<= 767) the 16:9 `gen/cta` is cropped at `object-position: 28% 50%` so the light river crosses the band on a diagonal with dark corners, and the navy scrim is only an ellipse (72% x 38%) behind the text block, so the rest of the light stays amber.

**Prose** `.prose` (legal pages, article bodies): h2, h3, p, ul (square bullets), ol (01 numbering), blockquote, hr, code, `.mail`. Article layout: `.article > .article__rail (sticky) + .prose`.

**Other blocks**
- `.mosaic` (5fr 2fr 3fr image strip of `.media` cells), `.gallery` (`.gallery__wide` 16:9, `.gallery__half` / `.gallery__third` 4:5).
- `.facts > .fact > .fact__label + .fact__value` (4 stat cells with hairline). `.figure > .figure__num + .figure__unit` (giant number). Only true facts.
- `.rows > .rows__item > h3.rows__title + p.rows__text + span.rows__end` (label | text | short uppercase end).
- `.pile > .pile__item > p.t-label.pile__label + .pile__grid > h2 + p.pile__text` (sticky stacking rows, up to 6).
- `.direct > .direct__cell > span.t-label + .direct__value` (contact strip; put the copy-email `.mail` in a value).
- `.chips > a.chip` (`.is-current` or `aria-current="page"`).
- `.link-arrow` (small text link + arrow).

## 5. Motion attributes (JS, all optional, off under reduced motion)

| Attribute | Effect |
|---|---|
| `data-reveal="lines"` | headings: SplitText lines fade + rise .25em, .5s power3.out, once. The heading's aria-label reads a `<br>` as a space |
| `data-reveal="statement"` | characters fill from 15% to 100% opacity, scrubbed by scroll. Put it on an `aria-hidden` span next to a `.sr-only` copy of the text (see Home) |
| `data-reveal="fade"` | fade + rise .5em (`data-delay=".3"`: a choreography offset, played at half) |
| `data-reveal="stagger"` | direct children fade + rise, .08s stagger (`data-stagger`, `data-delay`) |
| `data-reveal="frame"` | scale .95 -> 1 + rise 2em, .6s |
| `data-reveal="status"` | hero status card, delay .27s |
| `data-bars` | `.ledger__fill` bars grow on scroll, staggered per row, then a slow light pass (`.is-live`) |
| `data-copy-email` / `="urgent"` | copy info@yellow-force.com + toast |
| `data-carousel*`, `data-faq`, `data-streaks*`, `data-clock`, `data-lenis-prevent` | see components |

Elements with `data-reveal` are hidden until JS runs (`html.motion`), with opacity only, never `visibility`, so content below the fold stays reachable by Tab and screen readers; a 3.5s failsafe shows everything if JS fails. Reveals start when the element's top enters the viewport, after .05s, and run .5s power3.out (speed pass, Oct 26: `qa/speed/AFTER.md`); they are set up lazily, within 3/4 of a screen of the viewport.

**First screen (`data-intro`)**: the build adds `data-intro` + `--in-d` (half the delay) to every reveal in a page's first `<section>`. At `fonts-in`, `boot.js` does the same for every other reveal already inside the viewport (the tiles under the Services and Coverage titles, the Contact photo on phones, legal page rails...: exact per screen size, the rest keeps its scroll reveal). Those play from CSS (`base.css`, keyframes on `translate`/`scale`, so a design transform is never overridden) as soon as `boot.js` sees the fonts (`html.fonts-in`, 700 ms cap), without waiting for the JS bundle; main.js skips them. Nothing on the first screen waits for main.js. Keep the hero in the first `<section>`.

Smooth scroll is Lenis (lerp .15) wired to ScrollTrigger, only with a mouse or trackpad on a capable machine: touch screens and weak machines (4 cores or fewer, or 4 GB or less) keep native scrolling, and Lenis hands back to native scrolling by itself if smooth-scroll frames run over 25 ms. Anchor links scroll smoothly where Lenis runs. Internal links are prefetched on hover (65 ms), focus, press or touch (`<link rel=prefetch>`, skipped on Save-Data/2G).

## 6. Tokens and rules

- Fluid base: body font-size = clamp(768px, 100vw, 1920px) / (1440 / unit). Unit 17 (768-1439), 15 (>= 1440, 15px at 1440), 20 at <= 767 (10.67px, same as the reference). Every small size has a 10px floor (`--fs-4xs` to `--fs-s` use `max(..., 10px)`, `--fs-sm` is exactly 10px on phones), so no label is under 10px. Phones (<= 479): gutters 1em; the nav bar spans the gutters (368px at 390).
- Brand colors (Axel's kit, `brand/`): `--navy #071B3E` is the ink everywhere (text on paper, nav pill, hero, dark cards, footer). Alpha steps `--navy-05/08/11/16/22/40/48/68/72/78/90`. Deeper navy for big image surfaces and shadows: `--navy-deep #041029`, `--navy-abyss #030B1C`; raised navy `--navy-2 #0C2350`, `--navy-3`.
- `--amber #FFBF00` is the only accent (`--amber-warm` for glow, `--amber-hot` for white-hot cores, `--amber-55/24/12/00`). Use it like light: the mark, live dots, hover/active on dark, focus on dark, selection, imagery. Never amber text on paper.
- Slate: `--slate #777F98` (large secondary text, "Force" on paper), `--slate-ink #5A627A` (small secondary text on paper, AA), `--slate-light #A3AABF` (secondary text on navy, "Force" on dark).
- Paper: `--paper #F4F5F7` (cool off-white) with `--paper-82/62/48/16/14/10/07/00`; `--white` for raised cards.
- Semantic (flip inside `.on-dark`): `--text`, `--text-2`, `--text-meta`, `--text-4`, `--line`, `--card`. Logo: `--logo-front`, `--logo-back`, `--logo-yellow`, `--logo-force`.
- Legacy Vantra names (`--ink*`, `--signal*`, `--black`) still exist as aliases of the brand values; prefer the brand names in new code.
- Radii: 12px (nav, buttons), 16px (image cards), 20px (content cards, hero), 24px (CTA band top).
- Easing: `--ease` power2.inOut, `--ease-strong` power4.inOut (buttons), `--t .45s`, `--t-fast .24s`.
- Accessibility: every interactive thing is a real `<a>` or `<button>`, visible focus, Esc closes the menu, reduced motion turns off Lenis, reveals, marquee and the reel loop (static frame).
