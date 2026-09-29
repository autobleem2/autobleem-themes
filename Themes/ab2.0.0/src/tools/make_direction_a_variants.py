"""Direction A (CONSOLE-14): four style variants of the launcher mockup, to pick a less generic look.

v02 (2026-09-29), after the owner found v01 too generic. The same Games screen and layout as
make_direction_a_mockup.py, drawn four ways:
  a  chamfer + amber    cut corners (the memory card's shape) everywhere, amber for the focused item,
                        Saira headings, covers as CD jewel cases in perspective
  b  chamfer + magenta  the same shapes, magenta focus, a faint CRT scanline over the whole screen
  c  CRT                rounded, all cyan, strong scanlines, phosphor glow on the headings, a vignette
  d  minimal            no glows: thin steel lines, frosted dark panels, one cyan accent on the focus
The glyphs come from make_direction_a_icons.py (same masks), recoloured per variant.
Run: python tools/make_direction_a_variants.py --launcher ../../../repos/autobleem
"""
import argparse
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_direction_a_icons as ic  # noqa: E402

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
A = os.path.join(REPO, "Themes", "ab2.0.0", "src", "design")
DEF = os.path.join(REPO, "Themes", "default")
SAIRA = os.path.join(DEF, "saira-semicondensed-medium.ttf")
SS = ic.SS

CYAN = (54, 217, 224)
AMBER = (255, 176, 59)
MAGENTA = (255, 70, 170)
STEEL = (170, 184, 198)
WHITE = (240, 248, 250)
GREY = (150, 164, 178)

VARIANTS = {
    "a": dict(name="chamfer + amber", shape="chamfer", line=CYAN, focus=AMBER, glow=1.0, heading=SAIRA,
              cases=True, scan=0, vignette=0, phosphor=False),
    "b": dict(name="chamfer + magenta", shape="chamfer", line=CYAN, focus=MAGENTA, glow=1.0, heading=SAIRA,
              cases=True, scan=18, vignette=0.25, phosphor=False),
    "c": dict(name="CRT", shape="round", line=CYAN, focus=CYAN, glow=1.4, heading=SAIRA,
              cases=False, scan=70, vignette=0.8, phosphor=True, bezel=True),
    "d": dict(name="minimal", shape="round-small", line=STEEL, focus=CYAN, glow=0.0, heading=None,
              cases=True, scan=0, vignette=0, phosphor=False),
}


# --- shapes ------------------------------------------------------------------------------------------------

def shape_mask(w, h, box, kind, inset=0.0, ss=SS):
    x0, y0, x1, y1 = [v * ss for v in box]
    i = inset * ss
    x0, y0, x1, y1 = x0 + i, y0 + i, x1 - i, y1 - i
    m = Image.new("L", (w * ss, h * ss), 0)
    d = ImageDraw.Draw(m)
    bh = y1 - y0
    if kind == "chamfer":
        c = max(2 * ss, min(bh * 0.28, 16 * ss)) - i * 0.4
        d.polygon([(x0, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1), (x0 + c, y1), (x0, y1 - c)], fill=255)
    elif kind == "round-small":
        d.rounded_rectangle([x0, y0, x1, y1], radius=max(1, 4 * ss - i), fill=255)
    else:
        d.rounded_rectangle([x0, y0, x1, y1], radius=max(1, min(bh / 2, 14 * ss) - i), fill=255)
    return m


def solid(size, rgb, alpha):
    im = Image.new("RGBA", size, rgb + (0,))
    im.putalpha(alpha)
    return im


