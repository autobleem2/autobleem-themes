"""The 4:3 launcher backgrounds (layout4x3.images.background, 640x480) of aergb, default, evolution, ab2 and
Legacy of 2018, cut from each
theme's own 16:9 launcher_background.png - nothing new is drawn but what the 4:3 layout moves:

  aergb, default   the 800x600 window at (400, 0) of the 1280x720 art (the arc and the hill, clear of the hint
                   swoosh and the logo at its foot), scaled to 640x480; the AutoBleem logo cut from the 16:9 art
                   and set again in the top-right corner (the 4:3 hint bar runs the full width at the foot)
  evolution        the art shifted so its circle and cover frame sit on the 4:3 carousel's cover (196, 214 at
                   640x480; the art at 1.5x of the canvas, its own scale), the details box moved and sized to the
                   4:3 meta block (308, 162, 292 x 110 plus a margin); the texture under the old box is copied up
                   from the rows below it
  ab2              the circuit art's 800x600 window at (400, 0), clear of its logo and band at the foot; its
                   wordmark ("AUTOBLEEM 2 / PS CLASSIC MODIFICATION HUB") cut off the art and set again top-right
  Legacy of 2018   the 960x720 window at (240, 0): the column of PlayStation symbols at the left edge, the cover
                   beside it rather than on it; no logo (its art has none)

Each also gets a 4:3 hint band (images/launcher_footer_4x3.png, 640 x 66 at the canvas's foot): its own 16:9 band
fitted to the 4:3 hint bar - these themes' hint colours are made for that band - and evolution, whose logo was in the
footer it no longer shows, the AutoBleem logo top-right like the other two.
Writes Themes/<name>/images/launcher_background_4x3.png and launcher_footer_4x3.png. With --shots <dir> also a sheet of the three with the 4:3
layout's boxes drawn on (cover, play, meta, menu row, hint bar).
Run: python tools/make_4x3_backgrounds.py [--shots <dir>]
"""
import json
import os
import sys

import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
THEMES = os.path.join(HERE, "..", "Themes")
SHOTS = sys.argv[sys.argv.index("--shots") + 1] if "--shots" in sys.argv else None
W, H = 640, 480

# aergb / default: the window of the 16:9 art that becomes the 4:3 picture, and the logo in the 16:9 art
WINDOW = (400, 0, 1200, 600)
LOGO_BOX = (70, 515, 350, 712)          # the stacked "Auto Bleem" + its small arc + the four symbols
LOGO_H = 52                             # its height at 640x480, top-right, clear of the side-cover shelf (y 60)
LOGO_XY = (626, 8)                      # its top-right corner

# evolution: the art's cover square centre and details box (1280x720), and where the 4:3 layout wants them
EVO_SQUARE = (523, 176, 757, 410)
EVO_BOX = (765, 285, 1279, 418)
EVO_CIRCLE = (640, 310, 205)           # the disc (centre, radius with its rim), symmetric about x 640
K = 1.5                                 # the 16:9 art's pixels per 4:3 canvas pixel (720 / 480)
COVER = (196, 214)                      # layout4x3.carousel centre
META = (308, 162, 292, 110)             # layout4x3.meta x, y, w, h
META_PAD = 6


def logo_cut(art):
    """the logo as RGBA: its white letters, black outline, the small rainbow arc and the symbols, off the blue"""
    box = art.crop(LOGO_BOX).convert("RGB")
    hsv = box.convert("HSV")
    a = Image.new("L", box.size, 0)
    pa, pr, ph = a.load(), box.load(), hsv.load()
    for y in range(box.height):
        for x in range(box.width):
            r, g, b = pr[x, y]
            h, s, v = ph[x, y]
            lum = (r * 3 + g * 6 + b) / 10
            blue = 120 <= h <= 175 and s > 90             # the background's blues (PIL hue 0-255)
            if lum > 170 or lum < 34 or (not blue and s > 110 and v > 120):
                pa[x, y] = 255
    a = a.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))     # close the outline's gaps
    keep = a.getbbox()
    out = box.convert("RGBA")
    out.putalpha(a.filter(ImageFilter.GaussianBlur(0.6)))
    return out.crop(keep)


def arc_theme(name):
    art = Image.open(os.path.join(THEMES, name, "images", "launcher_background.png")).convert("RGBA")
    im, box = with_logo(art.crop(WINDOW).resize((W, H), Image.LANCZOS))
    return im, {"logo": box}


