"""Direction A (CONSOLE-14): five logo concepts, drawn as vectors, to pick one from.

Writes into design/direction-a/logo/:
  logo-a<N>.png          each concept on a transparent 480x360 canvas (the size theme.json gives the logo)
  logo-a<N>@2x.png       the same at 960x720
  logo-concepts.png      all five on the background, numbered, for choosing
Run: python tools/make_direction_a_logo.py [--font-dir DIR]
DIR holds OpenSans-Bold.ttf and OpenSans-Medium.ttf - by default the launcher's own
src/resources/fonts when this repository is its submodule; AB_FONT_DIR or --font-dir override it.
Saira Semi Condensed comes from Themes/default. No third-party marks (no controller-button shapes).
"""
import argparse
import math
import os
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DESIGN = os.path.join(REPO, "design", "direction-a")
OUT = os.path.join(DESIGN, "logo")
_ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
_ap.add_argument("--font-dir", default=os.environ.get("AB_FONT_DIR") or os.path.join(
    REPO, "..", "src", "resources", "fonts"))
FONT_DIR = os.path.normpath(_ap.parse_args().font_dir)
OS_BOLD = os.path.join(FONT_DIR, "OpenSans-Bold.ttf")
OS_MED = os.path.join(FONT_DIR, "OpenSans-Medium.ttf")
SAIRA = os.path.join(REPO, "Themes", "default", "saira-semicondensed-medium.ttf")
for f in (OS_BOLD, OS_MED, SAIRA):
    if not os.path.isfile(f):
        raise SystemExit(f"font not found: {f} - pass --font-dir")

CYAN = (54, 217, 224)
CYAN_DEEP = (22, 150, 170)
WHITE = (240, 248, 250)
STEEL = (150, 164, 178)
GRAPHITE = (39, 47, 56)
NAVY = (22, 32, 52)

W, H = 480, 360
SS = 4                       # supersampling over the 2x render


# ---------- helpers (all sizes are in 1x pixels; k = scale * SS) ----------

def canvas(k):
    return Image.new("RGBA", (W * k, H * k), (0, 0, 0, 0))


