# Generated visuals (YellowForce)

Made by `tools/gen_all.py` (engine `tools/gen_core.py`, compositions `tools/gen_scenes.py`).
Our own work, rendered from code: no third-party images, no licence limits. Seeded, so a re-run gives the same files.

Look (brand kit, 2026-10-26, round 1): long-exposure light trails in amber #FFBF00 with warm-white hot cores (#FFF3D1)
on deep, moody navy: open dark fields about #051026 (averaging #040C1E), corners down to #020712, lifted back towards
brand navy #071B3E where light scatters into the air; never neutral black. Photographic compositions (roads, tunnels,
beams in haze, fields in every focus plane) rather than diagrams; lit haze gives the dark soft midtones.
Very faint slate-blue (#777F98) out-of-focus particles add depth. HDR accumulation, hue-keeping filmic tone map,
bloom (the wide part lifts the navy instead of tinting it), amber halation, film grain, vignette.
Check: `qa/brand-swatch-check.jpg` (images between flat #071B3E and #FFBF00 swatches, measured colours).

Round 2 (2026-10-26): the card grids alternate bright and dark like the reference. One card per row is high-key
(light fills most of the frame, a warm-white core, like `cta`): Services 2, 3, 6 and Coverage endpoint, cloud,
applications, data, governance, in a checkerboard. The others stay dark but were lifted (service-4, identity,
ot-iot, network). Domain images keep the domain hero readable: the white title zone keeps at least 3:1 and the
paragraph zone at least 4.5:1 against the brightest 5% of pixels once the hero scrim is applied.
Home tiles 03 and 04 are full scenes now: `threat-phishing` (deepfakes, a stream and its copy) and
`threat-ransomware` (a torrent piling into a bright wall). No icons.

Round 3 (2026-10-26): `domain-ai-agents` is a murmuration of light now (was a faint dust smear, mean 23): a folded
3D sheet of tiny agents arcing over the upper half and down the right third, dense warm-white folds where the
sheet turns edge-on, stragglers and two small rogue clusters flying against the flow (mean 44). The centred hero
title keeps navy behind it (white text at 10:1 or more) and the coverage card's top-left label band stays dark.
`service-1` gained depth (two soft, out-of-focus deltas behind the sharp one, lit haze; was 91% near-black) and
`service-5` more light in its stream and air. The photo family was regraded to sit nearer this set (see
`assets/img/photo/MANIFEST.md`).

Round 4 (2026-10-26): the darkest images were lifted without changing their shapes (additions use their own seeds,
drawn after the original elements). `threat-swarm` (was mean 24, 73% near-black) gains an outer, out-of-focus shell of
the same swarm through the top and bottom of the frame and a warm haze over the disc (mean about 39, 45% near-black).
`threat-breach` (was 29, 72%) gains a deeper, soft layer of the funnelling field and a wider spray, with no extra light
in the gap so the pinch stays tight (about 40, 51%). The four dark domain heroes now carry structure into the lower
third under the centred title and sit at mean 35+: `domain-email` (soft near lanes rising from below into the same
vanishing point), `domain-network` (a lower ring of softer nodes linked up into the graph), `domain-ot-iot` (rings turn
all the way round under the axis), `domain-identity` (outer ridges fall off less, haze lit under the print). Hero text
contrast stays well above 3:1 (title) and 4.5:1 (paragraph) with the hero scrim. The photo family was regraded to
this set's near-black navy floor with muted slate mids (`assets/img/photo/MANIFEST.md`).

Phone versions (2026-10-27, `tools/gen_mobile.py`; Axel: "first image is a little blurry"): phones fill tall frames
with these 16:9 pictures by their height, and `sizes="100vw"` gave an iPhone 15 the 1200 px hero stretched 3.7x.
`NAME-m.webp` 2048x2560 (+ `-m-1536`, `-m-1024`) is the same scene rendered at phone resolution, cut 4:5 at the page's
object-position (hero 50%, cta 28%, domain-* 50%), so a frame up to 4:5 shows the same pixels as before, sharp (the hero
canvas still rides its streaks). The hero's phone render drops about 20 trails that zigzag where its field flips
(a speck at 2400 px, a staircase at phone size). `NAME-sq.webp` 1200 (+ `-sq-800`) is the centre square a tile shows
(domain-*, service-*). Served with `<picture>`: portrait under `(max-width: 1023px) and (max-aspect-ratio: 4/5)`
(cta: 767px), squares under 1024px. Desktop files are untouched.
Round 2 (critic, 2026-10-27): `cta-t.webp` 2048x2560 (+ `-t-1536`, `-t-1024`) is the CTA band's 4:5 crop at 50%, the
tablet framing, served to 768-1023px screens up to 4:5 (the 1600 px 16:9 file was 0.44 px per device px there).
`threat-breach-m.webp` 2408x3440 (+ `-m-2016`, `-m-1536`, `-m-1120`) is the 404's phone file: 7:10 at 50%, full height,
so the page's 1.28x zoom from the top and the pinch position streaks.js reads from it are unchanged (critic round 2:
the 2016 px top size was 0.89 px per device px on an iPhone 15; now 1.06 there, 1.13 on a Pixel 7).
`domain-applications-m` (critic round 2) is rendered with `flaw_row=34`: the same lines of code, but the flaring line
sits at about 75 to 80% of the frame, below the centred phone title and text, instead of right under "Apps / and APIs."
(the desktop file and the `-sq` tile keep row 22).

Round 3 (critic, 2026-10-27): tablet crops for the domain pages' "What we do." band, `NAME-t.webp` (+ `NAME-t-<w>.webp`),
`tools/gen_mobile.py --kind ops` (OPS_T). At 768-1023 the band is a portrait frame filled by height and grown by the
page's `--ops-zoom`, so the desktop files were 0.62 to 0.89 px per device px on a 768x1024 tablet. Each is the scene
rendered taller and cut 9:10, full height, at the page's desktop `--ops-pos` X, so the frame shows the same pixels, sharp
(1.0 to 1.2 at 768x1024, about 1.0 on iPad Air and iPad Pro 11): service-3 (endpoint, 3053x3392), service-1, about-1,
service-5 (2196x2440), hero, reel-poster, about-3 (1908x2120). Square and 4:5 pictures stay whole: threat-swarm 2160,
threat-breach 2560 (identity, and the 404 on every 768-1023 screen: `threat-breach.webp` is only 1600 px wide), contact
2160x2700 (email). Served with `<picture>` under `(min-width: 768px) and (max-width: 1023px)` (+ `(max-aspect-ratio: 4/5)`
for the 9:10 crops); desktop and phones keep their files.

Every image ships in three widths: `NAME.webp` (main), `NAME-1600.webp`, `NAME-800.webp`, WebP q82.
For square and 4:5 images the main file is 1600 wide, so `NAME.webp` and `NAME-1600.webp` are the same picture.
Suggested `srcset`: `NAME-800.webp 800w, NAME-1600.webp 1600w, NAME.webp <main width>w`.
Most compositions keep the left and bottom-left calm for overlaid text; the hero keeps its bottom-left (headline) and bottom-right (status card) clean.

| File (base name) | Aspect | Main size | Main KB | Slot | Description |
|---|---|---|---|---|---|
| `hero` | 16:9 | 2400x1350 | 161 | Home hero, behind 'Fight AI. With AI.' (text bottom-left) | A coherent ribbon of warm light arcs in from the top; an amber swarm breaks against it. Bottom-left stays dark for the headline. |
| `threat-swarm` | 1:1 | 1600x1600 | 215 | Threat card: AI swarms | Thousands of tiny lights spiral into one dense, hot vortex. |
| `threat-ransomware` | 1:1 | 1600x1600 | 247 | Threat card: ransomware | A torrent of light streaks rushes in from the left and piles up against a bright wall: heads stack and burn warm white along its face, sparks splash back, the space behind it stays locked and dim. |
| `threat-phishing` | 1:1 | 1600x1600 | 177 | Threat card: deepfakes and impersonation | A wide stream of light sweeps up through the frame and so does its copy, a twin stream offset beside it with the same twists: a double exposure, the real one warm white, the fake amber, a fainter third echo behind. |
| `threat-breach` | 1:1 | 1600x1600 | 264 | Threat card: breach and data theft | A wide field of light funnels into a narrow gap and bursts out the other side. |
| `domain-network` | 16:9 | 2400x1350 | 111 | Coverage: Network security (domain page hero + card) | Glowing nodes joined by fine links, packets of light racing along them; a second network glows out of focus behind. |
| `domain-endpoint` | 16:9 | 2400x1350 | 122 | Coverage: Endpoint and device security (high-key card) | A dense night floor of device lights in perspective, shallow focus, under a glowing horizon; one guarded device burns hot in the middle. |
| `domain-cloud` | 16:9 | 2400x1350 | 188 | Coverage: Cloud security (high-key card) | Wisps of white-gold light drift across the frame like a cloud bank, with a bright river of light running through it that burns warm white at its core; a softer bank lower down. |
| `domain-identity` | 16:9 | 2400x1350 | 238 | Coverage: Identity and access | Fingerprint-like ridges drawn in light on a tilted plane, centred in the frame, sharp in the middle and falling out of focus, in lit haze. |
| `domain-email` | 16:9 | 2400x1350 | 154 | Coverage: Email security | Message traffic streams like highway light trails towards a glowing gate; one stream is pulled out. |
| `domain-applications` | 16:9 | 2400x1350 | 135 | Coverage: Application and API security (high-key card) | Lines of code written in light on a tilted, backlit page, sharp near the focus and melting into bokeh; the lines around the flaw burn hotter and one line flares where the flaw is. |
| `domain-data` | 16:9 | 2400x1350 | 171 | Coverage: Data protection (high-key card) | A bright stream of light crosses the frame above a dark, glossy floor that holds its copy: a softer reflection broken into ripples. Every byte has a backup. |
| `domain-ai-agents` | 16:9 | 2400x1350 | 297 | Coverage: AI and agent security | A murmuration of light: tens of thousands of tiny agents fly as one folded sheet arcing over the upper half of the frame and down its right side, burning warm white where the sheet turns edge-on; two small rogue clusters fly against the flow. The title area and the top-left corner stay dark navy. |
| `domain-ot-iot` | 16:9 | 2400x1350 | 297 | Coverage: OT and IoT security | Long-exposure arcs of rotating machinery around a glowing axis inside the frame, dense and layered in depth, some blinking like sensors. |
| `domain-governance` | 16:9 | 2400x1350 | 168 | Coverage: Governance, risk and compliance (high-key card) | A ruled floor falling away to the horizon, flooded by one wide, warm beam that lights the rules it crosses and the haze above them. |
| `service-1` | 4:3 | 2400x1800 | 227 | Services 001 Deploy and connect | One beam enters from the left and branches into a delta of fine filaments reaching every corner; two more deltas glow out of focus behind it, so the whole frame is wired. |
| `service-2` | 4:3 | 2400x1800 | 297 | Services 002 Detect 24/7 (high-key card) | A broad river of soft-focus light drifts through the whole frame in every focus plane; one sharp trail moves against the grain and lights up. |
| `service-3` | 4:3 | 2400x1800 | 295 | Services 003 Respond (high-key card) | A hard line of light cuts across the frame and blows the light around it into two wide fans of sparks flying away from the cut, the air between them lit. |
| `service-4` | 4:3 | 2400x1800 | 294 | Services 004 Attack (red team) | Hundreds of curving trails sweep in from every side and converge on one ringed target, which glows in the haze. |
| `service-5` | 4:3 | 2400x1800 | 259 | Services 005 Harden | Streams of light run into an unseen curved wall and slide along it: the wall shows only as the bright seam where they pile up, the space behind it stays calm. |
| `service-6` | 4:3 | 2400x1800 | 305 | Services 006 Govern (high-key card) | A broad stream of light, turbulent and out of focus on the left, settles into evenly spaced lanes and gathers into one calm, bright band with a warm-white core on the right. |
| `cta` | 16:9 | 2400x1350 | 181 | Closing CTA band, full bleed behind the centred heading | A wide river of long-exposure light sweeps up through the centre: a hot warm-white core, soft out-of-focus streaks around it, lit haze. |
| `status` | 1:1 | 1600x1600 | 72 | Hero status card thumbnail (small, 1:1) | A hot point of light at the head of a long, curving exposure trail, glowing in soft haze. Reads at thumbnail size. |
| `reel-poster` | 16:9 | 2400x1350 | 173 | Reel frame poster (pill control sits bottom centre) | A light-painted orb: hundreds of orbits traced by a spinning light, sparks flying off, centred. |
| `about-1` | 4:3 | 2400x1800 | 142 | About: AI plus experts, one team | Seen from a bridge in a long exposure: a warm-white stream and an amber stream of light run in from either side of a night road and merge into one lane towards a glowing horizon. |
| `about-2` | 4:3 | 2400x1800 | 186 | About: we go inside your company | A long exposure from inside a moving tunnel: ceiling, wall and floor lights stretch into streaks that rush towards a bright opening. |
| `about-3` | 4:3 | 2400x1800 | 154 | About: 24/7, always on | A beacon sweeps through night haze over dark water; the long exposure turns its beam into a soft fan of light with glints on the sea. |
| `contact` | 4:5 | 1600x2000 | 129 | Contact page image (4:5) | A single calm ribbon of light rises through the frame in an S curve, trailing fine sparks. |

Regenerate: `/path/to/.venv/bin/python tools/gen_all.py [names] [--ss 2]` (numpy, scipy, opencv, pillow).

- `about-2-320.webp`, `threat-swarm-320.webp`, `status-320.webp` (2026-10-26): 320 px downsizes of the full frames (PIL Lanczos, WebP q84) for the 32 px reason chips on Home, which scale the image up to about 2.6x. Same crop (object-position and scale stay in CSS).
