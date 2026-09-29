"""Direction A (CONSOLE-14), v02b: the full-screen pictures with logo C3 (the owner, 2026-09-29).

  bg-direction-a-02p.png   a STAND-IN background drawn here (no lines by construction: a graphite-navy
                           gradient, a soft cyan glow up right, a faint magenta one low left, a darker bottom
                           third, fine grain, dithered) - until the FLUX space gives the real one
  splash/splash-c3.jpg     the launcher splash (src/resources/splash/autobleem.jpg)
  splash/plymouth-c3.png   the boot picture on black (appliance payload_linux/system/plymouth/splash.png)
  emu/ab_background-c3.jpg the emulator's in-game menu art (pcsx-abnxt frontend/ab/skin/ab_background.jpg):
                           the logo bottom left, the bar the menu writes its hints on (from x 490, y 647)
  screens-c3.png           the three side by side, the emulator art also with a sketch of the menu over it
Run: python tools/make_direction_a_screens_v2.py --font-dir ../../../repos/autobleem/src/resources/fonts
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_direction_a_logo as base  # noqa: E402  (parses --font-dir)
import make_direction_a_logo3 as l3  # noqa: E402
import make_direction_a_variants as va  # noqa: E402
from deband import deband  # noqa: E402

A = base.DESIGN
SW, SH = 1280, 720
MAGENTA = l3.MAGENTA


def glow(xx, yy, cx, cy, rx, ry):
    d = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
    return np.clip(1 - d, 0, 1) ** 2


def background():
    yy, xx = np.mgrid[0:SH, 0:SW].astype(np.float32)
    t = yy / SH
    top, mid, bot = np.array([44, 54, 68.]), np.array([24, 32, 46.]), np.array([9, 12, 18.])
    col = np.where((t < 0.55)[..., None], top + (mid - top) * (t / 0.55)[..., None],
                   mid + (bot - mid) * ((t - 0.55) / 0.45)[..., None])
    # a gentle side-to-side falloff so the frame is not a flat band
    col *= (1 - 0.18 * np.abs(xx / SW - 0.55) ** 1.5)[..., None]
    col += glow(xx, yy, 0.72 * SW, 0.18 * SH, 0.55 * SW, 0.55 * SH)[..., None] * np.array([30, 120, 135.]) * 0.55
    col += glow(xx, yy, 0.06 * SW, 0.95 * SH, 0.35 * SW, 0.35 * SH)[..., None] * np.array([140, 30, 95.]) * 0.35
    rng = np.random.default_rng(20260929)
    col += rng.normal(0, 1.6, (SH, SW, 1))  # fine grain, the same in all channels
    col += rng.uniform(-0.5, 0.5, (SH, SW, 3))  # dither against banding
    return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def logo_c3(width):
    im = l3.c_logo(2, MAGENTA, True)
    im = im.crop(im.getchannel("A").getbbox())
    return im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)


def splash(bg):
    im = bg.copy()
    logo = logo_c3(820)
    x, y = (SW - logo.width) // 2, 300 - logo.height // 2
    im.alpha_composite(logo, (x, y))
    tag = base.text_img("RETRO GAME LAUNCHER", base.SAIRA, 24, 1, base.STEEL, tracking=10)
    im.alpha_composite(tag, (x + 4, y + logo.height + 30))
    return im.convert("RGB")


def plymouth():
    import make_direction_a_splash as sp  # noqa: E402  (only for its radial glow)
    im = Image.new("RGBA", (SW, SH), (0, 0, 0, 255))
    im.alpha_composite(sp.radial((SW, SH), (SW // 2, SH // 2), 560, (18, 40, 60), 200))
    im.alpha_composite(sp.radial((SW, SH), (SW // 2, SH // 2 + 40), 380, base.CYAN, 26))
    logo = logo_c3(720)
    im.alpha_composite(logo, ((SW - logo.width) // 2, (SH - logo.height) // 2))
    d = ImageDraw.Draw(im)
    for w in range(6):
        d.rectangle((w, w, SW - 1 - w, SH - 1 - w), outline=(0, 0, 0, 255))
    rgb = im.convert("RGB")
    black = rgb.convert("L").point(lambda v: 255 if v == 0 else 0)
    return Image.composite(Image.new("RGB", rgb.size, (0, 0, 0)), deband(rgb), black)


def emu(bg):
    im = bg.copy()
    V = va.VARIANTS["b"]
    bar = va.frame(SW, SH, (466, 614, 1268, 684), V, stroke=2, body_alpha=225, glow_px=5, glow_a=0.35, ss=2)
    im.alpha_composite(bar.resize((SW, SH), Image.LANCZOS))
    logo = logo_c3(400)
    im.alpha_composite(logo, (32, 649 - logo.height // 2))
    return im.convert("RGB")


def emu_sketch(art):
    """The emulator's menu over the art, roughly as ab_menu.c lays it out (panel 32..572, hints on the bar)."""
    im = art.convert("RGBA")
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle([32, 40, 572, 596], radius=14, fill=(4, 18, 48, 210))
    f = ImageFont.truetype(base.OS_BOLD, 22)
    rows = ["Resume", "Save state", "Load state", "Change disc", "Filter", "Options", "Exit"]
    for i, r in enumerate(rows):
        y = 70 + i * 52
        if i == 1:
            d.rounded_rectangle([42, y - 8, 562, y + 36], radius=8, fill=(26, 126, 196, 170))
        d.text((60, y), r, font=f, fill=(244, 246, 248, 255))
    d.text((612, 40), "Neon Run", font=ImageFont.truetype(base.OS_BOLD, 36), fill=(244, 246, 248, 255))
    d.text((612, 86), "SLUS-00000  ·  NTSC  ·  BIOS  ·  22:41", font=ImageFont.truetype(base.OS_MED, 20),
           fill=(154, 164, 178, 255))
    hint = Image.open(os.path.join(va.DEF, "images", "hint_cross.png")).convert("RGBA")
    im.alpha_composite(hint, (490, 647 - 15))
    d.text((528, 647), "Select", font=f, fill=(244, 246, 248, 255), anchor="lm")
    hint = Image.open(os.path.join(va.DEF, "images", "hint_circle.png")).convert("RGBA")
    im.alpha_composite(hint, (640, 647 - 15))
    d.text((678, 647), "Resume", font=f, fill=(244, 246, 248, 255), anchor="lm")
    return im.convert("RGB")