def evolution():
    art = Image.open(os.path.join(THEMES, "evolution", "images", "launcher_background.png")).convert("RGB")
    # 1. the details box out: the texture under it from the same columns 160 rows down (clear of the box and its shadow) (the maze repeats nothing
    #    a viewer can follow), its edges a few px wider so the frame line goes too
    #    - where the box crosses the circle, the circle's own mirror image from its left half (it is symmetric)
    l, t, r, b = EVO_BOX
    src = art.copy()
    px, sp = art.load(), src.load()
    cx, cy, cr = EVO_CIRCLE
    for y in range(t - 12, b + 13):                   # the box and its drop shadow
        for x in range(l - 12, min(r + 1, art.width)):
            if (x - cx) ** 2 + (y - cy) ** 2 <= cr * cr:
                px[x, y] = sp[2 * cx - x, y]
            else:
                px[x, y] = sp[x, y + 160]
    # 2. the canvas at the art's own scale (960x720), shifted so the cover square's centre lands on the 4:3 cover
    cw, ch = round(W * K), round(H * K)
    sx = (EVO_SQUARE[0] + EVO_SQUARE[2]) / 2 - COVER[0] * K
    sy = (EVO_SQUARE[1] + EVO_SQUARE[3]) / 2 - COVER[1] * K
    canvas = Image.new("RGB", (cw, ch))
    canvas.paste(art, (round(-sx), round(-sy)))
    # past the art's edges: its last columns / rows repeated (the stripe and the texture run on)
    ox, oy = round(-sx), round(-sy)
    if ox + art.width < cw:
        edge = art.crop((art.width - (cw - ox - art.width), 0, art.width, art.height))
        canvas.paste(edge, (ox + art.width, oy))
    if oy > 0:
        canvas.paste(canvas.crop((0, oy, cw, 2 * oy)), (0, 0))
    # 3. the details box again, on the 4:3 meta block: the art's own look - a dark veil and a light 3 px line
    x, y, w, h = META
    bx = (round((x - META_PAD) * K), round((y - META_PAD) * K), round((x + w + META_PAD) * K), round((y + h + META_PAD) * K))
    veil = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(veil)
    d.rectangle(bx, fill=(4, 18, 40, 150))
    d.rectangle(bx, outline=(200, 212, 226, 210), width=3)
    canvas = Image.alpha_composite(canvas.convert("RGBA"), veil)
    im, box = with_logo(canvas.resize((W, H), Image.LANCZOS))          # its 16:9 logo sits in the footer it loses
    return im, {"details box": tuple(round(v / K) for v in bx), "logo": box}


# the 4:3 hint band (layout4x3.images.footer): the theme's own 16:9 band under the hints, fitted to the 4:3 hint bar
# (8, 418, 624 x 58) - the hint colours of these themes are made for their band (aergb's and evolution's are dark),
# so without it the labels sink into the background. The footer picture sits on the canvas's foot, full width.
FOOT_H = 66                             # the picture: y 414..480
BAND = (-30, 2, 640, 64)                # the band inside it: its slanted end half off the left edge, so the first hint
                                        # column stands on the band's flat inside; it runs off the right edge as in 16:9
BAND_SRC = {                            # the band's parallelogram in the 16:9 art: top-left, top-right, foot-right, foot-left
    "aergb": ((455, 617), (1280, 617), (1280, 694), (394, 694)),
    "default": ((412, 612), (1280, 612), (1280, 708), (352, 708)),
}
# aergb's strip is mostly frame (black 8, rainbow 12, silver 40, rainbow 10 + shadow of 77 rows): scaled as a whole its
# silver inside is too low for the two hint lines (the owner, 2026-10-06: "wyzszy pasek") - rows (16:9 art) -> px
BAND_ROWS = {
    "aergb": (((617, 627), 3), ((627, 639), 4), ((639, 679), 50), ((679, 694), 5)),
}
EVO_SLOT_X = 522                        # evolution's footer: the silver bar right of its POWER / logo / OPEN block
AB2_BAND = (462, 621, 1280, 695)        # ab2's cyan hint band in its 16:9 art (a plain rectangle)
AB2_WORDMARK = (24, 600, 440, 700)      # its "AUTOBLEEM 2" + tagline, under the emblem
AB2_WORDMARK_H = 30
LEGACY_WINDOW = (240, 0, 1200, 720)


