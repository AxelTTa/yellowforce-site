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
- Partials (shared-ui lane owns them): `head`, `nav`, `cta`, `footer`, `toast`, `logo`, `logo-mark`.
- Logo: `<!-- include:logo -->` = the full lockup (inline SVG mark + live-text wordmark "**Yellow**Force" in our Inter, `.logo > .logo__mark + .logo__word > .logo__yellow + .logo__force`). `<!-- include:logo-mark -->` = the mark only (`.logo__mark`, inlines `assets/logo/mark.svg`). Never put the wordmark in an `<img>` (SVG text cannot load our font). Colors come from tokens, so the same markup works everywhere: on paper amber front + navy back, "Yellow" navy, "Force" slate; inside `.on-dark` and the nav pill the back turns white, "Yellow" white, "Force" slate-light. Size it with `font-size` on the parent (the mark is 3.17em wide). After a mark swap run `../.venv/bin/python tools/make_icons.py` (favicons, manifest icons, OG image).
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

**Copy email (text style)**: `<button class="mail" type="button" data-copy-email aria-label="Copy email address info@yellow-force.com"><span data-email-text>info@yellow-force.com</span><svg class="icon">copy</svg></button>`. Big contact version: add `mail--xl`. Never `mailto:`, never a form. The toast lives in the layout; JS falls back to selecting `[data-email-text]` if the clipboard is blocked.

**Image cards 2x2** `.tiles > .tiles__cell > a.tile` with `.tile__media.media > img`, `.tile__glass > .tile__row (.tile__name + .tile__meta > span x2) + .tile__reveal > .tile__reveal-inner > .tile__line + .tile__more`. Add `data-reveal="stagger"` on `.tiles`.
One look on Home, Services and Coverage (all in components.css, no page overrides needed): at rest a light frosted panel at least 50% wide x 4em, name (1.75em, 500, one line) with the two meta lines stacked right next to it; hover/focus grows it to the full card width x 8em and opens the line + link. Keep names short (one to three words) so the rest panel stays near half the card. On phones the line and link stay hidden (the whole card is the link), like the reference.

**Coverage table** `ul.ledger[data-reveal=stagger][data-bars] > li > a.ledger__row` with `h3.ledger__name`, `.ledger__tag`, `.ledger__gauge > .ledger__gauge-meta (2 spans) + .ledger__track > .ledger__fill`, `.ledger__end`. Bars fill on scroll (`--fill` custom property for partial width, e.g. `style="--fill: 60%"` on `.ledger__fill`).
`.ledger--compact` (Home, 5 rows like the reference): on phones each row is one line, name left and gauge (meta over the bar) right; tag and end label drop out. Without it, rows stack (name/end, tag/gauge) on phones.

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
Slide width 28em (`.carousel--narrow` 23.9em), same on phones (298px at 390: the next card peeks under the paper fade, the arrow chip sits over the gap, like the reference). Buttons, drag/swipe, arrow keys; wraps at the ends.
Cards: `.practice` (`.practice__num`, `svg.glyph.practice__glyph`, `.practice__body > .practice__title + .practice__text`; can be an `<a>`; the text reserves two lines so titles align, keep it to two lines at 1440, about 60 characters), `.reason` (`.reason__who > .reason__icon + .reason__id > .reason__title + .reason__meta`, `.reason__text`; odd slides flip automatically), `.reason--feature on-dark` (`.reason__score > .reason__figure(24<small>/7</small>) + .reason__figure-text`, `.reason__crew > .reason__stack > .reason__chip` x4 + `.reason__crew-label`). Chips are 34px circles in place of faces: `--amber` (navy glyph), `--paper` (put `<!-- include:logo-mark -->` inside), `--slate`, `--live` (`<span class="dot dot--live">`); plain `.reason__chip` = navy with an amber glyph.
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

