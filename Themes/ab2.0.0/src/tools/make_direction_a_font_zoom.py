"""Direction A (CONSOLE-14): Red Hat Text next to today's Open Sans, at 1:1, on the same crops of the screens.

Crops of the v02b launcher (p5) - the game's details, the Play button, the hint bar, the banner - and of the
v02b emulator menu - the rows' panel and the game's title - each drawn in both fonts, side by side.
Writes design/direction-a/fonts/zoom-redhat-vs-opensans.png.
Run: python tools/make_direction_a_font_zoom.py --launcher ../../../repos/autobleem --fonts ../../../tmp/fonts
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_direction_a_fonts as mf  # noqa: E402  (parses --launcher/--fonts, sets --font-dir)
import make_direction_a_emu_v2 as emu  # noqa: E402
import make_direction_a_screens_v2 as sc  # noqa: E402
import make_direction_a_variants as va  # noqa: E402

# (left, top, right, bottom) in 1280x720
LAUNCHER_CROPS = [("szczegoly gry", (770, 200, 1110, 360)), ("Play", (520, 390, 760, 480)),
                  ("banner", (840, 10, 1270, 70)), ("pasek podpowiedzi", (420, 626, 1272, 714))]
EMU_CROPS = [("menu emulatora", (28, 36, 580, 600)), ("tytul w emulatorze", (600, 30, 1000, 130))]


def screens(med, bold, lf, out):
    bg = Image.open(os.path.join(va.A, "bg-proc", "bg-p5.png")).convert("RGBA")
    evo = va.render("b", dict(va.VARIANTS["b"], heading=bold), bold, med, bg=bg, label=False)
    va.SAIRA = bold
    ef = os.path.join(out, "_emu_fonts")
    os.makedirs(ef, exist_ok=True)
    for src, dst in ((bold, "OpenSans-Bold.ttf"), (med, "OpenSans-Medium.ttf")):
        with open(src, "rb") as a, open(os.path.join(ef, dst), "wb") as b:
            b.write(a.read())
    return evo, emu.menu_v2(sc.emu(bg), ef)


def main():
    lf = os.path.join(mf.LAUNCHER, "src", "resources", "fonts")
    out = os.path.join(va.A, "fonts")
    os_ = ("Open Sans (dzis)", os.path.join(lf, "OpenSans-Medium.ttf"), os.path.join(lf, "OpenSans-Bold.ttf"))
    rh = mf.family("Red Hat Text", "other/RedHatText[wght].ttf", "other/RedHatText[wght].ttf", 500, 650)
    shots = {name: screens(med, bold, lf, out) for name, med, bold in (os_, rh)}
    crops = [(lab, box, 0) for lab, box in LAUNCHER_CROPS] + [(lab, box, 1) for lab, box in EMU_CROPS]
    gap, head = 24, 40
    widths = [b[2] - b[0] for _, b, _ in crops]
    heights = [b[3] - b[1] for _, b, _ in crops]
    colw = max(widths)
    W = 2 * colw + 3 * gap
    H = head + sum(h + head for h in heights) + gap * (len(crops) + 1)
    sheet = Image.new("RGB", (W, H), (12, 15, 20))
    d = ImageDraw.Draw(sheet)
    f_head = ImageFont.truetype(os.path.join(lf, "OpenSans-Bold.ttf"), 26)
    f_lab = ImageFont.truetype(os.path.join(lf, "OpenSans-Bold.ttf"), 20)
    for c, name in enumerate(shots):
        d.text((gap + c * (colw + gap), 8), name, font=f_head, fill=(54, 217, 224) if c else (154, 164, 178))
    y = head + gap
    for (lab, box, which), h in zip(crops, heights):
        for c, name in enumerate(shots):
            x = gap + c * (colw + gap)
            d.text((x, y), lab, font=f_lab, fill=(200, 210, 220))
            sheet.paste(shots[name][which].crop(box), (x, y + 30))
        y += h + head + gap
    sheet.save(os.path.join(out, "zoom-redhat-vs-opensans.png"))
    print("written")


if __name__ == "__main__":
    main()
