"""The default theme's hint band: the launcher background's bottom strip, redrawn so the launcher's two hint lines
(UIREV-36, launcher.hintBar) sit on it readably.

The original strip (y 620..690: a black frame, a rainbow line, a 40 px silver inside) was made for one line of dark
text; the launcher now writes two lines of white text there, and the hintBar (360,632 900x64) also ran over the
strip's slanted corner next to the logo. The new band keeps the strip's idea - the slanted left end, a black frame,
the rainbow line of the big swoosh - but is 96 px high (y 612..708) with a dark navy inside, starts clear of the
logo (x 352 at its foot), and the hintBar is its inside: 430,620 832x80.

Writes Themes/default/images/launcher_background.png from the original (kept as
read back from git (ORIG_REV) into tmp/, never committed; the script always starts from it) and, with --shots <dir>, before/after mockups of the launcher's
bottom with the hints drawn as the code lays them out (4 columns x 2 lines).
Run: python tools/make_default_hintband.py [--shots <dir>]
"""
import json
import subprocess
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
THEME = os.path.join(HERE, "..", "Themes", "default")
IMG = os.path.join(THEME, "images", "launcher_background.png")
ORIG = os.path.join(HERE, "..", "tmp", "default_launcher_background.orig.png")   # a local copy, never committed
ORIG_REV = "006d636"   # the last commit with the original art (the strip), read back from git
SHOTS = sys.argv[sys.argv.index("--shots") + 1] if "--shots" in sys.argv else None
SS = 4
Y0, Y1 = 612, 708                   # the band
X_TOP, X_FOOT = 412, 352            # its slanted left end (the original leans the same way)
HINTBAR = (430, 620, 832, 80)       # launcher.hintBar: the band's inside
RAINBOW = [(0.0, (226, 30, 60)), (0.18, (240, 120, 30)), (0.36, (236, 196, 30)), (0.56, (110, 190, 80)),
           (0.76, (20, 168, 160)), (1.0, (44, 122, 196))]


def grad(t):
    for (a, ca), (b, cb) in zip(RAINBOW, RAINBOW[1:]):
        if t <= b:
            k = (t - a) / (b - a)
            return tuple(round(ca[i] + (cb[i] - ca[i]) * k) for i in range(3))
    return RAINBOW[-1][1]


def band_poly(inset):
    """the band's outline grown inward by inset px: the slanted left end, the right end off the screen"""
    slope = (X_TOP - X_FOOT) / (Y1 - Y0)
    y0, y1 = Y0 + inset, Y1 - inset
    return [(X_TOP + slope * inset + inset * 0.6 - slope * 0, y0), (1300, y0), (1300, y1),
            (X_FOOT + inset * 0.6 + (slope * inset), y1)]


def mask(poly):
    m = Image.new("L", (1280 * SS, 720 * SS), 0)
    ImageDraw.Draw(m).polygon([(x * SS, y * SS) for x, y in poly], fill=255)
    return m.resize((1280, 720), Image.LANCZOS)


