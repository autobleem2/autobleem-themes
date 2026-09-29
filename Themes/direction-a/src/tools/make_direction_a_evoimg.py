"""Direction A (CONSOLE-14): the launcher's own small icons (its src/resources/evoimg/), drawn as vectors.

v01 (2026-09-29). These live in the launcher, not in a theme; this draws the Direction A versions as design
sources (same file names and canvases), so the look can be judged before deciding how they get in.
Left out on purpose: ps1.png and ra.png (third-party marks) and the 226x226 cover placeholders.
Writes design/direction-a/evoimg/*.png and a sheet: today's icons over the new ones.
Run: python tools/make_direction_a_evoimg.py --launcher ../../../repos/autobleem
"""
import argparse
import math
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
HERE = os.path.join(REPO, "Themes", "direction-a", "src", "design")
OUT = os.path.join(HERE, "evoimg")
BG = os.path.join(HERE, "bg-direction-a-01-smooth.png")

CYAN = (54, 217, 224)
SS = 8


def canvas(w, h):
    return Image.new("L", (w * SS, h * SS), 0)


def outline(mask, px):
    k = int(px * SS) * 2 + 1
    return ImageChops.subtract(mask, mask.filter(ImageFilter.MinFilter(k)))


def render(mask, w, h, glow_px=1.2, glow_a=0.7):
    size = mask.size
    out = Image.new("RGBA", size, CYAN + (0,))
    g = mask.filter(ImageFilter.GaussianBlur(glow_px * SS)).point(lambda v: int(min(255, v * glow_a)))
    out.putalpha(g)
    solid = Image.new("RGBA", size, CYAN + (0,))
    solid.putalpha(mask)
    return Image.alpha_composite(out, solid).resize((w, h), Image.LANCZOS)


def S(v):
    return v * SS


# --- badges: USB / SD / HD -------------------------------------------------------------------------------

def badge(text, w, h, box, font, px=1.4):
    m = canvas(w, h)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([S(v) for v in box], radius=S(3), fill=255)
    m = outline(m, px)
    d = ImageDraw.Draw(m)
    fs = S(box[3] - box[1]) * 0.62
    f = ImageFont.truetype(font, int(fs))
    d.text((S((box[0] + box[2]) / 2), S((box[1] + box[3]) / 2) + fs * 0.02), text, font=f, fill=255, anchor="mm")
    return m


# --- lock / unlock -----------------------------------------------------------------------------------------

def lock(open_):
    w = h = 30
    m = canvas(w, h)
    d = ImageDraw.Draw(m)
    # shackle: a thick arc; open = lifted and swung to the right
    sx = 21 if open_ else 15
    top = 2 if open_ else 4
    d.arc([S(sx - 6), S(top), S(sx + 6), S(top + 12)], 180, 360, fill=255, width=round(S(2.4)))
    d.line([S(sx - 6 + 1.2), S(top + 6), S(sx - 6 + 1.2), S(14 if not open_ else 11)], fill=255, width=round(S(2.4)))
    if not open_:
        d.line([S(sx + 6 - 1.2), S(top + 6), S(sx + 6 - 1.2), S(14)], fill=255, width=round(S(2.4)))
    body = canvas(w, h)
    ImageDraw.Draw(body).rounded_rectangle([S(7), S(13), S(23), S(27)], radius=S(3), fill=255)
    hole = canvas(w, h)
    hd = ImageDraw.Draw(hole)
    hd.ellipse([S(13.2), S(17), S(16.8), S(20.6)], fill=255)
    hd.rectangle([S(14.2), S(19), S(15.8), S(23.5)], fill=255)
    return ImageChops.subtract(ImageChops.lighter(m, body), hole)


# --- favourite (a star), disc, light guns ------------------------------------------------------------------

def star(w, h, cx, cy, r_out, r_in):
    m = canvas(w, h)
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        r = r_out if k % 2 == 0 else r_in
        pts.append((S(cx + r * math.cos(a)), S(cy + r * math.sin(a))))
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return m


def disc(w, h, cx, cy, r, px, hole):
    m = canvas(w, h)
    d = ImageDraw.Draw(m)
    d.ellipse([S(cx - r), S(cy - r), S(cx + r), S(cy + r)], outline=255, width=round(S(px)))
    d.ellipse([S(cx - hole), S(cy - hole), S(cx + hole), S(cy + hole)], outline=255, width=round(S(px)))
    # a short shine arc between the two rings
    rr = (r + hole) / 2
    d.arc([S(cx - rr), S(cy - rr), S(cx + rr), S(cy + rr)], 200, 250, fill=255, width=round(S(px * 0.8)))
    return m


def gun_poly(ox, oy, k):
    """A generic pistol facing left, in a 30-wide box, scaled by k."""
    # front sight, barrel, the grip slanting back, the trigger guard under the barrel
    p = [(1, 5), (2, 5), (2, 3.5), (4, 3.5), (4, 5), (28, 5), (28, 12), (26.5, 12), (25, 25), (18, 25),
         (19, 16), (15.5, 16), (14, 18.5), (10.5, 18.5), (11.5, 12), (1, 12)]
    return [(S(ox + x * k), S(oy + y * k)) for x, y in p]


