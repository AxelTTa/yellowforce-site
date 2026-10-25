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
    return dict(exposure=1.0, bloom=0.11, halation=0.07, vignette=0.4)


@scene("threat-ransomware", R11, "Threat card: ransomware",
       "Streams of light slam into a hard, locked square and pile up along its edges.")
def threat_ransomware(cv):
    rng = np.random.default_rng(31)
    c = np.array([960.0, 820.0])
    hs = 250.0
    x0, y0, x1, y1 = c[0] - hs, c[1] - hs, c[0] + hs, c[1] + hs
    n = 700
    ang = np.deg2rad(rng.normal(8, 9, n))
    d = np.c_[np.cos(ang), np.sin(ang)]
    aim = np.c_[np.full(n, x0), np.clip(rng.normal(c[1] - 30, 180, n), y0 - 130, y1 + 70)]
    start = aim - d * rng.uniform(450, 1700, n)[:, None]
    with np.errstate(divide="ignore", invalid="ignore"):
        tx0 = (x0 - start[:, 0]) / d[:, 0]
        tx1 = (x1 - start[:, 0]) / d[:, 0]
        ty0 = (y0 - start[:, 1]) / d[:, 1]
        ty1 = (y1 - start[:, 1]) / d[:, 1]
    tmin = np.maximum(np.minimum(tx0, tx1), np.minimum(ty0, ty1))
    tmax = np.minimum(np.maximum(tx0, tx1), np.maximum(ty0, ty1))
    hit = (tmax >= tmin) & (tmin > 0)
    tend = np.where(hit, tmin, rng.uniform(1700, 2600, n))
    M = 100
    s = np.linspace(0, 1, M)
    P = start[:, None, :] + d[:, None, :] * (tend[:, None] * s[None])[..., None]
    nrm = np.c_[-d[:, 1], d[:, 0]]
    P += nrm[:, None, :] * (rng.normal(0, 8, n)[:, None] * np.sin(np.pi * s)[None])[..., None]
    lenpx = tend[:, None] * (1 - s[None])
    prof = np.where(hit[:, None], (0.15 + 0.85 * s[None] ** 2) * (1 + 3.0 * np.exp(-lenpx / 45)),
                    0.4 * (1 - smoothstep(0.6, 1.0, s[None])))
    hue = np.where(hit[:, None], 0.85 - 0.65 * s[None] ** 3, 0.85)
    inten = lognormal_int(rng, n, 0.07, 0.7)
    trails(cv, P, inten, hue, np.where(rng.random(n) < 0.12, rng.uniform(3, 14, n), rng.uniform(0.5, 0.9, n)),
           rng, env=(0.35, 0.02), prof=prof)
    hp = start[hit] + d[hit] * tend[hit][:, None]
    onleft = np.abs(hp[:, 0] - x0) < 1.0
    for (a, b) in (((x0, y0), (x0, y1)), ((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x0, y1), (x1, y1))):
        a, b = np.array(a), np.array(b)
        m = 500
        s = np.linspace(0, 1, m)
        pts = a + (b - a) * s[:, None]
        dd = np.linalg.norm(pts[:, None, :] - hp[None, :, :], axis=2)
        dens = np.exp(-(dd / 24.0) ** 2).sum(1)
        I = 0.12 + 0.09 * dens
        for inset, mul, bl in ((0, 1.0, 0.5), (0, 0.35, 6), (14, 0.25, 0.5)):
            q = pts.copy()
            q += np.sign(c - q) * inset * (np.abs(q - c) > hs - 1)
            cv.polylines(q[None], (I * mul)[None], ramp(0.2), bl)
    cv.points(hp, lognormal_int(rng, len(hp), 0.5, 0.6), ramp(rng.uniform(0, 0.4, len(hp))), 0.8)
    k = len(hp)
    sg = rng.choice([-1.0, 1.0], k)
    dirv = np.where(onleft[:, None], np.c_[0 * sg, sg], np.c_[sg, 0 * sg])
    swarm_streaks(cv, hp + dirv * 16, dirv, rng.uniform(16, 80, k), lognormal_int(rng, k, 0.10, 0.6),
                  rng.uniform(0.2, 0.6, k), 0.6)
    motes(cv, 12, (0, 0, 1600, 1600), energy=(0.01, 0.04), blur=(20, 60), seed=5)
    return dict(exposure=1.0, bloom=0.11, halation=0.06, vignette=0.42)


@scene("threat-phishing", R11, "Threat card: phishing and impersonation",
       "One bright lure line hooks down through the frame; many faint followers drift towards its tip.")