def frame(w, h, box, v, edge=None, stroke=2, body_alpha=255, glow_px=6, glow_a=0.5, ss=SS):
    """The variant's panel/tile: glow (if any), a stroke in `edge`, a graphite body."""
    edge = edge or v["line"]
    size = (w * ss, h * ss)
    m = shape_mask(w, h, box, v["shape"], ss=ss)
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    # the inside, so a see-through body shows the background and not the stroke's colour or the glow
    inner = shape_mask(w, h, box, v["shape"], inset=stroke if v["shape"] != "round-small" else 1, ss=ss)
    if v["glow"] > 0:
        g = m.filter(ImageFilter.GaussianBlur(glow_px * ss)).point(lambda p: int(min(255, p * glow_a * v["glow"])))
        out = Image.alpha_composite(out, solid(size, edge, ImageChops.subtract(g, inner)))
    out = Image.alpha_composite(out, solid(size, edge, ImageChops.subtract(m, inner)))
    if v["shape"] == "round-small":  # frosted: lighter, a little see-through
        top, bot = (58, 66, 78), (36, 42, 52)
    else:
        top, bot = ic.FILL_TOP, ic.FILL_BOT
    body = Image.new("RGBA", size)
    bd = ImageDraw.Draw(body)
    y0, y1 = box[1] * ss, box[3] * ss
    for y in range(size[1]):
        t = min(1.0, max(0.0, (y - y0) / max(1, y1 - y0)))
        bd.line([(0, y), (size[0], y)], fill=tuple(round(top[k] + (bot[k] - top[k]) * t) for k in range(3)) + (255,))
    body.putalpha(inner.point(lambda p: p * body_alpha // 255))
    return Image.alpha_composite(out, body)


def lines(base, mask, rgb, v, glow_px=2.5, glow_a=0.7):
    size = base.size
    if v["glow"] > 0:
        g = mask.filter(ImageFilter.GaussianBlur(glow_px * SS)).point(lambda p: int(min(255, p * glow_a * v["glow"])))
        base = Image.alpha_composite(base, solid(size, rgb, g))
    return Image.alpha_composite(base, solid(size, rgb, mask))


# --- the pieces --------------------------------------------------------------------------------------------

def menu_icon(kind, v):
    base = frame(118, 118, ic.BOX, v, stroke=2 if v["shape"] != "round-small" else 1)
    cx, cy = ic.CX, ic.CY
    lw = ic.LINE if v["shape"] != "round-small" else 2
    if kind == "settings":
        g = ic.gear_mask(118, 118, cx, cy, 21, 15.5)
        m = ImageChops.add(ic.outline(g, lw), ic.ring(118, 118, cx, cy, 6.5, lw))
    elif kind == "guide":
        p = ic.pad_mask(118, 118, cx, cy + 1, 50, 30)
        m = ImageChops.add(ic.outline(p, lw), ic.pad_details(118, 118, cx, cy + 1, 50, 30, lw))
    elif kind == "memcard":
        c = ic.memcard_mask(118, 118, cx, cy, 32, 42)
        m = ImageChops.add(ic.outline(c, lw), ic.memcard_details(118, 118, cx, cy, 32, 42, lw))
    else:  # resume: a screen with a play mark
        wx, wy, ww, wh = 25, 33, 68, 52
        base = frame(118, 118, (wx - 6, wy - 6, wx + ww + 6, wy + wh + 6), v, stroke=2)
        win = shape_mask(118, 118, (wx, wy, wx + ww, wy + wh), v["shape"])
        base = Image.alpha_composite(base, solid(base.size, ic.WINDOW, win))
        tri = ic.shape(118, 118, lambda d, s: d.polygon(
            [((wx + ww / 2 - 6) * s, (wy + wh / 2 - 8) * s), ((wx + ww / 2 - 6) * s, (wy + wh / 2 + 8) * s),
             ((wx + ww / 2 + 8) * s, (wy + wh / 2) * s)], fill=255))
        base = Image.alpha_composite(base, solid(base.size, v["line"], tri.point(lambda p: p * 45 // 100)))
        return base.resize((118, 118), Image.LANCZOS)
    return lines(base, m, v["line"], v).resize((118, 118), Image.LANCZOS)


def play_button(v, font):
    w, h = 220, 72
    box = (14, 14, 206, 58)
    base = frame(w, h, box, v, edge=v["focus"], stroke=2, glow_px=7, glow_a=0.6)
    s = SS
    size = base.size
    tri_h = 20
    f = ImageFont.truetype(font, 26 * s)
    tw = f.getbbox("PLAY", anchor="lm")
    tw = (tw[2] - tw[0]) / s
    gx = (box[0] + box[2]) / 2 - (tri_h * 0.87 + 10 + tw) / 2
    cy = (box[1] + box[3]) / 2
    tri = Image.new("L", size, 0)
    ImageDraw.Draw(tri).polygon([(gx * s, (cy - tri_h / 2) * s), (gx * s, (cy + tri_h / 2) * s),
                                 ((gx + tri_h * 0.87) * s, cy * s)], fill=255)
    base = lines(base, tri, v["focus"], v)
    d = ImageDraw.Draw(base)
    d.text(((gx + tri_h * 0.87 + 10) * s, cy * s), "PLAY", font=f, fill=WHITE + (255,), anchor="lm")
    return base.resize((w, h), Image.LANCZOS)


def recolour(im, rgb, strip_glow=False):
    a = im.getchannel("A")
    if strip_glow:
        a = a.point(lambda p: 0 if p < 150 else min(255, int((p - 150) * 255 / 105)))
    out = Image.new("RGBA", im.size, rgb + (0,))
    out.putalpha(a)
    return out


def art(w, h, c1, c2, title, font):
    im = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=tuple(round(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)) + (255,))
    d.ellipse([w * 0.18, h * 0.24, w * 0.82, h * 0.88], fill=tuple(min(255, x + 40) for x in c2) + (255,))
    d.rectangle([0, 0, w, h * 0.2], fill=(15, 15, 20, 255))
    f = ImageFont.truetype(font, max(9, int(h * 0.1)))
    d.text((w / 2, h * 0.1), title, font=f, fill=(250, 250, 250, 255), anchor="mm")
    return im


def jewel_case(w, h, c1, c2, title, font):
    """A CD jewel case: the insert behind clear plastic, the dark hinge spine, a diagonal sheen, a rim."""
    spine = max(6, w // 14)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    im.alpha_composite(art(w - spine, h, c1, c2, title, font), (spine, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, spine - 1, h], fill=(18, 18, 22, 255))
    for y in range(4, h - 4, max(3, h // 40)):
        d.line([(1, y), (spine - 2, y)], fill=(44, 44, 50, 255))
    sheen = Image.new("L", (w, h), 0)
    ImageDraw.Draw(sheen).polygon([(w * 0.45, 0), (w * 0.75, 0), (w * 0.3, h), (0, h)], fill=60)
    sheen = sheen.filter(ImageFilter.GaussianBlur(w / 30))
    im = Image.alpha_composite(im, solid((w, h), (255, 255, 255), sheen))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, h - 1], outline=(210, 220, 230, 160), width=1)
    return im


def flat_cover(w, h, c1, c2, title, font):
    im = art(w, h, c1, c2, title, font)
    ImageDraw.Draw(im).rectangle([0, 0, w * 0.06, h], fill=(20, 20, 24, 255))
    return im


def perspective(im, lean):
    """lean > 0: the right edge recedes; < 0: the left edge recedes."""
    w, h = im.size
    dd = abs(lean) * h
    if lean > 0:
        data = (0, 0, 0, h, w, h + dd, w, -dd)
    else:
        data = (0, -dd, 0, h + dd, w, h, w, 0)
    nw = int(w * (1 - abs(lean) * 0.8))
    return im.transform((nw, h), Image.QUAD, data, Image.BICUBIC, fillcolor=(0, 0, 0, 0)) if nw != w else im


def reflect(im, frac=0.3, strength=0.3):
    h = int(im.height * frac)
    r = im.transpose(Image.FLIP_TOP_BOTTOM).crop((0, 0, im.width, h))
    grad = Image.linear_gradient("L").resize((im.width, h)).point(lambda p: int((255 - p) * strength))
    r.putalpha(ImageChops.multiply(grad, r.getchannel("A")))
    return r


def txt(d, xy, s, font, fill, anchor="la", shadow=True):
    if shadow:
        d.text((xy[0] + 1, xy[1] + 2), s, font=font, fill=(0, 0, 0, 150), anchor=anchor)
    d.text(xy, s, font=font, fill=fill, anchor=anchor)


def phosphor(scr, draw_fn, rgb, v):
    """Draw text on its own layer and add a soft glow of it (the CRT variant's headings)."""
    layer = Image.new("RGBA", scr.size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer))
    if v["phosphor"]:
        g = layer.getchannel("A").filter(ImageFilter.GaussianBlur(4)).point(lambda p: int(p * 0.8))
        scr.alpha_composite(solid(scr.size, rgb, g))
    scr.alpha_composite(layer)


# --- the screen --------------------------------------------------------------------------------------------

GAMES = [("NEON RUN", (20, 60, 120), (60, 190, 230)), ("STAR KNIGHT", (90, 20, 60), (230, 90, 120)),
         ("DEEP ORBIT", (10, 30, 40), (40, 160, 140)), ("IRON FIST", (60, 40, 10), (220, 150, 40)),
         ("PIXEL QUEST", (40, 20, 90), (140, 90, 230)), ("TURBO KART", (80, 10, 10), (240, 70, 40)),
         ("SKY PATROL", (10, 50, 80), (120, 200, 240)), ("GHOST TOWN", (30, 30, 30), (130, 130, 140))]
LEFT = [("RETRO RALLY", (50, 70, 20), (170, 210, 60)), ("MOON BASE", (20, 20, 50), (90, 110, 200)),
        ("LAVA LAND", (90, 30, 0), (250, 120, 30)), ("ICE PALACE", (20, 60, 80), (170, 230, 250))]


def render(key, v, bold, med, bg=None, label=True):
    head = v["heading"] or bold
    scr = (bg.convert("RGBA").resize((1280, 720)) if bg is not None else
           Image.open(os.path.join(A, "bg-direction-a-01-smooth.png")).convert("RGBA").resize((1280, 720)))
    if v["shape"] == "round-small":  # minimal: calm the background down
        scr = Image.alpha_composite(scr, Image.new("RGBA", scr.size, (8, 11, 16, 170)))
    make = jewel_case if v["cases"] else flat_cover

    # the carousel
    x = 785
    for k, (t, c1, c2) in enumerate(GAMES[1:]):
        size = 118 - k * 4
        cv = make(size, size, c1, c2, t, bold)
        if v["cases"]:
            cv = perspective(cv, 0.08)
        scr.alpha_composite(cv, (x, 100 + (118 - size) // 2))
        scr.alpha_composite(reflect(cv, 0.3, 0.22), (x, 100 + (118 - size) // 2 + size + 2))
        x += cv.width - (34 if v["cases"] else 40)
    for k in reversed(range(len(LEFT))):
        t, c1, c2 = LEFT[k]
        size = 110 - k * 4
        cv = make(size, size, c1, c2, t, bold)
        if v["cases"]:
            cv = perspective(cv, -0.08)
        cv.putalpha(cv.getchannel("A").point(lambda p: p * 50 // 100))
        scr.alpha_composite(cv, (530 - 30 - cv.width - k * 60, 104 + (110 - size) // 2))
    sel = make(220, 220, *GAMES[0][1:], GAMES[0][0], bold)
    if v["glow"] > 0:
        gm = Image.new("L", (300, 300), 0)
        ImageDraw.Draw(gm).rectangle([40, 40, 260, 260], fill=255)
        scr.alpha_composite(solid((300, 300), v["focus"], gm.filter(ImageFilter.GaussianBlur(16)).point(
            lambda p: int(p * 0.45 * min(1, v["glow"])))), (490, 53))
    else:  # minimal: a thin cyan underline marks the selection
        ImageDraw.Draw(scr).rectangle([530, 93 + 226, 750, 93 + 228], fill=v["focus"] + (255,))
    scr.alpha_composite(sel, (530, 93))
    scr.alpha_composite(reflect(sel, 0.3, 0.3), (530, 93 + 232))

    # details and the meta row
    d = ImageDraw.Draw(scr)
    phosphor(scr, lambda dd: txt(dd, (786, 214), "Neon Run", ImageFont.truetype(head, 30), WHITE), v["line"], v)
    d = ImageDraw.Draw(scr)
    f = ImageFont.truetype(med, 15)
    txt(d, (787, 258), "Made-up Studio, 1997", f, GREY)
    txt(d, (787, 278), "Serial: SLUS-00000, Region: USA", f, GREY)
    txt(d, (787, 298), "Last played: yesterday", f, GREY)
    minimal = v["glow"] == 0

    def ev(n):
        im = Image.open(os.path.join(A, "evoimg", f"{n}-direction-a-01.png")).convert("RGBA")
        return recolour(im, v["line"], strip_glow=minimal) if v["line"] != CYAN or minimal else im

    my = 322
    if minimal:  # a thin outline pad, no tile
        pm = ic.outline(ic.pad_mask(30, 30, 15, 15.5, 22, 13), 1.4)
        pad = solid(pm.size, v["line"], pm).resize((30, 30), Image.LANCZOS)
    else:
        pad = ic.icon_meta()
    scr.alpha_composite(pad, (784, my))
    txt(d, (818, my + 15), "1 Player", ImageFont.truetype(bold, 15), WHITE, anchor="lm")
    xx = 900
    for n, extra in (("cd", "1"), ("favorite", None), ("sd", None), ("lock", None)):
        icon = ev(n)
        scr.alpha_composite(icon, (xx, my + (30 - icon.height) // 2))
        xx += icon.width + 6
        if extra:
            txt(d, (xx - 2, my + 15), extra, ImageFont.truetype(bold, 15), WHITE, anchor="lm")
            xx += 16
        xx += 6

    # Play and the game menu
    play = play_button(v, head)
    scr.alpha_composite(play, (640 - play.width // 2, 402))
    for k, n in enumerate(("settings", "guide", "memcard", "resume")):
        icon = menu_icon(n, v).resize((96, 96), Image.LANCZOS)
        scr.alpha_composite(icon, (640 - 48 + k * 118, 500))

    # the banner and the hint bar
    def panel(w, h):
        return frame(w, h, (1, 1, w - 1, h - 1), v, stroke=2 if not minimal else 1, body_alpha=225,
                     glow_px=5, glow_a=0.35, ss=3).resize((w, h), Image.LANCZOS)

    scr.alpha_composite(panel(420, 46), (1280 - 16 - 420, 16))
    d = ImageDraw.Draw(scr)
    phosphor(scr, lambda dd: txt(dd, (1280 - 16 - 420 + 20, 16 + 23), "Showing: All games (24)",
                                 ImageFont.truetype(head, 20), WHITE, anchor="lm"), v["line"], v)
    hx, hy, hw = 1280 - 16 - 840, 720 - 12 - 76, 840
    scr.alpha_composite(panel(hw, 76), (hx, hy))
    d = ImageDraw.Draw(scr)
    hf = ImageFont.truetype(med, 19)

    def keycap(label):
        f2 = ImageFont.truetype(bold, 12)
        w_ = int(d.textlength(label, font=f2)) + 12
        k = Image.new("RGBA", (w_, 22), (0, 0, 0, 0))
        kd = ImageDraw.Draw(k)
        kd.rounded_rectangle([0, 0, w_ - 1, 21], radius=4, fill=(70, 82, 96, 255))
        kd.text((w_ / 2, 11), label, font=f2, fill=WHITE, anchor="mm")
        return k

    def hint_row(y, items):
        widths = [icon.width + 6 + d.textlength(label, font=hf) for icon, label in items]
        x0 = hx + (hw - sum(widths) - 34 * (len(items) - 1)) / 2
        for (icon, label), w_ in zip(items, widths):
            scr.alpha_composite(icon, (int(x0), int(y - icon.height / 2)))
            txt(d, (x0 + icon.width + 6, y), label, hf, WHITE, anchor="lm", shadow=False)
            x0 += w_ + 34

    hint = lambda n: Image.open(os.path.join(DEF, "images", n)).convert("RGBA")  # noqa: E731
    small = lambda im: im.resize((24, 24), Image.LANCZOS)  # noqa: E731
    hint_row(hy + 24, [(hint("hint_cross.png"), "Play"), (small(ev("dpad_down")), "Game menu"),
                       (small(ev("dpad_up")), "Quick menu")])
    hint_row(hy + 54, [(keycap("SELECT"), "Games shown"), (keycap("START"), "Random"),
                       (hint("hint_triangle.png"), "Guide"), (keycap("L2+R2"), "System")])

    # the logo
    logo = Image.open(os.path.join(A, "logo", "logo-c3.png")).convert("RGBA")
    logo = logo.resize((int(logo.width * 0.72), int(logo.height * 0.72)), Image.LANCZOS)
    scr.alpha_composite(logo, (6, 720 - logo.height + 38))

    # CRT: scanlines and a vignette over everything
    if v["scan"]:
        sl = Image.new("L", scr.size, 0)
        sd = ImageDraw.Draw(sl)
        for y in range(0, 720, 2 if v.get("bezel") else 3):
            sd.line([(0, y), (1280, y)], fill=v["scan"])
        scr = Image.alpha_composite(scr, solid(scr.size, (0, 0, 0), sl))
    if v["vignette"]:
        vg = Image.radial_gradient("L").resize((1280, 720)).point(
            lambda p: int(max(0, p - 110) * v["vignette"] * 1.6))
        scr = Image.alpha_composite(scr, solid(scr.size, (0, 0, 0), vg))

    if v.get("bezel"):  # the tube's rounded corners
        bz = Image.new("L", (1280 * 2, 720 * 2), 255)
        ImageDraw.Draw(bz).rounded_rectangle([6, 6, 2560 - 7, 1440 - 7], radius=90, fill=0)
        bz = bz.filter(ImageFilter.GaussianBlur(6)).resize((1280, 720), Image.LANCZOS)
        scr = Image.alpha_composite(scr, solid(scr.size, (0, 0, 0), bz))

    # label
    d = ImageDraw.Draw(scr)
    if label:
        d.text((14, 12), f"v02{key}  {v['name']}", font=ImageFont.truetype(bold, 16), fill=(255, 255, 255, 200))
    return scr.convert("RGB")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--launcher", required=True)
    a = ap.parse_args()
    fonts = os.path.join(a.launcher, "src", "resources", "fonts")
    bold, med = os.path.join(fonts, "OpenSans-Bold.ttf"), os.path.join(fonts, "OpenSans-Medium.ttf")
    out = os.path.join(A, "mockup")
    os.makedirs(out, exist_ok=True)
    shots = []
    for key, v in VARIANTS.items():
        im = render(key, v, bold, med)
        p = os.path.join(out, f"launcher-games-direction-a-02{key}.png")
        im.save(p)
        shots.append(im)
    grid = Image.new("RGB", (1280, 720))
    for k, im in enumerate(shots):
        grid.paste(im.resize((640, 360), Image.LANCZOS), ((k % 2) * 640, (k // 2) * 360))
    grid.save(os.path.join(out, "launcher-variants-02.png"))
    print("written:", out)


if __name__ == "__main__":
    main()