def footer(name):
    out = Image.new("RGBA", (W, FOOT_H), (0, 0, 0, 0))
    if name == "evolution":
        f = Image.open(os.path.join(THEMES, name, "images", "launcher_footer.png")).convert("RGBA")
        out = f.crop((EVO_SLOT_X, 0, f.width, f.height)).resize((W, FOOT_H), Image.LANCZOS)
        return out
    if name == "Legacy of 2018":                        # its 16:9 footer is a plain silver bar: the whole of it
        f = Image.open(os.path.join(THEMES, name, "images", "launcher_footer.png")).convert("RGBA")
        return f.resize((W, FOOT_H), Image.LANCZOS)
    if name == "ab2":
        art = Image.open(os.path.join(THEMES, name, "images", "AB-EvoBack.jpg")).convert("RGBA")
        out.alpha_composite(art.crop(AB2_BAND).resize((W - 8, BAND[3] - BAND[1]), Image.LANCZOS), (8, BAND[1]))
        return out
    art = Image.open(os.path.join(THEMES, name, "images", "launcher_background.png")).convert("RGBA")
    poly = BAND_SRC[name]
    x0, y0 = min(p[0] for p in poly), min(p[1] for p in poly)
    x1, y1 = max(p[0] for p in poly), max(p[1] for p in poly)
    mask = Image.new("L", art.size, 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    band = art.crop((x0, y0, x1, y1))
    band.putalpha(mask.crop((x0, y0, x1, y1)))
    bw, bh = BAND[2] - BAND[0], BAND[3] - BAND[1]
    if name in BAND_ROWS:                               # rebuilt row band by row band: a thinner frame, a taller inside
        b = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        y = 0
        for (r0, r1), h in BAND_ROWS[name]:
            b.alpha_composite(band.crop((0, r0 - y0, band.width, r1 - y0)).resize((bw, h), Image.LANCZOS), (0, y))
            y += h
        assert y == bh
    else:
        b = band.resize((bw, bh), Image.LANCZOS)
    out.paste(b, (BAND[0], BAND[1]), b)                 # paste: its left end may start off the picture
    return out


def with_logo(im):
    """the AutoBleem logo from aergb's 16:9 art, top-right"""
    logo = logo_cut(Image.open(os.path.join(THEMES, "aergb", "images", "launcher_background.png")))
    logo = logo.resize((round(logo.width * LOGO_H / logo.height), LOGO_H), Image.LANCZOS)
    im = im.convert("RGBA")
    im.alpha_composite(logo, (LOGO_XY[0] - logo.width, LOGO_XY[1]))
    return im.convert("RGB"), (LOGO_XY[0] - logo.width, LOGO_XY[1], LOGO_XY[0], LOGO_XY[1] + LOGO_H)


def ab2():
    art = Image.open(os.path.join(THEMES, "ab2", "images", "AB-EvoBack.jpg")).convert("RGBA")
    im = art.crop(WINDOW).resize((W, H), Image.LANCZOS)
    wm = art.crop(AB2_WORDMARK)
    # its alpha: the bright letters off the dark art, softened at the edge
    lum = wm.convert("L").point(lambda v: max(0, min(255, (v - 70) * 3)))
    wm.putalpha(lum.filter(ImageFilter.GaussianBlur(0.5)))
    wm = wm.crop(lum.point(lambda v: 255 if v > 60 else 0).getbbox())
    wm = wm.resize((round(wm.width * AB2_WORDMARK_H / wm.height), AB2_WORDMARK_H), Image.LANCZOS)
    x, y = LOGO_XY[0] - wm.width, LOGO_XY[1] + 4
    shade = Image.new("RGBA", im.size, (0, 0, 0, 0))   # a soft dark plate so it reads on the busy circuit
    ImageDraw.Draw(shade).rounded_rectangle((x - 8, y - 6, x + wm.width + 8, y + wm.height + 6), 8, fill=(0, 10, 30, 150))
    im = Image.alpha_composite(im, shade.filter(ImageFilter.GaussianBlur(4)))
    im.alpha_composite(wm, (x, y))
    # the game details on the busy circuit: a soft dark plate behind the meta box
    mx, my, mw, mh = META
    shade = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(shade).rounded_rectangle((mx - 12, my - 8, mx + mw + 12, my + mh + 8), 12, fill=(0, 8, 24, 175))
    im = Image.alpha_composite(im, shade.filter(ImageFilter.GaussianBlur(8)))
    return im.convert("RGB"), {"wordmark": (x, y, x + wm.width, y + wm.height), "meta plate": META}


DEV_ZONE = (0, 64, 126, 102)            # the launcher's DEV badge + build id, top-left at 640x480 - kept clear of symbols


def legacy():
    art = Image.open(os.path.join(THEMES, "Legacy of 2018", "images", "launcher_background.png")).convert("RGB")
    im = art.crop(LEGACY_WINDOW).resize((W, H), Image.LANCZOS)
    # the plain gradient under the symbols: a smooth (cubic) surface fitted to the symbol-free part of the art, right
    # of the symbols' cascade, then used where the symbols must go
    a = np.asarray(im, dtype=np.float64)
    yy, xx = np.mgrid[0:H, 0:W]
    u, v = xx / W, yy / H
    terms = [u ** i * v ** j for i in range(4) for j in range(4 - i)]
    free = xx > 200                                   # the cascade ends at canvas x ~190
    A = np.stack([t[free] for t in terms], 1)
    plain = np.zeros_like(a)
    for c in range(3):
        coef = np.linalg.lstsq(A, a[..., c][free], rcond=None)[0]
        plain[..., c] = sum(k * t for k, t in zip(coef, terms))
    plain = Image.fromarray(np.clip(plain, 0, 255).round().astype(np.uint8))
    # every symbol that reaches into the zone goes whole (no half-faded symbols): the symbols are the pixels off the
    # plain gradient, each one a connected blob
    sym = np.abs(a - np.asarray(plain, dtype=np.float64)).max(2) > 12
    blobs, _ = ndimage.label(sym, structure=np.ones((3, 3)))
    x0, y0, x1, y1 = DEV_ZONE
    gone = np.isin(blobs, np.unique(blobs[y0:y1, x0:x1])[1:])
    gone = ndimage.binary_dilation(gone, iterations=2)
    mask = Image.fromarray((gone * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))
    im = Image.composite(plain, im, mask)
    im, box = with_logo(im)
    return im, {"logo": box, "dev zone": DEV_ZONE}


def layout(name):
    return json.load(open(os.path.join(THEMES, "ab2.0.0", "theme.json"), encoding="utf-8"))["layout4x3"]


def sheet(results):
    lay = layout("ab2.0.0")
    tiles = []
    for name, (im, extra) in results.items():
        t = im.convert("RGBA")
        t.alpha_composite(footer(name), (0, H - FOOT_H))
        d = ImageDraw.Draw(t)
        c = lay["carousel"]
        m = c["coverMax"] / 2
        d.rectangle((c["centreX"] - m, c["centreY"] - m, c["centreX"] + m, c["centreY"] + m), outline=(255, 255, 255), width=2)
        p, me, hb = lay["playButton"], lay["meta"], lay["hintBar"]
        d.rectangle((p["x"], p["y"], p["x"] + p["w"], p["y"] + p["h"]), outline=(255, 210, 0), width=2)
        d.rectangle((me["x"], me["y"], me["x"] + me["w"], me["y"] + me["h"]), outline=(0, 255, 140), width=2)
        d.rectangle((hb["x"], hb["y"], hb["x"] + hb["w"], hb["y"] + hb["h"]), outline=(255, 70, 170), width=2)
        d.rectangle((0, c["shelfY"], W, c["shelfY"] + c["shelfH"]), outline=(160, 160, 160), width=1)
        tiles.append(t)
    out = Image.new("RGB", (len(tiles) * (W + 10), H), (0, 0, 0))
    for i, t in enumerate(tiles):
        out.paste(t.convert("RGB"), (i * (W + 10), 0))
    os.makedirs(SHOTS, exist_ok=True)
    out.save(os.path.join(SHOTS, "backgrounds-4x3-boxes.png"))
    for name, (im, _) in results.items():
        im.save(os.path.join(SHOTS, "%s-background-4x3.png" % name))


def main():
    results = {"aergb": arc_theme("aergb"), "default": arc_theme("default"), "evolution": evolution(), "ab2": ab2(),
               "Legacy of 2018": legacy()}
    for name, (im, extra) in results.items():
        im.save(os.path.join(THEMES, name, "images", "launcher_background_4x3.png"), optimize=True)
        footer(name).save(os.path.join(THEMES, name, "images", "launcher_footer_4x3.png"), optimize=True)
        print(name, extra)
    if SHOTS:
        sheet(results)


if __name__ == "__main__":
    main()
