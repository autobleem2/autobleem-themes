"""Direction A (CONSOLE-14): three procedural backgrounds with more pull than the plain stand-in, none with lines.

The owner (2026-09-29): no lines/stripes/brushed metal, and the plain gradient was not eye-catching. So:
  p1 glass   large translucent cut-corner panels (the v02b shape) at depth, cyan rim light, magenta behind
  p2 bokeh   out-of-focus cyan/magenta lights, thinner through the middle third
  p3 aurora  soft wide cyan-to-magenta light bands, blurred until no edge is left
Each keeps the middle third calmer and the bottom third darker for the UI, has a fine grain and is dithered.
Writes design/direction-a/bg-proc/bg-p1..p3.png and bg-proc-sheet.png (each raw and under the splash logo).
Run: python tools/make_direction_a_bg_proc.py --font-dir ../../../repos/autobleem/src/resources/fonts
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_direction_a_logo as base  # noqa: E402  (parses --font-dir)
import make_direction_a_screens_v2 as sc  # noqa: E402

SW, SH = 1280, 720
CYAN = np.array([54, 217, 224.])
MAG = np.array([255, 70, 170.])
OUT = os.path.join(base.DESIGN, "bg-proc")


def base_grad():
    yy, xx = np.mgrid[0:SH, 0:SW].astype(np.float32)
    t = yy / SH
    top, mid, bot = np.array([30, 40, 56.]), np.array([18, 25, 38.]), np.array([6, 8, 13.])
    col = np.where((t < 0.5)[..., None], top + (mid - top) * (t / 0.5)[..., None],
                   mid + (bot - mid) * ((t - 0.5) / 0.5)[..., None])
    return col, xx, yy


def add_light(col, layer_rgba):
    """Screen-blend a float RGBA layer (0..255 colour, 0..1 alpha) onto col."""
    rgb, a = layer_rgba[..., :3], layer_rgba[..., 3:4]
    return col + (255 - col) * (rgb / 255) * a


def calm(xx, yy):
    """1 at the top, ~0.45 through the middle third, ~0.3 at the bottom: how much decoration each row keeps."""
    t = yy / SH
    return np.clip(1 - 0.55 * np.exp(-((t - 0.5) / 0.14) ** 2) - 0.7 * np.clip((t - 0.62) / 0.38, 0, 1), 0.2, 1)


def finish(col, seed):
    rng = np.random.default_rng(seed)
    col = col + rng.normal(0, 1.6, (SH, SW, 1)) + rng.uniform(-0.5, 0.5, (SH, SW, 3))
    return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8), "RGB")


def glowf(xx, yy, cx, cy, rx, ry):
    d = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
    return np.clip(1 - d, 0, 1) ** 2


def p1_glass():
    col, xx, yy = base_grad()
    col = add_light(col, np.dstack([np.broadcast_to(MAG, (SH, SW, 3)),
                                    (glowf(xx, yy, 0.25 * SW, 0.75 * SH, 0.5 * SW, 0.45 * SH) * 0.35)[..., None]]))
    col = add_light(col, np.dstack([np.broadcast_to(CYAN, (SH, SW, 3)),
                                    (glowf(xx, yy, 0.78 * SW, 0.2 * SH, 0.55 * SW, 0.5 * SH) * 0.4)[..., None]]))
    img = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    # panels: (cx, cy, w, h, angle, blur, fill alpha, rim alpha)
    panels = [(1050, 150, 560, 300, -14, 10, 26, 120), (250, 120, 420, 220, 10, 16, 18, 80),
              (820, 360, 380, 200, -8, 3, 20, 150), (160, 520, 520, 260, -18, 22, 16, 60),
              (1180, 560, 420, 240, 12, 14, 14, 70), (560, 60, 260, 140, 22, 26, 12, 50)]
    for cx, cy, w, h, ang, blur, fa, ra in panels:
        c = h * 0.28
        pts = [(-w / 2, -h / 2), (w / 2 - c, -h / 2), (w / 2, -h / 2 + c), (w / 2, h / 2), (-w / 2 + c, h / 2),
               (-w / 2, h / 2 - c)]
        a = math.radians(ang)
        pts = [(cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)) for x, y in pts]
        body = Image.new("L", (SW, SH), 0)
        ImageDraw.Draw(body).polygon(pts, fill=fa)
        rim = Image.new("L", (SW, SH), 0)
        ImageDraw.Draw(rim).polygon(pts, outline=ra, width=3)
        body = body.filter(ImageFilter.GaussianBlur(blur))
        rim = rim.filter(ImageFilter.GaussianBlur(max(1.2, blur * 0.6)))
        img.alpha_composite(sc_solid((200, 235, 245), body))
        img.alpha_composite(sc_solid(tuple(int(v) for v in CYAN), rim))
    col = np.asarray(img.convert("RGB")).astype(np.float32)
    k = calm(xx, yy)[..., None]
    col = base_grad()[0] + (col - base_grad()[0]) * k
    return finish(col, 11)


def sc_solid(rgb, alpha):
    im = Image.new("RGBA", alpha.size, rgb + (0,))
    im.putalpha(alpha)
    return im


def p2_bokeh():
    col, xx, yy = base_grad()
    col = add_light(col, np.dstack([np.broadcast_to(CYAN, (SH, SW, 3)),
                                    (glowf(xx, yy, 0.7 * SW, 0.25 * SH, 0.6 * SW, 0.55 * SH) * 0.3)[..., None]]))
    img = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    rng = np.random.default_rng(7)
    for _ in range(170):
        r = float(rng.choice([rng.uniform(4, 14), rng.uniform(14, 40), rng.uniform(40, 90)], p=[0.5, 0.35, 0.15]))
        x, y = rng.uniform(0, SW), rng.beta(1.3, 2.2) * SH
        rgb = (54, 217, 224) if rng.random() < 0.62 else ((255, 70, 170) if rng.random() < 0.7 else (230, 240, 250))
        a = rng.uniform(0.08, 0.35) * (0.6 if r > 40 else 1)
        m = Image.new("L", (SW, SH), 0)
        dd = ImageDraw.Draw(m)
        dd.ellipse([x - r, y - r, x + r, y + r], fill=int(255 * a))
        dd.ellipse([x - r, y - r, x + r, y + r], outline=int(255 * min(1, a * 1.6)), width=max(1, int(r / 10)))
        m = m.filter(ImageFilter.GaussianBlur(0.8 + r / 14))
        img.alpha_composite(sc_solid(rgb, m))
    col = np.asarray(img.convert("RGB")).astype(np.float32)
    g = base_grad()[0]
    col = g + (col - g) * calm(xx, yy)[..., None]
    return finish(col, 12)


def p3_aurora():
    col, xx, yy = base_grad()
    bands = [(0.22, 0.10, 1.3, 0.3, 90, CYAN, 0.55), (0.34, 0.07, 2.1, 1.7, 70, MAG, 0.4),
             (0.12, 0.05, 0.9, 2.6, 60, CYAN * 0.6 + MAG * 0.4, 0.35), (0.80, 0.06, 1.1, 0.9, 110, MAG, 0.25)]
    for yc, amp, freq, ph, width, rgb, strength in bands:
        centre = (yc + amp * np.sin(freq * 2 * math.pi * xx / SW + ph)) * SH
        a = np.exp(-((yy - centre) / width) ** 2) * strength
        a *= 0.55 + 0.45 * np.sin(1.7 * 2 * math.pi * xx / SW + ph * 2) ** 2  # brighter and dimmer stretches
        col = add_light(col, np.dstack([np.broadcast_to(rgb, (SH, SW, 3)), a[..., None]]))
    img = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8), "RGB").filter(ImageFilter.GaussianBlur(18))
    col = np.asarray(img).astype(np.float32)
    g = base_grad()[0]
    col = g + (col - g) * calm(xx, yy)[..., None]
    return finish(col, 13)


def noise(seed, scales=((6, 1.0), (12, 0.5), (24, 0.25), (48, 0.12))):
    """Smooth fractal noise in 0..1: random grids upsampled and summed."""
    rng = np.random.default_rng(seed)
    acc = np.zeros((SH, SW), np.float32)
    for cells, w in scales:
        g = Image.fromarray((rng.random((cells * 9 // 16 + 2, cells + 2)) * 255).astype(np.uint8), "L")
        acc += np.asarray(g.resize((SW, SH), Image.BICUBIC)).astype(np.float32) / 255 * w
    acc -= acc.min()
    return acc / acc.max()


def tint(col, a, rgb):
    return add_light(col, np.dstack([np.broadcast_to(rgb, (SH, SW, 3)), np.clip(a, 0, 1)[..., None]]))


def keep_calm(col, xx, yy):
    g = base_grad()[0]
    return g + (col - g) * calm(xx, yy)[..., None]


def p4_horizon():
    """A glowing horizon behind a dark floor, its light mirrored soft on the floor - no grid."""
    col, xx, yy = base_grad()
    hy = 0.56 * SH
    col = tint(col, np.exp(-((yy - hy) / 26) ** 2) * (0.5 + 0.5 * glowf(xx, yy * 0 + hy, 0.5 * SW, hy, 0.7 * SW, 1)) * 0.9,
               CYAN)
    col = tint(col, np.exp(-((yy - hy + 60) / 120) ** 2) * 0.35 * glowf(xx, yy * 0 + hy, 0.62 * SW, hy, 0.5 * SW, 1),
               MAG)
    floor = yy > hy
    col = np.where(floor[..., None], col * (0.55 + 0.45 * np.exp(-((yy - hy) / 90)))[..., None], col)
    col = tint(col, glowf(xx, yy, 0.5 * SW, hy + 40, 0.45 * SW, 70) * 0.25 * floor, CYAN)
    col = tint(col, glowf(xx, yy, 0.8 * SW, 0.12 * SH, 0.35 * SW, 0.3 * SH) * 0.25, MAG)
    return finish(col, 14)


def p5_mosaic():
    """Big cut-corner tiles, filled (no outlines), each a slightly different shade, softly lit."""
    col, xx, yy = base_grad()
    img = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    rng = np.random.default_rng(5)
    tw, th, gap = 150, 96, 10
    for row in range(-1, SH // (th + gap) + 2):
        for colx in range(-1, SW // (tw + gap) + 2):
            x0 = colx * (tw + gap) + (row % 2) * (tw + gap) / 2
            y0 = row * (th + gap)
            c = th * 0.28
            m = Image.new("L", (SW, SH), 0)
            ImageDraw.Draw(m).polygon([(x0, y0), (x0 + tw - c, y0), (x0 + tw, y0 + c), (x0 + tw, y0 + th),
                                       (x0 + c, y0 + th), (x0, y0 + th - c)], fill=int(rng.uniform(4, 26)))
            img.alpha_composite(sc_solid((190, 230, 240) if rng.random() < 0.8 else (255, 120, 200), m))
    col = np.asarray(img.filter(ImageFilter.GaussianBlur(1.2)).convert("RGB")).astype(np.float32)
    col = tint(col, glowf(xx, yy, 0.72 * SW, 0.2 * SH, 0.5 * SW, 0.5 * SH) * 0.35, CYAN)
    col = tint(col, glowf(xx, yy, 0.12 * SW, 0.85 * SH, 0.4 * SW, 0.4 * SH) * 0.3, MAG)
    return finish(keep_calm(col, xx, yy), 15)


def p6_nebula():
    col, xx, yy = base_grad()
    n1, n2 = noise(21), noise(22)
    col = tint(col, np.clip(n1 - 0.45, 0, 1) * 1.3 * glowf(xx, yy, 0.65 * SW, 0.25 * SH, 0.8 * SW, 0.7 * SH), CYAN)
    col = tint(col, np.clip(n2 - 0.5, 0, 1) * 1.2 * glowf(xx, yy, 0.25 * SW, 0.55 * SH, 0.7 * SW, 0.6 * SH), MAG)
    # a few round, soft stars in the upper part (drawn as dots - thresholded noise gave streaks)
    img = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    m = Image.new("L", (SW, SH), 0)
    dd = ImageDraw.Draw(m)
    rng = np.random.default_rng(23)
    for _ in range(90):
        x, y, r = rng.uniform(0, SW), rng.beta(1.2, 2.6) * SH * 0.8, rng.uniform(0.6, 1.8)
        dd.ellipse([x - r, y - r, x + r, y + r], fill=int(rng.uniform(80, 220)))
    img.alpha_composite(sc_solid((235, 245, 255), m.filter(ImageFilter.GaussianBlur(0.6))))
    col = np.asarray(img.convert("RGB")).astype(np.float32)
    return finish(keep_calm(col, xx, yy), 16)


def p7_spotlights():
    """Two soft light cones from above, cyan and magenta, crossing behind the middle."""
    col, xx, yy = base_grad()
    for x_top, x_bot, rgb, s in ((0.3, 0.62, CYAN, 0.5), (0.78, 0.45, MAG, 0.35)):
        cx = (x_top + (x_bot - x_top) * yy / SH) * SW
        width = 60 + 260 * yy / SH
        a = np.exp(-((xx - cx) / width) ** 2) * s * np.clip(1.1 - yy / SH, 0, 1)
        col = tint(col, a, rgb)
    col = tint(col, glowf(xx, yy, 0.5 * SW, 0.02 * SH, 0.5 * SW, 0.2 * SH) * 0.3, np.array([200, 235, 245.]))
    img = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8), "RGB").filter(ImageFilter.GaussianBlur(6))
    return finish(keep_calm(np.asarray(img).astype(np.float32), xx, yy), 17)


def p8_duotone():
    """The frame split on a soft diagonal: cyan light up right, magenta low left, graphite between."""
    col, xx, yy = base_grad()
    d = (xx / SW - yy / SH)
    col = tint(col, np.clip((d - 0.15) * 1.6, 0, 1) ** 1.5 * 0.45, CYAN)
    col = tint(col, np.clip((-d - 0.25) * 1.6, 0, 1) ** 1.5 * 0.4, MAG)
    col = tint(col, np.exp(-((d - 0.08) / 0.05) ** 2) * 0.15, np.array([220, 240, 250.]))
    img = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8), "RGB").filter(ImageFilter.GaussianBlur(10))
    return finish(keep_calm(np.asarray(img).astype(np.float32), xx, yy), 18)


def p9_glass_bokeh():
    glass = np.asarray(p1_glass()).astype(np.float32)
    bok = np.asarray(p2_bokeh()).astype(np.float32)
    g = base_grad()[0]
    return finish(g + (glass - g) * 0.9 + (bok - g) * 0.45, 19)


def p10_halftone():
    """A halftone dot field (dots, not lines) that swells toward the lit corner and fades out."""
    col, xx, yy = base_grad()
    col = tint(col, glowf(xx, yy, 0.8 * SW, 0.15 * SH, 0.6 * SW, 0.6 * SH) * 0.35, CYAN)
    col = tint(col, glowf(xx, yy, 0.1 * SW, 0.9 * SH, 0.35 * SW, 0.35 * SH) * 0.3, MAG)
    img = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    m = Image.new("L", (SW * 2, SH * 2), 0)
    dd = ImageDraw.Draw(m)
    step = 18
    for y in range(0, SH, step):
        for x in range(0, SW, step):
            ox = x + (step / 2 if (y // step) % 2 else 0)
            t = glowf(np.array(ox), np.array(y), 0.82 * SW, 0.1 * SH, 0.75 * SW, 0.85 * SH)
            r = float(t) ** 0.7 * step * 0.46
            if r > 0.4:
                dd.ellipse([(ox - r) * 2, (y - r) * 2, (ox + r) * 2, (y + r) * 2], fill=46)
    m = m.resize((SW, SH), Image.LANCZOS)
    img.alpha_composite(sc_solid((120, 230, 240), m))
    return finish(keep_calm(np.asarray(img.convert("RGB")).astype(np.float32), xx, yy), 20)


def main():
    os.makedirs(OUT, exist_ok=True)
    gens = [("p1 szklo", p1_glass), ("p2 bokeh", p2_bokeh), ("p3 zorza", p3_aurora), ("p4 horyzont", p4_horizon),
            ("p5 mozaika", p5_mosaic), ("p6 mglawica", p6_nebula), ("p7 reflektory", p7_spotlights),
            ("p8 duotone", p8_duotone), ("p9 szklo+bokeh", p9_glass_bokeh), ("p10 raster", p10_halftone)]
    cols, tw, th = 2, 640, 360
    rows = (len(gens) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw + 48, rows * (th + 36 + 16) + 16), (12, 15, 20))
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(base.OS_BOLD, 24)
    for i, (name, fn) in enumerate(gens):
        bg = fn()
        bg.save(os.path.join(OUT, f"bg-{name.split()[0]}.png"))
        spl = sc.splash(bg.convert("RGBA"))
        x, y = 16 + (i % cols) * (tw + 16), 16 + (i // cols) * (th + 36 + 16)
        d.text((x, y), name, font=font, fill=base.CYAN)
        sheet.paste(spl.resize((tw, th), Image.LANCZOS), (x, y + 36))
        print(name, flush=True)
    sheet.save(os.path.join(OUT, "bg-proc-sheet-10.png"))
    print("written:", OUT)


if __name__ == "__main__":
    main()
