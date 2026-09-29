"""Direction A (CONSOLE-14): the game menu's icons and the small glyphs, drawn as vectors.

v01 (2026-09-29). Same canvases and boxes as the default theme's files, so the layout does not move:
  menu_settings/guide/memcard.png  118x118, the tile at (23, 27)-(95, 91)
  menu_resume.png                  118x118, a frame around the save state's picture window (25, 33) 68x52
  meta_panel.png                   30x30, the pad glyph next to "n Players" - framed, with a proper glow
  arrow.png                        24x24, the arrow at the selected cover
Style = the Play pill: graphite gradient body, 2 px cyan frame, soft cyan glow; the glyphs are cyan lines.
No Sony shapes (no button symbols on the pad).
Writes into design/direction-a/icons/ plus a sheet on the background next to today's default icons.
Run: python tools/make_direction_a_icons.py
"""
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
HERE = os.path.join(REPO, "design", "direction-a")
OUT = os.path.join(HERE, "icons")
BG = os.path.join(HERE, "bg-direction-a-01-smooth.png")
DEFAULT = os.path.join(REPO, "Themes", "default", "images")

CYAN = (54, 217, 224)
FILL_TOP = (46, 55, 66)
FILL_BOT = (33, 40, 49)
WINDOW = (14, 18, 24)
SS = 4


def blank(w, h, v=0):
    return Image.new("L", (w * SS, h * SS), v)


def shape(w, h, fn):
    m = blank(w, h)
    fn(ImageDraw.Draw(m), SS)
    return m


def outline(mask, px):
    """A stroke of px pixels (scale 1) along the inside of a filled mask."""
    k = int(px * SS) * 2 + 1
    return ImageChops.subtract(mask, mask.filter(ImageFilter.MinFilter(k)))


def colour(size, rgb, alpha):
    im = Image.new("RGBA", size, rgb + (0,))
    im.putalpha(alpha)
    return im


def gradient(size, box):
    im = Image.new("RGBA", size)
    d = ImageDraw.Draw(im)
    y0, y1 = box[1] * SS, box[3] * SS
    for y in range(size[1]):
        t = min(1.0, max(0.0, (y - y0) / max(1, y1 - y0)))
        d.line([(0, y), (size[0], y)], fill=tuple(round(FILL_TOP[i] + (FILL_BOT[i] - FILL_TOP[i]) * t)
                                                   for i in range(3)) + (255,))
    return im


def glow(mask, blur, strength):
    return mask.filter(ImageFilter.GaussianBlur(blur * SS)).point(lambda v: int(min(255, v * strength)))


def tile(w, h, box, radius, stroke=2, glow_px=6, glow_a=0.5):
    """The Play pill's look on a rounded rectangle: glow, cyan frame, graphite body."""
    size = (w * SS, h * SS)
    m = shape(w, h, lambda d, s: d.rounded_rectangle([v * s for v in box], radius=radius * s, fill=255))
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out = Image.alpha_composite(out, colour(size, CYAN, glow(m, glow_px, glow_a)))
    out = Image.alpha_composite(out, colour(size, CYAN, m))
    body = gradient(size, box)
    inner = shape(w, h, lambda d, s: d.rounded_rectangle(
        [(box[0] + stroke) * s, (box[1] + stroke) * s, (box[2] - stroke) * s, (box[3] - stroke) * s],
        radius=(radius - stroke) * s, fill=255))
    body.putalpha(inner)
    return Image.alpha_composite(out, body)


def glyph(base, line_mask, glow_px=2.5, glow_a=0.7):
    size = base.size
    out = Image.alpha_composite(base, colour(size, CYAN, glow(line_mask, glow_px, glow_a)))
    return Image.alpha_composite(out, colour(size, CYAN, line_mask))


def finish(im, w, h):
    return im.resize((w, h), Image.LANCZOS)


# --- the glyphs, as filled masks at scale 1 coordinates (cx, cy = the tile's centre) --------------------

