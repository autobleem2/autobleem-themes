"""Direction A (CONSOLE-14): the ten procedural backgrounds on the two screens that use them.

Each background (design/direction-a/bg-proc/bg-p*.png, from make_direction_a_bg_proc.py) under the v02b launcher
Games screen (EvolutionUI) and under the emulator's in-game menu art with a sketch of its menu - the owner asked
to judge them there, not on the splash. Writes bg-proc/bg-screens-1.png (p1-p5) and bg-screens-2.png (p6-p10).
Run: python tools/make_direction_a_bg_screens.py --launcher ../../../repos/autobleem
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

LAUNCHER = sys.argv[sys.argv.index("--launcher") + 1]
sys.argv = [sys.argv[0], "--font-dir", os.path.join(LAUNCHER, "src", "resources", "fonts")]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_direction_a_screens_v2 as sc  # noqa: E402  (parses --font-dir)
import make_direction_a_variants as va  # noqa: E402

NAMES = ["p1 szklo", "p2 bokeh", "p3 zorza", "p4 horyzont", "p5 mozaika", "p6 mglawica", "p7 reflektory",
         "p8 duotone", "p9 szklo+bokeh", "p10 raster"]


def main():
    launcher = LAUNCHER
    fonts = os.path.join(launcher, "src", "resources", "fonts")
    bold, med = os.path.join(fonts, "OpenSans-Bold.ttf"), os.path.join(fonts, "OpenSans-Medium.ttf")
    d_in = os.path.join(va.A, "bg-proc")
    font = ImageFont.truetype(bold, 24)
    tw, th = 640, 360
    for part in range(2):
        names = NAMES[part * 5:(part + 1) * 5]
        sheet = Image.new("RGB", (2 * tw + 48, len(names) * (th + 52) + 16), (12, 15, 20))
        d = ImageDraw.Draw(sheet)
        for i, name in enumerate(names):
            bg = Image.open(os.path.join(d_in, f"bg-{name.split()[0]}.png")).convert("RGBA")
            evo = va.render("b", va.VARIANTS["b"], bold, med, bg=bg, label=False)
            emu = sc.emu_sketch(sc.emu(bg))
            y = 16 + i * (th + 52)
            d.text((16, y), f"{name} - launcher", font=font, fill=(54, 217, 224))
            d.text((16 + tw + 16, y), f"{name} - emulator", font=font, fill=(54, 217, 224))
            sheet.paste(evo.resize((tw, th), Image.LANCZOS), (16, y + 36))
            sheet.paste(emu.resize((tw, th), Image.LANCZOS), (16 + tw + 16, y + 36))
            print(name, flush=True)
        sheet.save(os.path.join(d_in, f"bg-screens-{part + 1}.png"))


if __name__ == "__main__":
    main()
