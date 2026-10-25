"""YellowForce generated imagery: a small physically-minded light renderer.

Everything is drawn as light energy into float HDR buffers (one buffer per
depth-of-field bin), then developed like a photograph: defocus, multi-scale
bloom + halation, filmic tone mapping, cool-shadow split tone, film grain,
vignette and dithering.

Coordinates and sizes are in *design pixels*: the main export size of the
image (e.g. 2400 x 1350). The renderer can draw at any output size and
supersampling factor and the picture keeps the same look.
"""
from __future__ import annotations

import math
import numpy as np
import cv2

cv2.setNumThreads(4)

# --------------------------------------------------------------------------
# colour


def srgb_to_lin(c):
    c = np.asarray(c, dtype=np.float64) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(x):
    x = np.clip(x, 0.0, 1.0)
    return np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)


LUMA = np.array([0.2126, 0.7152, 0.0722])


def _norm(c):
    c = srgb_to_lin(c)
    return c / float(c @ LUMA)


# Brand (official logo kit): navy #071B3E, amber #FFBF00, slate #777F98.
NAVY = (7, 27, 62)          # #071B3E, brand navy (reference)
NAVY_DEEP = (3, 11, 28)     # #030B1C, brand shadow (reference)
# Image fields (round 1, 2026-10-26): darker and moodier than flat brand
# navy, same hue, so the imagery reads like a premium night photograph.
# The open dark averages about #040C1E; light lifts it back towards navy.
FIELD = (5, 16, 38)         # #051026, open dark field
FIELD_DEEP = (2, 7, 18)     # #020712, corners and deep shadow
HOT = (255, 243, 209)       # #FFF3D1, warm-white hot cores
SLATE = (119, 127, 152)     # #777F98, faint secondary particles

# Light ramp, luminance-normalised so "intensity" means luminance.
# 0 = warm white (#FFF3D1), 0.55 = brand amber #FFBF00, 1 = deep amber.
RAMP_POS = np.array([0.0, 0.22, 0.55, 0.8, 1.0])
RAMP_COL = np.stack([
    _norm(HOT),               # #FFF3D1 warm white
    _norm((255, 224, 140)),   # pale amber
    _norm((255, 191, 0)),     # #FFBF00 brand amber
    _norm((255, 182, 0)),     # amber
    _norm((255, 171, 6)),     # deep amber
])
SLATE_COL = _norm(SLATE)


def ramp(h):
    """Brand colour for hue position h in [0,1] (array ok). Returns (...,3)."""
    h = np.clip(np.asarray(h, dtype=np.float64), 0, 1)
    out = np.empty(h.shape + (3,))
    for k in range(3):
        out[..., k] = np.interp(h, RAMP_POS, RAMP_COL[:, k])
    return out


# --------------------------------------------------------------------------
# small maths helpers