def threat_phishing(cv):
    rng = np.random.default_rng(41)
    top = bezier(np.array([[1120, -90], [1090, 250], [1010, 560], [1030, 860]]), np.linspace(0, 1, 320))
    R = 118.0
    th = np.linspace(0, np.deg2rad(212), 220)[1:]
    b = np.c_[1030 - R + R * np.cos(th), 860 + R * np.sin(th)]
    hook = np.vstack([top, b])
    bait = hook[-1]
    M = len(hook)
    s = np.linspace(0, 1, M)
    nr = normals(hook)
    prof = envelope(s, 0.001, 0.03) * (0.55 + 0.45 * s)
    k = 16
    offs = rng.normal(0, 3.6, k)
    for o in offs:
        cv.polylines((hook + nr * o)[None], (lognormal_int(rng, 1, 0.12, 0.4)[0] * prof
                                             * (1 + 0.25 * wobble(rng, 1, s, terms=2)[0]))[None], ramp(0.06), 0.5)
    cv.polylines(hook[None], (0.5 * prof)[None], ramp(0.0), 0.5)
    cv.polylines(hook[None], (0.5 * prof)[None], ramp(0.35), 6)
    cv.polylines(hook[None], (0.3 * prof)[None], ramp(0.6), 18)
    cv.points(bait[None], 8.0, ramp(0.0), 0.8)
    glow(cv, bait, 10.0, 11, 0.5)
    fld = SinField(rng, n=8, wavelength=600)

    def field(px, py):
        dx, dy = bait[0] - px, bait[1] - py
        dn = np.hypot(dx, dy) + 1e-6
        vx, vy = fld.curl(px, py)
        return dx / dn + 0.9 * vx, dy / dn + 0.9 * vy

    n = 460
    ang = rng.uniform(np.deg2rad(95), np.deg2rad(265), n)
    rad = rng.uniform(450, 1500, n)
    st = bait + np.c_[np.cos(ang), np.sin(ang)] * rad[:, None]
    steps = 340
    paths = flow_trails(cv, field, st, steps, h=3.5)
    dist = np.linalg.norm(paths - bait, axis=2)
    stop = rng.uniform(80, 460, n)
    alive = np.cumprod(dist > stop[:, None], axis=1).astype(float)
    first = alive.sum(1).astype(int)
    lens = rng.integers(60, 280, n)
    idx = np.arange(steps + 1)[None]
    on = (idx >= (first - lens)[:, None]) & (idx < first[:, None])
    tl = np.clip((idx - (first - lens)[:, None]) / lens[:, None], 0, 1)
    prof = on * (0.12 + 0.88 * tl ** 1.8)
    inten = lognormal_int(rng, n, 0.06, 0.75)
    blur = np.where(rng.random(n) < 0.2, rng.uniform(3, 20, n), rng.uniform(0.5, 0.9, n))
    trails(cv, paths, inten, rng.uniform(0.45, 0.95, n), blur, rng, env=None, prof=prof)
    motes(cv, 14, (0, 0, 1600, 1600), energy=(0.01, 0.05), blur=(20, 70), seed=6)
    return dict(exposure=1.0, bloom=0.11, halation=0.06, vignette=0.42)


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
    return dict(exposure=1.0, bloom=0.11, halation=0.06, vignette=0.42)


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
            cv.polylines((sp + nn * off)[None], np.full((1, M), 0.11 * dim), ramp(0.5), bl)
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
    glow(cv, (1650.0, 560.0), 18000.0, 460, 0.5, n=8000, seed=9)
    motes(cv, 20, (900, 0, 2400, 1350), energy=(0.01, 0.05), blur=(20, 70), seed=8)
    return dict(exposure=1.1, bloom=0.12, halation=0.08, vignette=0.42)


@scene("domain-endpoint", R169, "Coverage: Endpoint and device security",
       "A night floor of device lights in perspective, shallow focus; one guarded device burns hot in the middle and sends a soft column of light into the haze.")
