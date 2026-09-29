"""Direction A (CONSOLE-14): five more logo concepts, each with the "2" worked into it.

Writes into design/direction-a/logo/:
  logo-b<N>.png, logo-b<N>@2x.png   each concept (480x360 and 960x720, transparent)
  logo-concepts-2.png               all five on the background, numbered, for choosing
Run: python tools/make_direction_a_logo2.py [--font-dir DIR]   (the same fonts as make_direction_a_logo.py)
"""
import os
import sys
from PIL import Image, ImageChops, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_direction_a_logo as base  # noqa: E402  (parses --font-dir)
from make_direction_a_logo import (  # noqa: E402
    CYAN, WHITE, STEEL, NAVY, OS_BOLD, OS_MED, SAIRA, W, H, SS,
    canvas, text_img, glow, vgradient, fill_with, paste_center, finish)

DARK = (18, 24, 32)


def outline_text(text, font_path, px, k, stroke, color):
    """Only the outline of the glyphs (stroke in 1x px, drawn outside the letter shape)."""
    font = ImageFont.truetype(font_path, round(px * k))
    s = round(stroke * k)
    l, t, r, b = font.getbbox(text, stroke_width=s)
    size = (r - l + 4 * s, b - t + 4 * s)
    outer = Image.new("L", size, 0)
    inner = Image.new("L", size, 0)
    ImageDraw.Draw(outer).text((2 * s - l, 2 * s - t), text, font=font, fill=255, stroke_width=s, stroke_fill=255)
    ImageDraw.Draw(inner).text((2 * s - l, 2 * s - t), text, font=font, fill=255)
    ring = ImageChops.subtract(outer, inner)
    im = Image.new("RGBA", size, color + (255,))
    im.putalpha(ring)
    return im.crop(ring.getbbox())


def b1_tall_two(scale):
    """AUTO / BLEEM stacked, one tall cyan 2 spanning both lines."""
    k = scale * SS
    im = canvas(k)
    auto = text_img("AUTO", OS_BOLD, 86, k, WHITE, tracking=1)
    bleem = text_img("BLEEM", OS_BOLD, 86, k, WHITE, tracking=1)
    gap_lines = 18 * k
    block_h = auto.height + gap_lines + bleem.height
    two = text_img("2", SAIRA, 290, k, CYAN)
    two = two.resize((round(two.width * block_h / two.height), block_h), Image.LANCZOS)
    gap = 22 * k
    total = max(auto.width, bleem.width) + gap + two.width
    x0 = round(240 * k - total / 2)
    y0 = round(180 * k - block_h / 2)
    im.alpha_composite(auto, (x0, y0))
    im.alpha_composite(bleem, (x0, y0 + auto.height + gap_lines))
    layer = canvas(k)
    layer.alpha_composite(two, (x0 + max(auto.width, bleem.width) + gap, y0))
    im.alpha_composite(glow(layer, 7 * k, CYAN, 0.8))
    return finish(im, scale)