def smoothstep(a, b, x):
    if b == a:
        return (np.asarray(x, dtype=np.float64) >= a).astype(np.float64)
    t = np.clip((np.asarray(x, dtype=np.float64) - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def envelope(t, a=0.15, b=0.15, p=1.0):
    """Smooth fade in over [0,a] and out over [1-b,1]."""
    t = np.asarray(t, dtype=np.float64)
    e = smoothstep(0, a, t) * (1 - smoothstep(1 - b, 1, t))
    return e ** p


def bezier(ctrl, t):
    """ctrl (...,4,2), t (M,) -> (...,M,2) cubic bezier."""
    ctrl = np.asarray(ctrl, dtype=np.float64)
    t = np.asarray(t, dtype=np.float64)
    a, b, c, d = (ctrl[..., i, None, :] for i in range(4))
    u = (1 - t)[:, None]
    tt = t[:, None]
    return u ** 3 * a + 3 * u * u * tt * b + 3 * u * tt * tt * c + tt ** 3 * d


def bezier_deriv(ctrl, t):
    ctrl = np.asarray(ctrl, dtype=np.float64)
    t = np.asarray(t, dtype=np.float64)
    a, b, c, d = (ctrl[..., i, None, :] for i in range(4))
    u = (1 - t)[:, None]
    tt = t[:, None]
    return 3 * u * u * (b - a) + 6 * u * tt * (c - b) + 3 * tt * tt * (d - c)


def normals(P):
    """Unit normals along polylines P (...,M,2)."""
    d = np.gradient(P, axis=-2)
    n = np.stack([-d[..., 1], d[..., 0]], axis=-1)
    return n / (np.linalg.norm(n, axis=-1, keepdims=True) + 1e-9)


def wobble(rng, n, t, terms=3, fmin=0.4, fmax=2.2, amp=1.0):
    """n smooth random 1D signals over t (M,) -> (n,M), roughly unit amplitude."""
    t = np.asarray(t)
    out = np.zeros((n, t.size))
    a = amp
    for _ in range(terms):
        f = rng.uniform(fmin, fmax, size=(n, 1))
        ph = rng.uniform(0, 2 * np.pi, size=(n, 1))
        out += a * np.sin(2 * np.pi * f * t[None, :] + ph)
        a *= 0.5
        fmin, fmax = fmin * 1.9, fmax * 1.9
    return out / 1.5


class SinField:
    """Divergence-free smooth random flow (curl of a sum of plane waves)."""

    def __init__(self, rng, n=9, wavelength=700.0, spread=0.6):
        ang = rng.uniform(0, 2 * np.pi, n)
        lam = wavelength * np.exp(rng.normal(0, spread, n))
        k = 2 * np.pi / lam
        self.kx = k * np.cos(ang)
        self.ky = k * np.sin(ang)
        self.ph = rng.uniform(0, 2 * np.pi, n)
        self.a = (lam / lam.mean()) ** 0.8
        self.a /= self.a.sum()

    def curl(self, x, y):
        arg = x[..., None] * self.kx + y[..., None] * self.ky + self.ph
        c = np.cos(arg) * self.a
        # psi = sum a sin(arg) / k ; v = (dpsi/dy, -dpsi/dx)
        k = np.sqrt(self.kx ** 2 + self.ky ** 2)
        vx = (c * self.ky / k).sum(-1)
        vy = -(c * self.kx / k).sum(-1)
        return vx, vy

    def scalar(self, x, y):
        arg = x[..., None] * self.kx + y[..., None] * self.ky + self.ph
        return (np.sin(arg) * self.a).sum(-1)


# --------------------------------------------------------------------------
# canvas

BINS = np.array([0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0, 128.0, 256.0])


def _disk_kernel(R, soft):
    r = int(math.ceil(R + 3 * soft + 1))
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1].astype(np.float64)
    d = np.sqrt(xx * xx + yy * yy)
    # anti-aliased disk with a slightly brighter rim (lens bokeh), soft edge
    k = np.clip(R + 0.5 - d, 0, 1)
    rim = 1.0 + 0.18 * smoothstep(0.55 * R, R, d)
    k = k * rim
    if soft > 0:
        k = cv2.GaussianBlur(k, (0, 0), soft)
    return (k / k.sum()).astype(np.float32)


class Canvas:
    def __init__(self, dw, dh, out_w=None, ss=2, seed=0):
        self.dw, self.dh = dw, dh
        self.out_w = out_w or dw
        self.out_h = int(round(self.out_w * dh / dw))
        self.ss = ss
        self.r = ss * self.out_w / dw            # render px per design px
        self.W = self.out_w * ss
        self.H = self.out_h * ss
        self.bufs = {}
        self.rng = np.random.default_rng(seed)

    # ---- buffers ---------------------------------------------------------
    def _bin(self, blur):
        blur = max(float(blur), 0.5)
        return int(np.argmin(np.abs(np.log(BINS) - math.log(blur))))

    def _buf(self, bi):
        if bi not in self.bufs:
            b = BINS[bi]
            f = self.r if b <= 2 else min(self.r, 6.0 / b)
            w = max(8, int(round(self.dw * f)))
            f = w / self.dw
            h = max(8, int(round(self.dh * f)))
            self.bufs[bi] = (f, np.zeros((h, w, 3), np.float32))
        return self.bufs[bi]

    def _splat(self, bi, x, y, wrgb):
        """Bilinear splat of energies wrgb (N,3) at design coords x,y."""
        f, buf = self._buf(bi)
        h, w = buf.shape[:2]
        px = x * f - 0.5
        py = y * f - 0.5
        ix = np.floor(px).astype(np.int64)
        iy = np.floor(py).astype(np.int64)
        fx = (px - ix).astype(np.float32)
        fy = (py - iy).astype(np.float32)
        ok = (ix >= -1) & (ix < w) & (iy >= -1) & (iy < h)
        if not ok.any():
            return
        ix, iy, fx, fy, wrgb = ix[ok], iy[ok], fx[ok], fy[ok], wrgb[ok]
        idx_all, wt_all = [], []
        for dx, dy, wt in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)),
                           (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
            xx = ix + dx
            yy = iy + dy
            m = (xx >= 0) & (xx < w) & (yy >= 0) & (yy < h)
            idx_all.append((yy[m] * w + xx[m]))
            wt_all.append((wt[m, None] * wrgb[m]))
        idx = np.concatenate(idx_all)
        wt = np.concatenate(wt_all)
        n = w * h
        for k in range(3):
            buf[..., k] += np.bincount(idx, weights=wt[:, k], minlength=n).reshape(h, w).astype(np.float32)

    # ---- primitives --------------------------------------------------------
    def _bin_split(self, blur):
        """Continuous position between log-spaced bins -> (lo, hi, w_hi)."""
        lb = np.log2(np.maximum(np.asarray(blur, np.float64), 0.5) / 0.5)
        lb = np.clip(lb, 0, len(BINS) - 1)
        lo = np.floor(lb).astype(int)
        w = lb - lo
        w = np.where(w < 0.04, 0.0, np.where(w > 0.96, 1.0, w))
        lo = np.where(w >= 1.0, lo + 1, lo)
        w = np.where(w >= 1.0, 0.0, w)
        hi = np.minimum(lo + 1, len(BINS) - 1)
        return lo, hi, w

    def points(self, xy, energy, color, blur=0.5):
        """Point lights (bokeh motes / sparks). energy (N,), color (N,3)|(3,)."""
        xy = np.asarray(xy, np.float64).reshape(-1, 2)
        energy = np.broadcast_to(np.asarray(energy, np.float64), (len(xy),))
        color = np.broadcast_to(np.asarray(color, np.float64), (len(xy), 3))
        blur = np.broadcast_to(np.asarray(blur, np.float64), (len(xy),))
        lo, hi, w = self._bin_split(blur)
        for bins, wt in ((lo, 1 - w), (hi, w)):
            for bi in np.unique(bins):
                m = (bins == bi) & (wt > 0)
                if m.any():
                    self._splat(bi, xy[m, 0], xy[m, 1], (energy[m] * wt[m])[:, None] * color[m])

    def polylines(self, P, I, C, blur=0.5, chunk=3_000_000):
        """Draw light trails.

        P: (n,M,2) vertices in design px. I: (n,M) intensity (energy per unit
        length, roughly the peak brightness of an in-focus line). C: (n,3) or
        (n,M,3) linear colour (luminance-normalised). blur: scalar or (n,)
        defocus radius in design px.
        """
        P = np.asarray(P, np.float64)
        if P.ndim == 2:
            P = P[None]
        n, M = P.shape[:2]
        I = np.broadcast_to(np.asarray(I, np.float64), (n, M))
        C = np.asarray(C, np.float64)
        if C.ndim == 1:
            C = np.broadcast_to(C, (n, 3))
        if C.ndim == 2:
            C = np.broadcast_to(C[:, None, :], (n, M, 3))
        blur = np.broadcast_to(np.asarray(blur, np.float64), (n,))
        lo, hi, w = self._bin_split(blur)
        if np.any((w > 0) & (lo != hi)):
            m = w > 0
            self._polylines_bins(P[~m], I[~m], C[~m], lo[~m], chunk)
            self._polylines_bins(P[m], I[m] * (1 - w[m])[:, None], C[m], lo[m], chunk)
            self._polylines_bins(P[m], I[m] * w[m][:, None], C[m], hi[m], chunk)
        else:
            self._polylines_bins(P, I, C, lo, chunk)

    def polylines_var(self, P, I, C, B, piece=24):
        """Like polylines but with per-vertex blur B (n,M). Paths are drawn as
        overlapping pieces of 2*piece segments, each with its weighted mean
        blur and a triangular (hat) intensity window. The windows sum to one
        along the path, so the blur changes smoothly, with no visible seams
        where one piece hands over to the next."""
        P = np.asarray(P, np.float64)
        n, M = P.shape[:2]
        I = np.broadcast_to(np.asarray(I, np.float64), (n, M))
        C = np.asarray(C, np.float64)
        if C.ndim == 2:
            C = np.broadcast_to(C[:, None, :], (n, M, 3))
        B = np.broadcast_to(np.asarray(B, np.float64), (n, M))
        idx = np.arange(M)
        K = int(math.ceil((M - 1) / piece))
        for k in range(K + 1):
            c = k * piece
            a = max(0, c - piece)
            b = min(M, c + piece + 1)
            if b - a < 2:
                continue
            w = np.clip(1 - np.abs(idx[a:b] - c) / piece, 0, 1)
            bl = (B[:, a:b] * w).sum(1) / w.sum()
            self.polylines(P[:, a:b], I[:, a:b] * w[None], C[:, a:b], bl)

    def _polylines_bins(self, P, I, C, bins, chunk):
        if len(P) == 0:
            return
        for bi in np.unique(bins):
            sel = np.nonzero(bins == bi)[0]
            f = self._buf(bi)[0]
            ds = 0.45 / f                       # sample spacing in design px
            A = P[sel, :-1].reshape(-1, 2)
            B = P[sel, 1:].reshape(-1, 2)
            IA = I[sel, :-1].reshape(-1)
            IB = I[sel, 1:].reshape(-1)
            CA = C[sel, :-1].reshape(-1, 3)
            CB = C[sel, 1:].reshape(-1, 3)
            keep = (IA > 1e-6) | (IB > 1e-6)
            A, B, IA, IB, CA, CB = A[keep], B[keep], IA[keep], IB[keep], CA[keep], CB[keep]
            L = np.linalg.norm(B - A, axis=1)
            k = np.maximum(1, np.ceil(L / ds)).astype(np.int64)
            ends = np.cumsum(k)
            start = 0
            si = 0
            S = len(k)
            while si < S:
                # choose a block of segments with <= chunk samples
                base = ends[si - 1] if si > 0 else 0
                sj = int(np.searchsorted(ends, base + chunk, side="right"))
                sj = max(sj, si + 1)
                kk = k[si:sj]
                tot = int(kk.sum())
                seg = np.repeat(np.arange(si, sj), kk)
                off = np.repeat(np.cumsum(kk) - kk, kk)
                t = ((np.arange(tot) - off) + 0.5) / k[seg]
                x = A[seg, 0] + (B[seg, 0] - A[seg, 0]) * t
                y = A[seg, 1] + (B[seg, 1] - A[seg, 1]) * t
                inten = (IA[seg] + (IB[seg] - IA[seg]) * t) * (L[seg] / k[seg])
                col = CA[seg] + (CB[seg] - CA[seg]) * t[:, None]
                self._splat(bi, x, y, inten[:, None] * col)
                si = sj
            del start

    # ---- development -----------------------------------------------------
    def _defocus_all(self):
        hdr = np.zeros((self.H, self.W, 3), np.float32)
        for bi, (f, buf) in sorted(self.bufs.items()):
            b = BINS[bi]
            if b <= 2:
                sig = max(0.42 * b * f, 0.75)  # >= 0.75 render px keeps lines alias-free
                img = cv2.GaussianBlur(buf, (0, 0), sig)
            else:
                R = b * f
                k = _disk_kernel(R, soft=0.22 * R + 0.6)
                img = cv2.filter2D(buf, -1, k, borderType=cv2.BORDER_CONSTANT)
            # energy per design px^2
            img *= f * f
            if img.shape[:2] != (self.H, self.W):
                img = cv2.resize(img, (self.W, self.H), interpolation=cv2.INTER_CUBIC)
                np.maximum(img, 0, out=img)
            hdr += img
        return hdr

    @staticmethod
    def _blur_big(img, sigma):
        """Gaussian blur with large sigma via a pyramid."""
        d = 1
        small = img
        while sigma / d > 10 and min(small.shape[:2]) > 32:
            small = cv2.resize(small, (max(1, small.shape[1] // 2), max(1, small.shape[0] // 2)),
                               interpolation=cv2.INTER_AREA)
            d *= 2
        out = cv2.GaussianBlur(small, (0, 0), sigma / d)
        if d > 1:
            out = cv2.resize(out, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_LINEAR)
        return out

    def develop(self, exposure=1.0, bloom=0.10, halation=0.06, crosstalk=0.10,
                bg=FIELD, bg_edge=FIELD_DEEP, bg_top=None, bg_level=0.7, vignette=0.35, grain=1.15,
                haze=None, contrast=1.0, sat_low=0.7, occlude=0.85, occ_k=0.02, hot=HOT, air=60.0, far_warm=0.35, hue_keep=0.6, vibrance=0.35,
                warm_mid=1.0, atmos=0.0, seed=7):
        """Return the finished 8-bit sRGB image (out_h, out_w, 3) uint8.

        Brand grade: amber light with warm-white (#FFF3D1) cores over a deep
        navy field (FIELD #051026 in the open dark, FIELD_DEEP #020712 in the
        corners, lifted towards brand navy #071B3E around the light).
        bg_level: how close the open field gets to full navy (0 = all deep).
        occlude: how much bright light replaces the navy under it instead of
        adding to it (keeps glows amber/bronze, not grey-mauve).
        """
        rng = np.random.default_rng(seed)
        hdr = self._defocus_all()
        hdr *= exposure

        # bloom (white-ish, lens) + halation (amber, film) from the HDR
        q = 4
        small = cv2.resize(hdr, (self.W // q, self.H // q), interpolation=cv2.INTER_AREA)
        rq = self.r / q  # small px per design px
        bl = np.zeros_like(small)
        for s, w in ((3, 0.30), (9, 0.26), (24, 0.20)):
            bl += w * self._blur_big(small, s * rq)
        # the wide bloom only keeps part of its warmth; the rest lifts the
        # navy around the light (a cool halo), so big glows never mix amber
        # into navy as a grey-mauve haze
        far = np.zeros_like(small)
        for s, w in ((60, 0.14), (150, 0.10)):
            far += w * self._blur_big(small, s * rq)
        bl += far_warm * far
        far_l = bloom * (1 - far_warm) * (far @ LUMA.astype(np.float32))
        hal = self._blur_big(small, 14 * rq) * 0.75 + self._blur_big(small, 40 * rq) * 0.25
        hal_l = (hal @ LUMA.astype(np.float32))[..., None]
        hal_c = hal_l * ramp(0.75).astype(np.float32)
        glow = bloom * bl + halation * hal_c
        if atmos:
            # lit air: a very wide, warm scatter of all the light in the frame,
            # so the dark between the trails carries soft midtones like a photo
            # taken in a hazy room (round 1: fewer flat, empty navy areas)
            at = self._blur_big(small, 300 * rq) * 0.6 + self._blur_big(small, 640 * rq) * 0.4
            at_l = (at @ LUMA.astype(np.float32))[..., None]
            glow += atmos * at_l * ramp(0.45).astype(np.float32)
        if haze is not None:
            glow += haze(self).astype(np.float32)
        hdr += cv2.resize(glow, (self.W, self.H), interpolation=cv2.INTER_LINEAR)

        # channel crosstalk: very hot light burns towards white
        L = hdr @ LUMA.astype(np.float32)
        hot_e = np.maximum(L - 0.6, 0) * crosstalk
        hdr += hot_e[..., None]

        # filmic tone map (ACES fit). Per channel alone pushes bright amber
        # towards lemon (red clips first); blend in a hue-keeping version that
        # tone maps luminance and burns out towards white along the same hue.
        def aces(v):
            return (v * (2.51 * v + 0.03)) / (v * (2.43 * v + 0.59) + 0.14)
        y = np.clip(aces(hdr), 0, 1)
        if hue_keep > 0:
            LU0 = LUMA.astype(np.float32)
            Lx = hdr @ LU0
            Lt = np.clip(aces(Lx), 0, 1)
            yh = hdr * (Lt / np.maximum(Lx, 1e-7))[..., None]
            mx = yh.max(-1)
            k = np.where(mx > 1, (1 - Lt) / np.maximum(mx - Lt, 1e-7), 1.0)[..., None]
            yh = Lt[..., None] + (yh - Lt[..., None]) * k
            y = y + (np.clip(yh, 0, 1) - y) * hue_keep
        if contrast != 1.0:
            y = np.power(y, contrast)

        # down to output resolution in linear light
        if self.ss > 1:
            y = cv2.resize(y, (self.out_w, self.out_h), interpolation=cv2.INTER_AREA)
        oh, ow = y.shape[:2]
        f32 = np.float32
        LU = LUMA.astype(f32)

        # burnt-out cores land on warm white #FFF3D1, never paper white
        hw = srgb_to_lin(hot).astype(f32)
        h = smoothstep(0.35, 1.0, y.min(-1)).astype(f32)[..., None]
        y = y * (1 - h + h * hw)

        # geometry for the field and the vignette
        yy, xx = np.mgrid[0:oh, 0:ow].astype(f32)
        nx = (xx + 0.5) / ow * 2 - 1
        ny = (yy + 0.5) / oh * 2 - 1
        rr = 0.5 * (nx * nx + ny * ny)
        vig = 1 - vignette * smoothstep(0.15, 1.15, rr).astype(f32)
        y *= ((0.25 + 0.75 * vig) ** 0.6)[..., None]

        # dim light keeps its amber but loses a little chroma so faint trails
        # read as fine gold lines, not orange-brown
        # and mid-level light gets a little more chroma, so soft or defocused
        # gold reads as amber, not khaki, over the navy
        Ly = (y @ LU)[..., None]
        sat = sat_low + (1 - sat_low) * smoothstep(0.002, 0.05, Ly).astype(f32)
        if vibrance:
            band = (smoothstep(0.006, 0.05, Ly) * (1 - smoothstep(0.18, 0.55, Ly))).astype(f32)
            sat = sat * (1 + vibrance * band)
        y = Ly + (y - Ly) * sat
        y = np.maximum(y, 0)

        # background: navy in the open dark, deep navy-black in the corners
        nav = srgb_to_lin(bg).astype(f32)
        deep = srgb_to_lin(bg_edge).astype(f32)
        e = smoothstep(0.0, 1.05, rr * (0.6 + vignette)).astype(f32)
        mix = (bg_level * (1 - e))[..., None]
        if bg_top is not None:
            bt = srgb_to_lin(bg_top).astype(f32)
            g = ((yy + 0.5) / oh)[..., None]
            nav = bt * (1 - g) + nav * g
        bgimg = deep + (nav - deep) * mix
        # faint low-frequency mottling so the dark is not digitally flat
        mot = rng.normal(0, 1, (max(4, oh // 64), max(4, ow // 64))).astype(f32)
        mot = cv2.resize(cv2.GaussianBlur(mot, (0, 0), 1.2), (ow, oh), interpolation=cv2.INTER_CUBIC)
        bgimg = bgimg * (1 + 0.07 * mot[..., None])
        # air glow: the wide bloom lifts the navy around the light (depth)
        if air:
            Ls = cv2.resize(far_l, (ow, oh), interpolation=cv2.INTER_CUBIC)
            lift = np.clip(air * Ls, 0, 4)[..., None]
            bgimg = bgimg + (nav * 1.7 - bgimg) * (lift / (1 + lift))

        # light over the field: bright light partly replaces the navy under it
        a = occlude * (1 - np.exp(-Ly / occ_k))
        base = bgimg * (1 - a)
        img = base + y * (1 - base)

        out = lin_to_srgb(img).astype(f32)
        Y = out @ LU

        # warm the lit mids a touch (keeps glows golden over the navy)
        if warm_mid:
            mid = (smoothstep(0.12, 0.5, Y) * (1 - smoothstep(0.65, 1.0, Y))).astype(f32)[..., None]
            out += warm_mid * mid * np.array([0.010, 0.002, -0.014], f32)

        # film grain: luminance-shaped, slightly clumped, mostly monochrome
        if grain > 0:
            g = rng.normal(0, 1, (oh, ow)).astype(f32)
            g = cv2.GaussianBlur(g, (0, 0), 0.65)
            g /= g.std() + 1e-6
            Yc = np.clip(Y, 0, 1)
            amp = (0.9 + 4.5 * np.sqrt(Yc) * (1 - Yc) ** 1.2) / 255.0 * grain
            out += (g * amp)[..., None] * np.array([0.9, 1.0, 1.15], f32)
            gc = rng.normal(0, 1, (oh, ow, 3)).astype(f32)
            out += gc * (0.35 / 255.0) * grain
        # triangular dither then quantise
        d = (rng.random((oh, ow, 1), np.float32) - rng.random((oh, ow, 1), np.float32)) / 255.0
        out = np.clip(out + d, 0, 1)
        return (out * 255.0 + 0.5).astype(np.uint8)


# --------------------------------------------------------------------------
# reusable motifs


def lognormal_int(rng, n, median=1.0, sigma=0.8, cap=8.0):
    v = median * np.exp(rng.normal(0, sigma, n))
    return np.minimum(v, median * cap)


def ribbon(cv, ctrl, n=200, width=80.0, M=500, twist=0.0, twist_phase=0.0,
           spread_profile=None, wob=0.15, wob_terms=3, inten=0.6, isig=0.7,
           hue=(0.1, 0.7), blur=(0.5, 0.5), tjit=0.12, env=(0.12, 0.2),
           pulses=None, seed=None, dist="normal", speed_mod=0.35, along=None):
    """A bundle of long-exposure light trails around a cubic bezier spine.

    width: half-spread (design px). twist: number of half turns of the
    ribbon (its projected width goes through zero where it is edge on).
    blur: (min,max) defocus per trail, or callable(u)->blur.
    along: optional function t->intensity multiplier shared by all trails.
    Returns dict with the spine for reuse.
    """
    rng = np.random.default_rng(seed) if seed is not None else cv.rng
    t = np.linspace(0, 1, M)
    spine = bezier(ctrl, t)
    nrm = normals(spine)
    if dist == "normal":
        u = np.clip(rng.normal(0, 0.5, n), -1.3, 1.3)
    else:
        u = rng.uniform(-1, 1, n)
    prof = np.ones(M) if spread_profile is None else spread_profile(t)
    tw = np.cos(np.pi * twist * t + twist_phase) if twist else np.ones(M)
    w = wobble(rng, n, t, terms=wob_terms) * wob
    off = width * (u[:, None] * prof[None, :] * tw[None, :] + w * prof[None, :])
    P = spine[None] + off[..., None] * nrm[None]
    # each trail covers its own part of the spine
    t0 = rng.uniform(0, tjit, n)
    t1 = 1 - rng.uniform(0, tjit, n)
    tl = (t[None, :] - t0[:, None]) / (t1 - t0)[:, None]
    e = np.where((tl >= 0) & (tl <= 1), envelope(np.clip(tl, 0, 1), env[0], env[1]), 0.0)
    base = lognormal_int(rng, n, inten, isig)
    # brightness ~ 1/speed of the light: smooth random speed changes
    sp = 1 + speed_mod * wobble(rng, n, t, terms=2, fmin=0.5, fmax=1.6)
    I = base[:, None] * e * np.clip(sp, 0.2, 3)
    if along is not None:
        I = I * along(t)[None, :]
    if pulses is not None:
        freq, duty, depth = pulses
        ph = rng.uniform(0, 1, n)[:, None]
        L = np.cumsum(np.r_[0, np.linalg.norm(np.diff(spine, axis=0), axis=1)])
        s = (L[None, :] / freq + ph) % 1.0
        gate = smoothstep(0, 0.08, s) * (1 - smoothstep(duty, duty + 0.08, s))
        I = I * (1 - depth + depth * gate)
    h = rng.uniform(hue[0], hue[1], n)
    C = ramp(h)
    if callable(blur):
        bl = blur(u, rng)
    else:
        bl = rng.uniform(blur[0], blur[1], n)
    cv.polylines(P, I, C, bl)
    return {"spine": spine, "t": t}


def motes(cv, n, region, energy=(0.5, 3.0), blur=(12, 60), hue=(0.4, 1.0), seed=None, weight=None):
    """Out-of-focus dust motes (bokeh discs). region = (x0,y0,x1,y1) or callable."""
    rng = np.random.default_rng(seed) if seed is not None else cv.rng
    if callable(region):
        xy = region(rng, n)
    else:
        x0, y0, x1, y1 = region
        xy = np.c_[rng.uniform(x0, x1, n), rng.uniform(y0, y1, n)]
    b = np.exp(rng.uniform(np.log(blur[0]), np.log(blur[1]), n))
    e = np.exp(rng.uniform(np.log(energy[0]), np.log(energy[1]), n)) * (b / 10.0) ** 2
    if weight is not None:
        e = e * weight(xy)
    cv.points(xy, e, ramp(rng.uniform(hue[0], hue[1], n)), b)


def flow_trails(cv, field, start_xy, steps, h=2.0, speed=None, jitter=0.0, rng=None):
    """Integrate particles through a velocity function field(x,y)->(vx,vy).
    Returns (n,steps+1,2) paths. RK2 midpoint, step length h (normalised)."""
    rng = rng or cv.rng
    p = np.array(start_xy, np.float64)
    out = np.empty((len(p), steps + 1, 2))
    out[:, 0] = p
    for i in range(steps):
        vx, vy = field(p[:, 0], p[:, 1])
        nv = np.sqrt(vx * vx + vy * vy) + 1e-9
        mid = p + 0.5 * h * np.c_[vx / nv, vy / nv]
        vx, vy = field(mid[:, 0], mid[:, 1])
        nv = np.sqrt(vx * vx + vy * vy) + 1e-9
        p = p + h * np.c_[vx / nv, vy / nv]
        out[:, i + 1] = p
    return out


def glow(cv, xy, energy, sigma, hue, n=2500, seed=0):
    """Soft gaussian glow around point(s): many tiny lights scattered with a
    gaussian spread, so the halo has no hard bokeh edge."""
    rng = np.random.default_rng(seed)
    xy = np.asarray(xy, np.float64).reshape(-1, 2)
    energy = np.broadcast_to(np.asarray(energy, np.float64), (len(xy),))
    sigma = np.broadcast_to(np.asarray(sigma, np.float64), (len(xy),))
    for p, e, s in zip(xy, energy, sigma):
        q = p + rng.normal(0, s, (n, 2))
        cv.points(q, e / n, ramp(hue), max(0.5, s * 0.35))


def slate_dust(cv, n, region=None, peak=(0.003, 0.012), blur=(14, 70), seed=0, weight=None):
    """Very faint slate-blue (#777F98) out-of-focus particles, for depth only.
    peak: HDR brightness range at the disc centre (tiny: they sit just above
    the navy). region (x0,y0,x1,y1) in design px, default the whole frame.
    weight(xy)->(n,) scales brightness (use it to keep text areas clean)."""
    rng = np.random.default_rng(seed + 9001)
    x0, y0, x1, y1 = region or (0, 0, cv.dw, cv.dh)
    xy = np.c_[rng.uniform(x0, x1, n), rng.uniform(y0, y1, n)]
    b = np.exp(rng.uniform(np.log(blur[0]), np.log(blur[1]), n))
    pk = np.exp(rng.uniform(np.log(peak[0]), np.log(peak[1]), n))
    pk *= (b / blur[1]) ** -0.35          # small, nearer-focus motes a bit brighter
    e = pk * np.pi * b * b
    if weight is not None:
        e = e * weight(xy)
    col = SLATE_COL[None] * (1 + rng.normal(0, 0.04, (n, 1)))
    cv.points(xy, e, col, b)