def domain_endpoint(cv):
    rng = np.random.default_rng(72)
    f, cx, cy, h = 1250.0, 1250.0, 330.0, 1.5
    X, Z = np.meshgrid(np.arange(-40, 41, 0.8), np.geomspace(1.2, 70, 95))
    X = X.ravel() + rng.normal(0, 0.22, X.size)
    Z = Z.ravel() * np.exp(rng.normal(0, 0.03, Z.size))
    x = cx + f * X / Z
    y = cy + f * h / Z
    keep = (x > -200) & (x < 2600) & (y < 1500) & (rng.random(X.size) < 0.75 * np.minimum(1, (7 / Z) ** 0.7))
    X, Z, x, y = X[keep], Z[keep], x[keep], y[keep]
    Zf = 4.2
    blur = 0.5 + 105 * np.abs(1 / Z - 1 / Zf) ** 0.9
    # headline corner on the domain page stays calmer
    mask = 1 - 0.6 * (1 - smoothstep(450, 1100, x)) * smoothstep(780, 1150, y)
    E = lognormal_int(rng, len(x), 0.65, 0.7) * mask * (1 + 0.16 * blur ** 2) * np.minimum(1, (Zf / Z) ** 0.8)
    hue = rng.uniform(0.3, 1.0, len(x))
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
    glow(cv, (gx, gy - 120), 16000.0, 360, 0.45, n=8000, seed=2)
    glow(cv, (cx, cy + 40), 9000.0, 520, 0.6, n=8000, seed=4)
    return dict(exposure=1.2, bloom=0.12, halation=0.08, vignette=0.45)

# @@end domain-endpoint

@scene("domain-cloud", R169, "Coverage: Cloud security",
       "Wisps of soft white-gold light drift across the frame like a cloud bank lit from within.")
def domain_cloud(cv):
    rng = np.random.default_rng(81)
    fld = SinField(rng, n=8, wavelength=1000)
    shape = SinField(rng, n=7, wavelength=520)

    def field(x, y):
        vx, vy = fld.curl(x, y)
        return 1.0 + 0.3 * vx, 0.8 * vy

    n = 1100
    y0 = rng.normal(470, 260, n)
    st = np.c_[rng.uniform(-500, 700, n), y0]
    P = flow_trails(cv, field, st, 300, h=8.0)
    x, y = P[..., 0], P[..., 1]
    yc = 460 + 110 * np.sin(x / 600 + 0.5)
    thick = 260 + 120 * shape.scalar(x * 0.7, 0 * x)
    dens = smoothstep(0.1, 0.7, 1 - np.abs(y - yc) / thick + 0.8 * shape.scalar(x, y)) ** 1.5
    dens *= smoothstep(450, 1300, x)
    blur = np.exp(rng.uniform(np.log(0.5), np.log(40), n))
    inten = lognormal_int(rng, n, 0.011, 0.6) * (1 + blur / 4) ** 0.6
    crisp = rng.random(n) < 0.14
    inten[crisp] *= 3.0
    blur[crisp] = 0.6
    hue = np.where(crisp, rng.uniform(0.0, 0.45, n), rng.uniform(0.05, 0.6, n))
    trails(cv, P, inten, hue, blur, rng, env=(0.05, 0.05), prof=dens, speed=0.6)
    motes(cv, 26, (1100, 100, 2400, 900), energy=(0.01, 0.05), blur=(15, 60), seed=10)
    return dict(exposure=1.35, bloom=0.10, halation=0.05, vignette=0.42)


@scene("domain-identity", R169, "Coverage: Identity and access",
       "Fingerprint-like ridges drawn in light on a tilted plane, sharp in the middle and falling out of focus.")
def domain_identity(cv):
    rng = np.random.default_rng(91)
    c = np.array([1700.0, 640.0])
    rot = np.deg2rad(22)
    th = np.linspace(-np.pi, np.pi, 1100)
    ph = rng.uniform(0, 2 * np.pi, 4)
    mod = 1 + 0.11 * np.sin(2 * th + ph[0]) + 0.05 * np.sin(3 * th + ph[1]) + 0.025 * np.sin(5 * th + ph[2])
    paths, Is, hues = [], [], []
    K = 38
    for k in range(K):
        Lk = 28 + k * 20.5
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
        Is.append(g * (0.6 - 0.011 * k) * (0.7 + 0.3 * np.sin(th * 3 + k)))
        hues.append(np.full_like(th, 0.08 + 0.55 * k / K))
    P = np.array(paths)
    I = np.array(Is)
    nrm = np.array([np.sin(rot + 0.5), -np.cos(rot + 0.5)])
    dist = (P - c) @ nrm
    B = 0.5 + np.maximum(0, np.abs(dist) - 140) * 0.05
    trails(cv, P, np.ones(K), np.array(hues), B, rng, env=None, speed=0.15, prof=I, periodic=True)
    cv.points(c[None], 3.0, ramp(0.0), 4)
    motes(cv, 16, (1000, 0, 2400, 1350), energy=(0.01, 0.04), blur=(20, 60), seed=11)
    return dict(exposure=1.0, bloom=0.11, halation=0.07, vignette=0.42)


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
    motes(cv, 18, (1000, 0, 2400, 1350), energy=(0.01, 0.05), blur=(20, 60), seed=23)
    return dict(exposure=1.0, bloom=0.11, halation=0.07, vignette=0.42)


