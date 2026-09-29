"""Direction A (CONSOLE-14): the Play button, drawn as vectors.

v02 (2026-09-29): the triangle is smaller and kept clear of the pill's frame.
Writes into design/direction-a/:
  play_button-direction-a-02.png   the pill alone (200x68 at scale 1)
  play_text-direction-a-02.png     triangle + "PLAY" alone, same canvas as the pill
  play_full-direction-a-02.png     pill + triangle + "PLAY" (scale 1) and @2x
  preview_play_on_bg-02.png        the button at 2x on the background's lower third
Run: python tools/make_direction_a_play.py [--font PATH/OpenSans-Bold.ttf]
The font defaults to the launcher's own copy when this repository is its submodule
(<launcher>/src/resources/fonts/OpenSans-Bold.ttf); AB_FONT or --font override it.
"""
import argparse
import math
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
HERE = os.path.join(REPO, "design", "direction-a")
_ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
_ap.add_argument("--font", default=os.environ.get("AB_FONT") or os.path.join(
    REPO, "..", "src", "resources", "fonts", "OpenSans-Bold.ttf"))
FONT = os.path.normpath(_ap.parse_args().font)
if not os.path.isfile(FONT):
    raise SystemExit(f"font not found: {FONT} - pass --font path/to/OpenSans-Bold.ttf")
BG = os.path.join(HERE, "bg-direction-a-01.png")

CYAN = (54, 217, 224)
TEXT = (240, 248, 250)
FILL_TOP = (46, 55, 66)
FILL_BOT = (33, 40, 49)

# Geometry at scale 1 (pixels)
W, H = 200, 68
PILL = (14, 14, 186, 54)       # x0, y0, x1, y1 -> height 40, radius 20
STROKE = 2
TRI_H = 20                     # was ~26 at this scale; now half the pill height
TRI_W = round(TRI_H * 0.87)    # near-equilateral
GAP = 9                        # triangle -> text
FONT_PX = 25
SS = 4                         # supersampling


def _group_left():
    """Left edge of the triangle so that triangle + gap + "PLAY" sits centred in the pill."""
    text_w = ImageFont.truetype(FONT, FONT_PX * 16).getbbox("PLAY", anchor="lm")
    text_w = (text_w[2] - text_w[0]) / 16
    return round((PILL[0] + PILL[2]) / 2 - (TRI_W + GAP + text_w) / 2)


TRI_X = _group_left()          # left edge of the triangle


def pill_mask(scale, inset=0.0):
    s = scale * SS
    x0, y0, x1, y1 = [v * s for v in PILL]
    m = Image.new("L", (W * s, H * s), 0)
    d = ImageDraw.Draw(m)
    i = inset * s
    d.rounded_rectangle((x0 + i, y0 + i, x1 - i, y1 - i), radius=(y1 - y0) / 2 - i, fill=255)
    return m


def triangle_points(scale):
    s = scale * SS
    cy = (PILL[1] + PILL[3]) / 2
    x0 = TRI_X
    # optical centring: a play triangle sits a touch right of its box centre
    return [(x0 * s, (cy - TRI_H / 2) * s), (x0 * s, (cy + TRI_H / 2) * s), ((x0 + TRI_W) * s, cy * s)]


def clearance():
    """Smallest distance (px, scale 1) from the triangle to the inner edge of the frame."""
    x0, y0, x1, y1 = PILL
    r = (y1 - y0) / 2 - STROKE          # inner radius
    cx, cy = x0 + (y1 - y0) / 2, (y0 + y1) / 2
    best = 1e9
    pts = [(p[0] / SS, p[1] / SS) for p in triangle_points(1)]
    for a, b in [(pts[0], pts[1]), (pts[1], pts[2]), (pts[2], pts[0])]:
        for k in range(101):
            t = k / 100
            px, py = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            if px < cx:
                dist = r - math.hypot(px - cx, py - cy)
            else:
                dist = min(py - (cy - r), (cy + r) - py)
            best = min(best, dist)
    return best


def draw_pill(scale):
    s = scale * SS
    size = (W * s, H * s)
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    # outer cyan glow
    glow = Image.new("RGBA", size, CYAN + (0,))
    ga = pill_mask(scale).filter(ImageFilter.GaussianBlur(7 * s))
    glow.putalpha(ga.point(lambda v: int(v * 0.55)))
    out = Image.alpha_composite(out, glow)
    # frame
    frame = Image.new("RGBA", size, CYAN + (255,))
    frame.putalpha(pill_mask(scale))
    out = Image.alpha_composite(out, frame)
    # body: vertical gradient inside the stroke
    body = Image.new("RGBA", size)
    bd = ImageDraw.Draw(body)
    for y in range(size[1]):
        t = min(1.0, max(0.0, (y / s - PILL[1]) / (PILL[3] - PILL[1])))
        c = tuple(round(FILL_TOP[i] + (FILL_BOT[i] - FILL_TOP[i]) * t) for i in range(3))
        bd.line([(0, y), (size[0], y)], fill=c + (255,))
    body.putalpha(pill_mask(scale, STROKE))
    out = Image.alpha_composite(out, body)
    return out.resize((W * scale, H * scale), Image.LANCZOS)


def draw_content(scale):
    s = scale * SS
    size = (W * s, H * s)
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    pts = triangle_points(scale)
    # soft glow under the triangle
    tg = Image.new("L", size, 0)
    ImageDraw.Draw(tg).polygon(pts, fill=255)
    glow = Image.new("RGBA", size, CYAN + (0,))
    glow.putalpha(tg.filter(ImageFilter.GaussianBlur(2.5 * s)).point(lambda v: int(v * 0.6)))
    out = Image.alpha_composite(out, glow)
    d = ImageDraw.Draw(out)
    d.polygon(pts, fill=CYAN + (255,))
    font = ImageFont.truetype(FONT, FONT_PX * s)
    cy = (PILL[1] + PILL[3]) / 2 * s
    tx = (TRI_X + TRI_W + GAP) * s
    d.text((tx, cy), "PLAY", font=font, fill=TEXT + (255,), anchor="lm")
    return out.resize((W * scale, H * scale), Image.LANCZOS)


def main():
    c = clearance()
    print(f"triangle {TRI_W}x{TRI_H}px, clearance to the frame's inner edge: {c:.1f}px")
    assert c >= 4, "triangle too close to the frame"
    pill1, text1 = draw_pill(1), draw_content(1)
    pill1.save(os.path.join(HERE, "play_button-direction-a-02.png"))
    text1.save(os.path.join(HERE, "play_text-direction-a-02.png"))
    Image.alpha_composite(pill1, text1).save(os.path.join(HERE, "play_full-direction-a-02.png"))
    full2 = Image.alpha_composite(draw_pill(2), draw_content(2))
    full2.save(os.path.join(HERE, "play_full-direction-a-02@2x.png"))
    # preview: lower-third crop of the background with the 2x button centred in it
    bg = Image.open(BG).convert("RGBA")
    bw, bh = bg.size
    crop = bg.crop((bw // 2 - 320, bh - 300, bw // 2 + 320, bh - 20))
    crop.alpha_composite(full2, ((crop.width - full2.width) // 2, (crop.height - full2.height) // 2))
    crop.save(os.path.join(HERE, "preview_play_on_bg-02.png"))
    # text bbox check
    bbox = text1.getchannel("A").getbbox()
    print("content bbox (scale 1):", bbox, "pill:", PILL)


if __name__ == "__main__":
    main()