def b2_badge_two(scale):
    """The AB badge with a cyan 2 seal on its corner; the wordmark spaced out below."""
    k = scale * SS
    im = canvas(k)
    bx0, by0, bx1, by1 = 170, 30, 310, 170
    rim = Image.new("L", im.size, 0)
    ImageDraw.Draw(rim).rounded_rectangle((bx0 * k, by0 * k, bx1 * k, by1 * k), radius=34 * k, fill=255)
    inner = Image.new("L", im.size, 0)
    ImageDraw.Draw(inner).rounded_rectangle(((bx0 + 4) * k, (by0 + 4) * k, (bx1 - 4) * k, (by1 - 4) * k),
                                            radius=30 * k, fill=255)
    im.alpha_composite(glow(fill_with(rim, Image.new("RGBA", im.size, CYAN + (255,))), 8 * k, CYAN, 0.7))
    im.alpha_composite(fill_with(inner, vgradient(im.size, (52, 62, 76), NAVY)))
    paste_center(im, text_img("AB", OS_BOLD, 92, k, WHITE, tracking=-6), 240 * k, 100 * k)
    # the seal: a cyan disc over the lower-right corner, a dark ring separating it from the badge
    cx, cy, r = bx1 - 4, by1 - 4, 30
    seal = canvas(k)
    d = ImageDraw.Draw(seal)
    d.ellipse(((cx - r - 5) * k, (cy - r - 5) * k, (cx + r + 5) * k, (cy + r + 5) * k), fill=DARK + (255,))
    d.ellipse(((cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k), fill=CYAN + (255,))
    im.alpha_composite(glow(seal, 6 * k, CYAN, 0.5))
    paste_center(im, text_img("2", OS_BOLD, 46, k, DARK), cx * k, cy * k)
    paste_center(im, text_img("AUTOBLEEM", SAIRA, 50, k, WHITE, tracking=9), 240 * k, 255 * k)
    bar = canvas(k)
    ImageDraw.Draw(bar).rounded_rectangle((200 * k, 300 * k, 280 * k, 304 * k), radius=2 * k, fill=CYAN + (255,))
    im.alpha_composite(glow(bar, 4 * k, CYAN, 0.8))
    return finish(im, scale)


def b3_disc_two(scale):
    """The disc ring holds the 2; the stacked light/bold wordmark beside it."""
    k = scale * SS
    im = canvas(k)
    cx, cy, r = 118, 180, 78
    ring = canvas(k)
    d = ImageDraw.Draw(ring)
    d.ellipse(((cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k), outline=CYAN + (255,), width=8 * k)
    d.ellipse(((cx - r + 18) * k, (cy - r + 18) * k, (cx + r - 18) * k, (cy + r - 18) * k),
              outline=CYAN + (110,), width=2 * k)
    im.alpha_composite(glow(ring, 7 * k, CYAN, 0.8))
    paste_center(im, text_img("2", OS_BOLD, 104, k, WHITE), (cx + 1) * k, cy * k)
    auto = text_img("AUTO", SAIRA, 74, k, STEEL, tracking=6)
    bleem = text_img("BLEEM", OS_BOLD, 74, k, WHITE, tracking=1)
    x = 222 * k
    im.alpha_composite(auto, (x, round(cy * k - auto.height - 8 * k)))
    im.alpha_composite(bleem, (x, round(cy * k + 8 * k)))
    return finish(im, scale)


def b4_pill_two(scale):
    """One line AUTO|BLEEM and the 2 in the Play button's capsule at its end; a fading cyan bar under it."""
    k = scale * SS
    im = canvas(k)
    auto = text_img("AUTO", OS_MED, 54, k, STEEL, tracking=2)
    bleem = text_img("BLEEM", OS_BOLD, 54, k, WHITE, tracking=2)
    two = text_img("2", OS_BOLD, 47, k, WHITE)
    pill_h = round(bleem.height * 1.35)
    pill_w = round(pill_h * 1.25)
    gap, gap2 = 8 * k, 16 * k
    total = auto.width + gap + bleem.width + gap2 + pill_w
    x0 = round(240 * k - total / 2)
    base_y = 190 * k
    im.alpha_composite(auto, (x0, base_y - auto.height))
    im.alpha_composite(bleem, (x0 + auto.width + gap, base_y - bleem.height))
    px0 = x0 + auto.width + gap + bleem.width + gap2
    pcy = base_y - bleem.height / 2
    py0, py1 = round(pcy - pill_h / 2), round(pcy + pill_h / 2)
    rim = Image.new("L", im.size, 0)
    ImageDraw.Draw(rim).rounded_rectangle((px0, py0, px0 + pill_w, py1), radius=pill_h // 2, fill=255)
    inner = Image.new("L", im.size, 0)
    ImageDraw.Draw(inner).rounded_rectangle((px0 + 3 * k, py0 + 3 * k, px0 + pill_w - 3 * k, py1 - 3 * k),
                                            radius=pill_h // 2 - 3 * k, fill=255)
    im.alpha_composite(glow(fill_with(rim, Image.new("RGBA", im.size, CYAN + (255,))), 6 * k, CYAN, 0.7))
    im.alpha_composite(fill_with(inner, vgradient(im.size, (46, 55, 66), (33, 40, 49))))
    paste_center(im, two, px0 + pill_w / 2, pcy)
    bar = canvas(k)
    gd = ImageDraw.Draw(bar)
    bx0, bx1 = x0, x0 + total
    for x in range(bx0, bx1):
        t = (x - bx0) / max(1, bx1 - bx0)
        gd.line([(x, base_y + 22 * k), (x, base_y + 27 * k)], fill=CYAN + (round(255 * (1 - t) ** 1.4),))
    im.alpha_composite(glow(bar, 5 * k, CYAN, 0.8))
    return finish(im, scale)


def b5_outline_two(scale):
    """A huge glowing outline 2 behind, the wordmark crossing it on a dark band."""
    k = scale * SS
    im = canvas(k)
    two = outline_text("2", SAIRA, 330, k, 4, CYAN)
    layer = canvas(k)
    paste_center(layer, two, 240 * k, 178 * k)
    im.alpha_composite(glow(layer, 9 * k, CYAN, 0.9))
    band = canvas(k)
    ImageDraw.Draw(band).rectangle((0, 152 * k, W * k, 212 * k), fill=DARK + (215,))
    fade = Image.new("L", im.size, 0)
    fd = ImageDraw.Draw(fade)
    for x in range(W * k):
        t = abs(x / (W * k) - 0.5) * 2
        fd.line([(x, 0), (x, H * k)], fill=round(255 * max(0.0, 1 - t ** 3)))
    band.putalpha(ImageChops.multiply(band.getchannel("A"), fade))
    im.alpha_composite(band)
    word = text_img("AUTOBLEEM", OS_BOLD, 58, k, WHITE, tracking=7)
    paste_center(im, word, 240 * k, 182 * k)
    return finish(im, scale)


CONCEPTS = [b1_tall_two, b2_badge_two, b3_disc_two, b4_pill_two, b5_outline_two]


def main():
    os.makedirs(base.OUT, exist_ok=True)
    logos = []
    for i, fn in enumerate(CONCEPTS, 1):
        one = fn(1)
        one.save(os.path.join(base.OUT, f"logo-b{i}.png"))
        fn(2).save(os.path.join(base.OUT, f"logo-b{i}@2x.png"))
        print(f"b{i} {fn.__name__}: content bbox {one.getchannel('A').getbbox()}")
        logos.append(one)
    base.contact_sheet(logos, "B").convert("RGB").save(os.path.join(base.OUT, "logo-concepts-2.png"))


if __name__ == "__main__":
    main()