@scene("domain-applications", R169, "Coverage: Application and API security",
       "Lines of code written in light on a tilted page, sharp near the focus and melting into bokeh; one line flares where the flaw is.")
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
            Is.append(lognormal_int(rng, 1, 0.24, 0.45)[0] * boost)
            hs.append(0.03 if r == hot else rng.uniform(0.3, 0.95))
            u += ln + rng.uniform(14, 26)
    segs = np.array(segs)
    M = 18
    s = np.linspace(0, 1, M)
    Pp = segs[:, :1, :] + (segs[:, 1:, :] - segs[:, :1, :]) * s[None, :, None]
    P, wz = apply_h(Hm, Pp)
    ufocus, vfocus = 620.0, 30 + hot * 31.5
    dist = np.sqrt(np.maximum(0, np.abs(Pp[..., 0] - ufocus) - 140) ** 2 + (0.6 * (Pp[..., 1] - vfocus)) ** 2)
    B = 0.5 + dist * 0.05
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
    glow(cv, fp[0], 18000.0, 400, 0.45, n=8000, seed=2)
    motes(cv, 18, (900, 0, 2400, 1350), energy=(0.02, 0.06), blur=(20, 70), seed=12)
    return dict(exposure=1.15, bloom=0.12, halation=0.08, vignette=0.45)

# @@end domain-applications

@scene("domain-data", R169, "Coverage: Data protection",
       "Stacked rings of orbiting light, like a database seen in a long exposure, focus on the middle ring.")
def domain_data(cv):
    rng = np.random.default_rng(121)
    cx = 1700.0
    rings = [(290.0, 540.0), (480.0, 560.0), (675.0, 580.0), (870.0, 600.0), (1065.0, 620.0)]
    tilt = 0.21
    for ri, (cy, rx) in enumerate(rings):
        dfoc = abs(ri - 2)
        k = 46
        r = rx * (1 + rng.normal(0, 0.014, k))
        th0 = rng.uniform(0, 2 * np.pi, k)
        span = rng.uniform(0.3, 1.9, k)
        M = 200
        s = np.linspace(0, 1, M)
        th = th0[:, None] + span[:, None] * s[None]
        x = cx + r[:, None] * np.cos(th)
        y = cy + r[:, None] * np.sin(th) * tilt + rng.normal(0, 2.5, (k, 1))
        z = np.sin(th)
        B = 0.5 + dfoc * 5 + np.maximum(0, z) * (6 + dfoc * 6)
        prof = (0.08 + 0.92 * s ** 2)[None] * (0.6 + 0.4 * (1 - z) / 2)
        bright = (1.7, 1.2, 1.0, 1.2, 1.7)[ri] * (1.5 if ri == 2 else 1.0)
        trails(cv, np.stack([x, y], -1), lognormal_int(rng, k, 0.13 * bright, 0.7),
               rng.uniform(0.0 if ri == 2 else 0.25, 0.9, k)[:, None] * np.ones((1, M)), B, rng,
               env=(0.05, 0.02), prof=prof)
        heads = np.stack([x[:, -1], y[:, -1]], -1)
        cv.points(heads, lognormal_int(rng, k, 0.25, 0.6) * bright, ramp(0.1), B[:, -1])
    for side in (-1, 1):
        y = np.linspace(250, 1110, 300)
        x = cx + side * np.interp(y, [290, 1065], [540, 620])
        cv.polylines(np.c_[x, y][None], (0.05 * envelope(np.linspace(0, 1, 300), 0.3, 0.3))[None], ramp(0.6), 3)
    glow(cv, (cx, 680.0), 20000.0, 440, 0.5, n=8000, seed=9)
    motes(cv, 20, (900, 0, 2400, 1350), energy=(0.01, 0.05), blur=(20, 60), seed=13)
    return dict(exposure=1.3, bloom=0.12, halation=0.08, vignette=0.42)


@scene("domain-ai-agents", R169, "Coverage: AI and agent security",
       "A murmuration of tiny agent lights flowing as one, with a few rogue agents cutting across.")
