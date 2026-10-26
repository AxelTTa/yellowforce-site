# YellowForce website: build brief (source of truth, 2026-10-25)

Every agent working on this site reads this file first. When it conflicts with anything in `../prep/`, this file wins.

## What YellowForce is (Axel's words, made clear)
- YellowForce is a **fully managed cybersecurity company**. It is **not a SaaS**. We are the product: we run the client's whole cybersecurity from A to Z.
- We **stop all cyber threats, especially AI swarms**, by **fighting AI with AI plus our cyber experts**.
- Palantir-style approach: we **go inside the client's company**, put our technology in their environment, **connect to all their existing systems**, and **work on top of their existing workflows**. No rip and replace.
- **24/7**. Always on, day and night.
- We cover **every cyber domain** (list below).
- The company is very early. Some vagueness is fine. It must still look like a serious, premium, established-feeling firm.

## Axel's direct decisions on the live site (2026-10-26, do not undo)
- Home statement is exactly: "We run your entire cybersecurity. Our AI and our experts stop every threat. 24/7." (Oct 26: ", AI swarms included" removed everywhere: statement, meta, JSON-LD, footer.) Long claim sentences read badly: keep every claim short and plain.
- Home hero streaks run continuously, like the reel (Oct 26: no settle to a still frame). Reduced motion still gets one static frame.
- The reel must look sharp: trails drawn at device resolution, softness only in the glow (Oct 26: "very blurry").
- No deepfakes on Home (Oct 26). Threat 03 is "Account takeover" (identity and payments), fit for SMBs and payment companies.
- "Why YellowForce." cards: no tall empty cards (Oct 26). Each card has a top block and a filled bottom block (hairline + short supporting line); the dark 24/7 card leads.
- Hero headline is "Your Security. / Handled." (Oct 26, replaces "Fight AI. / With AI.", which could read as "we build AI slop"). Title Case here only. Its two lines must never overlap, and it never breaks inside a line: capped to the row from 992px up so the card stays beside it, capped to the screen width on phones. Nav (Oct 26, Axel rejected the old slab with the wordmark alone in the center): one compact centered navy glass bar with the kit lockup (mark + YellowForce wordmark) on the left, then Services, Coverage, About, Insights, a white Talk to us button and a square menu button; the same on every page, no per-page taglines. Amber in the bar only as light: the mark, the current-page square, hover and the open menu. Details in COMPONENTS.md. OG image says "Your Security. Handled." + "Fully managed cybersecurity. 24/7."
- Hero card is a Coverage card (Oct 26, replaces "Under attack?"): label "( Coverage )" + small arrow, "10 domains.", "Network to AI agents. / One team, 24/7." (one sentence per line, never broken inside), real photo thumbnail (photo/coverage-hero), whole card links to /coverage/, no copy-email. Hidden on phones. Still no "Status: live", no radar graphic. "Under attack?" stays in the menu, the FAQ and on Contact.
- Axel likes the rest of the site as it is ("website is great"). Refine, do not redesign.

## Hard rules for copy
- Clear above all. A visitor must understand in 3 seconds: fully managed cybersecurity, AI vs AI, 24/7, everything covered.
- Never imply slowness: no "30 days", "weeks", "phases", "pilot", "design partners", "first customers", "Q1 2027", "we are taking...". Speed words are good: now, minutes, instantly, day one.
- Never present YellowForce as software: avoid "platform", "SaaS", "sign up", "free trial", "log in", "product tour". Say team, service, we run, we defend, we deploy.
- EXCEPTION (Axel, 2026-10-26): every client gets a private, custom client dashboard. It is a supporting feature, not the product: an overview of what is going on, the key information at a glance, and a direct line to the team. We still talk to clients on whatever channel they prefer (Slack, Teams, email, phone, WhatsApp). Say "your private dashboard" / "client dashboard"; never imply they have to run it themselves.
- Never fabricate proof: no client logos, no testimonials, no ratings/stars, no invented numbers or percentages, no "trusted by", no certifications (SOC 2, ISO), no "since 20XX", no team size, no investors, no awards, no partner/vendor logos. Allowed descriptive facts: 24/7, A to Z, every domain, one team, AI + experts, San Francisco.
- Never write "Palantir" or "ontology" on the site.
- No em dashes anywhere (use periods, commas, colons). US English. Short sentences. Vantra cadence: 2 to 5 word headings ending with a period ("What we stop."), small uppercase bracket labels "( 24/7 )".
- No people names, no faces, no team section.
- Location: "San Francisco, CA" only. Copyright: "© 2026 YellowForce".

