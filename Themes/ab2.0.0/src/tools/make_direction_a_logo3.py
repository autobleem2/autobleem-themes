"""Direction A (CONSOLE-14): logo B4 in the v02b style - the "2" capsule with cut corners.

C1 = B4 with the chamfered capsule, cyan rim; C2 = the same with a magenta rim; C3 = C2 with its own underline
under the 2 (the owner, 2026-09-29), also drawn in cyan for comparison. The bar under the wordmark
gets a cut end too. Writes design/direction-a/logo/logo-c1/c2.png (+@2x) and logo-b4-vs-c.png: B4, C1, C2
on the background, and each at the launcher's corner on the v02b mockup.
Run: python tools/make_direction_a_logo3.py --font-dir ../../../repos/autobleem/src/resources/fonts
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_direction_a_logo as base  # noqa: E402  (parses --font-dir)
from make_direction_a_logo import (  # noqa: E402
    CYAN, WHITE, STEEL, OS_BOLD, OS_MED, SS, canvas, text_img, glow, vgradient, fill_with, paste_center, finish)

MAGENTA = (255, 70, 170)


def chamfer(d, box, c, fill):
    x0, y0, x1, y1 = box
    d.polygon([(x0, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1), (x0 + c, y1), (x0, y1 - c)], fill=fill)


def c_logo(scale, rim_rgb, underline_two=False):
    k = scale * SS
    im = canvas(k)
    auto = text_img("AUTO", OS_MED, 54, k, STEEL, tracking=2)
    bleem = text_img("BLEEM", OS_BOLD, 54, k, WHITE, tracking=2)
    two = text_img("2", OS_BOLD, 47, k, WHITE)
    pill_h = round(bleem.height * 1.35)
    pill_w = round(pill_h * 1.2)
    gap, gap2 = 8 * k, 16 * k
    total = auto.width + gap + bleem.width + gap2 + pill_w
    x0 = round(240 * k - total / 2)
    base_y = 190 * k
    im.alpha_composite(auto, (x0, base_y - auto.height))
    im.alpha_composite(bleem, (x0 + auto.width + gap, base_y - bleem.height))
    px0 = x0 + auto.width + gap + bleem.width + gap2
    pcy = base_y - bleem.height / 2
    py0, py1 = round(pcy - pill_h / 2), round(pcy + pill_h / 2)
    c = round(pill_h * 0.3)
    rim = Image.new("L", im.size, 0)
    chamfer(ImageDraw.Draw(rim), (px0, py0, px0 + pill_w, py1), c, 255)
    inner = Image.new("L", im.size, 0)
    s = 3 * k
    chamfer(ImageDraw.Draw(inner), (px0 + s, py0 + s, px0 + pill_w - s, py1 - s), round(c - s * 0.4), 255)
    im.alpha_composite(glow(fill_with(rim, Image.new("RGBA", im.size, rim_rgb + (255,))), 6 * k, rim_rgb, 0.7))
    im.alpha_composite(fill_with(inner, vgradient(im.size, (46, 55, 66), (33, 40, 49))))
    paste_center(im, two, px0 + pill_w / 2, pcy)
    # the bar: fading to the right, its left end cut like the shapes
    bar = canvas(k)
    gd = ImageDraw.Draw(bar)
    bx0, bx1 = x0, x0 + total
    y0, y1 = base_y + 22 * k, base_y + 27 * k
    for x in range(bx0, bx1):
        t = (x - bx0) / max(1, bx1 - bx0)
        top = y0 + max(0, (bx0 + 5 * k) - x)  # the cut at the left end
        gd.line([(x, top), (x, y1)], fill=CYAN + (round(255 * (1 - t) ** 1.4),))
    im.alpha_composite(glow(bar, 5 * k, CYAN, 0.8))
    if underline_two:
        # C3: the 2 gets its own underline in the capsule's colour, on the bar's line, cut like the shapes
        ul = canvas(k)
        ud = ImageDraw.Draw(ul)
        ux0, ux1 = px0, px0 + pill_w
        cut = 5 * k
        ud.polygon([(ux0, y1), (ux0 + cut, y0), (ux1, y0), (ux1 - cut, y1)], fill=rim_rgb + (255,))
        im.alpha_composite(glow(ul, 5 * k, rim_rgb, 0.9))
    return finish(im, scale)


def main():
    out = base.OUT
    c1, c2 = c_logo(1, CYAN), c_logo(1, MAGENTA)
    c3, c3c = c_logo(1, MAGENTA, True), c_logo(1, CYAN, True)
    c3.save(os.path.join(out, "logo-c3.png"))
    c3c.save(os.path.join(out, "logo-c3-cyan.png"))
    c_logo(2, MAGENTA, True).save(os.path.join(out, "logo-c3@2x.png"))
    c1.save(os.path.join(out, "logo-c1.png"))
    c2.save(os.path.join(out, "logo-c2.png"))
    c_logo(2, CYAN).save(os.path.join(out, "logo-c1@2x.png"))
    c_logo(2, MAGENTA).save(os.path.join(out, "logo-c2@2x.png"))
    b4 = Image.open(os.path.join(out, "logo-b4.png")).convert("RGBA")
    # row 1: the three at 1x on the background; row 2: each in the v02b mockup's corner
    bg = Image.open(os.path.join(os.path.dirname(base.OUT), "bg-direction-a-01-smooth.png")).convert("RGBA").resize((1280, 720))
    mock = Image.open(os.path.join(os.path.dirname(base.OUT), "mockup", "launcher-games-direction-a-02b.png")).convert("RGBA")
    sheet = Image.new("RGBA", (1920, 300 + 330), (0, 0, 0, 255))
    names = ("C1 sciete, cyjan", "C2 sciete, magenta", "C3 magenta + podkreslona 2", "C3 cyjan + podkreslona 2")
    f = ImageFont.truetype(OS_BOLD, 18)
    for i, (lg, nm) in enumerate(zip((c1, c2, c3, c3c), names)):
        tile = bg.crop((400, 200, 880, 500))
        tile.alpha_composite(lg, (0, -30))
        sheet.alpha_composite(tile, (i * 480, 0))
        # the corner of the mockup: clear the old logo with the background's own pixels, place this one
        m = mock.copy()
        m.alpha_composite(bg.crop((0, 560, 420, 720)), (0, 560))
        small = lg.resize((int(lg.width * 0.72), int(lg.height * 0.72)), Image.LANCZOS)
        m.alpha_composite(small, (6, 720 - small.height + 38))
        sheet.alpha_composite(m.crop((0, 470, 720, 720)).resize((480, 167), Image.LANCZOS), (i * 480, 300))
        d = ImageDraw.Draw(sheet)
        d.text((i * 480 + 12, 10), nm, font=f, fill=(255, 255, 255, 230))
    ImageDraw.Draw(sheet).text((12, 480), "w rogu ekranu (fragment mockupu v02b)", font=f, fill=(200, 210, 220, 255))
    sheet = sheet.crop((0, 0, 1920, 470))
    sheet.convert("RGB").save(os.path.join(out, "logo-b4-vs-c.png"))
    print("written:", out)


if __name__ == "__main__":
    main()