def build():
    if not os.path.exists(ORIG):
        os.makedirs(os.path.dirname(ORIG), exist_ok=True)
        data = subprocess.check_output(["git", "-C", HERE, "show", ORIG_REV + ":Themes/default/images/launcher_background.png"])
        open(ORIG, "wb").write(data)
    bg = Image.open(ORIG).convert("RGBA")
    # 1. a soft shadow under the band
    sh = mask(band_poly(-2)).filter(ImageFilter.GaussianBlur(6))
    bg.alpha_composite(Image.merge("RGBA", [Image.new("L", bg.size, 0)] * 3 + [sh.point(lambda p: p * 160 // 255)]))
    # 2. the black frame, 3. the rainbow line, 4. the navy inside (a slight vertical gradient)
    bg.alpha_composite(Image.merge("RGBA", [Image.new("L", bg.size, 6)] * 3 + [mask(band_poly(0))]))
    rb = Image.new("RGBA", bg.size)
    px = rb.load()
    for x in range(300, 1280):
        c = grad((x - 340) / 940)
        for y in range(Y0, Y1 + 1):
            px[x, y] = c + (255,)
    ring = mask(band_poly(3))
    rb.putalpha(ring)
    bg.alpha_composite(rb)
    inside = Image.new("RGBA", bg.size)
    d = ImageDraw.Draw(inside)
    for y in range(Y0, Y1 + 1):
        k = (y - Y0) / (Y1 - Y0)
        d.line([(0, y), (1280, y)], fill=(round(22 - 8 * k), round(40 - 12 * k), round(70 - 18 * k), 248))
    inside.putalpha(mask(band_poly(7)).point(lambda p: p * 248 // 255))
    bg.alpha_composite(inside)
    # a hairline of light along the inside's top edge
    hl = Image.new("RGBA", bg.size, (130, 183, 237, 0))
    m = Image.new("L", bg.size, 0)
    top = band_poly(7)
    ImageDraw.Draw(m).line([(top[0][0] + 6, Y0 + 8), (1280, Y0 + 8)], fill=90)
    hl.putalpha(m)
    bg.alpha_composite(hl)
    bg.convert("RGB").save(IMG)
    return Image.open(ORIG).convert("RGBA"), bg


before, after = build()
print("ok", IMG)
if not SHOTS:
    sys.exit(0)

os.makedirs(SHOTS, exist_ok=True)
spec = json.load(open(os.path.join(THEME, "theme.json"), encoding="utf-8"))
FONT = os.path.join(THEME, spec["classic"]["font"]["file"])
btn = lambda n: Image.open(os.path.join(THEME, spec["classic"]["buttons"][n])).convert("RGBA")
LINES = [[("cross", "Play"), ("square", "Play in RetroArch"), ("down", "Game menu"), ("up", "Quick menu")],
         [("SELECT", "Games shown"), ("START", "Random"), ("triangle", "Guide"), ("L2+R2", "System")]]


def hints(im, rect, colour):
    x0, y0, w, h = rect
    d = ImageDraw.Draw(im)
    size = 22
    while size > 14:                                   # the code: the largest size at which 4 columns fit
        f = ImageFont.truetype(FONT, size)
        widths = [max(30 + 8 + f.getlength(LINES[l][c][1]) for l in range(2)) for c in range(4)]
        if sum(widths) + 3 * 24 <= w - 32:
            break
        size -= 1
    chip_f = ImageFont.truetype(FONT, max(12, size - 8))
    colx = [x0 + 12]
    for c in range(3):
        colx.append(colx[-1] + widths[c] + 24 + (w - 32 - sum(widths) - 72) / 3)
    lh = h / 2
    for l, line in enumerate(LINES):
        cy = y0 + lh * l + lh / 2
        for c, (b, label) in enumerate(line):
            x = colx[c]
            if b in spec["classic"]["buttons"]:
                im.alpha_composite(btn(b).resize((26, 26), Image.LANCZOS), (int(x), int(cy - 13)))
                x += 26 + 8
            elif b in ("up", "down"):
                ay = cy
                pts = [(x + 4, ay - 4), (x + 22, ay - 4), (x + 13, ay + 8)] if b == "down" else \
                      [(x + 4, ay + 6), (x + 22, ay + 6), (x + 13, ay - 6)]
                d.polygon(pts, fill=(54, 217, 224))
                x += 26 + 8
            else:
                cw = chip_f.getlength(b) + 14
                d.rounded_rectangle([x, cy - 11, x + cw, cy + 11], 4, outline=(200, 210, 225), width=1, fill=(40, 48, 64))
                d.text((x + cw / 2, cy), b, font=chip_f, fill=(240, 240, 240), anchor="mm")
                x += cw + 8
            d.text((x, cy), label, font=ImageFont.truetype(FONT, size), fill=colour, anchor="lm")
    return size


old = json.load(open(os.path.join(THEME, "theme.json"), encoding="utf-8"))["launcher"]["hintBar"]
b = before.copy()
s1 = hints(b, (old["x"], old["y"], old["w"], old["h"]), (255, 255, 255))
a = after.copy()
s2 = hints(a, HINTBAR, (255, 255, 255))
b.convert("RGB").save(os.path.join(SHOTS, "launcher-hints-now.png"))
a.convert("RGB").save(os.path.join(SHOTS, "launcher-hints-new.png"))
pair = Image.new("RGB", (1280, 2 * 250 + 30), (14, 16, 20))
pair.paste(b.convert("RGB").crop((0, 470, 1280, 720)), (0, 0))
pair.paste(a.convert("RGB").crop((0, 470, 1280, 720)), (0, 280))
ImageDraw.Draw(pair).text((10, 254), "above: today (hintBar 360,632 900x64 over the silver strip)   below: the new band (hintBar %d,%d %dx%d)" % HINTBAR, fill=(230, 230, 230))
pair.save(os.path.join(SHOTS, "launcher-hints-compare.png"))
print("shots ok, font", s1, s2)
