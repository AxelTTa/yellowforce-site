# Generated visuals (YellowForce)

Made by `tools/gen_all.py` (engine `tools/gen_core.py`, compositions `tools/gen_scenes.py`).
Our own work, rendered from code: no third-party images, no licence limits. Seeded, so a re-run gives the same files.

Look (brand kit, 2026-10-26): long-exposure light trails in amber #FFBF00 with warm-white hot cores (#FFF3D1)
on deep navy: open dark fields about #071B3E, corners and shadows down to #030B1C, never neutral black.
Very faint slate-blue (#777F98) out-of-focus particles add depth. HDR accumulation, hue-keeping filmic tone map,
bloom (the wide part lifts the navy instead of tinting it), amber halation, film grain, vignette.
Check: `qa/brand-swatch-check.jpg` (images between flat #071B3E and #FFBF00 swatches, measured colours).

Every image ships in three widths: `NAME.webp` (main), `NAME-1600.webp`, `NAME-800.webp`, WebP q82.
For square and 4:5 images the main file is 1600 wide, so `NAME.webp` and `NAME-1600.webp` are the same picture.
Suggested `srcset`: `NAME-800.webp 800w, NAME-1600.webp 1600w, NAME.webp <main width>w`.
Most compositions keep the left and bottom-left calm for overlaid text; the hero keeps its bottom-left (headline) and bottom-right (status card) clean.

| File (base name) | Aspect | Main size | Main KB | Slot | Description |
|---|---|---|---|---|---|
| `hero` | 16:9 | 2400x1350 | 155 | Home hero, behind 'Fight AI. With AI.' (text bottom-left) | A coherent ribbon of warm light arcs in from the top; an amber swarm breaks against it. Bottom-left stays dark for the headline. |
| `threat-swarm` | 1:1 | 1600x1600 | 183 | Threat card: AI swarms | Thousands of tiny lights spiral into one dense, hot vortex. |
| `threat-ransomware` | 1:1 | 1600x1600 | 205 | Threat card: ransomware | Streams of light slam into a hard, locked square and pile up along its edges. |
| `threat-phishing` | 1:1 | 1600x1600 | 161 | Threat card: phishing and impersonation | One bright lure line hooks down through the frame; many faint followers drift towards its tip. |
| `threat-breach` | 1:1 | 1600x1600 | 257 | Threat card: breach and data theft | A wide field of light funnels into a narrow gap and bursts out the other side. |
| `domain-network` | 16:9 | 2400x1350 | 61 | Coverage: Network security (domain page hero + card) | Glowing nodes joined by fine links, packets of light racing along them, deep focus falloff. |
| `domain-endpoint` | 16:9 | 2400x1350 | 59 | Coverage: Endpoint and device security | A floor of device lights in perspective with shallow focus; one guarded device ringed by an orbit. |
| `domain-cloud` | 16:9 | 2400x1350 | 127 | Coverage: Cloud security | Wisps of soft white-gold light drift across the frame like a cloud bank lit from within. |
| `domain-identity` | 16:9 | 2400x1350 | 169 | Coverage: Identity and access | Fingerprint-like ridges drawn in light on a tilted plane, sharp in the middle and falling out of focus. |
| `domain-email` | 16:9 | 2400x1350 | 106 | Coverage: Email security | Message traffic streams like highway light trails towards a glowing gate; one stream is pulled out. |
| `domain-applications` | 16:9 | 2400x1350 | 82 | Coverage: Application and API security | Lines of code as light on a tilted page, sharp near the focus; one line flares where the flaw is. |
| `domain-data` | 16:9 | 2400x1350 | 65 | Coverage: Data protection | Stacked rings of orbiting light, like a database seen in a long exposure, focus on the middle ring. |
| `domain-ai-agents` | 16:9 | 2400x1350 | 242 | Coverage: AI and agent security | A murmuration of tiny agent lights flowing as one, with a few rogue agents cutting across. |
| `domain-ot-iot` | 16:9 | 2400x1350 | 131 | Coverage: OT and IoT security | Arcs of rotating machinery traced in light around an off-frame axis, some blinking like sensors. |
| `domain-governance` | 16:9 | 2400x1350 | 115 | Coverage: Governance, risk and compliance | A ruled floor grid falling away to the horizon, swept by one warm beam that lights the rules it crosses. |
| `service-1` | 4:3 | 2400x1800 | 181 | Services 001 Deploy and connect | One beam enters from the left and branches into a delta of fine filaments reaching every corner. |
| `service-2` | 4:3 | 2400x1800 | 175 | Services 002 Detect 24/7 | A calm field of drifting light; one trail moves against the grain and is lit up. |
| `service-3` | 4:3 | 2400x1800 | 300 | Services 003 Respond | A fast, hard line of light cuts through an amber cluster and blows it apart. |
| `service-4` | 4:3 | 2400x1800 | 282 | Services 004 Attack (red team) | Curving trails sweep in from every side and converge on one ringed target. |
| `service-5` | 4:3 | 2400x1800 | 113 | Services 005 Harden | Hand-painted loops of light tighten in perspective towards a bright, closed core. |
| `service-6` | 4:3 | 2400x1800 | 283 | Services 006 Govern | Tangled amber lines on the left settle into calm, evenly spaced light on the right. |
| `cta` | 16:9 | 2400x1350 | 94 | Closing CTA band (very dark, light rises from the bottom) | Embers of light rise from the bottom edge and fade into deep black. |
| `status` | 1:1 | 1600x1600 | 55 | Hero status card thumbnail (small, 1:1) | A bright live point with soft ripple rings, readable at thumbnail size. |
| `reel-poster` | 16:9 | 2400x1350 | 167 | Reel frame poster (pill control sits bottom centre) | A light-painted orb: hundreds of orbits traced by a spinning light, sparks flying off, centred. |
| `about-1` | 4:3 | 2400x1800 | 185 | About: AI plus experts, one team | Two bundles of light, one warm white and one amber, braid around each other in depth. |
| `about-2` | 4:3 | 2400x1800 | 90 | About: we go inside your company | Luminous paths weave through a deep lattice of soft points, lighting the ones they pass. |
| `about-3` | 4:3 | 2400x1800 | 142 | About: 24/7, always on | An infinity loop light-painted over and over in one continuous, never-ending pass. |
| `contact` | 4:5 | 1600x2000 | 125 | Contact page image (4:5) | A single calm ribbon of light rises through the frame in an S curve, trailing fine sparks. |

Regenerate: `/path/to/.venv/bin/python tools/gen_all.py [names] [--ss 2]` (numpy, scipy, opencv, pillow).