def domain_ai_agents(cv):
    rng = np.random.default_rng(131)
    fld = SinField(rng, n=8, wavelength=900)
    depth_f = SinField(rng, n=5, wavelength=900)
    sheets = [np.array([[760, 980], [1250, 180], [1900, 1100], [2600, 330]]),
              np.array([[1150, 1250], [1550, 760], [2050, 380], [2600, 640]])]
    xs, vs = [], []
    for si, ctrl in enumerate(sheets):
        n = (30000, 16000)[si]
        t = rng.uniform(0, 1, n) ** 0.85
        sp = bezier(ctrl, t)
        tg = bezier_deriv(ctrl, t)
        tg /= np.linalg.norm(tg, axis=-1, keepdims=True)
        nr = np.stack([-tg[..., 1], tg[..., 0]], -1)
        width = (150, 95)[si] * (0.25 + np.sin(np.pi * t) ** 0.8) * (1 + 0.45 * fld.scalar(sp[..., 0], sp[..., 1]))
        off = rng.normal(0, 1, n) * width
        p = sp + nr * off[:, None]
        xs.append(p)
        vs.append(tg)
    p = np.concatenate(xs)
    v = np.concatenate(vs)
    m = len(p)
    cx_, cy_ = fld.curl(p[:, 0], p[:, 1])
    v = v + 0.08 * np.c_[cx_, cy_]
    rogue = np.zeros(m, bool)
    v[rogue] = v[rogue] @ np.array([[0, 1], [-1, 0]]) * rng.choice([-1, 1], (rogue.sum(), 1))
    z = depth_f.scalar(p[:, 0], p[:, 1])
    blur = 0.5 + np.maximum(0, z - 0.2) * 26
    length = rng.uniform(26, 70, m) * np.where(rogue, 5, 1)
    inten = lognormal_int(rng, m, 0.024, 0.35) * np.where(rogue, 20, 1)
    hue = np.where(rogue, 0.03, rng.uniform(0.2, 0.75, m))
    swarm_streaks(cv, p, v, length, inten, hue, blur, curve=np.where(rogue, 0, rng.normal(0, 0.003, m)))
    motes(cv, 18, (900, 0, 2400, 1350), energy=(0.01, 0.05), blur=(20, 60), seed=24)
    return dict(exposure=1.3, bloom=0.10, halation=0.07, vignette=0.42)


@scene("domain-ot-iot", R169, "Coverage: OT and IoT security",
       "Long-exposure arcs of rotating machinery around a glowing axis, dense and layered in depth, some blinking like sensors.")
def domain_ot_iot(cv):
    rng = np.random.default_rng(142)
    c = np.array([2050.0, 1250.0])
    n = 1000
    r = np.sqrt(rng.uniform(0.003, 1, n)) * 2500
    th0 = rng.uniform(np.pi * 0.92, np.pi * 1.6, n)
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
    glow(cv, c, 30000.0, 420, 0.35, n=8000, seed=3)
    glow(cv, (c[0] - 300, c[1] - 250), 9000.0, 300, 0.5, n=6000, seed=4)
    motes(cv, 24, (600, 0, 2400, 1350), energy=(0.02, 0.08), blur=(20, 80), seed=14)
    return dict(exposure=1.1, bloom=0.12, halation=0.08, vignette=0.45)

# @@end domain-ot-iot

@scene("domain-governance", R169, "Coverage: Governance, risk and compliance",
       "A ruled floor grid falling away to the horizon, swept by one warm beam that lights the rules it crosses.")
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
    I = 0.10 * (Zs[None] / 7) ** -0.2 * fade(P) * envelope(np.linspace(0, 1, M), 0.0001, 0.3)[None]
    trails(cv, P, np.ones(len(Xs)), np.full((len(Xs), M), 0.55), dof(Zs)[None] * np.ones((len(Xs), 1)),
           rng, env=None, speed=0, prof=I)
    Zt = np.r_[np.arange(1.5, 12, 1.0), np.arange(12, 60, 2.0)]
    X = np.linspace(-16, 16, 400)
    P = proj(X[None], Zt[:, None])
    I = 0.09 * (Zt[:, None] / 7) ** -0.2 * fade(P)
    trails(cv, P, np.ones(len(Zt)), np.full((len(Zt), 400), 0.55), dof(Zt)[:, None] * np.ones((1, 400)),
           rng, env=None, speed=0, prof=I)
    # sweeping beam: longitudinal rules lit in a band, smeared behind the leading edge
    k = 140
    Xb = 0.6 - rng.uniform(0, 1, k) ** 1.3 * 5.0
    lead = np.exp(-(0.6 - Xb) / 0.9)
    P = proj(Xb[:, None], Zs[None])
    I = (0.03 + 0.55 * lead)[:, None] * (Zs[None] / 7) ** -0.35 * envelope(np.linspace(0, 1, M), 0.0001, 0.35)[None]
    trails(cv, P, np.ones(k), (0.05 + 0.8 * (1 - lead))[:, None] * np.ones((1, M)),
           dof(Zs)[None] * np.ones((k, 1)), rng, env=None, speed=0.15, prof=I)
    # crossings light up under the beam
    XX, ZZ = np.meshgrid(np.arange(-4, 1, 1.0), Zt[Zt < 40])
    q = proj(XX.ravel(), ZZ.ravel())
    w = np.exp(-(0.6 - XX.ravel()) / 1.2) * (ZZ.ravel() / 7) ** -0.5
    cv.points(q, 2.5 * w, ramp(0.1), dof(ZZ.ravel()))
    return dict(exposure=1.15, bloom=0.11, halation=0.07, vignette=0.42)