## Contact behavior (important)
- The only contact is **info@yellow-force.com**. No forms, no `mailto:` links anywhere.
- Every place the email appears (or any "Copy email" / "Talk to us" button that is meant to give the email) is a `<button>` that **copies info@yellow-force.com to the clipboard** and shows a small toast: "Email copied" + the address. Fallback when the Clipboard API fails: select the text so the user can copy it.
- "Talk to us" navigation buttons may link to `/contact/`, where the big email is the copy button.
- An "Under attack?" entry exists (nav menu row + contact page + FAQ): it copies the email too and says we answer 24/7.

## Cyber domains we cover (all of them)
1. Network security
2. Endpoint and device security
3. Cloud security
4. Identity and access
5. Email security (phishing, business email compromise, deepfakes)
6. Application and API security
7. Data protection (data loss, ransomware, backups)
8. AI and agent security (AI swarms, hijacked agents, prompt injection, model abuse)
9. OT and IoT security
10. Governance, risk and compliance

## What we do (six practices, numbered like Vantra "( 001 )")
001 Deploy and connect: we go in, place our technology inside your environment, connect every tool you run.
002 Detect 24/7: AI agents watch every signal across every domain, day and night.
003 Respond: we contain and shut down attacks in real time, and run the incident end to end.
004 Attack: we attack you first, with AI and human red teamers, to find every way in.
005 Harden: we fix what we find, patch, reconfigure, and retest until it is closed.
006 Govern: policies, risk and compliance, kept current as you change.

