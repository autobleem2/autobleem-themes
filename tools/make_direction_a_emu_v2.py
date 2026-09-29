"""Direction A (CONSOLE-14): a mockup of the emulator's in-game menu if its colours and shapes followed v02b.

Only a picture: the menu is drawn by pcsx-abnxt frontend/ab/ab_menu.c (frozen emulator code), in its layout -
the rows' panel x 32..572, the game top right, the hints on the art's bar from x 490, y 647. Here the panel is
the v02b graphite with cut corners and a cyan rim, the selected row a magenta-rimmed cut-corner bar, section
headings in Saira. Shown on backgrounds p5 and p6 next to today's colours.
Run: python tools/make_direction_a_emu_v2.py --launcher ../../../repos/autobleem
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

LAUNCHER = sys.argv[sys.argv.index("--launcher") + 1]
sys.argv = [sys.argv[0], "--font-dir", os.path.join(LAUNCHER, "src", "resources", "fonts")]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_direction_a_screens_v2 as sc  # noqa: E402  (parses --font-dir)
import make_direction_a_variants as va  # noqa: E402

V = va.VARIANTS["b"]
WHITE, DIM = (244, 246, 248, 255), (154, 164, 178, 255)
ROWS = [("Game", None), ("Resume", None), ("Save state", "Slot 1"), ("Load state", "Slot 1"), ("Change disc", "1/1"),
        ("Video", None), ("Filter", "Scale2x"), ("Aspect", "4:3"), (None, None), ("Options", None), ("Exit", None)]
SEL = 2


def piece(w, h, edge, glow_a=0.35, stroke=2, body_alpha=225):
    return va.frame(w, h, (1, 1, w - 1, h - 1), V, edge=edge, stroke=stroke, body_alpha=body_alpha,
                    glow_px=5, glow_a=glow_a, ss=2).resize((w, h), Image.LANCZOS)


def menu_v2(art, fonts):
    im = art.convert("RGBA")
    bold = os.path.join(fonts, "OpenSans-Bold.ttf")
    med = os.path.join(fonts, "OpenSans-Medium.ttf")
    im.alpha_composite(piece(540, 556, V["line"]), (32, 40))
    f_row, f_val = ImageFont.truetype(med, 22), ImageFont.truetype(med, 20)
    f_head = ImageFont.truetype(va.SAIRA, 20)
    d = ImageDraw.Draw(im)
    y = 64
    for i, (name, val) in enumerate(ROWS):
        if name is None:
            y += 14
            continue
        if val is None and name in ("Game", "Video"):  # a section heading
            d.text((60, y + 6), name.upper(), font=f_head, fill=(54, 217, 224, 255))
            d.line([(60 + d.textlength(name.upper(), font=f_head) + 12, y + 18), (548, y + 18)],
                   fill=(54, 217, 224, 70), width=1)
            y += 40
            continue
        if i == SEL:
            im.alpha_composite(piece(508, 44, V["focus"], glow_a=0.55, body_alpha=255), (48, y - 4))
            d = ImageDraw.Draw(im)
        d.text((72, y + 18), name, font=f_row, fill=WHITE, anchor="lm")
        if val:
            d.text((540, y + 18), val, font=f_val, fill=WHITE if i == SEL else DIM, anchor="rm")
        y += 48
    d.text((612, 40), "Neon Run", font=ImageFont.truetype(va.SAIRA, 40), fill=WHITE)
    d.text((614, 92), "SLUS-00000  ·  NTSC  ·  BIOS  ·  22:41", font=ImageFont.truetype(med, 20), fill=DIM)
    for x, name in ((490, "hint_cross.png"), (640, "hint_circle.png")):
        im.alpha_composite(Image.open(os.path.join(va.DEF, "images", name)).convert("RGBA"), (x, 647 - 15))
    d.text((528, 647), "Select", font=ImageFont.truetype(bold, 22), fill=WHITE, anchor="lm")
    d.text((678, 647), "Resume", font=ImageFont.truetype(bold, 22), fill=WHITE, anchor="lm")
    return im.convert("RGB")


def main():
    fonts = os.path.join(LAUNCHER, "src", "resources", "fonts")
    d_in = os.path.join(va.A, "bg-proc")
    tw, th = 640, 360
    sheet = Image.new("RGB", (2 * tw + 48, 2 * (th + 52) + 16), (12, 15, 20))
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(os.path.join(fonts, "OpenSans-Bold.ttf"), 24)
    for r, name in enumerate(("p5", "p6")):
        bg = Image.open(os.path.join(d_in, f"bg-{name}.png")).convert("RGBA")
        art = sc.emu(bg)
        old, new = sc.emu_sketch(art), menu_v2(art, fonts)
        new.save(os.path.join(va.A, "emu", f"emu-menu-v2-{name}.png"))
        y = 16 + r * (th + 52)
        d.text((16, y), f"{name} - menu dzis (kolory z kodu)", font=font, fill=(154, 164, 178))
        d.text((16 + tw + 16, y), f"{name} - menu po zmianie kodu (v02b)", font=font, fill=(54, 217, 224))
        sheet.paste(old.resize((tw, th), Image.LANCZOS), (16, y + 36))
        sheet.paste(new.resize((tw, th), Image.LANCZOS), (16 + tw + 16, y + 36))
    sheet.save(os.path.join(va.A, "emu", "emu-menu-v2-sheet.png"))
    print("written")


if __name__ == "__main__":
    main()
