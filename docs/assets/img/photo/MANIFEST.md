# Photo manifest (graded photographs)

All files are WebP, graded to the brand look (navy #071B3E, amber #FFBF00, slate #777F98; regraded 2026-10-26, round 1) by `tools/grade_photos.py` (re-run it from `site/` with `../.venv/bin/python tools/grade_photos.py`).
Sources: free Unsplash License only, originals in `../photo-src/orig/` (outside the site). Credits: `CREDITS.md` at the site root.

Each photo ships in three widths. Use real widths in `srcset` (some full-size files are narrower than 2400 because the source crop is):
`NAME-800.webp 800w, NAME-1600.webp 1600w, NAME.webp <full>w`.

| Name | Aspect | Full size | Slot | What it shows |
|---|---|---|---|---|
| insight-1 | 4:3 | 2000x1500 | Insight card + article hero: `ai-swarms` | A bundle of optical fibers seen end-on: hundreds of amber and warm-white light points streaming out of deep navy. Reads as a swarm. |
| insight-2 | 4:3 | 2000x1500 | Insight card + article hero: `fight-ai-with-ai` | Two hands typing on a dark keyboard, amber light on the knuckles, key legends glowing. Human operator at work. |
| insight-3 | 4:3 | 2000x1500 | Insight card + article hero: `one-team-every-domain` | Dozens of network cables converging symmetrically into one patch panel, amber tags and status LEDs on navy-blue cables. Everything connected into one place. |
| about-team | 16:9 | 2308x1298 | About page: "Join the fight." careers panel | A motion-blurred rider seen from behind on a night road lit amber, one street lamp, a warm light trail on the right. No face. Figure at about 40% from the left (panel crops at 30% 50%). |
| about-strip-1 | 4:3 | 2000x1500 | About page image strip (1 of 3) | Close-up of a finger on a backlit mechanical keyboard, amber bokeh along the bottom. |
| about-strip-2 | 4:3 | 2000x1500 | About page image strip (2 of 3) | Legs of a person walking across dark paving, long shadow, warm light pooling on the floor. |
| about-strip-3 | 4:3 | 2000x1500 | About page image strip (3 of 3) | Server drive bays in shallow focus, rows of amber status LEDs. |
| contact-photo | 4:5 | 1800x2250 | Contact page (beside the big copy-email button) | An open hand moving through warm light: motion-blurred fingers glowing amber to warm white on deep navy. No face. |
| services-hero | 16:9 | 2400x1350 | Services page hero | Long dark corridor of glass and steel, light lines running along the ceiling, a warm lit floor that fades into the dark towards the bottom edge. |
| coverage-hero | 16:9 | 2400x1350 | Coverage page hero | Long-exposure highway curving toward a city at night, amber and warm-white light trails, city lights on the horizon. Top half dark for text. |
| photo-spare-1 | 4:3 | 1578x1184 | Spare (404) | Lone figure seen from behind in a dark hall, a wall of warm, glowing light and amber reflections. |
| photo-spare-2 | 16:9 | 2342x1317 | Spare (good for a 24/7 / "night" moment) | One small figure walking down an empty road at night under a line of streetlights. Lots of negative space. |
| photo-spare-3 | 16:9 | 2400x1350 | Spare (good as a band or reel poster) | A passing train in long-exposure motion blur: horizontal amber light streaks on deep navy. Closest to the generated family. |
| photo-spare-4 | 4:5 | 1600x2000 | Spare (governance principle quote) | Two hands reaching towards a bright light in hazy dark; the light glows amber to warm white, rim light on the forearm. No face. |

## The look (matches the brand and the light-streak family in `assets/img/gen/`)
- Blacks sit on deep navy, never neutral black: floor `#020712`, open dark about `#040C1E`, deep shadows climbing to brand navy `#071B3E` (round 1: darker and moodier, same as the generated set). Corners fall to the floor through a 30% elliptical vignette.
- Midtones desaturated with a slight slate-blue cast: about `#202A44` to `#50576E`, brand slate `#777F98` at 66% of the tone range, then a neutral-warm climb to warm white `#F8F1E4`.
- Thin light (streaks, LEDs, lamps, keys, lit knuckles) maps through burnt orange `#965E0C` to brand amber `#FFBF00`, then rolls early into `#FFD678`, `#FFEABE` and a warm-white core `#FFF4E2`: hot light glows, it never sits as a flat amber block.
- Broad lit surfaces (a floor, a wall) get a low-chroma caramel to cream wash (about `#C09E72` to `#EAD4B0`), never khaki and never flat amber. `bottom` fades a lit floor into the dark, `gain` pulls a blown wall back from white.
- Bloom in linear light (three radii, soft knee), tinted towards warm white, plus amber halation around thin light: the same soft, luminous glow as the generated family. A hue-preserving shoulder burns the hottest light to warm white instead of lemon.
- Film grain uses the generated family's formula (luminance-shaped, strongest in the mids, mostly monochrome, navy-tinted in the shadows), so both families share one texture. Noisy night sources get a light pre-blur (`soften`) so sensor noise does not read as blue speckle.
- Per-photo knobs in `PHOTOS` (crop focus/zoom, exposure, spread, glow...). `services-hero` is graded darker with a bottom falloff so its lit floor reads as warm light, not sand; `photo-spare-1` uses `gain` 0.84 so its wall glows cream instead of clipping.
- Ramps and numbers live at the top of `tools/grade_photos.py` (`NAVY_FLOOR`, `NAVY`, `SLATE`, `AMBER`, `MONO`, `LIGHT`, `WASH`, `GLOW`, grain tints) if the generated set needs to share them.
- QA: `qa/photo-contact-sheet.jpg` (all 14 at 800 px on navy) and `qa/photo-brand-check.jpg` (six photos beside flat `#071B3E` / `#FFBF00` swatches, plus the floor and light colours sampled from the files). Both rebuild on every full run; `--sheet-only` rebuilds just them.