## Design
- Look and feel must be almost identical to https://vantra-studio.webflow.io/ when viewed side by side: same fluid em sizing system, same type (Inter display + Instrument Sans text), same paper/ink palette and alpha steps, same radii, same floating dark pill nav with dropdown panel, same inset dark hero, same section header pattern, same cards, table rows, numbered service slider, reel frame with pill control, score/quote card carousel, FAQ accordion, journal cards, closing CTA band, big footer, same motion (Lenis smooth scroll, line-by-line heading reveals, scroll-scrubbed character fill on the statement, 20s marquee, fade-up lists, button text roll + arrow chip).
- Measurements: `../prep/vantra-design-system.md` (tokens, components, motion) and `../prep/vantra-pages.md` (page anatomy). Reference HTML/CSS (READ ONLY): `../ref/vantra/`.
- **LICENSE: we did NOT buy the Vantra template.** Never copy their CSS file, HTML, JS, class names, SVGs, images, logo or text. Rebuild from the measured numbers with our own markup, our own class names and our own assets. Numbers (sizes, colors, timings) are facts and may match.
- **BRAND (Axel's official logo kit, in `brand/`; this overrides any earlier yellow/ink values):**
  - Mark: two slanted stacked parallelograms. On light backgrounds: amber front `#FFBF00` over navy back `#071B3E` (`brand/symbol_on_light.svg`). On dark backgrounds: amber front over WHITE back (`brand/symbol_on_dark.svg`, same as the app icon).
  - Wordmark: "Yellow" in Inter weight 750 (use 700/800 or the variable font) in navy `#071B3E`, "Force" in Inter 400 in slate `#777F98`, letter-spacing about -0.027em, horizontal or stacked. On the site render it as live HTML text in our self-hosted Inter next to the inline SVG mark (SVG `<text>` in an `<img>` cannot load web fonts). On dark surfaces: "Yellow" white, "Force" slate-light (about `#A3AABF`).
  - Palette tokens: `--navy: #071B3E` replaces Vantra's ink `#0a0a0a` everywhere (text on paper, nav pill glass, hero, dark cards, footer, alpha steps are navy-based). `--amber: #FFBF00` is the accent (replaces `--signal`). `--slate: #777F98` for secondary text on dark and large secondary text (on paper use a darker slate such as `#5A627A` or navy at about 64% so small text passes AA). Paper stays a light off-white, tuned slightly cool to sit with navy (for example `#F4F5F7`), white `#FFFFFF` for raised cards if useful.
  - Amber is used like light, sparingly: the mark, live/status dots, hover/active states on dark surfaces, focus rings on dark, text selection, key highlights, and in the imagery. Never amber text on paper (contrast fails). It must look like a premium design studio made it.
  - Favicons and app icons come from the kit (`favicon.svg`, `favicon.ico`, `app_icon.png`, `app_icon.svg`); OG image uses the kit mark + wordmark.
- Imagery: our own, high quality. Two families, graded to one look that matches the brand: (a) generated long-exposure light-streak visuals in amber `#FFBF00`/gold and white on deep navy-black (shadows toward `#030B1C` / `#071B3E`, not neutral black) with grain (in `assets/img/gen/`), (b) free-licence photos (Unsplash License, not Unsplash+) of motion-blurred figures, hands, server rooms, night city light trails, graded to navy shadows with amber highlights (in `assets/img/photo/`, credits in `CREDITS.md`). WebP, several widths, `srcset`, lazy loading below the fold.
- Accessibility: WCAG AA contrast, keyboard nav, Esc closes the menu, visible focus, `prefers-reduced-motion` turns off smooth scroll and reveals. Mobile labels no smaller than 10px.
- Performance/security: everything self-hosted (fonts, GSAP, Lenis), no third-party requests, no cookies, no analytics. CSP via `<meta http-equiv>`.

## Site map (pretty URLs, output in `docs/` for GitHub Pages)
| Page | URL | Vantra equivalent |
|---|---|---|
| Home | `/` | Home |
| Services | `/services/` | Work index (6 practices as cards + rows) |
| Coverage | `/coverage/` | Work index / categories (10 domain cards) |
| Domain pages x10 | `/coverage/<slug>/` | Case study template |
| About | `/about/` | About |
| Insights | `/insights/` | Journal index |
| Insight posts x3 | `/insights/<slug>/` | Journal note |
| Contact | `/contact/` | Contact (no form: big copy-email button) |
| Privacy | `/privacy/` | (legal) |
| Security | `/security/` | Responsible disclosure |
| 404 | `/404.html` | 404 |
| Plumbing | `CNAME` (yellow-force.com), `.nojekyll`, `robots.txt` (allow all), `sitemap.xml`, `/.well-known/security.txt`, favicons, OG image | |

Domain slugs: `network`, `endpoint`, `cloud`, `identity`, `email`, `applications`, `data`, `ai-agents`, `ot-iot`, `governance`.
Insight slugs: `ai-swarms`, `fight-ai-with-ai`, `one-team-every-domain`.

## Repo layout
```
site/
  BRIEF.md            this file
  build.py            renders src/pages/** + partials into docs/ (pretty URLs), copies assets
  src/partials/       head.html, nav.html, cta.html, footer.html, toast.html
  src/pages/          index.html, services.html, coverage.html, coverage/<slug>.html, about.html, insights.html, insights/<slug>.html, contact.html, privacy.html, security.html, 404.html
  src/content/        copy.md (all page copy, written first)
  assets/css/         tokens.css, base.css, components.css, pages/<page>.css
  assets/js/          main.js (+ modules), vendor/ (gsap, ScrollTrigger, SplitText, lenis; pinned versions)
  assets/fonts/       self-hosted woff2 (OFL)
  assets/img/gen/     generated visuals
  assets/img/photo/   graded photos
  assets/logo/        mark.svg, wordmark.svg (placeholders)
  static/             CNAME, .nojekyll, robots.txt, .well-known/security.txt, favicons
  docs/               BUILD OUTPUT (GitHub Pages source). Never hand-edit.
  tools/              shoot.py (Playwright screenshots), sidebyside.py (composites)
  qa/                 screenshots and diff notes
```
Preview: `python3 build.py && python3 -m http.server 8787 -d docs` then http://127.0.0.1:8787/.
