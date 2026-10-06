"""The 4:3 launcher backgrounds (layout4x3.images.background, 640x480) of aergb, default and evolution, cut from each
theme's own 16:9 launcher_background.png - nothing new is drawn but what the 4:3 layout moves:

  aergb, default   the 800x600 window at (400, 0) of the 1280x720 art (the arc and the hill, clear of the hint
                   swoosh and the logo at its foot), scaled to 640x480; the AutoBleem logo cut from the 16:9 art
                   and set again in the top-right corner (the 4:3 hint bar runs the full width at the foot)
  evolution        the art shifted so its circle and cover frame sit on the 4:3 carousel's cover (196, 214 at
                   640x480; the art at 1.5x of the canvas, its own scale), the details box moved and sized to the
                   4:3 meta block (308, 162, 292 x 110 plus a margin); the texture under the old box is copied up
                   from the rows below it

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
EVO_SLOT_X = 522                        # evolution's footer: the silver bar right of its POWER / logo / OPEN block


def footer(name):
    out = Image.new("RGBA", (W, FOOT_H), (0, 0, 0, 0))
    if name == "evolution":
        f = Image.open(os.path.join(THEMES, name, "images", "launcher_footer.png")).convert("RGBA")
        out = f.crop((EVO_SLOT_X, 0, f.width, f.height)).resize((W, FOOT_H), Image.LANCZOS)
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
    results = {"aergb": arc_theme("aergb"), "default": arc_theme("default"), "evolution": evolution()}
    for name, (im, extra) in results.items():
        im.save(os.path.join(THEMES, name, "images", "launcher_background_4x3.png"), optimize=True)
        footer(name).save(os.path.join(THEMES, name, "images", "launcher_footer_4x3.png"), optimize=True)
        print(name, extra)
    if SHOTS:
        sheet(results)


if __name__ == "__main__":
    main()
