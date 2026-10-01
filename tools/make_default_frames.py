"""The default theme's frames (launcher.frames): 9-slice PNGs at 1x and @2x for every classic panel and dialog, the
keyboard, the footers and the bubbles - the same flat style as the bridge set the imported 1.0 themes get (a thin
rim, a soft corner, no gradient), cut to default's own look: black sheets over the blue background, white text,
grey secondary. Sizes and limits follow docs/theme-format.md "Frames" (and autobleem-core's ab-gui-frames-spec.md).

Drawn in white/grey/black + alpha and tinted "text" (white) or "selectionBand", so a colour change in
launcher.colors still reaches them; the panel and the bubbles carry their own dark sheet (the code draws no sheet
under a frame that has a centre).

Writes Themes/default/frames/ and prints the launcher.frames block. With --shots <dir> it also draws mockups of the
Options list and the keyboard on default's background, tinted as the code tints (multiply), plus a sheet.
Run: python tools/make_default_frames.py [--shots <dir>]
"""
import json
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
THEME = os.path.join(HERE, "..", "Themes", "default")
OUT = os.path.join(THEME, "frames")
SHOTS = sys.argv[sys.argv.index("--shots") + 1] if "--shots" in sys.argv else None
os.makedirs(OUT, exist_ok=True)
SS = 8


def rrect_mask(size, box, r, corners=None):
    """an anti-aliased rounded-rectangle mask (box/r in pixels of this scale)"""
    w, h = size
    m = Image.new("L", (w * SS, h * SS), 0)
    x0, y0, x1, y1 = box
    kw = {"corners": corners} if corners else {}
    ImageDraw.Draw(m).rounded_rectangle([x0 * SS, y0 * SS, x1 * SS - 1, y1 * SS - 1], radius=r * SS, fill=255, **kw)
    return m.resize((w, h), Image.LANCZOS)


def ring(size, box, r, t, corners=None):
    x0, y0, x1, y1 = box
    return ImageChops.subtract(rrect_mask(size, box, r, corners),
                               rrect_mask(size, (x0 + t, y0 + t, x1 - t, y1 - t), max(0, r - t), corners))


def layer(size, mask, grey, alpha):
    im = Image.new("RGBA", size, (grey, grey, grey, 0))
    im.putalpha(mask.point(lambda p: round(p * alpha / 255)))
    return im


def sheet(w, h, bleed, r, sheet_a, rim_a, shadow_a):
    """a panel-like frame: a soft shadow in the bleed, its own sheet (a dark grey the tint turns into the theme's
    dark colour), a light hairline rim (the tint itself)"""
    def draw(s):
        size = (w * s, h * s)
        b = bleed * s
        box = (b, b, size[0] - b, size[1] - b)
        im = Image.new("RGBA", size, (0, 0, 0, 0))
        sh = rrect_mask(size, (box[0], box[1] + 2 * s, box[2], box[3] + 3 * s), r * s).filter(
            ImageFilter.GaussianBlur(min(b, 5 * s)))
        im.alpha_composite(layer(size, ImageChops.subtract(sh, rrect_mask(size, box, r * s)), 0, shadow_a))
        im.alpha_composite(layer(size, rrect_mask(size, box, r * s), SHEET_GREY, sheet_a))
        im.alpha_composite(layer(size, ring(size, box, r * s, s), 255, rim_a))
        return im
    return draw


def plate(w, h, bleed, r, fill_grey, fill_a, rim_a, glow_a=0):
    """the small frame: a fill and a 1 px rim, a soft glow in the bleed if asked"""
    def draw(s):
        size = (w * s, h * s)
        b = bleed * s
        box = (b, b, size[0] - b, size[1] - b)
        im = Image.new("RGBA", size, (0, 0, 0, 0))
        if glow_a:
            g = rrect_mask(size, box, r * s).filter(ImageFilter.GaussianBlur(2 * s))
            im.alpha_composite(layer(size, ImageChops.subtract(g, rrect_mask(size, box, r * s)), 255, glow_a))
        im.alpha_composite(layer(size, rrect_mask(size, box, r * s), fill_grey, fill_a))
        im.alpha_composite(layer(size, ring(size, box, r * s, s), 255, rim_a))
        return im
    return draw


def selection(s):
    size = (48 * s, 40 * s)
    b = 4 * s
    box = (b, b, size[0] - b, size[1] - b)
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    im.alpha_composite(layer(size, rrect_mask(size, box, 6 * s), 255, 64))            # the band, 25 %
    im.alpha_composite(layer(size, ring(size, box, 6 * s, s), 255, 175))              # the rim
    bar = Image.new("L", size, 0)
    ImageDraw.Draw(bar).rectangle([box[0] + s, box[1] + 5 * s, box[0] + 4 * s - 1, box[3] - 5 * s - 1], fill=255)
    im.alpha_composite(layer(size, bar, 255, 255))                                    # the 3 px bar
    return im