def gear_mask(w, h, cx, cy, r_out, r_in, teeth=8, tooth_w=0.42):
    import math

    def f(d, s):
        d.ellipse([(cx - r_in) * s, (cy - r_in) * s, (cx + r_in) * s, (cy + r_in) * s], fill=255)
        for k in range(teeth):
            a = 2 * math.pi * k / teeth
            half = tooth_w / 2
            pts = []
            for aa, rr in ((a - half * 0.9, r_in - 1), (a - half * 0.7, r_out), (a + half * 0.7, r_out),
                           (a + half * 0.9, r_in - 1)):
                pts.append(((cx + rr * math.cos(aa)) * s, (cy + rr * math.sin(aa)) * s))
            d.polygon(pts, fill=255)
    return shape(w, h, f)


def ring(w, h, cx, cy, r, px):
    return shape(w, h, lambda d, s: d.ellipse([(cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s],
                                              outline=255, width=int(px * s)))


def pad_mask(w, h, cx, cy, bw, bh):
    """A generic gamepad body: a rounded bar plus two grips."""
    def f(d, s):
        x0, x1 = cx - bw / 2, cx + bw / 2
        y0, y1 = cy - bh / 2, cy + bh / 2
        d.rounded_rectangle([x0 * s, y0 * s, x1 * s, (y1 - bh * 0.18) * s], radius=bh * 0.42 * s, fill=255)
        gr = bh * 0.34
        for gx in (x0 + bw * 0.2, x1 - bw * 0.2):
            d.ellipse([(gx - gr) * s, (y1 - 2 * gr) * s, (gx + gr) * s, y1 * s], fill=255)
    return shape(w, h, f)


def pad_details(w, h, cx, cy, bw, bh, px):
    """D-pad cross on the left, two plain dots on the right (no button symbols)."""
    def f(d, s):
        lx, rx = cx - bw * 0.27, cx + bw * 0.27
        yy = cy - bh * 0.1
        a, t = bw * 0.1, px / 2
        d.rectangle([(lx - a) * s, (yy - t) * s, (lx + a) * s, (yy + t) * s], fill=255)
        d.rectangle([(lx - t) * s, (yy - a) * s, (lx + t) * s, (yy + a) * s], fill=255)
        r = bw * 0.045
        for dx, dy in ((-a * 0.55, a * 0.45), (a * 0.55, -a * 0.45)):
            d.ellipse([(rx + dx - r) * s, (yy + dy - r) * s, (rx + dx + r) * s, (yy + dy + r) * s], fill=255)
    return shape(w, h, f)


def memcard_mask(w, h, cx, cy, cw, ch):
    """A card with a clipped top-right corner."""
    def f(d, s):
        x0, x1, y0, y1 = cx - cw / 2, cx + cw / 2, cy - ch / 2, cy + ch / 2
        c = cw * 0.3
        d.polygon([(x0 * s, y0 * s), ((x1 - c) * s, y0 * s), (x1 * s, (y0 + c) * s), (x1 * s, y1 * s),
                   (x0 * s, y1 * s)], fill=255)
    return shape(w, h, f)


def memcard_details(w, h, cx, cy, cw, ch, px):
    def f(d, s):
        x0, y1 = cx - cw / 2, cy + ch / 2
        # contacts along the bottom
        n, gap = 4, cw * 0.08
        pw = (cw - 2 * px - 2 * gap - (n - 1) * gap) / n
        for k in range(n):
            xa = x0 + px + gap + k * (pw + gap)
            d.rectangle([xa * s, (y1 - ch * 0.3) * s, (xa + pw) * s, (y1 - px - gap * 0.8) * s], fill=255)
        # label line
        d.rectangle([(x0 + px + gap) * s, (cy - ch * 0.2) * s, (cx + cw * 0.12) * s,
                     (cy - ch * 0.2 + px) * s], fill=255)
    return shape(w, h, f)


# --- the files --------------------------------------------------------------------------------------------

BOX = (23, 27, 95, 91)
CX, CY = (BOX[0] + BOX[2]) / 2, (BOX[1] + BOX[3]) / 2
LINE = 3


def icon_settings():
    base = tile(118, 118, BOX, 14)
    g = gear_mask(118, 118, CX, CY, 21, 15.5)
    lines = ImageChops.add(outline(g, LINE), ring(118, 118, CX, CY, 6.5, LINE))
    return finish(glyph(base, lines), 118, 118)


def icon_guide():
    base = tile(118, 118, BOX, 14)
    bw, bh = 50, 30
    p = pad_mask(118, 118, CX, CY + 1, bw, bh)
    lines = ImageChops.add(outline(p, LINE), pad_details(118, 118, CX, CY + 1, bw, bh, LINE))
    return finish(glyph(base, lines), 118, 118)


def icon_memcard():
    base = tile(118, 118, BOX, 14)
    cw, ch = 32, 42
    m = memcard_mask(118, 118, CX, CY, cw, ch)
    lines = ImageChops.add(outline(m, LINE), memcard_details(118, 118, CX, CY, cw, ch, LINE))
    return finish(glyph(base, lines), 118, 118)


def icon_resume():
    # frame 5 px around the picture window (25, 33) 68x52; the window stays dark (the picture goes there)
    wx, wy, ww, wh = 25, 33, 68, 52
    box = (wx - 6, wy - 6, wx + ww + 6, wy + wh + 6)
    base = tile(118, 118, box, 10)
    size = base.size
    win = shape(118, 118, lambda d, s: d.rounded_rectangle(
        [(wx - 1) * s, (wy - 1) * s, (wx + ww + 1) * s, (wy + wh + 1) * s], radius=3 * s, fill=255))
    base = Image.alpha_composite(base, colour(size, CYAN, glow(outline(win, 1), 1.5, 0.5)))
    base = Image.alpha_composite(base, colour(size, WINDOW, win))
    # a small play mark in the window, seen only when there is no picture
    tri = shape(118, 118, lambda d, s: d.polygon(
        [((wx + ww / 2 - 6) * s, (wy + wh / 2 - 8) * s), ((wx + ww / 2 - 6) * s, (wy + wh / 2 + 8) * s),
         ((wx + ww / 2 + 8) * s, (wy + wh / 2) * s)], fill=255))
    base = Image.alpha_composite(base, colour(size, CYAN, tri.point(lambda v: v * 45 // 100)))
    return finish(base, 118, 118)


def icon_meta():
    base = tile(30, 30, (3, 5, 27, 25), 6, stroke=1, glow_px=2, glow_a=0.6)
    bw, bh = 17, 10
    # filled: a 2 px outline does not read at 30x30
    p = pad_mask(30, 30, 15, 15.5, bw, bh)
    return finish(glyph(base, p, glow_px=1, glow_a=0.6), 30, 30)


def icon_arrow():
    size = (24 * SS, 24 * SS)
    tri = shape(24, 24, lambda d, s: d.polygon([(5 * s, 7 * s), (19 * s, 7 * s), (12 * s, 17.5 * s)], fill=255))
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out = Image.alpha_composite(out, colour(size, CYAN, glow(tri, 1.2, 0.8)))
    out = Image.alpha_composite(out, colour(size, CYAN, tri))
    return finish(out, 24, 24)


def sheet(new, old):
    """Two rows on the background at 2x: today's default icons over the new ones."""
    bg = Image.open(BG).convert("RGBA")
    names = list(new)
    cell = 260
    w, h = cell * len(names) + 40, 2 * cell + 40
    sc = max(w / bg.width, h / bg.height)
    bg = bg.resize((round(bg.width * sc) + 1, round(bg.height * sc) + 1), Image.LANCZOS)
    crop = bg.crop(((bg.width - w) // 2, (bg.height - h) // 2, (bg.width - w) // 2 + w, (bg.height - h) // 2 + h))
    for row, icons in enumerate((old, new)):
        for k, n in enumerate(names):
            im = icons[n]
            sc = 2 if im.width > 40 else 4
            im = im.resize((im.width * sc, im.height * sc), Image.LANCZOS)
            x = 20 + k * cell + (cell - im.width) // 2
            y = 20 + row * cell + (cell - im.height) // 2
            crop.alpha_composite(im, (x, y))
    return crop


def main():
    os.makedirs(OUT, exist_ok=True)
    new = {"menu_settings": icon_settings(), "menu_guide": icon_guide(), "menu_memcard": icon_memcard(),
           "menu_resume": icon_resume(), "meta_panel": icon_meta(), "arrow": icon_arrow()}
    for n, im in new.items():
        im.save(os.path.join(OUT, f"{n}-direction-a-01.png"))
    old = {n: Image.open(os.path.join(DEFAULT, n + ".png")).convert("RGBA") for n in new}
    sheet(new, old).save(os.path.join(OUT, "icons-sheet-01.png"))
    print("written:", OUT)


if __name__ == "__main__":
    main()
