"""YellowForce generated imagery: the compositions.

Each scene is a function (cv) -> develop kwargs, registered with its design
size. Design sizes are the main export sizes.
"""
from __future__ import annotations

import numpy as np
from gen_core import (Canvas, SinField, bezier, bezier_deriv, envelope, flow_trails, glow, lognormal_int,
                      motes, normals, ramp, ribbon, slate_dust, smoothstep, wobble)

SCENES = {}

R169 = (2400, 1350)
R43 = (2400, 1800)
R11 = (1600, 1600)
R45 = (1600, 2000)


def scene(name, size, slot, desc):
    def deco(fn):
        SCENES[name] = dict(fn=fn, size=size, slot=slot, desc=desc)
        return fn
    return deco


# ---------------------------------------------------------------------------
# helpers


def swarm_streaks(cv, xy, vel, length, inten, hue, blur, curve=None, M=6):
    """Many short motion streaks. xy (n,2) centres, vel (n,2) unit dirs,
    length (n,), inten (n,), hue (n,), blur (n,). curve: (n,) curvature."""
    n = len(xy)
    s = np.linspace(-0.5, 0.5, M)
    d = vel / (np.linalg.norm(vel, axis=1, keepdims=True) + 1e-9)
    nrm = np.c_[-d[:, 1], d[:, 0]]
    k = np.zeros(n) if curve is None else curve
    off_t = s[None, :] * length[:, None]
    off_n = 0.5 * k[:, None] * off_t ** 2
    P = xy[:, None, :] + off_t[..., None] * d[:, None, :] + off_n[..., None] * nrm[:, None, :]
    # comet profile: bright head, fading tail (the light moved towards +d)
    prof = (0.15 + 0.85 * smoothstep(-0.5, 0.45, s)) * (1 - smoothstep(0.42, 0.5, s) * 0.6)
    I = inten[:, None] * prof[None, :]
    cv.polylines(P, I, ramp(hue), blur)


# ---------------------------------------------------------------------------
# HERO


@scene("hero", R169, "Home hero, behind 'Fight AI. With AI.' (text bottom-left)",
       "A coherent ribbon of warm light arcs in from the top; an amber swarm breaks against it. Bottom-left stays dark for the headline.")
def hero(cv):
    rng = np.random.default_rng(11)
    ctrl = np.array([[1080, -80], [1330, 560], [1880, 760], [2580, 600]])
    sp = ribbon(cv, ctrl, n=300, width=60, twist=1.6, twist_phase=0.4, wob=0.12,
                inten=0.42, isig=0.75, hue=(0.0, 0.6), blur=(0.5, 1.1), tjit=0.10,
                env=(0.18, 0.12), seed=1, spread_profile=lambda t: 0.55 + 0.9 * t)
    ribbon(cv, ctrl, n=46, width=150, twist=0.7, wob=0.35, inten=0.10, isig=0.6, hue=(0.1, 0.7),
           blur=(0.5, 1.0), tjit=0.25, env=(0.2, 0.2), seed=7, dist="uniform",
           spread_profile=lambda t: 0.4 + t)
    ribbon(cv, ctrl + np.array([[-60, 0], [-40, -60], [0, -90], [0, -80]]), n=40, width=140,
           twist=0.8, wob=0.2, inten=0.09, isig=0.5, hue=(0.3, 0.9), blur=(14, 30), seed=2)
    spine = sp["spine"]
    tang_all = np.gradient(spine, axis=0)
    tang_all /= np.linalg.norm(tang_all, axis=1, keepdims=True)
    nrm_all = normals(spine)
    fld = SinField(rng, n=9, wavelength=620)
    base = np.array([-0.78, 0.62])

    def field(x, y):
        vx, vy = fld.curl(x, y)
        vx = base[0] + 0.65 * vx
        vy = base[1] + 0.65 * vy
        d = spine[None, ::2, :] - np.c_[x, y][:, None, :]
        dist = np.linalg.norm(d, axis=2)
        j = dist.argmin(1) * 2
        dm = dist.min(1)
        tg = tang_all[j]
        sgn = np.sign(tg[:, 0] * vx + tg[:, 1] * vy + 1e-6)
        w = np.exp(-(dm / 150.0) ** 2)
        vx = vx * (1 - w) + w * tg[:, 0] * sgn * 1.4
        vy = vy * (1 - w) + w * tg[:, 1] * sgn * 1.4
        return vx, vy

    # swarm: a soft cloud inside the arc (upper right) pressing towards the ribbon
    cand = np.c_[rng.normal(2080, 420, 40000), rng.normal(300, 260, 40000)]
    d = np.linalg.norm(cand[:, None, :] - spine[None, ::4, :], axis=2)
    j = d.argmin(1) * 4
    side = ((cand - spine[j]) * nrm_all[j]).sum(1)
    dm = d.min(1)
    # keep the headline corner (bottom-left) calm
    calm = 1 - (1 - smoothstep(1150, 1750, cand[:, 0])) * smoothstep(520, 860, cand[:, 1])
    acc = (side > 0) & (rng.random(len(cand)) < smoothstep(10, 120, dm) * (0.35 + 0.65 * np.exp(-dm / 300)) * calm)
    st = cand[acc][:3800]
    n = len(st)
    steps = 30
    paths = flow_trails(cv, field, st, steps, h=2.3)
    lens = rng.integers(5, steps, n)
    idx = np.arange(steps + 1)[None, :]
    tl = idx / lens[:, None]
    prof = (tl <= 1) * (0.08 + 0.92 * np.clip(tl, 0, 1) ** 1.8)
    dm0 = dm[acc][:n]
    inten = lognormal_int(rng, n, 0.09, 0.8) * (0.5 + 0.8 * np.exp(-dm0 / 260))
    hue = rng.uniform(0.45, 0.95, n)
    blur = np.where(rng.random(n) < 0.12, rng.uniform(3, 14, n), rng.uniform(0.5, 0.9, n))
    cv.polylines(paths, inten[:, None] * prof, ramp(hue), blur)
    k = 220
    tt = rng.uniform(0.3, 0.9, k)
    j = (tt * (len(spine) - 1)).astype(int)
    xy = spine[j] + nrm_all[j] * np.abs(rng.normal(0, 45, k))[:, None]
    swarm_streaks(cv, xy, tang_all[j] * rng.choice([-1, 1], (k, 1)) + rng.normal(0, 0.2, (k, 2)),
                  rng.uniform(12, 60, k), lognormal_int(rng, k, 0.30, 0.6), rng.uniform(0.15, 0.6, k),
                  rng.uniform(0.5, 1.0, k))
    motes(cv, 24, (1300, 0, 2400, 800), energy=(0.02, 0.08), blur=(18, 70), hue=(0.5, 1.0), seed=3)
    # slate depth particles only in the upper part: the headline (bottom-left)
    # and the status card (bottom-right) sit on clean navy
    return dict(exposure=1.0, bloom=0.10, halation=0.06, vignette=0.4,
                slate_weight=lambda xy: 1 - smoothstep(520, 820, xy[:, 1]))


# ---------------------------------------------------------------------------
# shared helpers for the rest of the family


def pwobble(rng, n, t, terms=3, fmin=0.4, fmax=2.2, amp=1.0):
    """wobble() with whole-number frequencies: periodic over t in [0,1], so a
    closed loop meets itself without a step. Same rng draws as wobble()."""
    t = np.asarray(t)
    out = np.zeros((n, t.size))
    a = amp
    for _ in range(terms):
        f = np.maximum(1.0, np.round(rng.uniform(fmin, fmax, size=(n, 1))))
        ph = rng.uniform(0, 2 * np.pi, size=(n, 1))
        out += a * np.sin(2 * np.pi * f * t[None, :] + ph)
        a *= 0.5
        fmin, fmax = fmin * 1.9, fmax * 1.9
    return out / 1.5


def trails(cv, P, inten, hue, blur, rng, env=(0.1, 0.1), speed=0.3, prof=None, periodic=False):
    """Draw trails with an end envelope and gentle 1/speed brightness changes.
    hue: (n,) or (n,M). blur: (n,) or (n,M) per-vertex (depth of field).
    periodic: closed loops, the brightness changes wrap around without a step."""
    P = np.asarray(P, np.float64)
    n, M = P.shape[:2]
    t = np.linspace(0, 1, M)
    I = np.asarray(inten, np.float64).reshape(n, 1) * np.ones((1, M))
    if env is not None:
        I = I * envelope(t, *env)[None]
    if speed:
        wob = pwobble if periodic else wobble
        I = I * np.clip(1 + speed * wob(rng, n, t, terms=2, fmin=0.5, fmax=1.6), 0.2, 3)
    if prof is not None:
        I = I * prof
    C = ramp(hue)
    blur = np.asarray(blur, np.float64)
    if blur.ndim == 2:
        cv.polylines_var(P, I, C, blur)
    else:
        cv.polylines(P, I, C, np.broadcast_to(blur, (n,)))


def circle_pts(c, r, th, sx=1.0, sy=1.0, rot=0.0):
    x = r * np.cos(th) * sx
    y = r * np.sin(th) * sy
    cr, sr = np.cos(rot), np.sin(rot)
    return np.stack([c[0] + x * cr - y * sr, c[1] + x * sr + y * cr], -1)


def homography(src, dst):
    import cv2
    return cv2.getPerspectiveTransform(np.float32(src), np.float32(dst)).astype(np.float64)


def apply_h(Hm, P):
    P = np.asarray(P, np.float64)
    sh = P.shape
    Q = P.reshape(-1, 2)
    q = np.c_[Q, np.ones(len(Q))] @ Hm.T
    return (q[:, :2] / q[:, 2:3]).reshape(sh), q[:, 2].reshape(sh[:-1])


# ---------------------------------------------------------------------------
# THREAT CARDS (square)


@scene("threat-swarm", R11, "Threat card: AI swarms",
       "Thousands of tiny lights spiral into one dense, hot vortex.")
def threat_swarm(cv):
    rng = np.random.default_rng(21)
    c = np.array([860.0, 760.0])
    tilt, rot = 0.42, np.deg2rad(-12)

    def place(r, th, hgt):
        x = r * np.cos(th)
        y = r * np.sin(th) * tilt + hgt
        cr, sr = np.cos(rot), np.sin(rot)
        return np.stack([c[0] + x * cr - y * sr, c[1] + x * sr + y * cr], -1), r * np.sin(th)

    n = 9000
    r0 = np.exp(rng.uniform(np.log(30), np.log(1100), n))
    th0 = rng.uniform(0, 2 * np.pi, n)
    L = 4.5 * r0 ** 0.45 * np.exp(rng.normal(0, 0.35, n))
    dth = L / r0
    M = 10
    s = np.linspace(0, 1, M)
    th = th0[:, None] + dth[:, None] * s[None]
    rr = r0[:, None] * np.exp(-0.2 * dth[:, None] * s[None])
    hgt = rng.normal(0, 1, n)[:, None] * (0.03 * r0[:, None] + 2)
    P, z = place(rr, th, hgt)
    zm = z.mean(1)
    blur = np.minimum(0.5 + np.where(zm > 0, zm * 0.012, -zm * 0.004), 12)
    inten = lognormal_int(rng, n, 0.12, 0.6) * (r0 / 150) ** 0.1 * np.where(zm > 250, 0.55, 1.0)
    prof = (0.12 + 0.88 * s ** 1.5)[None]
    hue = np.clip(0.05 + 0.2 * np.log(r0 / 30) + rng.normal(0, 0.08, n), 0, 0.92)
    trails(cv, P, inten, hue, blur, rng, env=None, speed=0, prof=prof)
    # spiral arms
    k = 360
    rs = rng.uniform(800, 1700, k)
    re = rng.uniform(50, 220, k)
    span = rng.uniform(2.4, 3.8, k)
    arm = rng.integers(0, 3, k)
    th0 = arm * 2 * np.pi / 3 + rng.normal(0, 0.35, k)
    M = 240
    s = np.linspace(0, 1, M)
    rr = rs[:, None] * (re / rs)[:, None] ** s[None]
    th = th0[:, None] + span[:, None] * s[None] ** 0.8
    P, z = place(rr, th, rng.normal(0, 8, (k, 1)))
    B = np.minimum(0.5 + np.where(z > 0, z * 0.02, -z * 0.005), 20)
    inten = lognormal_int(rng, k, 0.06, 0.6)
    trails(cv, P, inten, rng.uniform(0.3, 0.85, k), B, rng, env=(0.3, 0.2), prof=(0.25 + 0.75 * s ** 1.2)[None])
    # the core
    kk = 120
    r0 = np.exp(rng.uniform(np.log(5), np.log(45), kk))
    th0 = rng.uniform(0, 2 * np.pi, kk)
    s = np.linspace(0, 1, 30)
    th = th0[:, None] + rng.uniform(1.2, 3.4, kk)[:, None] * s[None]
    P, z = place(r0[:, None] * np.ones((1, 30)), th, 0)
    trails(cv, P, lognormal_int(rng, kk, 0.4, 0.5), rng.uniform(0, 0.3, kk), 0.6, rng, env=(0.2, 0.2))
    cv.points(c[None], 10.0, ramp(0.05), 1.0)
    glow(cv, c, 10.0, 12, 0.5)
    motes(cv, 16, (0, 0, 1600, 1600), energy=(0.01, 0.05), blur=(20, 70), hue=(0.5, 1.0), seed=4)
    # round 4 (QA C4): this card opens the home grid and was the darkest on the page (mean 24, 73% near-black).
    # The swarm now lights the air it turns in: an outer shell of the same swarm sweeps through the top and the
    # bottom of the frame (soft, out of focus on the near side), and a wide warm haze sits over the disc. The
    # vortex, its arms and the hot core above are unchanged (own seed, drawn after them).
    r4 = np.random.default_rng(2104)
    nf = SWARM_SHELL
    r0 = np.exp(r4.uniform(np.log(520), np.log(2000), nf))
    th0 = r4.uniform(0, 2 * np.pi, nf)
    L = 4.5 * r0 ** 0.45 * np.exp(r4.normal(0, 0.35, nf))
    dth = L / r0
    M = 10
    s = np.linspace(0, 1, M)
    th = th0[:, None] + dth[:, None] * s[None]
    rr = r0[:, None] * np.exp(-0.2 * dth[:, None] * s[None])
    P, z = place(rr, th, r4.normal(0, 1, nf)[:, None] * (0.06 * r0[:, None]))
    zm = z.mean(1)
    blur = np.minimum(1.0 + np.where(zm > 0, zm * 0.014, -zm * 0.005), 14)
    inten = lognormal_int(r4, nf, SWARM_SHELL_I, 0.6) * (1 + blur / 8) ** 0.6
    hue = np.clip(0.35 + 0.25 * np.log(r0 / 520) + r4.normal(0, 0.1, nf), 0, 0.95)
    trails(cv, P, inten, hue, blur, r4, env=None, speed=0, prof=(0.12 + 0.88 * s ** 1.5)[None])
    glow(cv, c, SWARM_HAZE, 520, 0.45, n=9000, seed=31)
    glow(cv, c, SWARM_HAZE * 0.35, 230, 0.3, n=6000, seed=32)
    return dict(exposure=SWARM_EXP, bloom=0.11, halation=0.07, vignette=0.4, atmos=SWARM_ATMOS)


SWARM_SHELL, SWARM_SHELL_I, SWARM_HAZE, SWARM_EXP, SWARM_ATMOS = 2000, 0.085, 16000.0, 1.2, 0.05