def heading(s):
    size = (40 * s, 24 * s)
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    im.alpha_composite(layer(size, rrect_mask(size, (0, 0, size[0], size[1]), 4 * s), 255, 22))   # 9 %
    foot = Image.new("L", size, 0)
    ImageDraw.Draw(foot).rectangle([4 * s, size[1] - s, size[0] - 4 * s - 1, size[1] - 1], fill=255)
    im.alpha_composite(layer(size, foot, 255, 80))
    return im


def footer(s):
    """64x62: a 56x54 body + 4 bleed; a darker strip with a hairline along its top, the panel's bottom corners"""
    size = (64 * s, 62 * s)
    b = 4 * s
    box = (b, b, size[0] - b, size[1] - b)
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    im.alpha_composite(layer(size, rrect_mask(size, box, 6 * s, (False, False, True, True)), SHEET_GREY // 2, 120))
    top = Image.new("L", size, 0)
    ImageDraw.Draw(top).rectangle([box[0] + 12 * s, box[1], box[2] - 12 * s - 1, box[1] + s - 1], fill=255)
    im.alpha_composite(layer(size, top, 255, 70))
    return im


def tab(s):
    """48x48, no bleed: a quiet band and a 4 px bar along the bottom (the current set)"""
    size = (48 * s, 48 * s)
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    im.alpha_composite(layer(size, rrect_mask(size, (0, 0, size[0], size[1]), 6 * s, (True, True, False, False)), 255, 38))
    bar = Image.new("L", size, 0)
    ImageDraw.Draw(bar).rounded_rectangle([8 * s, size[1] - 4 * s, size[0] - 8 * s - 1, size[1] - 1], radius=2 * s, fill=255)
    im.alpha_composite(layer(size, bar, 255, 255))
    return im


def bar(alpha):
    def draw(s):
        size = (16 * s, 8 * s)
        return layer(size, rrect_mask(size, (0, 0, size[0], size[1]), 3 * s), 255, alpha)
    return draw


SL = lambda l, t: {"left": l, "top": t, "right": l, "bottom": t}
SHEET_GREY = 62   # x the edge role = the sheet: default #82b7ed -> #1f2c3a (a dark navy)
FRAMES = {
    "panel": (sheet(96, 96, 12, 6, 200, 150, 150), {"slice": 36, "bleed": 12, "tint": "edge"}),
    "selection": (selection, {"slice": SL(12, 10), "bleed": 4, "tint": "selectionBand"}),
    "heading": (heading, {"slice": SL(12, 6), "tint": "edge"}),
    "key": (plate(48, 48, 4, 5, 255, 30, 120), {"slice": 16, "bleed": 4, "tint": "edge"}),
    "keyFunction": (plate(48, 48, 4, 5, 255, 16, 80), {"slice": 16, "bleed": 4, "tint": "edge"}),
    "keyLit": (plate(48, 48, 4, 5, 255, 80, 210), {"slice": 16, "bleed": 4, "tint": "edge"}),
    "keySelected": (plate(48, 48, 4, 5, 255, 115, 255, glow_a=200), {"slice": 16, "bleed": 4, "tint": "selectionBand"}),
    "field": (plate(56, 56, 4, 5, 30, 170, 170), {"slice": 16, "bleed": 4, "tint": "edge"}),
    "chip": (plate(32, 32, 2, 4, 255, 50, 170), {"slice": 10, "bleed": 2, "tint": "edge"}),
    "badge": (plate(40, 40, 4, 5, 30, 170, 150), {"slice": 12, "bleed": 4, "tint": "edge"}),
    "footer": (footer, {"slice": 16, "bleed": 4, "tint": "edge"}),
    "toast": (sheet(64, 64, 8, 8, 215, 165, 160), {"slice": 20, "bleed": 8, "tint": "edge"}),
    "plate": (sheet(48, 48, 2, 6, 210, 130, 0), {"slice": 16, "bleed": 2, "tint": "edge"}),
    "tab": (tab, {"slice": 16, "tint": "selectionBand"}),
    "progressTrack": (bar(64), {"slice": SL(4, 2), "tint": "edge"}),
    "progressFill": (bar(255), {"slice": SL(4, 2), "tint": "text"}),
}
FILE_NAMES = {"keyFunction": "key_function", "keyLit": "key_lit", "keySelected": "key_selected",
              "progressTrack": "progress_track", "progressFill": "progress_fill"}
images, entries = {}, {}
for name, (fn, spec) in FRAMES.items():
    fname = FILE_NAMES.get(name, name)
    one, two = fn(1), fn(2)
    one.save(os.path.join(OUT, fname + ".png"), optimize=True)
    two.save(os.path.join(OUT, fname + "@2x.png"), optimize=True)
    images[name] = one
    entries[name] = dict({"image": "frames/%s.png" % fname}, **spec)
print(json.dumps(entries, indent=2))
if not SHOTS:
    sys.exit(0)

# --- the mockups: drawn as the code draws (9-slice, tint = multiply) ---
os.makedirs(SHOTS, exist_ok=True)
spec = json.load(open(os.path.join(THEME, "theme.json"), encoding="utf-8"))
colors = spec["launcher"]["colors"]


def role(name):
    v = colors.get(name, "#ffffff")
    return role(v) if not v.startswith("#") else v


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def tinted(im, hexcol):
    c = rgb(hexcol)
    r, g, b, a = im.split()
    r, g, b = (ch.point(lambda p, k=k: round(p * k / 255)) for ch, k in zip((r, g, b), c))
    return Image.merge("RGBA", (r, g, b, a))


def nine(dst, name, box, frames_dir=None):
    fs = FRAMES[name][1]
    src = tinted(images[name], role(fs["tint"]))
    bl = fs.get("bleed", 0)
    x, y, w, h = box[0] - bl, box[1] - bl, box[2] + 2 * bl, box[3] + 2 * bl
    v = fs.get("slice", 0)
    L, T, R, B = (v, v, v, v) if isinstance(v, int) else (v["left"], v["top"], v["right"], v["bottom"])
    sw, sh = src.size
    cols = [(0, L, x, L), (L, sw - R, x + L, w - L - R), (sw - R, sw, x + w - R, R)]
    rows = [(0, T, y, T), (T, sh - B, y + T, h - T - B), (sh - B, sh, y + h - B, B)]
    for sy0, sy1, dy, dh in rows:
        for sx0, sx1, dx, dw in cols:
            if dw > 0 and dh > 0:
                dst.alpha_composite(src.crop((sx0, sy0, sx1, sy1)).resize((dw, dh), Image.LANCZOS), (dx, dy))


FONT = os.path.join(THEME, spec["classic"]["font"]["file"])
f = lambda n: ImageFont.truetype(FONT, n)
title, row_f, head_f, hint_f, key_f, chip_f = f(30), f(22), f(16), f(18), f(24), f(13)
TEXT, ROW, HEAD = rgb(role("text")), rgb(role("row")), rgb(role("heading"))
VALUE, FOOT = rgb(role("value")), rgb(role("footer"))
mp = spec["classic"]["menuPanel"]
P = (mp["x"], mp["y"], mp["w"], mp["h"])


def background():
    return Image.open(os.path.join(THEME, spec["classic"]["background"])).convert("RGBA").resize((1280, 720))


def footer_hints(im, d, px, py, pw, ph, items):
    fy = py + ph - 54
    nine(im, "footer", (px, fy, pw, 54))
    x = px + 24
    for chip, what in items:
        if chip in spec["classic"]["buttons"]:            # a face button is the theme's image, not a chip
            b = Image.open(os.path.join(THEME, spec["classic"]["buttons"][chip])).convert("RGBA").resize((28, 28), Image.LANCZOS)
            im.alpha_composite(b, (x, fy + 13))
            x += 28 + 8
        else:
            cw = max(28, round(chip_f.getlength(chip)) + 14)
            nine(im, "chip", (x, fy + 15, cw, 24))
            d.text((x + cw // 2, fy + 27), chip, font=chip_f, fill=TEXT, anchor="mm")
            x += cw + 8
        d.text((x, fy + 27), what, font=hint_f, fill=FOOT, anchor="lm")
        x += round(hint_f.getlength(what)) + 28


# 1. Options, in default's own menuPanel rect, with a toast and the battery plate
im = background()
px, py, pw, ph = P
nine(im, "panel", P)
d = ImageDraw.Draw(im)
d.text((px + 28, py + 20), "Options", font=title, fill=TEXT)
y = py + 74
rows = [("h", "Interface"), ("r", "Display", "Auto"), ("s", "Cover style", "default"), ("r", "Cover shine", "On"),
        ("r", "Theme", "default"), ("h", "Sound"), ("r", "Music", "On"), ("r", "Background music", "On"),
        ("r", "Menu sounds", "On")]
for r in rows:
    if r[0] == "h":
        nine(im, "heading", (px + 2, y + 4, pw - 4, 24))
        d.text((px + 32, y + 16), r[1].upper(), font=head_f, fill=HEAD, anchor="lm")
        y += 34
        continue
    if r[0] == "s":
        nine(im, "selection", (px + 2, y, pw - 4, 44))
    d.text((px + 32, y + 22), r[1], font=row_f, fill=TEXT if r[0] == "s" else ROW, anchor="lm")
    d.text((px + pw - 28, y + 22), r[2], font=row_f, fill=TEXT if r[0] == "s" else VALUE, anchor="rm")
    y += 44
footer_hints(im, d, px, py, pw, ph, (("cross", "Choose"), ("circle", "Back"), ("START", "Save"), ("L1", "Page")))
tx, ty = 1280 - 24 - 440, 24
nine(im, "toast", (tx, ty, 440, 72))
d.text((tx + 16, ty + 20), "Scanning games", font=hint_f, fill=TEXT, anchor="lm")
d.text((tx + 16, ty + 42), "Crash Bandicoot (12 / 40)", font=chip_f, fill=ROW, anchor="lm")
nine(im, "progressTrack", (tx + 16, ty + 58, 408, 4))
nine(im, "progressFill", (tx + 16, ty + 58, 122, 4))
options = im
options.convert("RGB").save(os.path.join(SHOTS, "default-options.png"))

# 2. the keyboard
im = background()
nine(im, "panel", P)
d = ImageDraw.Draw(im)
d.text((px + 28, py + 20), "Game name", font=title, fill=TEXT)
for i, b in enumerate(("USB", "HD", "SD")):
    bx = px + pw - 28 - (3 - i) * 44
    nine(im, "badge", (bx, py + 24, 32, 32))
    d.text((bx + 16, py + 40), b, font=chip_f, fill=TEXT, anchor="mm")
fx, fy, fw = px + 60, py + 84, pw - 120
nine(im, "field", (fx, fy, fw, 48))
d.text((fx + 16, fy + 24), "Crash Bandicoot", font=key_f, fill=TEXT, anchor="lm")
cx = fx + 16 + key_f.getlength("Crash Bandicoot") + 2
d.rectangle([cx, fy + 12, cx + 1, fy + 36], fill=TEXT)
kw, kh, gap = 96, 56, 8
kx0 = px + (pw - (10 * kw + 9 * gap)) // 2
ky = fy + 48 + 22
for r, keys in enumerate(["1234567890", "qwertyuiop", "asdfghjkl'", "zxcvbnm,.-"]):
    for c, ch in enumerate(keys):
        x, yy = kx0 + c * (kw + gap), ky + r * (kh + gap)
        nine(im, "keySelected" if (r, c) == (1, 4) else "key", (x, yy, kw, kh))
        d.text((x + kw // 2, yy + kh // 2), ch, font=key_f, fill=TEXT, anchor="mm")
yy, x = ky + 4 * (kh + gap), kx0
for word, span, fr in (("Shift", 2, "keyLit"), ("Space", 4, "keyFunction"), ("Del", 2, "keyFunction"),
                       ("Done", 2, "keyFunction")):
    w = span * kw + (span - 1) * gap
    nine(im, fr, (x, yy, w, kh))
    d.text((x + w // 2, yy + kh // 2), word, font=hint_f, fill=TEXT, anchor="mm")
    x += w + gap
footer_hints(im, d, px, py, pw, ph, (("START", "Done"), ("SELECT", "Shift"), ("L1", "Space"), ("R1", "Delete")))
keyboard = im
keyboard.convert("RGB").save(os.path.join(SHOTS, "default-keyboard.png"))

# 3. the sheet: both screens, then every frame at 2x on grey and on black
sh = Image.new("RGB", (1300, 2 * 370 + 420), (14, 16, 20))
d = ImageDraw.Draw(sh)
for i, (label, shot) in enumerate((("default - Options (+ a toast)", options), ("default - keyboard", keyboard))):
    d.text((20 + i * 640, 10), label, font=hint_f, fill=(230, 230, 230))
    sh.paste(shot.convert("RGB").resize((620, 349), Image.LANCZOS), (20 + i * 640, 40))
y0 = 400
d.text((20, y0), "every frame as drawn (white/grey/black + alpha), 2x, on grey and on black", font=hint_f, fill=(230, 230, 230))
x, y = 20, y0 + 36
for name in FRAMES:
    fr = images[name]
    tiles = []
    for bg in ((128, 128, 128), (0, 0, 0)):
        t = Image.new("RGBA", fr.size, bg + (255,))
        t.alpha_composite(fr)
        tiles.append(t.resize((fr.width * 2, fr.height * 2), Image.NEAREST))
    need = sum(t.width for t in tiles) + 8
    if x + need > 1280:
        x, y = 20, y + 230
    for t in tiles:
        sh.paste(t.convert("RGB"), (x, y))
        x += t.width + 4
    d.text((x - need, y + tiles[0].height + 4), name, font=chip_f, fill=(200, 200, 200))
    x += 20
sh = sh.crop((0, 0, 1300, y + 230))
sh.save(os.path.join(SHOTS, "default-frames.png"))
print("shots ok")
