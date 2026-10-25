# Photo manifest (graded photographs)

All files are WebP, graded to the brand look (navy #071B3E, amber #FFBF00, slate #777F98; regraded 2026-10-26) by `tools/grade_photos.py` (re-run it from `site/` with `../.venv/bin/python tools/grade_photos.py`).
Sources: free Unsplash License only, originals in `../photo-src/orig/` (outside the site). Credits: `CREDITS.md` at the site root.

Each photo ships in three widths. Use real widths in `srcset` (some full-size files are narrower than 2400 because the source crop is):
`NAME-800.webp 800w, NAME-1600.webp 1600w, NAME.webp <full>w`.

| Name | Aspect | Full size | Slot | What it shows |
|---|---|---|---|---|
| insight-1 | 4:3 | 2000x1500 | Insight card + article hero: `ai-swarms` | A bundle of optical fibers seen end-on: hundreds of amber and warm-white light points streaming out of deep navy. Reads as a swarm. |
| insight-2 | 4:3 | 2000x1500 | Insight card + article hero: `fight-ai-with-ai` | Two hands typing on a dark keyboard, amber light on the knuckles, key legends glowing. Human operator at work. |
| insight-3 | 4:3 | 2000x1500 | Insight card + article hero: `one-team-every-domain` | Dozens of network cables converging symmetrically into one patch panel, amber tags and status LEDs on navy-blue cables. Everything connected into one place. |
| about-team | 16:9 | 2308x1298 | About page: team/how-we-work band | Silhouette of a person working at a desk at night in front of a window, city skyline glowing amber. Second desk on the right. No faces. Dark left third works for text. |
| about-strip-1 | 4:3 | 2000x1500 | About page image strip (1 of 3) | Close-up of a finger on a backlit mechanical keyboard, amber bokeh along the bottom. |
| about-strip-2 | 4:3 | 2000x1500 | About page image strip (2 of 3) | Legs of a person walking across dark paving, long shadow, warm light pooling on the floor. |
| about-strip-3 | 4:3 | 2000x1500 | About page image strip (3 of 3) | Server drive bays in shallow focus, rows of amber status LEDs. |
| contact-photo | 4:5 | 1800x2250 | Contact page (beside the big copy-email button) | Profile silhouette of a woman in front of a huge screen of streaking amber light on navy. Fully silhouetted, not identifiable. |
| services-hero | 16:9 | 2400x1350 | Services page hero | Long dark corridor of glass and steel, light lines running along the ceiling, warm lit floor leading to a vanishing point. |
| coverage-hero | 16:9 | 2400x1350 | Coverage page hero | Long-exposure highway curving toward a city at night, amber and warm-white light trails, city lights on the horizon. Top half dark for text. |
| photo-spare-1 | 4:3 | 1578x1184 | Spare | Lone silhouette standing in a dark hall, floor lit by big amber reflections. |
| photo-spare-2 | 16:9 | 2342x1317 | Spare (good for a 24/7 / "night" moment) | One small figure walking down an empty road at night under a line of streetlights. Lots of negative space. |
| photo-spare-3 | 16:9 | 2400x1350 | Spare (good as a band or reel poster) | A passing train in long-exposure motion blur: horizontal amber light streaks on deep navy. Closest to the generated family. |
| photo-spare-4 | 4:5 | 1600x2000 | Spare (bold, use once at most) | Profile silhouette against a large round window flooded with amber light. Very graphic. |

## The look (matches the brand and the light-streak family in `assets/img/gen/`)
- Blacks sit on deep navy, never neutral black: floor `#030B1C`, deep shadows climbing to about `#071B3E` (brand navy). Corners fall to the navy floor through a subtle 26% elliptical vignette.
- Midtones desaturated with a slight slate-blue cast: about `#242E48` to `#545A70`, brand slate `#777F98` at 64% of the tone range, then a neutral-warm climb to warm white `#F8F1E4`.
- Thin light (streaks, LEDs, lamps, keys, lit knuckles) maps through burnt orange `#9C620C` to brand amber `#FFBF00`, then `#FFD870` and a warm-white core `#FFF3DE`.
- Broad lit surfaces (sky, floor, wall, the round window) get a softer amber-caramel wash (about `#DA9C4A` to `#F6C26C`), never khaki: cool-to-warm transitions pass through neutral warm grey, never olive.
- Soft amber halation around bright light; a hue-preserving highlight shoulder so hot amber burns to warm white instead of clipping to lemon yellow.
- Gentle S-curve; film grain about 2.2% std (1.9% on the 800 px files), slightly softened, strongest in the mids, navy-tinted in the shadows so they never turn grey; a trace (4%) of the original colour in the upper tones only.
- Per-photo knobs in `PHOTOS` (crop focus/zoom, exposure, spread, glow...). `services-hero` is graded 15% darker so its lit floor reads as amber light, not sand; `photo-spare-4` 20% darker so the window reads amber, not lemon.
- Ramps and numbers live at the top of `tools/grade_photos.py` (`NAVY_FLOOR`, `NAVY`, `SLATE`, `AMBER`, `MONO`, `LIGHT`, `WASH`, `GLOW`, grain tints) if the generated set needs to share them.
- QA: `qa/photo-contact-sheet.jpg` (all 14 at 800 px on navy) and `qa/photo-brand-check.jpg` (six photos beside flat `#071B3E` / `#FFBF00` swatches, plus the floor and light colours sampled from the files). Both rebuild on every full run; `--sheet-only` rebuilds just them.