@scene("threat-ransomware", R11, "Threat card: ransomware",
       "A torrent of light streaks rushes in from the left and piles up against a bright wall: heads stack and burn warm white along its face, sparks splash back, the space behind it stays locked and dim.")
def threat_ransomware(cv):
    """Round 2: a full long-exposure scene (no box). The wall is never drawn as a line: it is the
    bright face where thousands of streak heads stop, stack and glow."""
    rng = np.random.default_rng(33)
    W = 1600.0

    def wall_x(y):
        # a slightly tilted wall (the top leans away), so the pile-up reads in depth
        return 1130.0 + 0.10 * (y - 800.0)

    # 1) the torrent: long streaks from the left, every focus plane, converging a little towards the wall
    n = 2600
    # bundles (lanes) of traffic, like the breach and swarm cards: density varies, it is not a curtain
    lanes = np.r_[rng.normal(820, 300, 11)]
    lw = rng.uniform(0.4, 1.6, len(lanes)) * np.exp(-((lanes - 820) / 520) ** 2)
    li = rng.choice(len(lanes), n, p=lw / lw.sum())
    y_end = np.clip(lanes[li] + rng.normal(0, 1, n) * rng.uniform(18, 90, len(lanes))[li], -120, 1720)
    xw = wall_x(y_end)
    stop = rng.exponential(55, n) * (1 + 0.6 * rng.random(n))          # heads stack in front of the wall
    x_end = xw - 6 - stop
    ln = rng.uniform(420, 1700, n)
    # perspective: the torrent comes from a wide mouth near the lens (left) and narrows into the wall
    y_start = y_end + rng.normal(0, 1, n) * 160 + (y_end - 820) * rng.uniform(0.9, 2.4, n)
    x_start = x_end - ln
    M = 120
    s = np.linspace(0, 1, M)
    sag = rng.normal(0, 14, n)
    P = np.stack([x_start[:, None] + (x_end - x_start)[:, None] * s[None],
                  y_start[:, None] + (y_end - y_start)[:, None] * (s[None] ** 0.8)
                  + sag[:, None] * np.sin(np.pi * s)[None]], -1)
    depth = rng.random(n)
    blur = np.where(depth < 0.30, 3 + 46 * (0.30 - depth) / 0.30, rng.uniform(0.5, 0.9, n))
    near = np.exp(-stop / 70)                                           # heads right at the wall burn hottest
    prof = (0.10 + 0.90 * s[None] ** 2.2) * (1 + 2.6 * near[:, None] * s[None] ** 8)
    inten = lognormal_int(rng, n, 0.026, 0.75) * (1 + blur / 6) ** 0.5
    hue = np.clip(0.9 - 0.75 * s[None] ** 3 * (0.4 + 0.6 * near[:, None]) + rng.normal(0, 0.05, (n, 1)), 0, 1)
    trails(cv, P, inten, hue, blur, rng, env=(0.25, 0.0), speed=0.25, prof=prof)
    # 2) the pile-up on the wall face: a dense, hot band of short vertical smears where the heads hit
    k = 3200
    yy = np.clip(rng.normal(820, 380, k), -100, 1700)
    xx = wall_x(yy) - np.abs(rng.normal(0, 14, k))
    dens = np.exp(-((yy - 820) / 420) ** 2)
    swarm_streaks(cv, np.c_[xx, yy], np.c_[rng.normal(0, 0.12, k), rng.choice([-1.0, 1.0], k)],
                  rng.uniform(10, 70, k), lognormal_int(rng, k, 0.06, 0.6) * (0.15 + 0.85 * dens),
                  rng.uniform(0.0, 0.35, k), np.where(rng.random(k) < 0.3, rng.uniform(3, 12, k), 0.6))
    # the face itself glows: a soft vertical sheet of light, hottest in the middle
    yv = np.linspace(-120, 1720, 600)
    face = np.c_[wall_x(yv), yv]
    fall = np.exp(-((yv - 820) / 380) ** 2)
    for I0, bl, h in ((0.20, 1.0, 0.0), (0.18, 9, 0.15), (0.16, 34, 0.35), (0.06, 90, 0.5)):
        cv.polylines(face[None], (I0 * fall ** 1.3)[None], ramp(h), bl)
    glow(cv, (wall_x(820.0) - 120, 820.0), 6000.0, 80, 0.05, n=8000, seed=7)
    # 3) sparks splashing back off the wall
    k = 1100
    yy = np.clip(rng.normal(820, 360, k), 0, 1600)
    p0 = np.c_[wall_x(yy) - 4, yy]
    dirv = np.c_[-np.abs(rng.normal(0.8, 0.35, k)), rng.normal(0, 0.9, k)]
    dist = rng.exponential(120, k)
    swarm_streaks(cv, p0 + dirv / np.linalg.norm(dirv, axis=1, keepdims=True) * dist[:, None], dirv,
                  rng.uniform(10, 80, k), lognormal_int(rng, k, 0.08, 0.6) * np.exp(-((yy - 820) / 520) ** 2),
                  rng.uniform(0.1, 0.7, k), np.where(rng.random(k) < 0.35, rng.uniform(3, 16, k), 0.6))
    # 4) behind the wall: locked and dim, a faint warm leak only
    k = 160
    q = np.c_[rng.uniform(1250, 1650, k), rng.uniform(0, 1600, k)]
    cv.points(q, lognormal_int(rng, k, 0.25, 0.6), ramp(rng.uniform(0.5, 0.95, k)), rng.uniform(12, 50, k))
    # lit air in front of the wall
    glow(cv, (930.0, 820.0), 14000.0, 300, 0.3, n=9000, seed=3)
    glow(cv, (700.0, 820.0), 12000.0, 520, 0.55, n=8000, seed=4)
    motes(cv, 18, (0, 0, 1100, 1600), energy=(0.02, 0.08), blur=(20, 80), seed=5)
    return dict(exposure=0.82, bloom=0.12, halation=0.08, vignette=0.45, atmos=0.02)


@scene("threat-phishing", R11, "Threat card: deepfakes and impersonation",
       "A wide stream of light sweeps up through the frame and so does its copy, a twin stream offset beside it with the same twists: a double exposure, the real one warm white, the fake amber, a fainter third echo behind.")
def threat_phishing(cv):
    """Round 2: no hook. The deepfake is a copy: the same ribbon drawn twice with the same seed,
    offset across the stream, plus a soft third echo far out of focus."""
    rng = np.random.default_rng(43)
    ctrl = np.array([[-260.0, 1560.0], [420.0, 1380.0], [760.0, 560.0], [1880.0, 120.0]])

    def fan(t):
        return 0.5 + 0.3 * (1 - t) ** 2 + 0.85 * t ** 2.2

    # the perpendicular of the stream's mid direction: the copy is shifted across it
    d = ctrl[3] - ctrl[0]
    d /= np.linalg.norm(d)
    nrm = np.array([-d[1], d[0]])
    if nrm[1] < 0:
        nrm = -nrm                                                      # copy sits below-right
    shift = nrm * 300 + d * 40
    common = dict(n=420, width=105, twist=1.1, twist_phase=0.6, wob=0.18, isig=0.8, tjit=0.16,
                  env=(0.2, 0.12), spread_profile=fan, speed_mod=0.4)
    # the real stream: warm white core
    ribbon(cv, ctrl, inten=0.09, hue=(0.0, 0.45), blur=lambda u, r: 0.5 + 6.0 * np.abs(u) ** 2.4, seed=61, **common)
    # the copy: the same trails (same seed), shifted, a little softer and amber
    ribbon(cv, ctrl + shift, inten=0.07, hue=(0.35, 0.85), blur=lambda u, r: 0.8 + 9.0 * np.abs(u) ** 2.0,
           seed=61, **common)
    # a third echo, far out of focus, behind both
    ribbon(cv, ctrl + 2.1 * shift, n=60, width=170, twist=1.1, twist_phase=0.6, wob=0.2, inten=0.07, isig=0.5,
           hue=(0.4, 0.9), blur=(28, 70), tjit=0.2, env=(0.2, 0.15), spread_profile=fan, seed=62)
    ribbon(cv, ctrl - 0.9 * shift, n=50, width=160, twist=0.8, wob=0.25, inten=0.06, isig=0.5,
           hue=(0.3, 0.9), blur=(36, 90), tjit=0.25, env=(0.25, 0.2), spread_profile=fan, seed=63)
    # sparks shed by both streams
    for off, sd in ((np.zeros(2), 64), (shift, 65)):
        r2 = np.random.default_rng(sd)
        k = 520
        t = r2.uniform(0.1, 0.95, k)
        sp = bezier(ctrl + off, t)
        tg = bezier_deriv(ctrl + off, t)
        tg /= np.linalg.norm(tg, axis=1, keepdims=True)
        nr = np.c_[-tg[:, 1], tg[:, 0]]
        swarm_streaks(cv, sp + nr * r2.normal(0, 1, (k, 1)) * 230 * fan(t)[:, None], tg + r2.normal(0, 0.25, (k, 2)),
                      r2.uniform(14, 90, k), lognormal_int(r2, k, 0.05, 0.6), r2.uniform(0.15, 0.85, k),
                      np.where(r2.random(k) < 0.35, r2.uniform(4, 22, k), 0.6))
    # lit air between and around the twins
    mid = bezier(ctrl + 0.5 * shift, np.array([0.55]))[0]
    glow(cv, mid, 11000.0, 420, 0.4, n=9000, seed=3)
    glow(cv, mid + np.array([260.0, -180.0]), 7000.0, 300, 0.2, n=7000, seed=4)
    motes(cv, 22, (0, 0, 1600, 1600), energy=(0.02, 0.08), blur=(20, 90), hue=(0.4, 0.95), seed=6)
    return dict(exposure=0.8, bloom=0.12, halation=0.08, vignette=0.45, atmos=0.04)


@scene("threat-breach", R11, "Threat card: breach and data theft",
       "A wide field of light funnels into a narrow gap and bursts out the other side.")
def threat_breach(cv):
    rng = np.random.default_rng(51)
    g = np.array([760.0, 800.0])
    gh = 22.0
    n = 1150
    sx = rng.uniform(-250, 380, n)
    sy = rng.uniform(-150, 1750, n)
    gy = g[1] + rng.uniform(-gh, gh, n)
    M1, M2 = 160, 170
    t = np.linspace(0, 1, M1)
    ctrl = np.stack([np.c_[sx, sy], np.c_[sx + 380, sy],
                     np.c_[np.full(n, g[0] - 260), gy + (sy - gy) * 0.08], np.c_[np.full(n, g[0]), gy]], 1)
    A = bezier(ctrl, t)
    ang = rng.normal(0, 0.32, n) + (gy - g[1]) / gh * 0.12
    ln = rng.uniform(380, 1250, n)
    curv = rng.normal(0, 0.0004, n)
    u = np.linspace(0, 1, M2)[1:]
    dist = ln[:, None] * u[None]
    a2 = ang[:, None] + curv[:, None] * dist
    Bx = g[0] + np.cumsum(np.cos(a2) * (ln[:, None] / (M2 - 1)), 1)
    By = gy[:, None] + np.cumsum(np.sin(a2) * (ln[:, None] / (M2 - 1)), 1)
    P = np.concatenate([A, np.stack([Bx, By], -1)], 1)
    s1 = np.r_[t, np.ones(M2 - 1)]
    s2 = np.r_[np.zeros(M1), u]
    prof = (0.12 + 0.88 * s1 ** 2.6) * (1 - 0.55 * np.exp(-(s2 * 6)) * (s2 > 0)) * (1 - smoothstep(0.35, 1.0, s2))
    prof = prof[None] * np.ones((n, 1))
    hue = (0.95 - 0.8 * s1 ** 4)[None] * np.ones((n, 1))
    hue = np.where(s2[None] > 0, 0.15 + 0.5 * s2[None], hue)
    inten = lognormal_int(rng, n, 0.045, 0.7)
    blur = np.where(rng.random(n) < 0.18, rng.uniform(3, 20, n), rng.uniform(0.5, 0.9, n))
    trails(cv, P, inten, hue, blur, rng, env=(0.12, 0.02), prof=prof)
    # the wall: barely there, lit only at the lips of the gap
    for ya, yb in ((-60.0, g[1] - gh - 4), (g[1] + gh + 4, 1660.0)):
        y = np.linspace(ya, yb, 600)
        dd = np.minimum(np.abs(y - (g[1] - gh)), np.abs(y - (g[1] + gh)))
        I = 0.035 + 0.5 * np.exp(-dd / 70)
        cv.polylines(np.c_[np.full(600, g[0] + 1), y][None], I[None], ramp(0.3), 0.5)
    cv.points(np.array([[g[0] + 4, g[1]]]), 5.0, ramp(0.05), 1.5)
    motes(cv, 14, (900, 0, 1600, 1600), energy=(0.01, 0.05), blur=(20, 70), seed=7)
    # round 4 (QA C4): second card of the home grid, was mean 29 with 72% near-black. A deeper, out-of-focus
    # layer of the same field funnels in behind the sharp one (so the left half carries soft light top to bottom),
    # the burst throws a wider soft spray, and the gap lights the haze around it. The bow-tie above is unchanged
    # (own seed, drawn after it).
    r4 = np.random.default_rng(5104)
    nb = BREACH_DEEP
    sx = r4.uniform(-300, 420, nb)
    sy = r4.uniform(-250, 1850, nb)
    gy = g[1] + r4.uniform(-gh, gh, nb)
    ctrl = np.stack([np.c_[sx, sy], np.c_[sx + 380, sy],
                     np.c_[np.full(nb, g[0] - 260), gy + (sy - gy) * 0.08], np.c_[np.full(nb, g[0]), gy]], 1)
    A = bezier(ctrl, t)
    ang = r4.normal(0, 0.42, nb)
    ln = r4.uniform(500, 1300, nb)
    dist = ln[:, None] * u[None]
    a2 = ang[:, None] + r4.normal(0, 0.0004, nb)[:, None] * dist
    Bx = g[0] + np.cumsum(np.cos(a2) * (ln[:, None] / (M2 - 1)), 1)
    By = gy[:, None] + np.cumsum(np.sin(a2) * (ln[:, None] / (M2 - 1)), 1)
    P = np.concatenate([A, np.stack([Bx, By], -1)], 1)
    # out of focus away from the gap (sharp where the lines squeeze through it)
    dg = np.hypot(P[..., 0] - g[0], P[..., 1] - g[1])
    blur = 1.0 + r4.uniform(6, 22, nb)[:, None] * smoothstep(60, 520, dg)
    prof = (0.30 + 0.70 * s1 ** 1.6) * (1 - smoothstep(0.45, 1.0, s2))
    # it gives the gap no extra light: the pinch stays as tight and hot as before
    prof = prof[None] * smoothstep(40, 360, dg)
    hue = np.where(s2 > 0, 0.2 + 0.5 * s2, 0.9 - 0.6 * s1 ** 3)[None] * np.ones((nb, 1))
    trails(cv, P, lognormal_int(r4, nb, BREACH_DEEP_I, 0.6), hue, blur, r4, env=(0.12, 0.02), prof=prof)
    glow(cv, g + np.array([420.0, 0.0]), BREACH_HAZE, 420, 0.5, n=8000, seed=53)
    glow(cv, g - np.array([440.0, 0.0]), BREACH_HAZE * 0.8, 520, 0.6, n=8000, seed=54)
    return dict(exposure=BREACH_EXP, bloom=0.12, halation=0.07, vignette=0.42, atmos=0.05)


BREACH_DEEP, BREACH_DEEP_I, BREACH_HAZE, BREACH_EXP = 700, 0.03, 8000.0, 1.12