# ---------------------------------------------------------------------------
# SERVICES (4:3)


@scene("service-1", R43, "Services 001 Deploy and connect",
       "One beam enters from the left and branches into a delta of fine filaments reaching every corner.")
def service_deploy(cv):
    rng = np.random.default_rng(161)
    leaves = []

    def grow(path, d, length, depth):
        p = path[-1]
        if depth == 6:
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

    grow([np.array([-160.0, 940.0])], np.array([1.0, -0.02]), 900.0, 0)
    L = max(len(lf) for lf in leaves)
    nl = len(leaves)
    leaves.sort(key=lambda a: a[-1, 1])
    out = []
    for i, lf in enumerate(leaves):
        pad = np.vstack([lf, np.repeat(lf[-1:], L - len(lf), 0)])
        out.append(pad)
    base = np.array(out)
    M = L
    s = np.linspace(0, 1, M)
    nr = normals(base)
    lane = (np.arange(nl) / (nl - 1) - 0.5)
    strands = 4
    P, I, H, B = [], [], [], []
    for k in range(strands):
        off = (lane[:, None] * 120 * (1 - s[None]) ** 2.2 + rng.normal(0, 2.5, (nl, 1)) * (1 - s[None])
               + rng.normal(0, 1.2, (nl, 1)))
        P.append(base + nr * off[..., None])
        I.append(lognormal_int(rng, nl, 0.075, 0.5))
        H.append(rng.uniform(0.0, 0.8, nl))
        B.append(np.where(rng.random(nl) < 0.15, rng.uniform(3, 12, nl), rng.uniform(0.5, 1.0, nl)))
    P = np.concatenate(P)
    lenmask = np.concatenate([np.array([np.r_[np.ones(len(lf)), np.zeros(L - len(lf))] for lf in leaves])] * strands)
    prof = lenmask * (1 - smoothstep(0.7, 1.0, np.cumsum(lenmask, 1) / lenmask.sum(1, keepdims=True)))
    hue = np.concatenate(H)[:, None] * 0.4 + 0.6 * s[None] * np.ones((len(P), 1))
    trails(cv, P, np.concatenate(I), np.clip(hue, 0, 1), np.concatenate(B), rng, env=(0.06, 0.0), prof=prof)
    tips = np.array([lf[-1] for lf in leaves])
    cv.points(tips, lognormal_int(rng, nl, 0.25, 0.5), ramp(rng.uniform(0.3, 0.9, nl)), rng.uniform(0.5, 6, nl))
    motes(cv, 18, (600, 0, 2400, 1800), energy=(0.01, 0.05), blur=(20, 70), seed=15)
    return dict(exposure=1.0, bloom=0.10, halation=0.06, vignette=0.42)


@scene("service-2", R43, "Services 002 Detect 24/7",
       "A deep field of drifting light in every focus plane; one trail moves against the grain and lights up.")