def text_img(text, font_path, px, k, fill, tracking=0.0):
    """Text as a tight RGBA image; tracking in 1x pixels between letters."""
    font = ImageFont.truetype(font_path, round(px * k))
    widths = [font.getlength(c) for c in text]
    asc, desc = font.getmetrics()
    tw = int(sum(widths) + tracking * k * (len(text) - 1)) + 4 * k
    im = Image.new("RGBA", (tw, asc + desc + 4 * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = 2 * k
    for c, w in zip(text, widths):
        d.text((x, 2 * k), c, font=font, fill=fill + (255,))
        x += w + tracking * k
    return im.crop(im.getchannel("A").getbbox())


def glow(layer, radius, color, strength):
    g = Image.new("RGBA", layer.size, color + (0,))
    a = layer.getchannel("A").filter(ImageFilter.GaussianBlur(radius))
    g.putalpha(a.point(lambda v: min(255, int(v * strength))))
    return Image.alpha_composite(g, layer)


def vgradient(size, top, bot):
    im = Image.new("RGBA", size)
    d = ImageDraw.Draw(im)
    for y in range(size[1]):
        t = y / max(1, size[1] - 1)
        d.line([(0, y), (size[0], y)], fill=tuple(round(top[i] + (bot[i] - top[i]) * t) for i in range(3)) + (255,))
    return im


def fill_with(mask, fill_img):
    out = fill_img.copy()
    out.putalpha(ImageChops.multiply(mask, fill_img.getchannel("A")))
    return out


def paste_center(dst, im, cx, cy):
    dst.alpha_composite(im, (round(cx - im.width / 2), round(cy - im.height / 2)))


def play_tri(d, cx, cy, h, k, fill):
    w = h * 0.87
    x0 = cx - w * 0.42          # optical centre of a play triangle
    d.polygon([(x0 * k, (cy - h / 2) * k), (x0 * k, (cy + h / 2) * k), ((x0 + w) * k, cy * k)], fill=fill)


def finish(im, scale):
    return im.resize((W * scale, H * scale), Image.LANCZOS)


# ---------- the five concepts ----------

def a1_arc(scale):
    """Two lines, the old logo's arc kept as one cyan sweep - continuity with today's logo."""
    k = scale * SS
    im = canvas(k)
    arc = canvas(k)
    d = ImageDraw.Draw(arc)
    d.arc((70 * k, 40 * k, 430 * k, 250 * k), start=200, end=335, fill=CYAN + (255,), width=9 * k)
    arc = glow(arc, 6 * k, CYAN, 0.9)
    im.alpha_composite(arc)
    auto = text_img("Auto", OS_BOLD, 118, k, WHITE, tracking=-2)
    bleem = text_img("Bleem", OS_BOLD, 118, k, WHITE, tracking=-2)
    paste_center(im, glow(auto, 3 * k, (0, 0, 0), 0.6), 240 * k, 150 * k)
    paste_center(im, glow(bleem, 3 * k, (0, 0, 0), 0.6), 240 * k, 265 * k)
    return finish(im, scale)


def a2_badge(scale):
    """An AB monogram in a rounded badge with a cyan rim; the wordmark spaced out below."""
    k = scale * SS
    im = canvas(k)
    bx0, by0, bx1, by1 = 170, 30, 310, 170
    rim = Image.new("L", im.size, 0)
    ImageDraw.Draw(rim).rounded_rectangle((bx0 * k, by0 * k, bx1 * k, by1 * k), radius=34 * k, fill=255)
    inner = Image.new("L", im.size, 0)
    ImageDraw.Draw(inner).rounded_rectangle(((bx0 + 4) * k, (by0 + 4) * k, (bx1 - 4) * k, (by1 - 4) * k),
                                            radius=30 * k, fill=255)
    rim_l = fill_with(rim, Image.new("RGBA", im.size, CYAN + (255,)))
    im.alpha_composite(glow(rim_l, 8 * k, CYAN, 0.7))
    im.alpha_composite(fill_with(inner, vgradient(im.size, (52, 62, 76), NAVY)))
    mono = text_img("AB", OS_BOLD, 92, k, WHITE, tracking=-6)
    paste_center(im, mono, 240 * k, 100 * k)
    word = text_img("AUTOBLEEM", SAIRA, 50, k, WHITE, tracking=9)
    paste_center(im, word, 240 * k, 250 * k)
    bar = canvas(k)
    ImageDraw.Draw(bar).rounded_rectangle((200 * k, 296 * k, 280 * k, 300 * k), radius=2 * k, fill=CYAN + (255,))
    im.alpha_composite(glow(bar, 4 * k, CYAN, 0.8))
    return finish(im, scale)


def a3_disc(scale):
    """A disc ring with a play triangle - the thing it does - next to a stacked light/bold wordmark."""
    k = scale * SS
    im = canvas(k)
    cx, cy, r = 118, 180, 78
    ring = canvas(k)
    d = ImageDraw.Draw(ring)
    d.ellipse(((cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k), outline=CYAN + (255,), width=8 * k)
    d.ellipse(((cx - r + 18) * k, (cy - r + 18) * k, (cx + r - 18) * k, (cy + r - 18) * k),
              outline=CYAN + (110,), width=2 * k)
    play_tri(d, cx, cy, 58, k, WHITE + (255,))
    im.alpha_composite(glow(ring, 7 * k, CYAN, 0.8))
    auto = text_img("AUTO", SAIRA, 74, k, STEEL, tracking=6)
    bleem = text_img("BLEEM", OS_BOLD, 74, k, WHITE, tracking=1)
    x = 222 * k
    im.alpha_composite(auto, (x, round(cy * k - auto.height - 8 * k)))
    im.alpha_composite(bleem, (x, round(cy * k + 8 * k)))
    return finish(im, scale)


def a4_split(scale):
    """One line, AUTO in steel and BLEEM in white, a cyan bar under it that fades out to the right."""
    k = scale * SS
    im = canvas(k)
    auto = text_img("AUTO", OS_MED, 80, k, STEEL, tracking=2)
    bleem = text_img("BLEEM", OS_BOLD, 80, k, WHITE, tracking=2)
    gap = 10 * k
    total = auto.width + gap + bleem.width
    scale_fit = min(1.0, 440 * k / total)
    if scale_fit < 1.0:
        auto = auto.resize((round(auto.width * scale_fit), round(auto.height * scale_fit)), Image.LANCZOS)
        bleem = bleem.resize((round(bleem.width * scale_fit), round(bleem.height * scale_fit)), Image.LANCZOS)
        gap = round(gap * scale_fit)
        total = auto.width + gap + bleem.width
    x0 = round(240 * k - total / 2)
    base = 190 * k
    im.alpha_composite(auto, (x0, base - auto.height))
    im.alpha_composite(bleem, (x0 + auto.width + gap, base - bleem.height))
    bar = canvas(k)
    grad = Image.new("RGBA", im.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    bx0, bx1 = x0, x0 + total
    for x in range(bx0, bx1):
        t = (x - bx0) / max(1, bx1 - bx0)
        gd.line([(x, base + 18 * k), (x, base + 24 * k)], fill=CYAN + (round(255 * (1 - t) ** 1.4),))
    bar.alpha_composite(grad)
    im.alpha_composite(glow(bar, 5 * k, CYAN, 0.8))
    tag = text_img("RETRO LAUNCHER", SAIRA, 22, k, STEEL, tracking=8)
    im.alpha_composite(tag, (x0, base + 44 * k))
    return finish(im, scale)


def a5_pill(scale):
    """The Play button's pill as the emblem: an 'ab' mark in a cyan-rimmed capsule above the wordmark."""
    k = scale * SS
    im = canvas(k)
    px0, py0, px1, py1 = 150, 50, 330, 150
    rim = Image.new("L", im.size, 0)
    ImageDraw.Draw(rim).rounded_rectangle((px0 * k, py0 * k, px1 * k, py1 * k), radius=50 * k, fill=255)
    inner = Image.new("L", im.size, 0)
    ImageDraw.Draw(inner).rounded_rectangle(((px0 + 4) * k, (py0 + 4) * k, (px1 - 4) * k, (py1 - 4) * k),
                                            radius=46 * k, fill=255)
    im.alpha_composite(glow(fill_with(rim, Image.new("RGBA", im.size, CYAN + (255,))), 8 * k, CYAN, 0.7))
    im.alpha_composite(fill_with(inner, vgradient(im.size, (46, 55, 66), (33, 40, 49))))
    mark = canvas(k)
    d = ImageDraw.Draw(mark)
    play_tri(d, 192, 100, 42, k, CYAN + (255,))
    im.alpha_composite(glow(mark, 3 * k, CYAN, 0.6))
    ab = text_img("ab", OS_BOLD, 76, k, WHITE, tracking=-3)
    im.alpha_composite(ab, (round(228 * k), round(100 * k - ab.height / 2 - 4 * k)))
    word = text_img("AUTOBLEEM", OS_BOLD, 54, k, WHITE, tracking=5)
    paste_center(im, word, 240 * k, 225 * k)
    sub = text_img("PLAY  ·  RETRO  ·  MORE", SAIRA, 20, k, STEEL, tracking=6)
    paste_center(im, sub, 240 * k, 272 * k)
    return finish(im, scale)


CONCEPTS = [a1_arc, a2_badge, a3_disc, a4_split, a5_pill]


def contact_sheet(logos, prefix="A"):
    bg = Image.open(os.path.join(DESIGN, "bg-direction-a-01.png")).convert("RGBA")
    tile_w, tile_h = 640, 360
    bg_tile = bg.resize((tile_w, tile_h), Image.LANCZOS)
    cols, rows = 3, 2
    sheet = Image.new("RGBA", (cols * tile_w + (cols + 1) * 16, rows * tile_h + (rows + 1) * 16), (12, 15, 20, 255))
    label_font = ImageFont.truetype(OS_BOLD, 34)
    for i, logo in enumerate(logos):
        t = bg_tile.copy()
        t.alpha_composite(logo, ((tile_w - logo.width) // 2, (tile_h - logo.height) // 2))
        d = ImageDraw.Draw(t)
        d.text((18, 12), f"{prefix}{i + 1}", font=label_font, fill=CYAN + (255,))
        c, r = i % cols, i // cols
        sheet.alpha_composite(t, (16 + c * (tile_w + 16), 16 + r * (tile_h + 16)))
    # the last tile: today's logo size cue left empty -> show A1..A5 legend instead
    return sheet


def main():
    os.makedirs(OUT, exist_ok=True)
    logos = []
    for i, fn in enumerate(CONCEPTS, 1):
        one = fn(1)
        one.save(os.path.join(OUT, f"logo-a{i}.png"))
        fn(2).save(os.path.join(OUT, f"logo-a{i}@2x.png"))
        bbox = one.getchannel("A").getbbox()
        print(f"a{i} {fn.__name__}: content bbox {bbox}")
        logos.append(one)
    contact_sheet(logos).convert("RGB").save(os.path.join(OUT, "logo-concepts.png"))


if __name__ == "__main__":
    main()