**FAQ** `.faq` (12-col: `.faq__head` left, `.faq__list[data-faq]` right) > `.faq__item > h3.faq__h > button.faq__q#id[aria-expanded][aria-controls] (span + .faq__icon)` and `div.faq__a#id[role=region][aria-labelledby] > .faq__a-inner > p`. Answers are open without JS. Add `is-open` on an item to start it open. The question text must be the button's first `<span>` (it carries the 1.375em display size; the button keeps the base size so rows are 2em of the base, about 85px at 1440). No rule above the first row, a hairline under every row. Keep it to 5 or 6 questions.

**Insights** `.notes` (2 cols, `.notes--3`) > `a.note` (`.note__media.media > img`, `.note__scrim`, `.note__body > .note__meta (spans) + .note__title`, `.note__more` arrow chip). Index list: `ul.index > li > a.index__row` (`.index__content > .index__label + .index__title`, `.index__meta > .index__peek.media > img` hover preview + `.index__date` + `svg.icon.index__arrow`). `.notes + .index` spacing is automatic. `.notes__foot` for a button below. Card titles keep the h4 size on phones (two lines, max 13em).

**Hero (home)** `.hero.on-dark > .hero__media.media > img` + optional `canvas.hero__streaks[data-streaks=accent]` + `.hero__inner.gutter > .hero__row.frame > .hero__copy (p.hero__label.t-label + h1.hero__title.t-h0) + button.status`. `.hero__title` uses line-height 1.02 (not .9): at .9 the "g" of "Fight" overlaps the "W" below; 1.02 leaves .03 to .04em at every width.
Status card = the "Under attack?" copy-email button: `<button class="status" type="button" data-copy-email="urgent" aria-label="...">` > `.status__body > .status__label (.dot--live + "Under attack?") + .status__main > .status__text + .status__mail ([data-email-text] address + svg.status__icon copy + svg.status__icon.status__icon--done check)`, then `.status__thumb.media > img` (a real photo, not a graphic). Dark chip (deep navy 46%), hides <= 767 like the reference.

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

- Fluid base: body font-size = clamp(768px, 100vw, 1920px) / (1440 / unit). Unit 17 (768-1439), 15 (>= 1440, 15px at 1440), 20 at <= 767 (10.67px, same as the reference). Every small size has a 10px floor (`--fs-4xs` to `--fs-s` use `max(..., 10px)`, `--fs-sm` is exactly 10px on phones), so no label is under 10px. Phones (<= 479): gutters 1em, nav pill 34.5em (368px at 390).
- Brand colors (Axel's kit, `brand/`): `--navy #071B3E` is the ink everywhere (text on paper, nav pill, hero, dark cards, footer). Alpha steps `--navy-05/08/11/16/22/40/48/68/72/78/90`. Deeper navy for big image surfaces and shadows: `--navy-deep #041029`, `--navy-abyss #030B1C`; raised navy `--navy-2 #0C2350`, `--navy-3`.
- `--amber #FFBF00` is the only accent (`--amber-warm` for glow, `--amber-hot` for white-hot cores, `--amber-55/24/12/00`). Use it like light: the mark, live dots, hover/active on dark, focus on dark, selection, imagery. Never amber text on paper.
- Slate: `--slate #777F98` (large secondary text, "Force" on paper), `--slate-ink #5A627A` (small secondary text on paper, AA), `--slate-light #A3AABF` (secondary text on navy, "Force" on dark).
- Paper: `--paper #F4F5F7` (cool off-white) with `--paper-82/62/48/16/14/10/07/00`; `--white` for raised cards.
- Semantic (flip inside `.on-dark`): `--text`, `--text-2`, `--text-meta`, `--text-4`, `--line`, `--card`. Logo: `--logo-front`, `--logo-back`, `--logo-yellow`, `--logo-force`.
- Legacy Vantra names (`--ink*`, `--signal*`, `--black`) still exist as aliases of the brand values; prefer the brand names in new code.
- Radii: 12px (nav, buttons), 16px (image cards), 20px (content cards, hero), 24px (CTA band top).
- Easing: `--ease` power2.inOut, `--ease-strong` power4.inOut (buttons), `--t .45s`, `--t-fast .24s`.
- Accessibility: every interactive thing is a real `<a>` or `<button>`, visible focus, Esc closes the menu, reduced motion turns off Lenis, reveals, marquee and the reel loop (static frame).