def service_detect(cv):
    rng = np.random.default_rng(172)
    fld = SinField(rng, n=7, wavelength=1300)
    n = 2600
    x = rng.uniform(-250, 2650, n)
    y = 900 + rng.normal(0, 1, n) * 520
    depth = rng.random(n)                                # 0 near ... 1 far
    blur = np.where(depth < 0.35, 6 + 70 * (0.35 - depth) / 0.35, 0.5 + 6 * (depth - 0.35) ** 2)
    ln = rng.uniform(50, 420, n) * (1.6 - depth)
    M = 24
    s = np.linspace(-0.5, 0.5, M)
    vx, vy = fld.curl(x, y)
    ang = np.deg2rad(-9) + 0.3 * vx
    P = np.stack([x[:, None] + np.cos(ang)[:, None] * ln[:, None] * s[None],
                  y[:, None] + np.sin(ang)[:, None] * ln[:, None] * s[None]], -1)
    inten = lognormal_int(rng, n, 0.06, 0.65) * (1 + blur / 5) ** 0.55
    trails(cv, P, inten, np.clip(0.3 + 0.6 * depth + rng.normal(0, 0.1, n), 0, 1), blur, rng, env=(0.3, 0.3))
    # the anomaly: against the grain, through the middle of the frame
    ctrl = np.array([[2050.0, 1750.0], [1800.0, 1300.0], [1450.0, 880.0], [950.0, 560.0]])
    along = lambda t: 0.25 + 0.75 * t ** 1.4
    ribbon(cv, ctrl, n=40, width=7, inten=0.45, isig=0.4, hue=(0.0, 0.2), blur=(0.5, 0.9), tjit=0.03,
           env=(0.3, 0.02), seed=3, along=along)
    ribbon(cv, ctrl, n=8, width=12, inten=0.25, hue=(0.25, 0.55), blur=(8, 14), tjit=0.02, env=(0.3, 0.02), seed=4, along=along)
    ribbon(cv, ctrl, n=6, width=20, inten=0.2, hue=(0.4, 0.7), blur=(30, 44), tjit=0.02, env=(0.3, 0.02), seed=5)
    cv.points(np.array([[950.0, 560.0]]), 14.0, ramp(0.0), 1.2)
    glow(cv, (950.0, 560.0), 400.0, 30, 0.2, n=4000)
    glow(cv, (1250.0, 760.0), 16000.0, 420, 0.5, n=8000, seed=2)
    return dict(exposure=1.1, bloom=0.12, halation=0.08, vignette=0.45)

# @@end service-2

@scene("service-3", R43, "Services 003 Respond",
       "A fast, hard line of light cuts through an amber cluster and blows it apart.")
def service_respond(cv):
    rng = np.random.default_rng(181)
    A, B = np.array([250.0, 1900.0]), np.array([2500.0, 180.0])
    d = (B - A) / np.linalg.norm(B - A)
    nr = np.array([-d[1], d[0]])
    n = 3600
    c = np.array([1520.0, 860.0])
    p = c + rng.normal(0, 1, (n, 2)) * np.array([380, 300])
    sd = (p - A) @ nr
    push = 240 * np.exp(-np.abs(sd) / 120) + rng.uniform(3, 14, n)
    dirv = np.sign(sd)[:, None] * nr + d * rng.normal(0.3, 0.3, (n, 1)) + rng.normal(0, 0.18, (n, 2))
    blur = np.where(rng.random(n) < 0.14, rng.uniform(3, 18, n), rng.uniform(0.5, 0.9, n))
    inten = lognormal_int(rng, n, 0.09, 0.65) * (0.8 + 1.4 * np.exp(-np.abs(sd) / 110))
    hue = np.clip(0.85 - 0.55 * np.exp(-np.abs(sd) / 100) + rng.normal(0, 0.06, n), 0.2, 0.95)
    swarm_streaks(cv, p + dirv * push[:, None] * 0.5, dirv, push, inten, hue, blur)
    ctrl = np.array([A, A + (B - A) / 3, A + 2 * (B - A) / 3, B])
    ribbon(cv, ctrl, n=60, width=4, inten=0.35, isig=0.4, hue=(0.0, 0.2), blur=(0.5, 0.8), tjit=0.02,
           env=(0.06, 0.06), seed=5, wob=0.08)
    ribbon(cv, ctrl, n=8, width=8, inten=0.3, hue=(0.3, 0.6), blur=(8, 12), tjit=0.02, seed=6)
    ribbon(cv, ctrl, n=8, width=14, inten=0.25, hue=(0.4, 0.7), blur=(26, 34), tjit=0.02, seed=7)
    motes(cv, 14, (600, 0, 2400, 1800), energy=(0.01, 0.05), blur=(20, 70), seed=16)
    return dict(exposure=1.0, bloom=0.10, halation=0.06, vignette=0.42)


@scene("service-4", R43, "Services 004 Attack (red team)",
       "Curving trails sweep in from every side and converge on one ringed target.")
