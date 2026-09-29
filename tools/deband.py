"""Deband and dither a picture: smooth the 1-2 level steps of a dark gradient, keep the texture, dither to 8 bits.

How: in floating point, a low-pass copy is made (three box blurs ~ a Gaussian). Where the picture differs
from it by less than THRESHOLD levels (a band step, not texture), the low-pass value is taken - blended
softly, so there is no hard edge between smoothed and kept areas. Triangular (TPDF) noise of +-DITHER
levels is added before rounding back to 8 bits, so the smooth ramp does not band again.

Use: from deband import deband;  deband(img)   or   python tools/deband.py IN OUT [--radius 20]
Needs numpy (pip install numpy).
"""
import argparse
import numpy as np
from PIL import Image


def _box(a, r, axis):
    """Box blur of radius r along one axis (edges clamped), via a cumulative sum."""
    pad = [(0, 0)] * a.ndim
    pad[axis] = (r + 1, r)
    c = np.cumsum(np.pad(a, pad, mode="edge"), axis=axis, dtype=np.float64)
    n = a.shape[axis]
    hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
    lo = np.take(c, np.arange(0, n), axis=axis)
    return ((hi - lo) / (2 * r + 1)).astype(np.float32)


def low_pass(a, radius):
    r = max(1, radius // 2)
    for _ in range(3):
        a = _box(_box(a, r, 0), r, 1)
    return a


def deband(img, radius=20, threshold=3.5, dither=1.0, seed=981205):
    """Return img (RGB or RGBA; alpha untouched) debanded and dithered."""
    mode = img.mode
    rgba = np.asarray(img.convert("RGBA")).astype(np.float32)
    rgb = rgba[..., :3]
    low = low_pass(rgb, radius)
    d = rgb - low
    k = np.clip(np.abs(d) / threshold, 0.0, 1.0) ** 2
    rng = np.random.default_rng(seed)
    noise = (rng.random(rgb.shape, dtype=np.float32) - rng.random(rgb.shape, dtype=np.float32)) * dither
    out = np.clip(np.rint(low + d * k + noise), 0, 255)
    rgba[..., :3] = out
    res = Image.fromarray(rgba.astype(np.uint8), "RGBA")
    return res if mode == "RGBA" else res.convert("RGB")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--radius", type=int, default=20)
    ap.add_argument("--threshold", type=float, default=3.5)
    ap.add_argument("--dither", type=float, default=1.0)
    a = ap.parse_args()
    deband(Image.open(a.src), a.radius, a.threshold, a.dither).save(a.dst)


if __name__ == "__main__":
    main()
