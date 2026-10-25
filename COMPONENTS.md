# YellowForce components (for page builders)

Read BRIEF.md first. This file tells you which classes and attributes exist so you can build a page without reading the CSS.
Source: `assets/css/tokens.css`, `base.css`, `components.css`, `assets/js/main.js`, `assets/js/streaks.js`.
Own markup only. Never paste Vantra HTML, class names or SVGs.

## 1. Build, pages, partials

- Build: `python3 build.py` (production) or `tools/serve.sh` (build + http://127.0.0.1:8787/). `python3 build.py --dev` drops `upgrade-insecure-requests` from the CSP if a browser ever upgrades local asset URLs (Chromium does not).
- The build prints warnings: missing images/pages, unknown `{{vars}}`, and copy-rule hits (em dash, `mailto:`, "platform", "SaaS", "dashboard", "pilot", "N days/weeks", quarter dates, "trusted by"...). Fix copy-rule hits.
- A page is `src/pages/<name>.html` = front matter + the content of `<main>`. Layout (head, skip link, nav, main, footer, toast) is added for you.

```
---
title: Services | YellowForce fully managed cybersecurity   (" | YellowForce" is appended if the name is missing)
description: One sentence.
tagline: Six practices, one team        (centered line in the nav pill)
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
- Partials (foundation lane owns them): `head`, `nav`, `cta`, `footer`, `toast`. The logo is referenced only in `nav.html` and `footer.html` via `<!-- inline:assets/logo/mark.svg -->` / `wordmark.svg`: swapping those two files swaps the logo everywhere. After a logo swap run `../.venv/bin/python tools/make_icons.py` (favicons, manifest icons, OG image).
- Bracket labels: write `( 24/7 )` with single spaces; the build widens the inner spacing automatically.

## 2. Images

```html
<div class="shot shot--16x9 media"><img src="/assets/img/gen/hero.webp" data-variants sizes="(max-width: 767px) 100vw, 50vw" alt=""></div>
```
- `data-variants`: build adds `srcset` from `NAME-800.webp`, `NAME-1600.webp`, `NAME.webp` (only files that exist), `loading="lazy"`, `decoding="async"`. Add `loading="eager" fetchpriority="high"` for the first image on a page.
- Every image container gets class `media`: dark amber gradient fallback + the img fills it (`object-fit: cover`). A missing/broken file keeps the gradient.
- Ratios: `.shot--16x9 --21x9 --4x3 --3x2 --4x5 --1x1`, `.shot` = radius 16px, `.shot--hover` = scale 1.05 on hover.
- Decorative images: `alt=""` and `aria-hidden="true"` on the container.

## 3. Layout and type

| Class | Use |
|---|---|
| `.block` | section vertical padding 6em (`.block--top-0`, `.block--bottom-0`, `.block--about` 10.5em bottom, `.block--clip` overflow hidden, needed around carousels) |
| `.gutter` | side padding 3em (1.25em <= 991) |
| `.frame` | max 1920 container |
| `.stack` | column gap 5em (header to content). `.stack--m` 3em, `.stack--s` 1.5em |
| `.grid-12` + `.span-4/6/12` | 12 col grid, 1.5em gutter |
| `.on-dark` | flips text/line tokens for dark surfaces (focus ring becomes yellow) |
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

**Buttons** (text roll + arrow chip). Variants: `btn--dark` (default), `btn--light` (on dark/photo), `btn--ghost` (on paper), `btn--glass` (on dark), `btn--block`. Row: `.btn-row` (`--center`).
```html
<a class="btn btn--dark" href="/contact/">
  <span class="btn__roll"><span class="btn__line">Talk to us</span><span class="btn__line" aria-hidden="true">Talk to us</span></span>
  <span class="btn__chip" aria-hidden="true"><svg class="btn__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M7 17 17 7M9 7h8v8"/></svg><svg class="btn__icon" ...same...></svg></span>
</a>
```
Copy-email button: a `<button type="button" data-copy-email>` (use `data-copy-email="urgent"` for the Under attack toast line). Chip: two copy icons + a third `btn__icon btn__icon--done` check icon (shown after copying). Second roll line may read the address. Exact markup: FAQ "under attack" item in `src/pages/index.html`.

**Copy email (text style)**: `<button class="mail" type="button" data-copy-email aria-label="Copy email address info@yellow-force.com"><span data-email-text>info@yellow-force.com</span><svg class="icon">copy</svg></button>`. Big contact version: add `mail--xl`. Never `mailto:`, never a form. The toast lives in the layout; JS falls back to selecting `[data-email-text]` if the clipboard is blocked.

**Image cards 2x2** `.tiles > .tiles__cell > a.tile` with `.tile__media.media > img`, `.tile__glass > .tile__row (.tile__name + .tile__meta > span x2) + .tile__reveal > .tile__reveal-inner > .tile__line + .tile__more`. Panel grows on hover/focus. Add `data-reveal="stagger"` on `.tiles`.

**Coverage table** `ul.ledger[data-reveal=stagger][data-bars] > li > a.ledger__row` with `h3.ledger__name`, `.ledger__tag`, `.ledger__gauge > .ledger__gauge-meta (2 spans) + .ledger__track > .ledger__fill`, `.ledger__end`. Bars fill on scroll (`--fill` custom property for partial width; we only use full bars).

**Carousel** (practices, reasons, any card row)
```html
<section class="block gutter block--clip"> ...
<div class="carousel" data-carousel role="region" aria-roledescription="carousel" aria-label="Six practices">
  <div class="carousel__viewport" data-carousel-viewport tabindex="0" aria-label="Six practices. Use the arrow keys to move.">
    <ul class="carousel__track" data-carousel-track data-reveal="stagger"><li class="carousel__slide">CARD</li>...</ul>
  </div>
  <button class="carousel__btn carousel__btn--prev" type="button" data-carousel-prev aria-label="Previous"><span class="carousel__arrow">svg</span></button>
  <button class="carousel__btn carousel__btn--next" type="button" data-carousel-next aria-label="Next"><span class="carousel__arrow">svg</span></button>
</div>
```
Slide width 28em (`.carousel--narrow` 23.9em). Buttons, drag/swipe, arrow keys; wraps at the ends.
Cards: `.practice` (`.practice__num`, `svg.glyph.practice__glyph`, `.practice__body > .practice__title + .practice__text`; can be an `<a>`), `.reason` (`.reason__who > .reason__icon + .reason__id > .reason__title + .reason__meta`, `.reason__text`; odd slides flip automatically), `.reason--feature on-dark` (`.reason__score > .reason__figure(24<small>/7</small>) + .reason__figure-text`, `.reason__crew > .reason__stack > .reason__chip`, `.reason__crew-label`).
Pixel glyphs: inline SVG, 30px cells on a 180 grid, `<rect width="24" height="24" rx="5">` LED blocks, `fill: currentColor` via `.glyph`. Examples in `src/pages/index.html`.

**Reel** (live canvas)
```html
<div class="reel on-dark" data-streaks-scope data-reveal="frame">
  <canvas class="reel__canvas" data-streaks="reel" aria-hidden="true"></canvas>
  <div class="reel__island"><span class="reel__dot"></span><span class="reel__items"><span class="reel__label">YellowForce reel</span><span class="reel__time" data-clock>Live</span></span><span class="reel__sep"></span>
    <button class="reel__toggle" type="button" data-streaks-toggle data-label-play="Play reel" data-label-pause="Pause reel" aria-pressed="false" aria-label="Pause reel">pause svg.is-pause + play svg.is-play</button></div>
</div>
```
`data-streaks="accent"` = transparent, softer version to lay over a hero/cover image (`<canvas class="hero__streaks">` or `.cover__streaks`). Optional `data-seed="7"` changes the layout. `[data-clock]` shows live San Francisco time.

**FAQ** `.faq` (12-col: `.faq__head` left, `.faq__list[data-faq]` right) > `.faq__item > h3.faq__h > button.faq__q#id[aria-expanded][aria-controls] (span + .faq__icon)` and `div.faq__a#id[role=region][aria-labelledby] > .faq__a-inner > p`. Answers are open without JS. Add `is-open` on an item to start it open.

**Insights** `.notes` (2 cols, `.notes--3`) > `a.note` (`.note__media.media > img`, `.note__scrim`, `.note__body > .note__meta (spans) + .note__title`, `.note__more` arrow chip). Index list: `ul.index > li > a.index__row` (`.index__content > .index__label + .index__title`, `.index__meta > .index__peek.media > img` hover preview + `.index__date` + `svg.icon.index__arrow`). `.notes + .index` spacing is automatic. `.notes__foot` for a button below.

**Hero (home)** `.hero.on-dark > .hero__media.media > img` + optional `canvas.hero__streaks[data-streaks=accent]` + `.hero__inner.gutter > .hero__row.frame > .hero__copy (p.hero__label.t-label + h1.hero__title.t-h0) + a.status` (`.status__body > .status__label (.dot) + .status__text`, `.status__thumb.media > img`). Status card hides <= 767.

**Inner page heroes**
- `.page-head` (centered, 12em top padding): `p.t-label` + `h1.page-head__title` + `p.page-head__text`. `.page-head--left` variant.
- `.cover.on-dark` (inset dark card like the home hero, 960px max): `.cover__media.media > img` (scrim added), optional `canvas.cover__streaks[data-streaks=accent]`, `.cover__inner` (`--bottom` variant) > `p.t-label.cover__label`, `h1.cover__title`, `p.cover__text`, `.btn-row`. `.cover--full` (full height, 20px radius), `.cover--short` (80vh). Use for About hero, domain pages, 404.

**Closing CTA band**: `<!-- include:cta -->` (copy from copy.md, Talk to us + How we work + copy-email line). Not on Contact, Privacy, Security, 404.

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
| `data-reveal="lines"` | headings: SplitText lines fade + rise .25em, .45s, once |
| `data-reveal="statement"` | characters fill from 15% to 100% opacity, scrubbed by scroll |
| `data-reveal="fade"` | fade + rise .5em (`data-delay=".3"`) |
| `data-reveal="stagger"` | direct children fade + rise, .15s stagger (`data-stagger`, `data-delay`) |
| `data-reveal="frame"` | scale .95 -> 1 + rise 2em, .6s |
| `data-reveal="status"` | hero status card, delay .54s |
| `data-bars` | `.ledger__fill` bars grow on scroll |
| `data-copy-email` / `="urgent"` | copy info@yellow-force.com + toast |
| `data-carousel*`, `data-faq`, `data-streaks*`, `data-clock`, `data-lenis-prevent` | see components |

Elements with `data-reveal` are hidden until JS runs (`html.motion`); a 3.5s failsafe shows everything if JS fails. Smooth scroll is Lenis (lerp .1) wired to ScrollTrigger; anchor links scroll smoothly.

## 6. Tokens and rules

- Fluid base: body font-size = clamp(768px, 100vw, 1920px) / (1440 / unit). Unit 17 (992-1439), 15 (>= 1440), 24 at <= 767 (12.8px, so labels are >= 10px; all small sizes also have a 10px floor).
- Colors: `--paper #f5f4f0`, `--ink #0a0a0a`, alpha steps `--ink-05/08/11/16/22/40/48/68/72/78`, `--paper-82/62/48/16/14/07`. Semantic: `--text`, `--text-2`, `--text-meta`, `--line`, `--card`.
- Accent: `--signal #ffcc00` (+ `--signal-amber #ffad1f` for glow/imagery). Use only on dark surfaces, dots, focus on dark, selection, logo, imagery. Never yellow text on paper.
- Radii: 12px (nav, buttons), 16px (image cards), 20px (content cards, hero), 24px (CTA band top).
- Easing: `--ease` power2.inOut, `--ease-strong` power4.inOut (buttons), `--t .45s`, `--t-fast .24s`.
- Accessibility: every interactive thing is a real `<a>` or `<button>`, visible focus, Esc closes the menu, reduced motion turns off Lenis, reveals, marquee and the reel loop (static frame).