def lightgun(two):
    w = h = 30
    m = canvas(w, h)
    d = ImageDraw.Draw(m)
    if not two:
        d.polygon(gun_poly(0.5, 1, 1.0), fill=255)
        # the trigger guard's opening
        d.polygon([(S(x), S(y)) for x, y in [(13.3, 13), (18.3, 13), (17.8, 15.8), (15, 15.8), (14.5, 17), (12.8, 17)]],
                  fill=0)
    else:
        d.polygon(gun_poly(0, 0, 0.6), fill=255)
        d.polygon(gun_poly(12.5, 13, 0.6), fill=255)
    return m


# --- tabs (64x64, line icons) and the d-pad hint arrows (28x28) ---------------------------------------------

def tab_apps():
    m = canvas(64, 64)
    d = ImageDraw.Draw(m)
    for x in (8, 35):
        for y in (8, 35):
            d.rounded_rectangle([S(x), S(y), S(x + 21), S(y + 21)], radius=S(5), outline=255, width=round(S(3)))
    return m


def tab_playstation():
    return disc(64, 64, 32, 32, 27, 3, 7)


def tab_retroarch():
    m = canvas(64, 64)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([S(8), S(40), S(56), S(56)], radius=S(5), outline=255, width=round(S(3)))
    d.line([S(24), S(40), S(24), S(18)], fill=255, width=round(S(3.5)))
    d.ellipse([S(16), S(5), S(32), S(21)], outline=255, width=round(S(3)))
    d.ellipse([S(39), S(26), S(47), S(34)], fill=255)
    d.ellipse([S(44), S(47), S(50), S(53)], fill=255)
    return ImageChops.offset(m, 0, int(1.5 * SS))  # optical centre


def dpad(direction):
    m = canvas(28, 28)
    # an arrow pointing up, then rotated
    pts = [(14, 2), (25, 13), (18, 13), (18, 26), (10, 26), (10, 13), (3, 13)]
    ImageDraw.Draw(m).polygon([(S(x), S(y)) for x, y in pts], fill=255)
    rot = {"up": 0, "left": 90, "down": 180, "right": 270}[direction]
    return m.rotate(rot, resample=Image.BICUBIC)


def build(font):
    icons = {
        "usb": (badge("USB", 30, 30, (1, 8, 29, 22), font), 30, 30),
        "sd": (badge("SD", 30, 30, (3, 8, 27, 22), font), 30, 30),
        "hd": (badge("HD", 30, 30, (3, 8, 27, 22), font), 30, 30),
        "lock": (lock(False), 30, 30),
        "unlock": (lock(True), 30, 30),
        "favorite": (star(29, 32, 14.5, 17, 12, 5.2), 29, 32),
        "cd": (disc(30, 30, 15, 15, 12.5, 2, 3.5), 30, 30),
        "lightgun": (lightgun(False), 30, 30),
        "lightgun2": (lightgun(True), 30, 30),
        "tab_apps": (tab_apps(), 64, 64),
        "tab_playstation": (tab_playstation(), 64, 64),
        "tab_retroarch": (tab_retroarch(), 64, 64),
    }
    for dname in ("up", "down", "left", "right"):
        icons[f"dpad_{dname}"] = (dpad(dname), 28, 28)
    return {n: render(m, w, h, glow_px=1.2 if w <= 32 else 2) for n, (m, w, h) in icons.items()}


def sheet(new, evo_dir):
    names = list(new)
    # a plain graphite backdrop and a fixed grid: every canvas centred in its cell at the same scale per size
    cell, left = 120, 70
    half = len(names) // 2
    w, h = left + cell * half + 20, 4 * cell + 40
    out = Image.new("RGBA", (w, h), (24, 29, 36, 255))
    d = ImageDraw.Draw(out)
    for block in range(2):
        y0 = 20 + block * 2 * cell
        d.rectangle([left - 10, y0 + cell, w - 20, y0 + cell], fill=(60, 70, 82, 255))
        d.text((12, y0 + cell // 2), "dzis", fill=(150, 160, 170, 255), anchor="lm")
        d.text((12, y0 + cell + cell // 2), "A v01", fill=CYAN + (255,), anchor="lm")
    for k, n in enumerate(names):
        col, block = k % half, k // half
        old = Image.open(os.path.join(evo_dir, n + ".png")).convert("RGBA")
        for row, im in enumerate((old, new[n])):
            f = 3 if im.width <= 32 else 1.5
            im = im.resize((round(im.width * f), round(im.height * f)), Image.LANCZOS)
            x = left + col * cell + (cell - im.width) // 2
            y = 20 + (block * 2 + row) * cell + (cell - im.height) // 2
            out.alpha_composite(im, (x, y))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--launcher", required=True, help="the launcher's checkout (for evoimg/ and the font)")
    a = ap.parse_args()
    evo = os.path.join(a.launcher, "src", "resources", "evoimg")
    font = os.path.join(a.launcher, "src", "resources", "fonts", "OpenSans-Bold.ttf")
    os.makedirs(OUT, exist_ok=True)
    new = build(font)
    for n, im in new.items():
        im.save(os.path.join(OUT, f"{n}-direction-a-01.png"))
    sheet(new, evo).save(os.path.join(OUT, "evoimg-sheet-01.png"))
    print("written:", OUT)


if __name__ == "__main__":
    main()
