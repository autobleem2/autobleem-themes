"""Direction A (CONSOLE-14): the launcher splash and the plymouth boot screen with logo B4.

The two stay slightly different, as today's pair does: the splash (launcher src/resources/splash/autobleem.jpg)
sets the logo on the Direction A background (the debanded copy, tools/deband.py) with a tagline; the plymouth picture (appliance
payload_linux/system/plymouth/splash.png) sets it on black - its script paints black around the picture and
fades it in - so the frame's edges stay pure black and only a soft glow sits behind the logo.

Writes into design/direction-a/splash/:
  splash-b4.jpg          1280x720, the launcher splash
  plymouth-b4.png        1280x720, the plymouth picture
  splash-compare.png     today's pair above, the new pair below
Run: python tools/make_direction_a_splash.py [--font-dir DIR] [--launcher DIR] [--appliance DIR]
"""
import argparse
import os
import sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
_ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
_ap.add_argument("--launcher", default=None, help="launcher checkout (for today's splash in the comparison)")
_ap.add_argument("--appliance", default=None, help="appliance checkout (for today's plymouth picture)")
ARGS, rest = _ap.parse_known_args()
sys.argv = [sys.argv[0]] + rest
import make_direction_a_logo as base  # noqa: E402  (parses --font-dir)
import make_direction_a_logo2 as logos  # noqa: E402
from deband import deband  # noqa: E402

OUT = os.path.join(base.DESIGN, "splash")
SW, SH = 1280, 720


def logo_at(width):
    """Logo B4 drawn at 2x, cropped to its content, scaled to the given width."""
    im = logos.b4_pill_two(2)
    im = im.crop(im.getchannel("A").getbbox())
    return im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)


def radial(size, center, radius, color, peak):
    """A soft radial glow of one colour, alpha falling from peak to 0 at radius."""
    small = (size[0] // 4, size[1] // 4)
    a = Image.new("L", small, 0)
    px = a.load()
    cx, cy, r = center[0] / 4, center[1] / 4, radius / 4
    for y in range(small[1]):
        for x in range(small[0]):
            d = (((x - cx) / r) ** 2 + ((y - cy) / (r * 0.55)) ** 2) ** 0.5
            if d < 1:
                px[x, y] = round(peak * (1 - d) ** 2)
    g = Image.new("RGBA", size, color + (0,))
    g.putalpha(a.resize(size, Image.BICUBIC))
    return g


def splash():
    bg = Image.open(os.path.join(base.DESIGN, "bg-direction-a-01-smooth.png")).convert("RGBA").resize((SW, SH), Image.LANCZOS)
    logo = logo_at(820)
    x, y = (SW - logo.width) // 2, 300 - logo.height // 2
    bg.alpha_composite(logo, (x, y))
    tag = base.text_img("RETRO GAME LAUNCHER", base.SAIRA, 24, 1, base.STEEL, tracking=10)
    bg.alpha_composite(tag, (x + 4, y + logo.height + 26))
    return bg.convert("RGB")


def plymouth():
    im = Image.new("RGBA", (SW, SH), (0, 0, 0, 255))
    im.alpha_composite(radial((SW, SH), (SW // 2, SH // 2), 560, (18, 40, 60), 200))
    im.alpha_composite(radial((SW, SH), (SW // 2, SH // 2 + 40), 380, base.CYAN, 26))
    logo = logo_at(720)
    im.alpha_composite(logo, ((SW - logo.width) // 2, (SH - logo.height) // 2))
    # the script paints black around the picture: keep a pure-black border so the seam never shows
    d = ImageDraw.Draw(im)
    for w in range(6):
        d.rectangle((w, w, SW - 1 - w, SH - 1 - w), outline=(0, 0, 0, 255))
    # the glows are 8-bit alpha ramps: smooth + dither them, but keep what was pure black exactly black
    rgb = im.convert("RGB")
    black = rgb.convert("L").point(lambda v: 255 if v == 0 else 0)
    return Image.composite(Image.new("RGB", rgb.size, (0, 0, 0)), deband(rgb), black)


def compare(new_splash, new_ply):
    tiles = []
    old_s = os.path.join(ARGS.launcher, "src", "resources", "splash", "autobleem.jpg") if ARGS.launcher else None
    old_p = os.path.join(ARGS.appliance, "payload_linux", "system", "plymouth", "splash.png") if ARGS.appliance else None
    for p in (old_s, old_p):
        tiles.append(Image.open(p).convert("RGB").resize((640, 360), Image.LANCZOS) if p and os.path.isfile(p) else None)
    tiles += [new_splash.resize((640, 360), Image.LANCZOS), new_ply.resize((640, 360), Image.LANCZOS)]
    labels = ["today: splash", "today: plymouth", "B4: splash", "B4: plymouth"]
    sheet = Image.new("RGB", (2 * 640 + 3 * 16, 2 * 360 + 3 * 16 + 2 * 36), (12, 15, 20))
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(base.OS_BOLD, 24)
    for i, (t, lab) in enumerate(zip(tiles, labels)):
        c, r = i % 2, i // 2
        x, y = 16 + c * (640 + 16), 16 + r * (360 + 16 + 36)
        d.text((x, y), lab, font=font, fill=base.CYAN if r else base.STEEL)
        if t is not None:
            sheet.paste(t, (x, y + 36))
    return sheet


def main():
    os.makedirs(OUT, exist_ok=True)
    s, p = splash(), plymouth()
    s.save(os.path.join(OUT, "splash-b4.jpg"), quality=95, subsampling=0)
    p.save(os.path.join(OUT, "plymouth-b4.png"))
    compare(s, p).save(os.path.join(OUT, "splash-compare.png"))
    print("written:", sorted(os.listdir(OUT)))


if __name__ == "__main__":
    main()