# ---------------------------------------------------------------------------
# DOMAIN HEROES (16:9). Light sits right and up; left and bottom-left stay calm.


@scene("domain-network", R169, "Coverage: Network security (domain page hero + card)",
       "Glowing nodes joined by fine links, packets of light racing along them; a second network glows out of focus behind.")
def domain_network(cv):
    rng = np.random.default_rng(61)
    pts = []
    while len(pts) < 16:
        p = np.array([rng.uniform(820, 2520), rng.uniform(-40, 1180)])
        if all(np.hypot(*(p - q)) > 300 for q in pts):
            pts.append(p)
    pts = np.array(pts)
    N = len(pts)
    depth = rng.uniform(0, 1, N) ** 2
    depth[rng.choice(N, 2, replace=False)] = rng.uniform(0.85, 1.0, 2)
    D = np.hypot(*(pts[:, None] - pts[None]).transpose(2, 0, 1))
    inT = [0]
    edges = []
    while len(inT) < N:
        best = None
        for i in inT:
            for j in range(N):
                if j not in inT and (best is None or D[i, j] < best[0]):
                    best = (D[i, j], i, j)
        edges.append((best[1], best[2]))
        inT.append(best[2])
    extra = sorted(((D[i, j], i, j) for i in range(N) for j in range(i + 1, N)
                    if (i, j) not in edges and (j, i) not in edges))[:7]
    edges += [(i, j) for _, i, j in extra]
    for (i, j) in edges:
        A, B = pts[i], pts[j]
        v = B - A
        L = np.linalg.norm(v)
        nr = np.array([-v[1], v[0]]) / L
        bend = rng.normal(0, 0.04) * L
        ctrl = np.array([A, A + v / 3 + nr * bend, A + 2 * v / 3 + nr * bend, B])
        dz = 0.5 * (depth[i] + depth[j])
        bl = 0.5 + 34 * dz ** 2
        dim = 1 - 0.5 * dz
        M = 400
        t = np.linspace(0, 1, M)
        sp = bezier(ctrl, t)
        nn = normals(sp)
        # the fibre: a few faint parallel strands
        for off in (-1.5, 0.0, 1.6):
            cv.polylines((sp + nn * off)[None], np.full((1, M), 0.15 * dim), ramp(0.5), bl)
        # packets: comets travelling along the link
        for _ in range(rng.integers(2, 5)):
            a0 = rng.uniform(0.05, 0.75)
            ln = rng.uniform(0.08, 0.22)
            tt = np.clip((t - a0) / ln, 0, 1)
            on = (t >= a0) & (t <= a0 + ln)
            prof = on * (0.05 + 0.95 * tt ** 2.2)
            dirn = rng.choice([1, -1])
            if dirn < 0:
                prof = prof[::-1]
            cv.polylines(sp[None], (prof * lognormal_int(rng, 1, 1.4, 0.4) * dim)[None], ramp(0.12), bl)
            cv.polylines(sp[None], (prof * 0.25 * dim)[None], ramp(0.5), bl + 7)
    e = 22.0 * (1 - 0.5 * depth)
    bl = 0.5 + 34 * depth ** 2
    cv.points(pts, e * (1 + (bl / 6) ** 2 * 0.25), ramp(0.03), bl)
    glow(cv, pts, e * 2.5, 8 + bl * 0.6, 0.5, n=800)
    # round 1: a second, far network out of focus behind the first (depth, midtones)
    k = 150
    q = np.c_[rng.uniform(250, 2550, k), rng.uniform(-60, 1300, k)]
    bq = rng.uniform(12, 60, k)
    cv.points(q, lognormal_int(rng, k, 0.9, 0.6) * (1 + (bq / 6) ** 2 * 0.25), ramp(rng.uniform(0.2, 0.8, k)), bq)
    dq = np.hypot(*(q[:, None] - q[None]).transpose(2, 0, 1))
    np.fill_diagonal(dq, 1e9)
    nb = dq.argmin(1)
    tq = np.linspace(0, 1, 60)
    segs = q[:, None, :] + (q[nb] - q)[:, None, :] * tq[None, :, None]
    cv.polylines(segs, np.full((k, 60), 0.05), ramp(0.5), bq * 0.8)
    glow(cv, (1650.0, 560.0), 22000.0, 460, 0.5, n=8000, seed=9)
    glow(cv, (1000.0, 420.0), 9000.0, 360, 0.55, n=7000, seed=10)
    motes(cv, 20, (900, 0, 2400, 1350), energy=(0.01, 0.05), blur=(20, 70), seed=8)
    # round 4 (QA C5): the graph now carries on down the frame (it stopped at two thirds, so phones showed an
    # empty lower 40%). A lower ring of nodes sits a little nearer the camera, softer, linked to each other and up
    # into the graph above, with packets on the links; its light fills the haze under the title. The graph above
    # is unchanged (own seed, drawn after it).
    r4 = np.random.default_rng(6104)
    low = []
    while len(low) < NET_LOW:
        q0 = np.array([r4.uniform(520, 2560), r4.uniform(940, 1500)])
        if all(np.hypot(*(q0 - q1)) > 330 for q1 in low) and np.min(np.hypot(*(pts - q0).T)) > 220:
            low.append(q0)
    low = np.array(low)
    dlow = r4.uniform(0.3, 0.62, len(low))

    def link(A, B, dz):
        v = B - A
        L = np.linalg.norm(v)
        nr = np.array([-v[1], v[0]]) / L
        bend = r4.normal(0, 0.04) * L
        ctrl = np.array([A, A + v / 3 + nr * bend, A + 2 * v / 3 + nr * bend, B])
        bl = 0.5 + 34 * dz ** 2
        dim = (1 - 0.5 * dz) * (1 + bl / 6) ** 0.5
        M = 400
        t = np.linspace(0, 1, M)
        sp = bezier(ctrl, t)
        nn = normals(sp)
        for off in (-1.5, 0.0, 1.6):
            cv.polylines((sp + nn * off)[None], np.full((1, M), 0.15 * dim * NET_LOW_I), ramp(0.5), bl)
        for _ in range(r4.integers(2, 5)):
            a0 = r4.uniform(0.05, 0.75)
            ln = r4.uniform(0.08, 0.22)
            tt = np.clip((t - a0) / ln, 0, 1)
            on = (t >= a0) & (t <= a0 + ln)
            prof = on * (0.05 + 0.95 * tt ** 2.2)
            if r4.random() < 0.5:
                prof = prof[::-1]
            cv.polylines(sp[None], (prof * lognormal_int(r4, 1, 1.4, 0.4) * dim * NET_LOW_I)[None], ramp(0.12), bl)
            cv.polylines(sp[None], (prof * 0.25 * dim * NET_LOW_I)[None], ramp(0.5), bl + 7)

    # each lower node: its nearest lower neighbour and its nearest node in the graph above
    Dl = np.hypot(*(low[:, None] - low[None]).transpose(2, 0, 1))
    np.fill_diagonal(Dl, 1e9)
    done = set()
    for i in range(len(low)):
        j = int(Dl[i].argmin())
        if (j, i) not in done:
            done.add((i, j))
            link(low[i], low[j], 0.5 * (dlow[i] + dlow[j]))
        up = np.hypot(*(pts - low[i]).T)
        u = int(up.argmin())
        link(low[i], pts[u], 0.5 * (dlow[i] + depth[u]))
    e = 22.0 * (1 - 0.5 * dlow)
    bl = 0.5 + 34 * dlow ** 2
    cv.points(low, e * (1 + (bl / 6) ** 2 * 0.25) * NET_LOW_I, ramp(0.03), bl)
    glow(cv, low, e * 2.5 * NET_LOW_I, 8 + bl * 0.6, 0.5, n=800)
    glow(cv, (1250.0, 1120.0), NET_HAZE, 480, 0.5, n=8000, seed=11)
    return dict(exposure=NET_EXP, bloom=0.13, halation=0.08, vignette=0.42, atmos=0.04)


NET_LOW, NET_LOW_I, NET_HAZE, NET_EXP = 7, 1.0, 24000.0, 1.45


@scene("domain-endpoint", R169, "Coverage: Endpoint and device security (high-key card)",
       "A dense night floor of device lights in perspective, shallow focus, under a glowing horizon; one guarded device burns hot in the middle.")
def domain_endpoint(cv):
    rng = np.random.default_rng(72)
    f, cx, cy, h = 1250.0, 1250.0, 330.0, 1.5
    X, Z = np.meshgrid(np.arange(-40, 41, 0.8), np.geomspace(1.2, 70, 95))
    X = X.ravel() + rng.normal(0, 0.22, X.size)
    Z = Z.ravel() * np.exp(rng.normal(0, 0.03, Z.size))
    x = cx + f * X / Z
    y = cy + f * h / Z
    # round 2: high-key card: a denser, brighter floor of device light under a glowing horizon
    keep = (x > -200) & (x < 2600) & (y < 1500) & (rng.random(X.size) < 0.95 * np.minimum(1, (7 / Z) ** 0.7))
    X, Z, x, y = X[keep], Z[keep], x[keep], y[keep]
    Zf = 4.2
    blur = 0.5 + 105 * np.abs(1 / Z - 1 / Zf) ** 0.9
    # headline corner on the domain page stays calmer
    mask = 1 - 0.6 * (1 - smoothstep(450, 1100, x)) * smoothstep(780, 1150, y)
    E = lognormal_int(rng, len(x), 0.95, 0.7) * mask * (1 + 0.16 * blur ** 2) * np.minimum(1, (Zf / Z) ** 0.8)
    hue = np.clip(rng.uniform(0.15, 1.0, len(x)) - 0.25 * np.exp(-Z / 30), 0, 1)
    ln = 0.16 * f / Z
    P = np.stack([np.c_[x - ln / 2, y], np.c_[x + ln / 2, y]], 1)
    cv.polylines(P, (E / ln * 0.5)[:, None] * np.ones((1, 2)), ramp(hue), blur)
    cv.points(np.c_[x, y], E * 0.45, ramp(hue), blur)
    # the guarded device, in focus
    gx, gy = cx + f * 0.35 / Zf, cy + f * h / Zf
    cv.points(np.array([[gx, gy]]), 30.0, ramp(0.0), 1.0)
    glow(cv, (gx, gy), 260.0, 22, 0.1, n=4000)
    # a soft column of light rises from it into the haze
    col = np.stack([np.full(300, gx), np.linspace(gy, gy - 700, 300)], -1)
    tcol = np.linspace(0, 1, 300)
    for I0, bl, hh in ((0.10, 3.0, 0.1), (0.08, 18.0, 0.3), (0.07, 60.0, 0.5)):
        cv.polylines(col[None], (I0 * (1 - tcol) ** 1.5)[None], ramp(hh), bl)
    glow(cv, (gx, gy - 120), 22000.0, 360, 0.35, n=8000, seed=2)
    # the horizon glows: the far floor of devices lights the haze above it, edge to edge
    for k, hx in enumerate(np.linspace(150.0, 2250.0, 8)):
        glow(cv, (hx, cy - 10), 3600.0 * (0.8 + 0.4 * np.sin(k * 2.3) ** 2), 170, 0.4, n=6000, seed=10 + k)
    glow(cv, (cx, cy + 40), 14000.0, 520, 0.5, n=8000, seed=4)
    return dict(exposure=1.25, bloom=0.14, halation=0.09, vignette=0.42, atmos=0.02)


@scene("domain-cloud", R169, "Coverage: Cloud security (high-key card)",
       "Wisps of white-gold light drift across the frame like a cloud bank, with a bright river of light running through it that burns warm white at its core; a softer bank lower down.")
def domain_cloud(cv):
    rng = np.random.default_rng(81)
    fld = SinField(rng, n=8, wavelength=1000)
    shape = SinField(rng, n=7, wavelength=520)

    def field(x, y):
        vx, vy = fld.curl(x, y)
        return 1.0 + 0.3 * vx, 0.8 * vy

    # round 2: high-key card (bright one of its row). The round 1 wisps, now across the whole width,
    # with a broad river of soft light running through the bank: its core burns warm white, so the
    # cloud reads as lit from within. The lower middle (the domain hero's text) stays mid-dark.
    n = 1500
    y0 = rng.normal(480, 270, n)
    st = np.c_[rng.uniform(-600, 900, n), y0]
    P = flow_trails(cv, field, st, 320, h=8.0)
    x, y = P[..., 0], P[..., 1]
    yc = 470 + 110 * np.sin(x / 600 + 0.5)
    thick = 280 + 120 * shape.scalar(x * 0.7, 0 * x)
    dens = smoothstep(0.1, 0.7, 1 - np.abs(y - yc) / thick + 0.8 * shape.scalar(x, y)) ** 1.5
    dens *= smoothstep(-200, 500, x)
    blur = np.exp(rng.uniform(np.log(0.5), np.log(40), n))
    inten = lognormal_int(rng, n, 0.011, 0.6) * (1 + blur / 4) ** 0.6
    crisp = rng.random(n) < 0.14
    inten[crisp] *= 3.0
    blur[crisp] = 0.6
    hue = np.where(crisp, rng.uniform(0.0, 0.45, n), rng.uniform(0.05, 0.6, n))
    trails(cv, P, inten, hue, blur, rng, env=(0.05, 0.05), prof=dens, speed=0.6)
    # the river of light inside the bank (follows the bank's centre line)
    xs = np.linspace(-300, 2700, 4)
    ctrl = np.c_[xs, 470 + 110 * np.sin(xs / 600 + 0.5) - np.array([0, 60, -40, 0])]
    W2 = lambda t: 0.7 + 0.6 * np.sin(np.pi * t) ** 2
    ribbon(cv, ctrl, n=380, width=120, twist=0.6, wob=0.3, inten=0.10, isig=0.8, hue=(0.0, 0.45),
           blur=lambda u, r: 0.5 + 18.0 * np.abs(u) ** 2, tjit=0.3, env=(0.2, 0.2), spread_profile=W2, seed=12, speed_mod=0.5)
    ribbon(cv, ctrl + np.array([[0, 40], [0, 20], [0, -20], [0, 30]]), n=120, width=260, twist=0.3, wob=0.4,
           inten=0.06, isig=0.6, hue=(0.2, 0.75), blur=(20, 80), tjit=0.3, env=(0.25, 0.25), spread_profile=W2, seed=13)
    # a lower, fainter bank under the hero text: light reaches the bottom of the card too
    r = np.random.default_rng(84)
    n = 700
    st = np.c_[r.uniform(-600, 900, n), r.normal(1170, 110, n)]
    P = flow_trails(cv, field, st, 320, h=8.0)
    x, y = P[..., 0], P[..., 1]
    yc = 1170 + 60 * np.sin(x / 500 + 2.0)
    dens = smoothstep(0.1, 0.7, 1 - np.abs(y - yc) / (150 + 60 * shape.scalar(x * 0.7, 0 * x + 400))
                      + 0.8 * shape.scalar(x, y + 700)) ** 1.5 * smoothstep(-200, 500, x)
    blur = np.exp(r.uniform(np.log(4), np.log(70), n))
    trails(cv, P, lognormal_int(r, n, 0.0042, 0.6) * (1 + blur / 4) ** 0.6, r.uniform(0.3, 0.85, n), blur, r,
           env=(0.05, 0.05), prof=dens, speed=0.6)
    glow(cv, (1350.0, 470.0), 16000.0, 300, 0.35, n=9000, seed=9)
    glow(cv, (1500.0, 1170.0), 3500.0, 260, 0.5, n=7000, seed=11)
    motes(cv, 26, (0, 0, 2400, 1350), energy=(0.01, 0.06), blur=(15, 70), seed=10)
    return dict(exposure=1.25, bloom=0.14, halation=0.08, vignette=0.42)