def service_attack(cv):
    rng = np.random.default_rng(191)
    T = np.array([1580.0, 820.0])
    n = 340
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
    trails(cv, P, lognormal_int(rng, n, 0.07, 0.65), hue, blur, rng, env=(0.25, 0.02), prof=prof)
    th = np.linspace(0, 2 * np.pi, 1600)
    gap = np.ones_like(th)
    for q in range(4):
        dd = np.abs(np.angle(np.exp(1j * (th - q * np.pi / 2 - np.pi / 4))))
        gap *= smoothstep(0.03, 0.055, dd)
    for r, I0, bl in ((280, 0.30, 0.5), (284, 0.12, 0.5), (280, 0.12, 6)):
        cv.polylines(circle_pts(T, r, th)[None], (I0 * gap)[None], ramp(0.1), bl)
    cv.points(T[None], 9.0, ramp(0.0), 0.8)
    glow(cv, T, 8.0, 11, 0.5)
    motes(cv, 14, (0, 0, 2400, 1800), energy=(0.01, 0.04), blur=(20, 70), seed=25)
    return dict(exposure=1.0, bloom=0.11, halation=0.06, vignette=0.42)


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
    return dict(exposure=1.1, bloom=0.12, halation=0.08, vignette=0.45)

# @@end service-5

@scene("service-6", R43, "Services 006 Govern",
       "Tangled amber lines on the left settle into calm, evenly spaced light on the right.")
def service_govern(cv):
    rng = np.random.default_rng(211)
    n = 72
    M = 800
    x = np.linspace(-150, 2550, M)
    yi = 880 + (np.arange(n) - n / 2) * 7.5
    t = (x + 150) / 2700
    w = wobble(rng, n, t * 3.0, terms=4, fmin=0.5, fmax=1.5)
    ynoise = yi[:, None] + 430 * w + 110 * wobble(rng, n, t * 9, terms=2)
    m = smoothstep(700, 1600, x)[None]
    y = (1 - m) * ynoise + m * yi[:, None]
    P = np.stack([np.broadcast_to(x, (n, M)), y], -1)
    inten = lognormal_int(rng, n, 0.12, 0.45)
    prof = (0.25 + 0.75 * m) * envelope(t, 0.18, 0.05)[None]
    hue = (0.75 - 0.65 * m) * np.ones((n, 1))
    blur = np.where(rng.random(n) < 0.15, rng.uniform(3, 12, n), rng.uniform(0.5, 0.9, n))
    trails(cv, P, inten, hue, blur, rng, env=None, speed=0.25, prof=prof)
    band = np.stack([x, np.full(M, yi.mean())], -1)
    cv.polylines(band[None], (0.5 * m[0] * envelope(t, 0.1, 0.05))[None], ramp(0.4), 60)
    motes(cv, 14, (0, 0, 2400, 1800), energy=(0.01, 0.04), blur=(20, 70), seed=18)
    return dict(exposure=1.0, bloom=0.10, halation=0.06, vignette=0.42)


# ---------------------------------------------------------------------------
# BANDS, THUMBS, ABOUT, CONTACT


@scene("cta", R169, "Closing CTA band, full bleed behind the centred heading",
       "A wide river of long-exposure light sweeps up through the centre: a hot warm-white core, soft out-of-focus streaks around it, lit haze.")
def cta(cv):
    rng = np.random.default_rng(223)
    ctrl = np.array([[-300.0, 1260.0], [650.0, 1080.0], [1150.0, 420.0], [2750.0, 300.0]])

    def fan(t):
        # gathered where it crosses the heading, opening wide towards the right like a flare
        return 0.45 + 0.5 * (1 - t) ** 2 + 1.9 * t ** 2.4

    # in-focus core: fine trails, hot towards warm white
    ribbon(cv, ctrl, n=560, width=170, twist=0.7, twist_phase=0.5, wob=0.22, inten=0.19, isig=0.85,
           hue=(0.0, 0.5), blur=lambda u, r: 0.5 + 12.0 * np.abs(u) ** 2.2, tjit=0.28, env=(0.22, 0.22),
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
    ctrl2 = np.array([[-200.0, 900.0], [700.0, 860.0], [1500.0, 700.0], [2700.0, 760.0]])
    ribbon(cv, ctrl2, n=160, width=120, twist=0.5, wob=0.3, inten=0.05, isig=0.7, hue=(0.3, 0.9),
           blur=lambda u, r: 2.0 + 30.0 * np.abs(u) ** 1.5, tjit=0.3, env=(0.3, 0.3), seed=44)
    # the air lit by the light: midtones behind the heading
    glow(cv, (1250.0, 640.0), 34000.0, 480, 0.45, n=9000, seed=3)
    glow(cv, (1250.0, 620.0), 7000.0, 190, 0.2, n=6000, seed=4)
    motes(cv, 40, (0, 0, 2400, 1350), energy=(0.02, 0.10), blur=(30, 110), hue=(0.4, 0.9), seed=19)
    return dict(exposure=1.25, bloom=0.13, halation=0.09, vignette=0.55, slate=0.6)

# @@end cta

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

# @@end status

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

# @@end about-1

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

# @@end about-2

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

# @@end about-3

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
