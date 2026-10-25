# Photo manifest (graded photographs)

All files are WebP, graded to the brand look (navy #071B3E, amber #FFBF00, slate #777F98; regraded 2026-10-26, round 3: lifted to a navy floor; round 4: darker navy floor, muted slate mids) by `tools/grade_photos.py` (re-run it from `site/` with `../.venv/bin/python tools/grade_photos.py`).
Sources: free Unsplash License only, originals in `../photo-src/orig/` (outside the site). Credits: `CREDITS.md` at the site root.

Each photo ships in three widths. Use real widths in `srcset` (some full-size files are narrower than 2400 because the source crop is):
`NAME-800.webp 800w, NAME-1600.webp 1600w, NAME.webp <full>w`.

| Name | Aspect | Full size | Slot | What it shows |
|---|---|---|---|---|
| insight-1 | 4:3 | 2000x1500 | Insight card + article hero: `ai-swarms` | A bundle of optical fibers seen end-on: hundreds of amber and warm-white light points streaming out of deep navy. Reads as a swarm. |
| insight-2 | 4:3 | 2000x1500 | Insight card + article hero: `fight-ai-with-ai` | Two hands typing on a dark keyboard, amber light on the knuckles, key legends glowing. Human operator at work. |
| insight-3 | 4:3 | 2000x1500 | Insight card + article hero: `one-team-every-domain` | Dozens of network cables converging symmetrically into one patch panel, amber tags and status LEDs on navy-blue cables. Everything connected into one place. |
| about-team | 16:9 | 2308x1298 | About page: "Join the fight." careers panel | Round 3: a zoom-burst long exposure from a moving train. Amber and warm-white streaks rush in from the left and meet at a vanishing point at about 58% from the left, so the panel's square crop at 30% 50% ends on it. No people. |
| about-strip-1 | 4:3 | 2000x1500 | About page image strip (1 of 3), home hero "Under attack?" card thumbnail, email and endpoint pages | A finger reaching for a backlit keyboard: rows of keys glowing amber to warm white on deep navy, the hand a dark navy silhouette. Bright at thumbnail size (round 2). |
| about-strip-2 | 4:3 | 2000x1500 | About page image strip (2 of 3) | Legs of a person walking across dark paving, long shadow, warm light pooling on the floor. |
| about-strip-3 | 4:3 | 2000x1500 | About page image strip (3 of 3) | Server drive bays in shallow focus, rows of amber status LEDs. |
| contact-photo | 4:5 | 1800x2250 | Contact page (beside the big copy-email button), data page | An open hand moving through warm light: motion-blurred fingers glowing amber to warm white on navy. No face. Round 3: cropped a little tighter so the lit hand sits in the frame (fingertips about 17% from the top, no empty top third). |
| services-hero | 16:9 | 2400x1350 | Services page hero | Long dark corridor of glass and steel, light lines running along the ceiling, a warm lit floor that fades into the dark towards the bottom edge. |
| coverage-hero | 16:9 | 2400x1350 | Coverage page hero | Long-exposure highway curving toward a city at night, amber and warm-white light trails, city lights on the horizon. Top half dark for text. |
| photo-spare-1 | 4:3 | 1578x1184 | Identity gallery (tall), data principle | An empty aisle between long rows of locked boxes under warm strip lights, vanishing point in the middle. No people (round 2). |
| photo-spare-2 | 16:9 | 2342x1317 | Spare (good for a 24/7 / "night" moment) | One small figure walking down an empty road at night under a line of streetlights. Lots of negative space. |
| photo-spare-3 | 16:9 | 2400x1350 | Spare (good as a band or reel poster) | A passing train in long-exposure motion blur: horizontal amber light streaks on deep navy. Closest to the generated family. |
| photo-spare-4 | 4:5 | 1600x2000 | Spare (governance principle quote) | Two hands reaching towards a bright light in hazy dark; the light glows amber to warm white, rim light on the forearm. No face. |

## The look (matches the brand and the light-streak family in `assets/img/gen/`)
- Round 3 (2026-10-26): the set was far darker than the generated family and the reference's mid-key galleries (mean luma 16 to 30, up to 89% near-black). Shadows now sit on a navy floor: open shadows about `#0B1E45`, only the vignetted corners fall to `#050E22`, never neutral black. Midtones are lifted about +0.5 EV in linear light with a soft shoulder (`mid`), the darkest sources get an extra `shadow` lift. Every file is now mean luma 41 to 56 with 30 to 50% of pixels under 25 (was 16 to 36 and 62 to 90%).
- Round 4 (2026-10-26, QA C1): next to the generated family (near-black navy floor, warm-neutral mids) the round 3 grade read as a royal-blue duotone (median tone about 15/28/59, darkest 10% about 6/17/40). The darkest 10% now sit at about `#060F22` (between `#050E22` and `#071B3E`, near the generated floor) and the blue chroma of the shadow and mid steps is cut by about 40 to 50% at the same luminance (median tone about 20/26/43), with a slightly stronger S-curve so the deeper floor reads as depth. Amber light, bloom and grain are unchanged. Every file stays at mean luma 41 to 56 with 37 to 55% of pixels under 25.
- Midtones are a muted, near-neutral dark slate: open shadows about `#131C2F`, mids about `#29304A` to `#585B6C`, `#83848E` at 62% of the tone range, then a neutral-warm climb to warm white `#F8F1E4`.
- Thin light (streaks, LEDs, lamps, keys, lit knuckles) maps through burnt orange `#965E0C` to brand amber `#FFBF00`, then rolls early into `#FFD678`, `#FFEABE` and a warm-white core `#FFF4E2`: hot light glows, it never sits as a flat amber block.
- Broad lit surfaces (a floor, a wall) get a low-chroma caramel to cream wash (about `#C09E72` to `#EAD4B0`), never khaki and never flat amber. `bottom` fades a lit floor into the dark, `gain` pulls a blown wall back from white.
- Bloom in linear light (three radii, soft knee, round 3 strength 0.5), tinted towards warm white, plus amber halation around light (round 3: a third, wide radius and less suppression on broad light, so glows fall off into the navy): the same soft, luminous glow as the generated family. A hue-preserving shoulder burns the hottest light to warm white instead of lemon.
- Film grain uses the generated family's formula (luminance-shaped, strongest in the mids, mostly monochrome, navy-tinted in the shadows), so both families share one texture. Noisy night sources get a light pre-blur (`soften`) so sensor noise does not read as blue speckle.
- Per-photo knobs in `PHOTOS` (crop focus/zoom, exposure, spread, glow...). `services-hero` is graded darker with a bottom falloff so its lit floor reads as warm light, not sand; `photo-spare-1` (round 2, an empty aisle) uses `bottom` 0.45 so the lit floor falls into the dark.
- Ramps and numbers live at the top of `tools/grade_photos.py` (`NAVY_FLOOR`, `NAVY`, `SLATE`, `AMBER`, `MONO`, `LIGHT`, `WASH`, `GLOW`, grain tints) if the generated set needs to share them.
- Weight: each file steps its WebP quality down (82 to 62 at most) until it fits a budget scaled by pixel count (about 165 KB main, 105 KB at 1600, 34 KB at 800 for 16:9), so the lifted shadows do not inflate page weight.
- QA: `qa/photo-contact-sheet.jpg` (all 14 at 800 px on navy) and `qa/photo-brand-check.jpg` (six photos beside flat `#071B3E` / `#FFBF00` swatches, plus the floor and light colours sampled from the files). Both rebuild on every full run; `--sheet-only` rebuilds just them.