@scene("domain-identity", R169, "Coverage: Identity and access",
       "Fingerprint-like ridges drawn in light on a tilted plane, centred in the frame, sharp in the middle and falling out of focus, in lit haze.")
def domain_identity(cv):
    rng = np.random.default_rng(91)
    # round 2: moved into the middle of the card (the tile crop showed only half of it), bigger, brighter
    c = np.array([1420.0, 700.0])
    rot = np.deg2rad(22)
    th = np.linspace(-np.pi, np.pi, 1100)
    ph = rng.uniform(0, 2 * np.pi, 4)
    mod = 1 + 0.11 * np.sin(2 * th + ph[0]) + 0.05 * np.sin(3 * th + ph[1]) + 0.025 * np.sin(5 * th + ph[2])
    paths, Is, hues = [], [], []
    K = 46
    for k in range(K):
        Lk = 28 + k * 21.5
        per = 0.018 * pwobble(rng, 1, (th + np.pi) / (2 * np.pi), terms=2, fmin=2, fmax=5)[0]
        r = Lk / mod * (1 + per)
        cc = c + k * np.array([2.5, -1.8])
        p = circle_pts(cc, r, th, 1.0, 1.33, rot)
        g = np.ones_like(th)
        for _ in range(rng.integers(1, 4)):
            a = rng.uniform(-np.pi, np.pi)
            w = rng.uniform(0.04, 0.2)
            dd = np.angle(np.exp(1j * (th - a)))
            g *= smoothstep(w * 0.5, w, np.abs(dd))
        paths.append(p)
        # round 4 (QA C5): outer ridges fall off less (they carry the print into the lower third)
        Is.append(g * (0.66 - ID_FALL * k) * (0.7 + 0.3 * np.sin(th * 3 + k)))
        hues.append(np.full_like(th, 0.08 + 0.55 * k / K))
    P = np.array(paths)
    I = np.array(Is)
    nrm = np.array([np.sin(rot + 0.5), -np.cos(rot + 0.5)])
    dist = (P - c) @ nrm
    B = 0.5 + np.maximum(0, np.abs(dist) - 180) * 0.045
    trails(cv, P, np.ones(K), np.array(hues), B, rng, env=None, speed=0.15, prof=I, periodic=True)
    cv.points(c[None], 3.0, ramp(0.0), 4)
    # a scanning light lifts the haze around the print (midtones, depth)
    glow(cv, c, 12000.0, 420, 0.5, n=8000, seed=12)
    glow(cv, c + np.array([380.0, -260.0]), 9000.0, 300, 0.5, n=7000, seed=13)
    motes(cv, 20, (300, 0, 2400, 1350), energy=(0.01, 0.05), blur=(20, 60), seed=11)
    # round 4 (QA C5): the scanning light also lights the haze under the print (was mean 29, dark lower third)
    glow(cv, c + np.array([-160.0, 430.0]), ID_HAZE, 440, 0.5, n=8000, seed=14)
    return dict(exposure=ID_EXP, bloom=0.13, halation=0.08, vignette=0.42, atmos=0.04)


ID_FALL, ID_HAZE, ID_EXP = 0.0065, 10000.0, 1.3


@scene("domain-email", R169, "Coverage: Email security",
       "Message traffic streams like highway light trails towards a glowing gate; one stream is pulled out.")