def main():
    os.makedirs(os.path.join(A, "splash"), exist_ok=True)
    os.makedirs(os.path.join(A, "emu"), exist_ok=True)
    bg = background()
    bg.convert("RGB").save(os.path.join(A, "bg-direction-a-02p.png"))
    s, p, e = splash(bg), plymouth(), emu(bg)
    s.save(os.path.join(A, "splash", "splash-c3.jpg"), quality=95, subsampling=0)
    p.save(os.path.join(A, "splash", "plymouth-c3.png"))
    e.save(os.path.join(A, "emu", "ab_background-c3.jpg"), quality=92, subsampling=0)
    tiles = [(s, "splash launchera"), (p, "Plymouth (start systemu)"), (e, "tlo emulatora (samo)"),
             (emu_sketch(e), "tlo emulatora + szkic menu")]
    sheet = Image.new("RGB", (2 * 640 + 48, 2 * 360 + 3 * 16 + 2 * 36), (12, 15, 20))
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(base.OS_BOLD, 24)
    for i, (t, lab) in enumerate(tiles):
        c, r = i % 2, i // 2
        x, y = 16 + c * 656, 16 + r * 412
        d.text((x, y), lab, font=font, fill=base.CYAN)
        sheet.paste(t.resize((640, 360), Image.LANCZOS), (x, y + 36))
    sheet.save(os.path.join(A, "screens-c3.png"))
    print("written")


if __name__ == "__main__":
    main()