def domain_email(cv):
    rng = np.random.default_rng(101)
    vp = np.array([3100.0, 600.0])
    gate_x = 1560.0
    n = 18
    yl = np.sort(np.r_[rng.uniform(60, 520, n // 2), rng.uniform(700, 1350, n - n // 2)])
    M = 900
    x = np.linspace(-150, 2560, M)
    a = (x + 150) / (vp[0] + 150)
    near = np.abs(yl - vp[1]) / 750
    blur = 0.5 + 26 * np.maximum(0, near - 0.3) ** 1.6
    caught = int(np.argmin(np.abs(yl - 760)))
    for i in range(n):
        yc = yl[i] + (vp[1] - yl[i]) * a
        k = 5
        offs = (rng.normal(0, 2.2, k) + np.linspace(-3, 3, k))[:, None] * (1 - a)[None]
        P = np.stack([np.broadcast_to(x, (k, M)), yc[None] + offs], -1)
        I = np.zeros((k, M))
        for q in range(k):
            sp = 1 + 0.6 * wobble(rng, 1, a, terms=3, fmin=1.5, fmax=5)[0]
            I[q] = lognormal_int(rng, 1, 0.07, 0.5)[0] * np.clip(sp, 0.1, 3)
        # message pulses: comet-like bursts travelling down the lane
        cm = np.zeros(M)
        for _ in range(rng.integers(2, 6)):
            x0c = rng.uniform(0, 2500)
            lc = rng.uniform(90, 260) * (1 - (x0c + 150) / (vp[0] + 150)) + 20
            on = (x >= x0c) & (x <= x0c + lc)
            cm += on * np.clip((x - x0c) / lc, 0, 1) ** 2.2 * lognormal_int(rng, 1, 0.45, 0.4)[0]
        I += cm[None] * np.r_[1.0, np.full(k - 1, 0.25)][:, None]
        H = np.where(x < gate_x, 0.82, 0.12)[None] * np.ones((k, 1))
        if i == caught:
            kk = x > gate_x
            dy = np.where(kk, ((x - gate_x) / 480) ** 2 * 360, 0)
            P[..., 1] += dy[None]
            I *= np.where(kk, np.exp(-(x - gate_x) / 240), 1)[None] * 1.4
            H = np.where(kk, 1.0, 0.82)[None] * np.ones((k, 1))
        I *= envelope(np.linspace(0, 1, M), 0.18, 0.02)[None] * (0.5 + 0.5 * smoothstep(gate_x - 200, gate_x + 60, x))[None]
        cv.polylines(P, I, ramp(H), np.full(k, blur[i]))
    ys = np.linspace(-60, 1420, 1000)
    lane_y = yl + (vp[1] - yl) * (gate_x + 150) / (vp[0] + 150)
    dens = np.exp(-((ys[:, None] - lane_y[None]) / 9.0) ** 2).sum(1)
    Ig = (0.12 + 0.7 * dens) * envelope(np.linspace(0, 1, 1000), 0.2, 0.2)
    for off, mul, bl, hh in ((0, 1.0, 0.5, 0.04), (2.0, 0.35, 0.5, 0.1), (0, 0.45, 9, 0.5)):
        cv.polylines(np.c_[np.full(1000, gate_x + off), ys][None], (Ig * mul)[None], ramp(hh), bl)
    # round 1: the gate lights the haze around it (midtones, less empty navy)
    glow(cv, (gate_x, float(vp[1])), 18000.0, 380, 0.45, n=8000, seed=9)
    motes(cv, 18, (1000, 0, 2400, 1350), energy=(0.01, 0.05), blur=(20, 60), seed=23)
    # round 4 (QA C5): the hero was mean 22 and its lower 40% was empty navy on phones. More lanes now come up
    # from below the frame into the same vanishing point: near the camera, so soft and out of focus, crossing the
    # lower third under the title. The gate lights the haze below it too. The lanes above are unchanged (own seed).
    r4 = np.random.default_rng(1104)
    yl2 = np.sort(r4.uniform(1380, 2080, EMAIL_LOW))
    for i in range(len(yl2)):
        yc = yl2[i] + (vp[1] - yl2[i]) * a
        k = 4
        offs = (r4.normal(0, 2.2, k) + np.linspace(-3, 3, k))[:, None] * (1 - a)[None]
        P = np.stack([np.broadcast_to(x, (k, M)), yc[None] + offs], -1)
        bl = min(0.5 + 26 * max(0.0, abs(yl2[i] - vp[1]) / 750 - 0.3) ** 1.6, 34.0)
        I = np.zeros((k, M))
        for q in range(k):
            sp = 1 + 0.6 * wobble(r4, 1, a, terms=3, fmin=1.5, fmax=5)[0]
            I[q] = lognormal_int(r4, 1, 0.07, 0.5)[0] * np.clip(sp, 0.1, 3)
        cm = np.zeros(M)
        for _ in range(r4.integers(2, 5)):
            x0c = r4.uniform(0, 2300)
            lc = r4.uniform(140, 380)
            on = (x >= x0c) & (x <= x0c + lc)
            cm += on * np.clip((x - x0c) / lc, 0, 1) ** 2.2 * lognormal_int(r4, 1, 0.45, 0.4)[0]
        I += cm[None] * np.r_[1.0, np.full(k - 1, 0.25)][:, None]
        I *= EMAIL_LOW_I * (1 + bl / 6) ** 0.7
        I *= envelope(np.linspace(0, 1, M), 0.10, 0.02)[None] * (0.5 + 0.5 * smoothstep(gate_x - 200, gate_x + 60, x))[None]
        H = np.where(x < gate_x, 0.82, 0.12)[None] * np.ones((k, 1))
        cv.polylines(P, I, ramp(H), np.full(k, bl))
    glow(cv, (gate_x - 60, 1080.0), EMAIL_HAZE, 440, 0.5, n=8000, seed=24)
    glow(cv, (gate_x + 200, 300.0), EMAIL_HAZE * 0.5, 380, 0.5, n=6000, seed=25)
    return dict(exposure=EMAIL_EXP, bloom=0.12, halation=0.08, vignette=0.42, atmos=0.04)


EMAIL_LOW, EMAIL_LOW_I, EMAIL_HAZE, EMAIL_EXP = 9, 1.0, 12000.0, 1.4


@scene("domain-applications", R169, "Coverage: Application and API security (high-key card)",
       "Lines of code written in light on a tilted, backlit page, sharp near the focus and melting into bokeh; the lines around the flaw burn hotter and one line flares where the flaw is.")
def domain_applications(cv):
    rng = np.random.default_rng(112)
    W, Hh = 1900.0, 1500.0
    Hm = homography([[0, 0], [W, 0], [W, Hh], [0, Hh]],
                    [[380, -260], [2650, 260], [2650, 1100], [380, 1640]])
    rows = 46
    ind = 0
    segs, Is, hs = [], [], []
    hot = 22
    for r in range(rows):
        ind = int(np.clip(ind + rng.choice([-1, 0, 0, 1]), 0, 5))
        if rng.random() < 0.1:
            continue
        v = 30 + r * 31.5
        u = 40 + ind * 70
        for _ in range(rng.integers(3, 9)):
            ln = rng.uniform(30, 210)
            if u + ln > W - 40:
                break
            segs.append([[u, v], [u + ln, v]])
            boost = 7.0 if r == hot else (1.6 if abs(r - hot) == 1 else 1.0)
            # round 2: high-key card: the whole page is lit, brighter towards the flawed line
            Is.append(lognormal_int(rng, 1, 0.46, 0.45)[0] * boost * (0.7 + 1.6 * np.exp(-abs(r - hot) / 6)))
            hs.append(0.03 if r == hot else rng.uniform(0.4, 0.95) - 0.3 * np.exp(-abs(r - hot) / 5))
            u += ln + rng.uniform(14, 26)
    segs = np.array(segs)
    M = 18
    s = np.linspace(0, 1, M)
    Pp = segs[:, :1, :] + (segs[:, 1:, :] - segs[:, :1, :]) * s[None, :, None]
    P, wz = apply_h(Hm, Pp)
    ufocus, vfocus = 620.0, 30 + hot * 31.5
    dist = np.sqrt(np.maximum(0, np.abs(Pp[..., 0] - ufocus) - 140) ** 2 + (0.6 * (Pp[..., 1] - vfocus)) ** 2)
    B = 0.5 + dist * 0.03
    prof = envelope(s, 0.06, 0.06)[None] * np.ones((len(segs), 1))
    I = np.array(Is) * (1 + B[:, 0] / 8) ** 0.4
    trails(cv, P, I, np.array(hs)[:, None] * np.ones((1, M)), B, rng, env=None, speed=0.1, prof=prof)
    # glow over the flawed line
    hp = np.array([[40, vfocus], [W - 40, vfocus]])
    q = hp[:1] + (hp[1:] - hp[:1]) * np.linspace(0, 1, 200)[:, None]
    Q, _ = apply_h(Hm, q)
    cv.polylines(Q[None], (0.35 * envelope(np.linspace(0, 1, 200), 0.3, 0.5))[None], ramp(0.4), 14)
    cv.polylines(Q[None], (0.22 * envelope(np.linspace(0, 1, 200), 0.3, 0.5))[None], ramp(0.6), 44)
    fp, _ = apply_h(Hm, np.array([[ufocus + 200, vfocus]]))
    glow(cv, fp[0], 26000.0, 420, 0.35, n=8000, seed=2)
    # light from behind the page washes over it (lit air in front of a bright screen)
    for k, (uu, vv, e) in enumerate(((900.0, 300.0, 30000.0), (1500.0, 1100.0, 26000.0), (500.0, 1200.0, 18000.0),
                                     (1300.0, 700.0, 30000.0))):
        q, _ = apply_h(Hm, np.array([[uu, vv]]))
        glow(cv, q[0], e, 420, 0.55, n=7000, seed=5 + k)
    motes(cv, 18, (900, 0, 2400, 1350), energy=(0.02, 0.06), blur=(20, 70), seed=12)
    return dict(exposure=1.3, bloom=0.15, halation=0.09, vignette=0.42, atmos=0.04)


@scene("domain-data", R169, "Coverage: Data protection (high-key card)",
       "A bright stream of light crosses the frame above a dark, glossy floor that holds its copy: a softer reflection broken into ripples. Every byte has a backup.")
def domain_data(cv):
    rng = np.random.default_rng(121)
    # round 2: high-key card. Backups as a photograph: a bright stream of light crosses the frame above
    # a dark, glossy floor, and the floor holds its copy, a softer reflection broken into ripples.
    # The horizon between the two stays darker (the domain hero's title sits there).
    hz = 650.0
    ctrl = np.array([[-300.0, 560.0], [600.0, 260.0], [1500.0, 660.0], [2700.0, 360.0]])
    W2 = lambda t: 0.65 + 0.7 * np.sin(np.pi * t) ** 1.5
    sp = ribbon(cv, ctrl, n=480, width=95, twist=1.4, twist_phase=0.3, wob=0.2, inten=0.085, isig=0.8,
                hue=(0.0, 0.5), blur=lambda u, r: 0.5 + 10.0 * np.abs(u) ** 2.2, tjit=0.2, env=(0.15, 0.15),
                spread_profile=W2, seed=31, speed_mod=0.45)
    ribbon(cv, ctrl + np.array([[0, -40], [0, -60], [0, -30], [0, -50]]), n=120, width=220, twist=0.4, wob=0.35,
           inten=0.05, isig=0.6, hue=(0.25, 0.8), blur=(18, 60), tjit=0.3, env=(0.2, 0.2), spread_profile=W2, seed=32)
    # the reflection: the same stream mirrored in the floor, softer, broken into horizontal ripples
    spine = sp["spine"]
    k = 9000
    j = rng.integers(0, len(spine), k)
    tj = j / (len(spine) - 1)
    nrm = normals(spine)[j]
    off = rng.normal(0, 1, (k, 1)) * 95 * W2(tj)[:, None] * 0.8
    src = spine[j] + nrm * off
    ry = 2 * hz - src[:, 1] + rng.normal(0, 18, k) + (2 * hz - src[:, 1] - hz) * rng.uniform(0.0, 0.5, k)
    rx = src[:, 0] + rng.normal(0, 10, k)
    fade = np.exp(-(ry - hz) / 520) * envelope(np.clip(tj, 0, 1), 0.15, 0.15)
    swarm_streaks(cv, np.c_[rx, ry], np.c_[np.ones(k), rng.normal(0, 0.02, k)], rng.uniform(20, 160, k),
                  lognormal_int(rng, k, 0.045, 0.6) * fade, np.clip(rng.uniform(0.15, 0.85, k), 0, 1),
                  np.where(rng.random(k) < 0.5, rng.uniform(4, 30, k), rng.uniform(0.6, 2.0, k)))
    # long soft vertical smears under the brightest part (light on a wet floor)
    k = 160
    xs = rng.uniform(300, 2300, k)
    tt = np.clip((xs + 300) / 3000, 0, 1)
    top = hz + rng.uniform(10, 60, k)
    P = np.stack([np.c_[xs, top], np.c_[xs + rng.normal(0, 6, k), top + rng.uniform(150, 520, k)]], 1)
    cv.polylines(P, (lognormal_int(rng, k, 0.035, 0.5) * np.exp(-((tt - 0.5) / 0.3) ** 2))[:, None] * np.array([[1.0, 0.0]]),
                 ramp(rng.uniform(0.3, 0.8, k)), rng.uniform(10, 40, k))
    # the floor edge and the lit air
    xs = np.linspace(-100, 2500, 400)
    cv.polylines(np.c_[xs, np.full(400, hz)][None], (0.03 * np.exp(-((xs - 1300) / 900) ** 2))[None], ramp(0.5), 6)
    glow(cv, (1300.0, 470.0), 18000.0, 360, 0.35, n=9000, seed=9)
    glow(cv, (1300.0, 860.0), 12000.0, 420, 0.5, n=8000, seed=10)
    motes(cv, 22, (0, 0, 2400, 1350), energy=(0.01, 0.06), blur=(20, 70), seed=13)
    return dict(exposure=1.2, bloom=0.14, halation=0.09, vignette=0.42, atmos=0.03)


@scene("domain-ai-agents", R169, "Coverage: AI and agent security",
       "A murmuration of light: tens of thousands of tiny agents fly as one folded sheet arcing over the upper half of the frame and down its right side, burning warm white where the sheet turns edge-on; two small rogue clusters fly against the flow. The title area and the top-left corner stay dark navy.")
def domain_ai_agents(cv):
    # Round 3: the old frame was a faint dust smear (mean 23). A starling murmuration is a thin 3D
    # sheet of birds: where the sheet turns edge-on to the camera its birds pile up into dense,
    # bright folds, where it faces the camera it thins to a veil. Sampling a twisted sheet evenly
    # and projecting it gives exactly that, so the swarm reads as one legible, living shape
    # (distinct from threat-swarm's vortex). The mass arcs over the upper half and down the right third;
    # the title (centre), the bottom-left and the card's top-left label band stay on dim navy.
    rng = np.random.default_rng(1310)
    fld = SinField(rng, n=9, wavelength=520, spread=0.5)
    holes = SinField(rng, n=7, wavelength=380, spread=0.5)

    def sheet(ctrl, n, width, twist, phase, inten, bend, zscale, hue_hot=(0.0, 0.25), hue_lo=(0.5, 0.95),
              length=(7, 16), seed=0, blur_far=10.0, wtaper=lambda u: 0.55 + 0.45 * np.sin(np.pi * u) ** 0.7,
              veil=None):
        r = np.random.default_rng(seed)
        u = r.uniform(0, 1, n)
        v = np.tanh(r.normal(0, 0.9, n))                      # soft edges, denser in the middle
        stray = r.uniform(0, 1, n) < 0.07                     # stragglers scattered around the edges
        v = np.where(stray, r.uniform(-1.7, 1.7, n), v)
        sp = bezier(ctrl, u)
        tg = bezier_deriv(ctrl, u)
        tg /= np.linalg.norm(tg, axis=-1, keepdims=True)
        nr = np.stack([-tg[..., 1], tg[..., 0]], -1)
        th = np.pi * (phase + twist * u) + 0.35 * np.sin(2 * np.pi * (1.3 * u + 0.2))
        W = width * wtaper(u) * (1 + 0.25 * fld.scalar(sp[:, 0], sp[:, 1]))
        c = np.cos(th)
        off_n = v * W * c + bend * W * (v ** 2 - 0.3)       # the sheet also curls, so folds are curved
        z = v * W * np.sin(th) * zscale
        p = sp + nr * off_n[:, None]
        # turbulence inside the flock: small drifts that keep it from looking drawn
        dx, dy = fld.curl(p[:, 0], p[:, 1])
        p = p + 22 * np.c_[dx, dy] / (np.sqrt(dx * dx + dy * dy)[:, None] + 1e-6) * r.normal(0, 1, (n, 1))
        # density holes and gaps, like the gaps that open and close inside a real murmuration
        keep = r.uniform(0, 1, n) < np.clip(0.55 + 0.6 * holes.scalar(p[:, 0], p[:, 1]), 0.08, 1)
        p, tg, z, c, v = p[keep], tg[keep], z[keep], c[keep], v[keep]
        m = len(p)
        # each agent flies along the flock, with its own small heading error
        ang = r.normal(0, 0.18, m)
        ca, sa = np.cos(ang), np.sin(ang)
        vel = np.c_[tg[:, 0] * ca - tg[:, 1] * sa, tg[:, 0] * sa + tg[:, 1] * ca]
        edge_on = 1 - np.abs(c)                                # 1 where the sheet is seen edge-on
        blur = np.minimum(0.5 + np.abs(z) * 0.03 + np.maximum(z, 0) * 0.02, blur_far)
        ln = r.uniform(*length, m) * (0.8 + 0.5 * edge_on)
        it = lognormal_int(r, m, inten, 0.55) * (0.32 + 1.5 * edge_on ** 1.5)
        if veil is not None:
            it = it * veil(p)
        hot = r.uniform(0, 1, m) < 0.25 + 0.5 * edge_on ** 2
        hue = np.where(hot, r.uniform(*hue_hot, m), r.uniform(*hue_lo, m))
        swarm_streaks(cv, p, vel, ln, it, hue, blur, curve=r.normal(0, 0.004, m))
        return p

    # The main flock: in from the upper left, across the top, banking down the right side.
    # Where it crosses the top left of the card crop (the card's label sits there) the flock thins to a veil.
    def veil(xy):
        x, y = xy[:, 0], xy[:, 1]
        return 1 - 0.8 * np.exp(-((x - 900) / 420) ** 2 - (np.maximum(y, 0) / 190) ** 2)
    main = np.array([[360, 560], [1250, 170], [2380, 160], [2130, 1230]])
    sheet(main, 170000, 330, twist=1.85, phase=0.32, inten=0.19, bend=0.35, zscale=1.0, seed=1, veil=veil)
    # A second, thinner layer just behind it, offset, so the folds overlap in depth.
    back = np.array([[640, 380], [1520, 170], [2520, 380], [2290, 1100]])
    sheet(back, 70000, 240, twist=2.4, phase=0.9, inten=0.085, bend=-0.3, zscale=1.4, seed=2,
          hue_lo=(0.5, 0.95), blur_far=14, veil=veil)
    # A far, soft flock high on the left: depth, out of focus.
    far = np.array([[-80, 190], [180, 40], [520, 60], [760, 170]])
    sheet(far, 14000, 120, twist=1.2, phase=0.6, inten=0.02, bend=0.2, zscale=1.0, seed=3,
          hue_lo=(0.55, 1.0), length=(6, 12), blur_far=4)

    # Rogue agents: two small hijacked clusters break away and fly against the flow, hotter than the flock.
    for (cx, cy, hd, nn, sd) in ((1960, 640, np.pi + 0.35, 260, 5), (1500, 250, 0.55, 160, 6)):
        r = np.random.default_rng(sd)
        dvec = np.array([np.cos(hd), np.sin(hd)])
        nvec = np.array([-dvec[1], dvec[0]])
        a_ = r.normal(0, 1, nn) ** 3 * 18 + r.normal(0, 30, nn)   # strung out along the heading
        b_ = r.normal(0, 9, nn)
        xy = np.array([cx, cy]) + a_[:, None] * dvec + b_[:, None] * nvec
        vel = np.tile(dvec, (nn, 1)) + r.normal(0, 0.08, (nn, 2))
        swarm_streaks(cv, xy, vel, r.uniform(18, 40, nn), lognormal_int(r, nn, 0.16, 0.5),
                      r.uniform(0.0, 0.18, nn), 0.5, curve=r.normal(0, 0.003, nn))

    motes(cv, 16, (1300, 0, 2400, 1350), energy=(0.01, 0.05), blur=(20, 60), seed=24)

    def calm(xy):
        # keep the title zone clear of slate dust
        x, y = xy[:, 0] / 2400, xy[:, 1] / 1350
        return 1 - 0.85 * np.exp(-((x - 0.5) / 0.22) ** 2 - ((y - 0.55) / 0.2) ** 2)
    return dict(exposure=1.6, bloom=0.12, halation=0.08, vignette=0.40, atmos=0.05, vibrance=0.7, slate_weight=calm)


@scene("domain-ot-iot", R169, "Coverage: OT and IoT security",
       "Long-exposure arcs of rotating machinery around a glowing axis inside the frame, dense and layered in depth, some blinking like sensors.")
def domain_ot_iot(cv):
    rng = np.random.default_rng(142)
    # round 2: the axis moves into the card (the tile crop missed it), more arcs, a lit core
    c = np.array([1640.0, 1020.0])
    n = 1500
    r = np.sqrt(rng.uniform(0.003, 1, n)) * 2300
    th0 = rng.uniform(np.pi * 0.70, np.pi * 1.75, n)
    span = rng.uniform(0.08, 0.75, n)
    M = 200
    s = np.linspace(0, 1, M)
    th = th0[:, None] + span[:, None] * s[None]
    P = np.stack([c[0] + r[:, None] * np.cos(th), c[1] + r[:, None] * np.sin(th)], -1)
    depth = rng.random(n)
    blur = np.where(depth < 0.25, 4 + 50 * (0.25 - depth) / 0.25, rng.uniform(0.5, 1.0, n))
    inten = lognormal_int(rng, n, 0.10, 0.75) * (1 + blur / 6) ** 0.5 * (0.6 + 0.8 * np.exp(-r / 900))
    hue = np.clip(0.15 + 0.8 * (r / 2500) ** 0.7 + rng.normal(0, 0.12, n), 0, 1)
    dashed = rng.random(n) < 0.2
    L = r[:, None] * span[:, None] * s[None]
    fq = rng.uniform(25, 70, n)[:, None]
    sg = (L / fq) % 1.0
    prof = np.where(dashed[:, None], 0.15 + 0.85 * (sg < 0.4), 1.0)
    # the headline corner (bottom-left) stays calmer
    calm = 1 - 0.55 * (1 - smoothstep(300, 1000, P[..., 0])) * smoothstep(800, 1200, P[..., 1])
    trails(cv, P, inten, hue[:, None] * np.ones((1, M)), blur, rng, env=(0.06, 0.06), prof=prof * calm)
    glow(cv, c, 15000.0, 420, 0.4, n=8000, seed=3)
    glow(cv, c, 900.0, 50, 0.1, n=5000, seed=5)
    glow(cv, (c[0] - 400, c[1] - 320), 9000.0, 320, 0.5, n=6000, seed=4)
    motes(cv, 24, (300, 0, 2400, 1350), energy=(0.02, 0.08), blur=(20, 80), seed=14)
    # round 4 (QA C5): wider rings. The machinery now turns all the way round under the axis too, so the lower
    # third (under the centred hero title) carries arcs instead of empty navy. The arcs above are unchanged.
    r4 = np.random.default_rng(1424)
    n2 = OT_LOW
    r = np.sqrt(r4.uniform(0.01, 1, n2)) * 1700
    th0 = r4.uniform(-0.05 * np.pi, 0.80 * np.pi, n2)
    span = r4.uniform(0.08, 0.6, n2)
    th = th0[:, None] + span[:, None] * s[None]
    P = np.stack([c[0] + r[:, None] * np.cos(th), c[1] + r[:, None] * np.sin(th)], -1)
    depth = r4.random(n2)
    blur = np.where(depth < 0.3, 4 + 46 * (0.3 - depth) / 0.3, r4.uniform(0.5, 1.0, n2))
    inten = lognormal_int(r4, n2, 0.10, 0.75) * (1 + blur / 6) ** 0.5 * (0.6 + 0.8 * np.exp(-r / 900)) * OT_LOW_I
    hue = np.clip(0.15 + 0.8 * (r / 2500) ** 0.7 + r4.normal(0, 0.12, n2), 0, 1)
    dashed = r4.random(n2) < 0.2
    L = r[:, None] * span[:, None] * s[None]
    sg = (L / r4.uniform(25, 70, n2)[:, None]) % 1.0
    prof = np.where(dashed[:, None], 0.15 + 0.85 * (sg < 0.4), 1.0)
    trails(cv, P, inten, hue[:, None] * np.ones((1, M)), blur, r4, env=(0.06, 0.06), prof=prof)
    glow(cv, (c[0] - 300, c[1] + 120), OT_HAZE, 460, 0.45, n=8000, seed=6)
    return dict(exposure=OT_EXP, bloom=0.13, halation=0.08, vignette=0.45, atmos=0.04)


OT_LOW, OT_LOW_I, OT_HAZE, OT_EXP = 1000, 1.0, 14000.0, 1.35


@scene("domain-governance", R169, "Coverage: Governance, risk and compliance (high-key card)",
       "A ruled floor falling away to the horizon, flooded by one wide, warm beam that lights the rules it crosses and the haze above them.")
def domain_governance(cv):
    rng = np.random.default_rng(151)
    f, cx, cy, h = 1150.0, 1640.0, 360.0, 1.4
    Zf = 7.0

    def proj(X, Z):
        X, Z = np.broadcast_arrays(np.asarray(X, float), np.asarray(Z, float))
        return np.stack([cx + f * X / Z, cy + f * h / Z], -1)

    def dof(Z):
        return 0.5 + 60 * np.abs(1 / Z - 1 / Zf)

    fade = lambda P: smoothstep(-0.1, 1, (P[..., 0] - 450) / 1300)
    M = 300
    Zs = np.geomspace(1.0, 120, M)
    Xs = np.arange(-16, 17, 1.0)
    P = proj(Xs[:, None], Zs[None])
    I = 0.065 * (Zs[None] / 7) ** -0.2 * fade(P) * envelope(np.linspace(0, 1, M), 0.0001, 0.3)[None]
    trails(cv, P, np.ones(len(Xs)), np.full((len(Xs), M), 0.55), dof(Zs)[None] * np.ones((len(Xs), 1)),
           rng, env=None, speed=0, prof=I)
    Zt = np.r_[np.arange(1.5, 12, 1.0), np.arange(12, 60, 2.0)]
    X = np.linspace(-16, 16, 400)
    P = proj(X[None], Zt[:, None])
    I = 0.055 * (Zt[:, None] / 7) ** -0.2 * fade(P)
    trails(cv, P, np.ones(len(Zt)), np.full((len(Zt), 400), 0.55), dof(Zt)[:, None] * np.ones((1, 400)),
           rng, env=None, speed=0, prof=I)
    # sweeping beam: longitudinal rules lit in a band, smeared behind the leading edge
    # round 2: high-key card: a much wider, brighter beam floods the floor
    k = 300
    Xb = 0.6 - rng.uniform(0, 1, k) ** 1.2 * 9.0
    lead = np.exp(-(0.6 - Xb) / 2.2)
    P = proj(Xb[:, None], Zs[None])
    I = (0.04 + 0.42 * lead)[:, None] * (Zs[None] / 7) ** -0.35 * envelope(np.linspace(0, 1, M), 0.0001, 0.35)[None]
    trails(cv, P, np.ones(k), (0.05 + 0.8 * (1 - lead))[:, None] * np.ones((1, M)),
           dof(Zs)[None] * np.ones((k, 1)), rng, env=None, speed=0.15, prof=I)
    # crossings light up under the beam
    XX, ZZ = np.meshgrid(np.arange(-8, 1, 1.0), Zt[Zt < 40])
    q = proj(XX.ravel(), ZZ.ravel())
    w = np.exp(-(0.6 - XX.ravel()) / 2.4) * (ZZ.ravel() / 7) ** -0.5
    cv.points(q, 2.5 * w, ramp(0.1), dof(ZZ.ravel()))
    # the beam lights the haze over the floor, brightest towards the horizon
    for k2, (X, Z, e, sg) in enumerate(((-1.5, 18.0, 22000.0, 340), (-3.0, 6.0, 20000.0, 480))):
        glow(cv, proj(X, Z), e, sg, 0.35, n=8000, seed=20 + k2)
    return dict(exposure=1.2, bloom=0.14, halation=0.09, vignette=0.42, atmos=0.04)



# ---------------------------------------------------------------------------
# SERVICES (4:3)


@scene("service-1", R43, "Services 001 Deploy and connect",
       "One beam enters from the left and branches into a delta of fine filaments reaching every corner; two more deltas glow out of focus behind it, so the whole frame is wired.")
def service_deploy(cv):
    # Round 3: the single sharp delta read like a vector tree on an empty field (91% near-black).
    # Now three deltas in depth: the sharp one in front, two larger, defocused ones behind it (like
    # out-of-focus fibre bundles), lit haze around the trunks and burning tips where they connect.
    def delta(seed, origin, d0, length, inten, blur_extra, hue_bias, spread=120.0, tips=0.25, depth_max=6):
        rng = np.random.default_rng(seed)
        leaves = []

        def grow(path, d, length, depth):
            p = path[-1]
            if depth == depth_max:
                leaves.append(np.array(path))
                return
            kids = 2 if depth < 1 else int(rng.choice([2, 2, 3]))
            angs = np.sort(rng.uniform(-0.55, 0.55, kids)) if kids > 1 else [0.0]
            if kids == 2:
                angs = np.array([-1, 1]) * rng.uniform(0.18, 0.45)
            for a in angs:
                a = a * (0.6 if depth == 0 else 1)
                nd = np.array([d[0] * np.cos(a) - d[1] * np.sin(a), d[0] * np.sin(a) + d[1] * np.cos(a)])
                nd[0] = max(nd[0], 0.35)
                nd /= np.linalg.norm(nd)
                ln = length * rng.uniform(0.62, 0.82)
                e = p + nd * ln
                ctrl = np.array([p, p + d * ln / 3, e - nd * ln / 3, e])
                seg = bezier(ctrl, np.linspace(0, 1, 40))[1:]
                grow(path + [q for q in seg], nd, ln, depth + 1)

        grow([np.array(origin, float)], np.array(d0, float) / np.linalg.norm(d0), length, 0)
        L = max(len(lf) for lf in leaves)
        nl = len(leaves)
        leaves.sort(key=lambda a: a[-1, 1])
        base = np.array([np.vstack([lf, np.repeat(lf[-1:], L - len(lf), 0)]) for lf in leaves])
        M = L
        sv = np.linspace(0, 1, M)
        nr = normals(base)
        lane = (np.arange(nl) / (nl - 1) - 0.5)
        strands = 4
        P, I, H, B = [], [], [], []
        for k in range(strands):
            off = (lane[:, None] * spread * (1 - sv[None]) ** 2.2 + rng.normal(0, 2.5, (nl, 1)) * (1 - sv[None])
                   + rng.normal(0, 1.2, (nl, 1)))
            P.append(base + nr * off[..., None])
            I.append(lognormal_int(rng, nl, inten, 0.5))
            H.append(rng.uniform(0.0, 0.8, nl))
            B.append(np.where(rng.random(nl) < 0.15, rng.uniform(3, 12, nl), rng.uniform(0.5, 1.0, nl)) + blur_extra)
        P = np.concatenate(P)
        lenmask = np.concatenate([np.array([np.r_[np.ones(len(lf)), np.zeros(L - len(lf))] for lf in leaves])] * strands)
        prof = lenmask * (1 - smoothstep(0.7, 1.0, np.cumsum(lenmask, 1) / lenmask.sum(1, keepdims=True)))
        hue = np.concatenate(H)[:, None] * 0.4 + 0.6 * sv[None] * np.ones((len(P), 1))
        trails(cv, P, np.concatenate(I), np.clip(hue + hue_bias, 0, 1), np.concatenate(B), rng, env=(0.06, 0.0), prof=prof)
        tp = np.array([lf[-1] for lf in leaves])
        bt = rng.uniform(0.5, 6, nl) + blur_extra
        cv.points(tp, lognormal_int(rng, nl, tips, 0.5) * (1 + (bt / 6) ** 2 * 0.25), ramp(rng.uniform(0.2, 0.9, nl)), bt)
        return base

    # behind: two big, soft deltas (out of focus, dimmer, warmer)
    delta(171, (-260, 380), (1.0, 0.10), 1150.0, 0.018, 24.0, 0.3, spread=160, tips=0.35)
    delta(172, (-200, 1500), (1.0, -0.22), 1000.0, 0.014, 40.0, 0.35, spread=150, tips=0.35)
    # in front: the sharp one, as before
    delta(161, (-160, 940), (1.0, -0.02), 900.0, 0.080, 0.0, 0.0, spread=120, tips=0.3)
    # lit haze along the trunk where the beam enters
    glow(cv, (260.0, 930.0), 9000.0, 300, 0.45, n=6000, seed=31)
    glow(cv, (900.0, 760.0), 7000.0, 520, 0.6, n=6000, seed=32)
    motes(cv, 18, (600, 0, 2400, 1800), energy=(0.01, 0.05), blur=(20, 70), seed=15)
    return dict(exposure=1.15, bloom=0.12, halation=0.08, vignette=0.42, atmos=0.05)


@scene("service-2", R43, "Services 002 Detect 24/7 (high-key card)",
       "A broad river of soft-focus light drifts through the whole frame in every focus plane; one sharp trail moves against the grain and lights up.")
def service_detect(cv):
    rng = np.random.default_rng(172)
    fld = SinField(rng, n=7, wavelength=1300)
    # round 2: high-key card (the bright one of its row), lit like the CTA band: a broad river of
    # soft-focus light drifts through the whole frame; one sharp trail moves against the grain.
    W2 = lambda t: 0.75 + 0.5 * np.sin(np.pi * t)
    for ctrl, n, wdt, inten, hue, blur, sd in (
            (np.array([[-300.0, 760.0], [700.0, 620.0], [1600.0, 700.0], [2700.0, 470.0]]), 420, 330, 0.085, (0.0, 0.5), (4, 40), 11),
            (np.array([[-300.0, 1260.0], [800.0, 1180.0], [1700.0, 1240.0], [2700.0, 1020.0]]), 260, 300, 0.06, (0.3, 0.85), (10, 70), 12),
            (np.array([[-300.0, 260.0], [900.0, 200.0], [1500.0, 300.0], [2700.0, 120.0]]), 160, 260, 0.05, (0.35, 0.9), (20, 90), 13)):
        ribbon(cv, ctrl, n=n, width=wdt, twist=0.3, wob=0.35, inten=inten, isig=0.7, hue=hue, blur=blur, tjit=0.35,
               env=(0.2, 0.2), spread_profile=W2, seed=sd, speed_mod=0.5)
    # a layer of crisp drifting streaks for texture, every focus plane
    n = 2200
    x = rng.uniform(-250, 2650, n)
    y = 760 + rng.normal(0, 1, n) * 560
    depth = rng.random(n)
    blur = np.where(depth < 0.35, 6 + 60 * (0.35 - depth) / 0.35, 0.5 + 6 * (depth - 0.35) ** 2)
    ln = rng.uniform(50, 420, n) * (1.6 - depth)
    M = 24
    s = np.linspace(-0.5, 0.5, M)
    vx, vy = fld.curl(x, y)
    ang = np.deg2rad(-7) + 0.3 * vx
    P = np.stack([x[:, None] + np.cos(ang)[:, None] * ln[:, None] * s[None],
                  y[:, None] + np.sin(ang)[:, None] * ln[:, None] * s[None]], -1)
    inten = lognormal_int(rng, n, 0.05, 0.65) * (1 + blur / 5) ** 0.55
    trails(cv, P, inten, np.clip(0.2 + 0.6 * depth + rng.normal(0, 0.1, n), 0, 1), blur, rng, env=(0.3, 0.3))
    # the anomaly: against the grain, through the middle of the frame
    ctrl = np.array([[2050.0, 1750.0], [1800.0, 1300.0], [1450.0, 880.0], [950.0, 560.0]])
    along = lambda t: 0.25 + 0.75 * t ** 1.4
    ribbon(cv, ctrl, n=40, width=7, inten=0.5, isig=0.4, hue=(0.0, 0.15), blur=(0.5, 0.9), tjit=0.03,
           env=(0.3, 0.02), seed=3, along=along)
    ribbon(cv, ctrl, n=8, width=12, inten=0.25, hue=(0.25, 0.55), blur=(8, 14), tjit=0.02, env=(0.3, 0.02), seed=4, along=along)
    cv.points(np.array([[950.0, 560.0]]), 14.0, ramp(0.0), 1.2)
    glow(cv, (950.0, 560.0), 400.0, 30, 0.2, n=4000)
    glow(cv, (1200.0, 700.0), 30000.0, 480, 0.25, n=9000, seed=2)
    motes(cv, 30, (0, 0, 2400, 1800), energy=(0.02, 0.10), blur=(30, 110), hue=(0.3, 0.9), seed=17)
    return dict(exposure=1.25, bloom=0.14, halation=0.09, vignette=0.45, atmos=0.06)


@scene("service-3", R43, "Services 003 Respond (high-key card)",
       "A hard line of light cuts across the frame and blows the light around it into two wide fans of sparks flying away from the cut, the air between them lit.")
def service_respond(cv):
    rng = np.random.default_rng(181)
    A, B = np.array([250.0, 1900.0]), np.array([2500.0, 180.0])
    d = (B - A) / np.linalg.norm(B - A)
    nr = np.array([-d[1], d[0]])
    # round 2: high-key card. The cut blows the cluster into two big, soft lobes of light, one on each
    # side of the line (out of focus, so they read as glowing masses, like the CTA band), with sharp
    # sparks flying out of them. A thin dark lane runs right along the cut.
    def blast(n, along_sd, off_mu, off_sd, blur, ln, inten, hue, seed):
        r = np.random.default_rng(seed)
        side = r.choice([-1.0, 1.0], n)
        t = r.normal(0.52, along_sd, n)
        off = side * np.abs(r.normal(off_mu, off_sd, n))
        p = A + (B - A) * t[:, None] + nr * off[:, None]
        # a coherent fan: sparks leave the cut perpendicular to it and splay out towards its ends
        dirv = side[:, None] * nr + d * (2.0 * (t - 0.52) + r.normal(0.15, 0.08, n))[:, None] + r.normal(0, 0.04, (n, 2))
        ad = np.abs(off)
        swarm_streaks(cv, p, dirv, r.uniform(*ln, n) * (0.6 + 0.8 * np.exp(-ad / 500)),
                      lognormal_int(r, n, inten, 0.6) * (0.4 + 1.2 * np.exp(-ad / 420)),
                      np.clip(hue[0] + (hue[1] - hue[0]) * smoothstep(80, 900, ad) + r.normal(0, 0.08, n), 0, 1),
                      r.uniform(*blur, n))
    blast(7000, 0.20, 260, 330, (0.5, 0.9), (40, 260), 0.075, (0.0, 0.85), 2)  # sharp sparks
    blast(1400, 0.22, 420, 360, (4, 18), (80, 360), 0.07, (0.2, 0.85), 1)       # a softer, nearer layer
    # the two lobes glow as smooth masses of lit air (no texture), hottest near the cut
    for k in range(8):
        t = 0.3 + 0.4 * k / 7
        for side in (-1, 1):
            q = A + (B - A) * t + nr * side * (260 + 60 * np.sin(k * 1.7))
            glow(cv, q, 6000.0 * np.exp(-((t - 0.52) / 0.2) ** 2), 240, 0.42, n=5000, seed=20 + 2 * k + (side > 0))
    ctrl = np.array([A, A + (B - A) / 3, A + 2 * (B - A) / 3, B])
    ribbon(cv, ctrl, n=60, width=4, inten=0.35, isig=0.4, hue=(0.0, 0.2), blur=(0.5, 0.8), tjit=0.02,
           env=(0.06, 0.06), seed=5, wob=0.08)
    ribbon(cv, ctrl, n=8, width=8, inten=0.3, hue=(0.3, 0.6), blur=(8, 12), tjit=0.02, seed=6)
    for k, (t, side, e) in enumerate(((0.45, 1, 30000.0), (0.6, -1, 30000.0))):
        glow(cv, A + (B - A) * t + nr * side * 360, e, 360, 0.5, n=8000, seed=3 + k)
    motes(cv, 24, (0, 0, 2400, 1800), energy=(0.02, 0.08), blur=(20, 90), seed=16)
    return dict(exposure=1.15, bloom=0.14, halation=0.09, vignette=0.42, atmos=0.06)


@scene("service-4", R43, "Services 004 Attack (red team)",
       "Hundreds of curving trails sweep in from every side and converge on one ringed target, which glows in the haze.")
def service_attack(cv):
    rng = np.random.default_rng(191)
    T = np.array([1380.0, 860.0])
    n = 640
    a = rng.uniform(0, 2 * np.pi, n)
    R = rng.uniform(1400, 2600, n)
    S = T + np.c_[np.cos(a), np.sin(a)] * R[:, None]
    rend = rng.uniform(30, 240, n)
    tw = rng.normal(0.9, 0.35, n)
    E = T + np.c_[np.cos(a + tw * 0.15), np.sin(a + tw * 0.15)] * rend[:, None]
    c1 = T + np.c_[np.cos(a + tw), np.sin(a + tw)] * (R * 0.55)[:, None]
    c2 = T + np.c_[np.cos(a + tw * 0.5), np.sin(a + tw * 0.5)] * (R * 0.2)[:, None]
    ctrl = np.stack([S, c1, c2, E], 1)
    M = 260
    s = np.linspace(0, 1, M)
    P = bezier(ctrl, s)
    prof = (0.12 + 0.88 * s[None] ** 2.5) * (1 + 1.5 * (240 - rend[:, None]) / 240 * s[None] ** 6)
    blur = np.where(rng.random(n) < 0.2, rng.uniform(3, 20, n), rng.uniform(0.5, 0.9, n))
    hue = np.clip(0.9 - 0.8 * s[None] ** 3 + rng.normal(0, 0.05, (n, 1)), 0, 1)
    trails(cv, P, lognormal_int(rng, n, 0.09, 0.65), hue, blur, rng, env=(0.25, 0.02), prof=prof)
    th = np.linspace(0, 2 * np.pi, 1600)
    gap = np.ones_like(th)
    for q in range(4):
        dd = np.abs(np.angle(np.exp(1j * (th - q * np.pi / 2 - np.pi / 4))))
        gap *= smoothstep(0.03, 0.055, dd)
    for r, I0, bl in ((280, 0.30, 0.5), (284, 0.12, 0.5), (280, 0.12, 6)):
        cv.polylines(circle_pts(T, r, th)[None], (I0 * gap)[None], ramp(0.1), bl)
    cv.points(T[None], 9.0, ramp(0.0), 0.8)
    glow(cv, T, 8.0, 11, 0.5)
    glow(cv, T, 18000.0, 380, 0.45, n=8000, seed=9)
    glow(cv, T, 1200.0, 60, 0.1, n=5000, seed=10)
    motes(cv, 20, (0, 0, 2400, 1800), energy=(0.02, 0.06), blur=(20, 80), seed=25)
    return dict(exposure=1.0, bloom=0.12, halation=0.08, vignette=0.42, atmos=0.02)


@scene("service-5", R43, "Services 005 Harden",
       "Streams of light run into an unseen curved wall and slide along it: the wall shows only as the bright seam where they pile up, the space behind it stays calm.")
def service_harden(cv):
    rng = np.random.default_rng(202)
    C = np.array([2750.0, 950.0])
    R = 1300.0
    fld = SinField(rng, n=7, wavelength=900)

    def field(x, y):
        cx_, cy_ = fld.curl(x, y)
        vx = 1.0 + 0.35 * cx_
        vy = 0.10 + 0.35 * cy_
        dx, dy = x - C[0], y - C[1]
        rr = np.sqrt(dx * dx + dy * dy) + 1e-9
        nx, ny = dx / rr, dy / rr
        d = rr - R
        vn = vx * nx + vy * ny
        w = 1 - smoothstep(0, 160, d)
        k = np.where(vn < 0, vn, 0) * w * 1.15
        vx = vx - k * nx
        vy = vy - k * ny
        # slide away from the nearest point of the seam, up or down
        tx, ty = -ny, nx
        sgn = np.sign(dy + 1e-6)
        vx = vx + w * 0.6 * tx * sgn * -1
        vy = vy + w * 0.6 * ty * sgn * -1
        return vx, vy

    n = 2400
    st = np.c_[rng.uniform(-500, 1350, n), rng.normal(950, 650, n)]
    steps = 200
    P = flow_trails(cv, field, st, steps, h=6.0)
    dd = np.linalg.norm(P - C, axis=2) - R
    lens = rng.integers(25, 110, n)
    idx = np.arange(steps + 1)[None]
    tl = idx / lens[:, None]
    # comets: dim tail, bright head; the head lights up where it meets the wall
    prof = (tl <= 1) * (0.06 + 0.94 * np.clip(tl, 0, 1) ** 1.6) * (0.35 + 3.2 * np.exp(-np.maximum(dd, 0) / 60))
    prof = prof * smoothstep(-80, 0, dd)                 # nothing passes the wall
    depth = rng.random(n)
    blur = np.where(depth < 0.4, 4 + 60 * (0.4 - depth) / 0.4, rng.uniform(0.5, 0.9, n))
    hue = np.clip(0.75 - 0.6 * np.exp(-np.maximum(dd, 0) / 110) + rng.normal(0, 0.06, (n, 1)), 0, 1)
    trails(cv, P, lognormal_int(rng, n, 0.06, 0.65) * (1 + blur / 6) ** 0.5, hue, blur, rng, env=None, speed=0.25, prof=prof)
    # sparks thrown back off the wall
    k = 900
    tt = rng.uniform(np.pi * 0.72, np.pi * 1.28, k)
    p0 = np.c_[C[0] + R * np.cos(tt), C[1] + R * np.sin(tt)]
    nrm = -np.c_[np.cos(tt), np.sin(tt)]
    dirv = nrm + rng.normal(0, 0.5, (k, 2))
    dist = rng.exponential(90, k)
    swarm_streaks(cv, p0 + dirv * dist[:, None], dirv, rng.uniform(8, 60, k),
                  lognormal_int(rng, k, 0.10, 0.6) * np.exp(-((tt - np.pi) / 0.3) ** 2), rng.uniform(0.0, 0.6, k),
                  np.where(rng.random(k) < 0.3, rng.uniform(3, 14, k), 0.6))
    # the seam
    th = np.linspace(np.pi * 0.62, np.pi * 1.38, 900)
    seam = np.c_[C[0] + R * np.cos(th), C[1] + R * np.sin(th)]
    fall = np.exp(-((th - np.pi) / 0.33) ** 2)
    for I0, bl, h in ((0.30, 0.7, 0.0), (0.18, 10, 0.3), (0.12, 40, 0.5)):
        cv.polylines(seam[None], (I0 * (0.25 + 0.75 * fall))[None], ramp(h), bl)
    glow(cv, (C[0] - R + 40, C[1]), 14000.0, 360, 0.45, n=7000, seed=3)
    # round 3: lifted (it was the darkest card in the set, mean 21): more light in the stream and the air
    return dict(exposure=1.45, bloom=0.13, halation=0.08, vignette=0.45, atmos=0.06)


@scene("service-6", R43, "Services 006 Govern (high-key card)",
       "A broad stream of light, turbulent and out of focus on the left, settles into evenly spaced lanes and gathers into one calm, bright band with a warm-white core on the right.")
def service_govern(cv):
    rng = np.random.default_rng(211)
    # round 2: high-key card, lit like the CTA band. A broad stream of light is turbulent and
    # scattered on the left; towards the right every trail settles into its own lane and the stream
    # gathers into one calm, bright band (warm-white core) that crosses the frame.
    n = 520
    M = 700
    t = np.linspace(0, 1, M)
    x = -250 + t * 2950
    spine_y = 980 - 160 * smoothstep(0.0, 1.0, t)
    calm = smoothstep(0.30, 0.62, t)                              # 0 chaos ... 1 order
    u = np.sort(rng.uniform(-1, 1, n))                            # each trail's final lane
    lane = u * (210 + 90 * np.abs(u))                             # evenly spaced lanes, a little wider at the edges
    turb = wobble(rng, n, t * 3.2, terms=4, fmin=0.5, fmax=1.5) * 520 + wobble(rng, n, t * 8, terms=2) * 120
    spread = rng.normal(0, 1, n)[:, None] * 380
    y = spine_y[None] + (1 - calm)[None] * (turb + spread) + calm[None] * lane[:, None]
    P = np.stack([np.broadcast_to(x, (n, M)), y], -1)
    core = np.exp(-(u / 0.55) ** 2)
    inten = lognormal_int(rng, n, 0.07, 0.45) * (0.5 + 0.8 * core)
    prof = (0.35 + 0.65 * calm)[None] * envelope(t, 0.10, 0.02)[None]
    hue = np.clip(0.72 - calm[None] * (0.15 + 0.55 * core[:, None]) + rng.normal(0, 0.06, (n, 1)), 0, 1)
    # chaos falls out of focus, order is sharp
    bl0 = np.where(rng.random(n) < 0.55, rng.uniform(5, 45, n), rng.uniform(0.6, 2.0, n))
    B = bl0[:, None] * (1 - calm)[None] + 0.6 * calm[None]
    trails(cv, P, inten, hue, B, rng, env=None, speed=0.15, prof=prof)
    # a soft out-of-focus copy of the calm band (the glow of the gathered light)
    ctrl = np.array([[700.0, 860.0], [1300.0, 840.0], [1900.0, 830.0], [2700.0, 820.0]])
    ribbon(cv, ctrl, n=90, width=290, inten=0.05, isig=0.4, hue=(0.1, 0.6), blur=(24, 70), tjit=0.15,
           env=(0.35, 0.05), wob=0.05, seed=5)
    glow(cv, (1800.0, 840.0), 30000.0, 460, 0.25, n=9000, seed=3)
    glow(cv, (600.0, 950.0), 12000.0, 520, 0.6, n=8000, seed=4)
    motes(cv, 16, (0, 0, 2400, 1800), energy=(0.02, 0.06), blur=(20, 90), seed=18)
    return dict(exposure=1.2, bloom=0.14, halation=0.09, vignette=0.42, atmos=0.06)


# ---------------------------------------------------------------------------
# BANDS, THUMBS, ABOUT, CONTACT


@scene("cta", R169, "Closing CTA band, full bleed behind the centred heading",
       "A wide river of long-exposure light sweeps up through the centre: a hot warm-white core, soft out-of-focus streaks around it, lit haze.")
def cta(cv):
    rng = np.random.default_rng(223)
    ctrl = np.array([[-300.0, 1300.0], [650.0, 1160.0], [1200.0, 520.0], [2750.0, 330.0]])

    def fan(t):
        # gathered where it crosses the heading, opening wide towards the right like a flare
        return 0.45 + 0.5 * (1 - t) ** 2 + 1.9 * t ** 2.4

    # in-focus core: fine trails, hot towards warm white
    ribbon(cv, ctrl, n=560, width=170, twist=0.7, twist_phase=0.5, wob=0.22, inten=0.22, isig=0.85,
           hue=(0.0, 0.4), blur=lambda u, r: 0.5 + 12.0 * np.abs(u) ** 2.2, tjit=0.28, env=(0.22, 0.22),
           spread_profile=fan, seed=41, speed_mod=0.45)
    # mid depth: softer, wider
    ribbon(cv, ctrl + np.array([[0, 70], [0, 50], [0, -30], [0, -70]]), n=200, width=310, twist=0.4, wob=0.35,
           inten=0.09, isig=0.7, hue=(0.15, 0.85), blur=(5, 24), tjit=0.3, env=(0.25, 0.25), spread_profile=fan, seed=42)
    # foreground: far out of focus bands, the depth of a real lens
    ribbon(cv, ctrl + np.array([[0, 160], [0, 190], [0, 110], [0, 30]]), n=28, width=430, twist=0.2, wob=0.4,
           inten=0.09, isig=0.5, hue=(0.25, 0.9), blur=(45, 120), tjit=0.3, env=(0.3, 0.3), spread_profile=fan, seed=43)
    # sparks shed along the stream
    t = rng.uniform(0.15, 0.9, 320)
    sp = bezier(ctrl, t)
    tg = bezier_deriv(ctrl, t)
    tg = tg / np.linalg.norm(tg, axis=1, keepdims=True)
    nr = np.c_[-tg[:, 1], tg[:, 0]]
    off = rng.normal(0, 1, (320, 1)) * 200
    swarm_streaks(cv, sp + nr * off, tg + rng.normal(0, 0.2, (320, 2)), rng.uniform(20, 120, 320),
                  lognormal_int(rng, 320, 0.08, 0.6), rng.uniform(0.2, 0.9, 320),
                  np.where(rng.random(320) < 0.4, rng.uniform(4, 24, 320), 0.6))
    # a second, fainter pass crossing lower: the light was moved twice during the exposure
    ctrl2 = np.array([[-200.0, 1050.0], [700.0, 1000.0], [1500.0, 900.0], [2700.0, 1050.0]])
    ribbon(cv, ctrl2, n=200, width=150, twist=0.5, wob=0.3, inten=0.07, isig=0.7, hue=(0.3, 0.9),
           blur=lambda u, r: 2.0 + 30.0 * np.abs(u) ** 1.5, tjit=0.3, env=(0.3, 0.3), seed=44)
    # the air lit by the light: midtones behind the heading
    glow(cv, (1250.0, 720.0), 24000.0, 360, 0.35, n=9000, seed=3)
    glow(cv, (1250.0, 700.0), 9000.0, 200, 0.15, n=6000, seed=4)
    # light pooling low in the frame, under the buttons
    glow(cv, (1350.0, 1120.0), 9000.0, 320, 0.4, n=8000, seed=5)
    motes(cv, 40, (0, 0, 2400, 1350), energy=(0.02, 0.10), blur=(30, 110), hue=(0.4, 0.9), seed=19)
    return dict(exposure=1.35, bloom=0.14, halation=0.09, vignette=0.5, slate=0.6)


@scene("status", R11, "Hero status card thumbnail (small, 1:1)",
       "A hot point of light at the head of a long, curving exposure trail, glowing in soft haze. Reads at thumbnail size.")
def status(cv):
    rng = np.random.default_rng(232)
    head = np.array([1010.0, 700.0])
    ctrl = np.array([[-300.0, 1500.0], [500.0, 1700.0], [450.0, 900.0], head])

    def taper(t):
        return 0.06 + 0.94 * (1 - t) ** 1.1

    ribbon(cv, ctrl, n=340, width=180, twist=0.6, wob=0.2, inten=0.20, isig=0.7, hue=(0.0, 0.7),
           blur=lambda u, r: 0.5 + 16 * np.abs(u) ** 2, tjit=0.25, env=(0.35, 0.03), spread_profile=taper,
           along=lambda t: 0.25 + 0.75 * t ** 1.6, seed=51)
    ribbon(cv, ctrl, n=30, width=280, inten=0.07, hue=(0.3, 0.9), blur=(30, 80), tjit=0.3, env=(0.4, 0.05),
           spread_profile=taper, seed=52)
    cv.points(head[None], 220.0, ramp(0.0), 10)
    glow(cv, head, 1500.0, 40, 0.05, n=5000)
    glow(cv, head, 6000.0, 130, 0.2, n=6000, seed=2)
    glow(cv, head, 22000.0, 380, 0.45, n=8000, seed=1)
    return dict(exposure=1.05, bloom=0.14, halation=0.09, vignette=0.4, slate=0.3)


@scene("reel-poster", R169, "Reel frame poster (pill control sits bottom centre)",
       "A light-painted orb: hundreds of orbits traced by a spinning light, sparks flying off, centred.")
def reel_poster(cv):
    rng = np.random.default_rng(241)
    c = np.array([1200.0, 590.0])
    Rs = 450.0
    n = 900
    M = 360
    ax = rng.normal(0, 1, (n, 3))
    ax /= np.linalg.norm(ax, axis=1, keepdims=True)
    tmp = np.where(np.abs(ax[:, :1]) < 0.9, np.array([[1.0, 0, 0]]), np.array([[0, 1.0, 0]]))
    u = np.cross(ax, tmp)
    u /= np.linalg.norm(u, axis=1, keepdims=True)
    v = np.cross(ax, u)
    th0 = rng.uniform(0, 2 * np.pi, n)
    span = rng.uniform(1.0, 3.5, n)
    s = np.linspace(0, 1, M)
    th = th0[:, None] + span[:, None] * s[None]
    R = Rs * (1 + rng.normal(0, 0.012, n))[:, None]
    p3 = R[..., None] * (np.cos(th)[..., None] * u[:, None, :] + np.sin(th)[..., None] * v[:, None, :])
    x = c[0] + p3[..., 0]
    y = c[1] + p3[..., 1]
    z = p3[..., 2]
    B = 0.5 + np.maximum(0, z) / Rs * 10 + np.maximum(0, -z) / Rs * 1.0
    prof = (0.06 + 0.94 * s[None] ** 1.5) * (0.45 + 0.55 * (1 - z / Rs) / 2)
    inten = lognormal_int(rng, n, 0.042, 0.8)
    hue = rng.uniform(0.0, 0.75, n)[:, None] * np.ones((1, M))
    trails(cv, np.stack([x, y], -1), inten, hue, B, rng, env=(0.05, 0.02), prof=prof)
    k = 600
    j = rng.integers(0, n, k)
    i = rng.integers(M // 2, M - 1, k)
    pos = np.stack([x[j, i], y[j, i]], -1)
    tg = np.stack([x[j, i + 1] - x[j, i - 1], y[j, i + 1] - y[j, i - 1]], -1)
    out = pos - c
    dirv = tg / (np.linalg.norm(tg, axis=1, keepdims=True) + 1e-9) + 0.6 * out / (np.linalg.norm(out, axis=1, keepdims=True) + 1e-9)
    dist = rng.exponential(110, k)
    swarm_streaks(cv, pos + dirv * dist[:, None], dirv, rng.uniform(8, 70, k), lognormal_int(rng, k, 0.09, 0.6),
                  rng.uniform(0.3, 1.0, k), np.where(rng.random(k) < 0.3, rng.uniform(3, 16, k), 0.6))
    glow(cv, c, 60.0, 160, 0.4, n=4000)
    motes(cv, 24, (300, 0, 2100, 1350), energy=(0.01, 0.06), blur=(20, 80), seed=20)
    return dict(exposure=1.0, bloom=0.11, halation=0.07, vignette=0.45)


@scene("about-1", R43, "About: AI plus experts, one team",
       "Seen from a bridge in a long exposure: a warm-white stream and an amber stream of light run in from either side of a night road and merge into one lane towards a glowing horizon.")
def about_1(cv):
    rng = np.random.default_rng(252)
    f, cx, hy, Hc = 1000.0, 1250.0, 560.0, 5.5
    Zf = 11.0

    def proj(X, Y, Z):
        bend = 0.0009 * Z ** 2          # the road bends gently to the right
        return np.stack([cx + f * (X + bend) / Z, hy + f * (Hc - Y) / Z], -1)

    def dof(Z):
        return 0.5 + 80.0 * np.abs(1 / Z - 1 / Zf)

    M = 300
    s = np.linspace(0, 1, M)[None]
    for (x0, x1), hue_rng, n, (za, zb), i0 in (((-4.2, -0.2), (0.0, 0.3), 300, (3.5, 26.0), 0.10),
                                               ((4.6, 0.6), (0.5, 0.95), 300, (3.0, 30.0), 0.10)):
        Z0 = rng.uniform(2.4, 6.0, n)
        Z1 = Z0 * np.exp(rng.uniform(np.log(4), np.log(40), n))
        Z = Z0[:, None] * (Z1 / Z0)[:, None] ** s           # log spacing along depth
        lane = x0 + (x1 - x0) * smoothstep(za, zb, Z)
        X = lane + rng.normal(0, 0.25, (n, 1)) + rng.choice([-0.55, 0.55], (n, 1))
        Y = rng.uniform(0.5, 0.9, (n, 1)) * np.ones_like(Z)
        P = proj(X, Y, Z)
        B = dof(Z)
        inten = lognormal_int(rng, n, i0, 0.6)
        prof = envelope(s, 0.06, 0.3) * np.ones((n, 1))
        trails(cv, P, inten, rng.uniform(*hue_rng, n)[:, None] * np.ones((1, M)), B, rng, env=None, speed=0.35, prof=prof)
    # street lamps on both sides
    Zl = np.arange(3.0, 160, 4.5)
    for X in (-9.0, 10.0):
        p = proj(np.full_like(Zl, X), np.full_like(Zl, 9.0), Zl)
        cv.points(p, 1.2 * (1 + 0.1 * dof(Zl) ** 2) * (8 / Zl) ** 0.6, ramp(0.12), dof(Zl))
        q = proj(np.full_like(Zl, X * 0.7), np.full_like(Zl, 0.0), Zl)   # their pools of light on the road
        cv.points(q, 4.0 * (8 / Zl) ** 0.8, ramp(0.55), 20 + 600 / Zl)
    # city lights on the horizon
    k = 320
    hx = rng.normal(cx + 250, 700, k)
    cv.points(np.c_[hx, hy - np.abs(rng.normal(0, 22, k)) + 6], lognormal_int(rng, k, 0.5, 0.8),
              ramp(rng.uniform(0.1, 0.9, k)), rng.uniform(2, 10, k))
    glow(cv, (cx + 250, hy), 26000.0, 420, 0.45, n=8000, seed=5)
    glow(cv, (cx + 150, hy + 30), 5000.0, 130, 0.2, n=5000, seed=6)
    return dict(exposure=1.1, bloom=0.12, halation=0.08, vignette=0.45)


@scene("about-2", R43, "About: we go inside your company",
       "A long exposure from inside a moving tunnel: ceiling, wall and floor lights stretch into streaks that rush towards a bright opening.")
def about_2(cv):
    rng = np.random.default_rng(262)
    f, vx, vy = 760.0, 1480.0, 800.0
    Zf = 7.0
    HW, YT, YB = 2.3, 1.7, -1.3          # half width, ceiling, floor (camera at 0)

    def proj(X, Y, Z):
        return np.stack([vx + f * (X + 0.004 * Z ** 1.7) / Z, vy - f * (Y - 0.002 * Z ** 1.5) / Z], -1)

    def dof(Z):
        return 0.5 + 36.0 * np.abs(1 / Z - 1 / Zf)

    def perimeter(u):
        """u in [0,1) -> (X, Y) on a rounded tunnel section: ceiling, right wall, floor, left wall."""
        L = np.array([2 * HW, YT - YB, 2 * HW, YT - YB])
        c = np.cumsum(L) / L.sum()
        X = np.where(u < c[0], -HW + 2 * HW * u / c[0],
            np.where(u < c[1], HW, np.where(u < c[2], HW - 2 * HW * (u - c[1]) / (c[2] - c[1]), -HW)))
        Y = np.where(u < c[0], YT, np.where(u < c[1], YT - (YT - YB) * (u - c[0]) / (c[1] - c[0]),
            np.where(u < c[2], YB, YB + (YT - YB) * (u - c[2]) / (c[3] - c[2]))))
        return X, Y

    M = 180
    s = np.linspace(0, 1, M)[None]

    def streaks(X, Y, inten, hue, zr=(1.2, 110), run=(5, 16), near_z=(0.8, 5.0)):
        n = len(X)
        zl = np.exp(rng.uniform(np.log(zr[0]), np.log(zr[1]), n))
        Z0 = np.maximum(0.6, zl - rng.uniform(*run, n))
        Z = Z0[:, None] * (zl / Z0)[:, None] ** s
        P = proj(X[:, None], Y[:, None], Z)
        near = smoothstep(near_z[0], near_z[1], Z)                    # close to the lens the light smears out and dims
        trails(cv, P, inten, hue[:, None] * np.ones((1, M)), dof(Z), rng, env=(0.08, 0.08), speed=0.3, prof=near)

    # the surfaces: dim light all round the section, so the tube itself reads
    n = 12000
    X, Y = perimeter(rng.random(n))
    streaks(X, Y, lognormal_int(rng, n, 0.009, 0.8), rng.uniform(0.3, 1.0, n), zr=(0.9, 80), run=(2, 20), near_z=(0.5, 1.4))
    # the four long edges of the tube catch the most light
    n = 900
    cx_ = rng.choice([-HW, HW], n) * 0.985
    cy_ = rng.choice([YT, YB], n) * 0.985
    streaks(cx_, cy_, lognormal_int(rng, n, 0.018, 0.5), rng.uniform(0.2, 0.7, n), zr=(0.9, 100), run=(6, 30), near_z=(0.5, 1.6))
    # fixtures: ceiling strips (warm white), wall lamps (amber), floor lane lines
    n = 700
    X = rng.choice([-0.7, 0.0, 0.7], n) + rng.normal(0, 0.04, n)
    streaks(X, np.full(n, YT - 0.02), lognormal_int(rng, n, 0.045, 0.5), rng.uniform(0.0, 0.25, n))
    n = 600
    streaks(rng.choice([-HW, HW], n) * 0.99, rng.choice([0.2, 0.9], n) + rng.normal(0, 0.03, n),
            lognormal_int(rng, n, 0.032, 0.5), rng.uniform(0.45, 0.9, n))
    n = 300
    streaks(rng.choice([-1.0, 1.0], n), np.full(n, YB + 0.01), lognormal_int(rng, n, 0.025, 0.5), rng.uniform(0.5, 1.0, n))
    # the opening at the far end and the light it throws into the haze
    end = proj(np.array([0.0]), np.array([0.2]), np.array([160.0]))[0]
    cv.points(end[None], 30.0, ramp(0.0), 12)
    glow(cv, end, 3000.0, 80, 0.05, n=5000, seed=2)
    glow(cv, end, 26000.0, 420, 0.4, n=8000, seed=3)
    return dict(exposure=1.1, bloom=0.12, halation=0.08, vignette=0.5)


@scene("about-3", R43, "About: 24/7, always on",
       "A beacon sweeps through night haze over dark water; the long exposure turns its beam into a soft fan of light with glints on the sea.")
def about_3(cv):
    rng = np.random.default_rng(272)
    src = np.array([640.0, 820.0])
    hz = 1180.0
    # beam: radial rays, denser where the beam lingered
    n = 1500
    a = np.deg2rad(-12) + rng.normal(0, 1, n) * np.deg2rad(13)
    dwell = 0.35 + 0.65 * (0.5 + 0.5 * np.sin(a * 9.0 + 1.3)) * (0.6 + 0.4 * np.sin(a * 3.1 + 0.4))
    keep = rng.random(n) < dwell
    a = a[keep]
    n = len(a)
    M = 220
    r = np.geomspace(40, 3200, M)[None]
    d = np.c_[np.cos(a), np.sin(a)]
    P = src[None, None, :] + r[..., None] * d[:, None, :]
    prof = smoothstep(40, 260, r) * (r / 260) ** -0.55
    B = 0.5 + r * 0.010 * rng.uniform(0.6, 1.6, (n, 1))
    hue = np.clip(0.05 + 0.75 * (r / 3200) ** 0.6 + rng.normal(0, 0.05, (n, 1)), 0, 1)
    trails(cv, P, lognormal_int(rng, n, 0.05, 0.6), hue, B, rng, env=(0.0, 0.25), speed=0.2, prof=prof)
    # a few wide, soft rays: the volume of the beam
    k = 60
    a2 = np.deg2rad(-12) + rng.normal(0, 1, k) * np.deg2rad(16)
    P2 = src[None, None, :] + r[..., None] * np.c_[np.cos(a2), np.sin(a2)][:, None, :]
    trails(cv, P2, lognormal_int(rng, k, 0.10, 0.4), 0.45 * np.ones((k, M)), rng.uniform(30, 90, k), rng,
           env=(0.0, 0.3), speed=0.0, prof=smoothstep(60, 500, r) * (r / 500) ** -0.4)
    # the lamp
    cv.points(src[None], 120.0, ramp(0.0), 4)
    glow(cv, src, 1500.0, 40, 0.05, n=4000)
    glow(cv, src, 16000.0, 300, 0.4, n=7000, seed=1)
    # the beam lights the haze it passes through
    for j, (dist, e, sg) in enumerate(((500, 9000.0, 260), (1050, 14000.0, 380), (1700, 16000.0, 520))):
        glow(cv, src + dist * np.array([np.cos(np.deg2rad(-12)), np.sin(np.deg2rad(-12))]), e, sg, 0.5, n=6000, seed=10 + j)
    # glints on the water below the horizon, strongest under the beam
    g = 1400
    gx = src[0] + rng.normal(0, 1, g) * np.abs(rng.normal(450, 250, g)) + 600 * rng.random(g)
    gy = hz + 20 + rng.exponential(220, g)
    ln = rng.uniform(15, 120, g) * (1 + (gy - hz) / 300)
    w = np.exp(-np.abs(gx - src[0] - 350) / 700) * np.exp(-(gy - hz) / 420)
    swarm_streaks(cv, np.c_[gx, gy], np.c_[np.ones(g), rng.normal(0, 0.04, g)], ln,
                  lognormal_int(rng, g, 0.10, 0.7) * w, rng.uniform(0.1, 0.8, g),
                  np.where(rng.random(g) < 0.3, rng.uniform(3, 12, g), 0.6))
    # faint horizon glow
    cv.polylines(np.stack([np.linspace(-100, 2500, 400), np.full(400, hz)], -1)[None],
                 (0.05 * np.exp(-((np.linspace(-100, 2500, 400) - 900) / 900) ** 2))[None], ramp(0.6), 18)
    return dict(exposure=1.1, bloom=0.12, halation=0.08, vignette=0.48)


@scene("contact", R45, "Contact page image (4:5)",
       "A single calm ribbon of light rises through the frame in an S curve, trailing fine sparks.")
def contact(cv):
    rng = np.random.default_rng(281)
    ctrl = np.array([[520, 2150], [140, 1350], [1480, 1000], [1040, -120]])
    sp = ribbon(cv, ctrl, n=300, width=58, twist=1.3, twist_phase=0.9, wob=0.12, inten=0.42, isig=0.7,
                hue=(0.0, 0.65), blur=(0.5, 1.1), tjit=0.08, env=(0.15, 0.15), seed=1,
                spread_profile=lambda t: 0.6 + 0.8 * np.sin(np.pi * t))
    ribbon(cv, ctrl + np.array([[80, 0], [80, 0], [-60, 0], [-40, 0]]), n=40, width=120, twist=0.6, inten=0.08,
           hue=(0.4, 0.9), blur=(16, 36), seed=2)
    spine = sp["spine"]
    k = 500
    j = rng.integers(0, len(spine), k)
    nr = normals(spine)[j]
    tang = np.gradient(spine, axis=0)[j]
    xy = spine[j] + nr * rng.normal(0, 1, (k, 1)) * 140
    swarm_streaks(cv, xy, tang * -1 + rng.normal(0, 0.4, (k, 2)), rng.uniform(8, 40, k),
                  lognormal_int(rng, k, 0.12, 0.6), rng.uniform(0.4, 1.0, k),
                  np.where(rng.random(k) < 0.25, rng.uniform(3, 14, k), 0.6))
    motes(cv, 18, (0, 0, 1600, 2000), energy=(0.01, 0.05), blur=(20, 70), seed=22)
    return dict(exposure=1.0, bloom=0.10, halation=0.07, vignette=0.45)


# ---------------------------------------------------------------------------
# registry helpers

ORDER = ["hero", "threat-swarm", "threat-ransomware", "threat-phishing", "threat-breach",
         "domain-network", "domain-endpoint", "domain-cloud", "domain-identity", "domain-email",
         "domain-applications", "domain-data", "domain-ai-agents", "domain-ot-iot", "domain-governance",
         "service-1", "service-2", "service-3", "service-4", "service-5", "service-6",
         "cta", "status", "reel-poster", "about-1", "about-2", "about-3", "contact"]


def render(name, out_w=None, ss=2, seed=0, grade=None):
    """Render one scene. Scenes return develop kwargs; two extra keys are
    handled here: slate (amount of faint slate-blue depth particles, 0 = none)
    and slate_weight (callable xy -> energy scale, to keep text areas clean).
    grade: optional dict of develop overrides (or JSON in env GEN_GRADE)."""
    import json
    import os
    sc = SCENES[name]
    dw, dh = sc["size"]
    cv = Canvas(dw, dh, out_w=out_w or dw, ss=ss, seed=seed)
    kw = dict(sc["fn"](cv) or {})
    amount = kw.pop("slate", 1.0)
    weight = kw.pop("slate_weight", None)
    if amount > 0:
        area = dw * dh / (2400 * 1350)
        slate_dust(cv, int(round(46 * amount * area)), weight=weight, seed=len(name) * 131 + sum(map(ord, name)))
    grade = grade if grade is not None else json.loads(os.environ.get("GEN_GRADE", "{}"))
    kw.update(grade)
    return cv.develop(**kw)
