"""ab2.0.0 (CONSOLE-14) - the ab_gui G4 9-slice frames, per core's docs/ab-gui-frames-spec.md (the first set).

panel, selection, heading, key, key_function, key_lit, key_selected, field - each at 1x and @2x, in the v02b
look: cut corners (top right + bottom left), a cyan rim on graphite, magenta for the focused item. Every
frame keeps the spec's sizes, slices and bleeds, the cut and the rim inside the corner slices, the glow inside the
bleed, edges uniform along their length (nothing along an edge but the rim and a glow fading outwards).

Variants (the owner asked to see both of each, 2026-09-30):
  sel  outline  the selected row: a magenta rim, a faint magenta tint inside
       fill     the selected row: a dim magenta fill, a thin brighter rim
  glow glow     rims with a soft glow in the bleed (the selected row / key the strongest)
       flat     rims only, no glow
Writes src/design/frames/<sel>-<glow>/frames/*.png and a preview: the frames 9-sliced by the same rule as
ab_gui (corners 1:1, edges stretched one way, centre both) into the Options screen and the on-screen keyboard,
on background p5 - src/design/frames/frames-options.png, frames-keyboard.png.
Run: python Themes/ab2.0.0/src/tools/make_direction_a_frames.py --launcher <launcher checkout>
"""
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

LAUNCHER = sys.argv[sys.argv.index("--launcher") + 1] if "--launcher" in sys.argv else None
HERE = os.path.dirname(os.path.abspath(__file__))
THEME = os.path.normpath(os.path.join(HERE, "..", ".."))
DESIGN = os.path.join(THEME, "src", "design")
OUT = os.path.join(DESIGN, "frames")
SS = 4

CYAN = (54, 217, 224)
MAGENTA = (255, 70, 170)
STEEL = (110, 124, 138)
G_TOP, G_BOT = (46, 55, 66), (33, 40, 49)


def poly(x0, y0, x1, y1, cut):
    """The v02b shape: cut corners at the top right and the bottom left."""
    return [(x0, y0), (x1 - cut, y0), (x1, y0 + cut), (x1, y1), (x0 + cut, y1), (x0, y1 - cut)]


def mask(size, pts):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return m


def solid(size, rgb, alpha_img):
    im = Image.new("RGBA", size, rgb + (0,))
    im.putalpha(alpha_img)
    return im


def frame(w, h, bleed, cut, rim, rim_rgb, fill, glow_a, scale, grad=True):
    """One frame image at `scale` (1 or 2). fill = (rgb_top, rgb_bottom, alpha 0-255) or None.
    rim in logical px (drawn on whole pixels at both scales); glow_a 0 = none (it stays inside the bleed)."""
    k = scale * SS
    size = (w * k, h * k)
    b = bleed * k
    outer = poly(b, b, size[0] - b, size[1] - b, cut * k)
    r = rim * k
    inner = poly(b + r, b + r, size[0] - b - r, size[1] - b - r, max(0, cut * k - r * 0.42))
    m_out, m_in = mask(size, outer), mask(size, inner)
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    if glow_a > 0 and bleed > 0:
        g = m_out.filter(ImageFilter.GaussianBlur(bleed * k * 0.45)).point(lambda p: int(min(255, p * glow_a)))
        out = Image.alpha_composite(out, solid(size, rim_rgb, ImageChops.subtract(g, m_out)))
    if fill:
        top, bot, a = fill
        body = Image.new("RGBA", size)
        d = ImageDraw.Draw(body)
        for y in range(size[1]):
            t = min(1, max(0, (y - b) / max(1, size[1] - 2 * b))) if grad else 0
            d.line([(0, y), (size[0], y)], fill=tuple(round(top[i] + (bot[i] - top[i]) * t) for i in range(3)) + (a,))
        body.putalpha(ImageChops.multiply(m_in, Image.new("L", size, a)))
        out = Image.alpha_composite(out, body)
    out = Image.alpha_composite(out, solid(size, rim_rgb, ImageChops.subtract(m_out, m_in)))
    return out.resize((w * scale, h * scale), Image.LANCZOS)


def build(sel, glow):
    g = 1.0 if glow == "glow" else 0.0
    f = {}
    # panel 96x96, box 72 (bleed 12), slice 36: corner art 24 -> cut 16, rim 2, graphite at ~90 %
    f["panel"] = lambda s: frame(96, 96, 12, 16, 2, CYAN, (G_TOP, G_BOT, 232), 0.7 * g, s, grad=False)
    # selection 48x40, box 40x32 (bleed 4), slice 12/10: art 8/6 -> cut 6, rim 2 (outline) or 1 (fill)
    if sel == "outline":
        f["selection"] = lambda s: frame(48, 40, 4, 6, 2, MAGENTA, (MAGENTA, MAGENTA, 38), 1.4 * g, s, grad=False)
    else:
        f["selection"] = lambda s: frame(48, 40, 4, 6, 1, (255, 120, 196), ((150, 40, 100), (120, 30, 82), 150),
                                         1.2 * g, s, grad=False)
    # heading 40x24, no bleed, slice 12/6: a quiet cyan-tinted band, no rim (never mistaken for the selection)
    f["heading"] = lambda s: frame(40, 24, 0, 5, 0, CYAN, ((40, 64, 74), (40, 64, 74), 170), 0, s, grad=False)
    # keys 48x48, box 40 (bleed 4), slice 16: art 12 -> cut 8
    f["key"] = lambda s: frame(48, 48, 4, 8, 1, STEEL, (G_TOP, G_BOT, 235), 0, s)
    f["key_function"] = lambda s: frame(48, 48, 4, 8, 1, (84, 96, 110), ((34, 41, 50), (26, 32, 40), 235), 0, s)
    f["key_lit"] = lambda s: frame(48, 48, 4, 8, 2, CYAN, ((40, 92, 104), (30, 70, 80), 240), 1.0 * g, s)
    if sel == "outline":
        f["key_selected"] = lambda s: frame(48, 48, 4, 8, 2, MAGENTA, ((70, 40, 60), (52, 32, 46), 240), 1.6 * g, s)
    else:
        f["key_selected"] = lambda s: frame(48, 48, 4, 8, 1, (255, 120, 196), ((170, 45, 112), (130, 34, 88), 245),
                                            1.4 * g, s)
    # field 56x56, box 48 (bleed 4), slice 16: a darker well with a cyan rim
    f["field"] = lambda s: frame(56, 56, 4, 8, 2, CYAN, ((18, 24, 31), (22, 28, 36), 240), 0.7 * g, s)
    return f


SPEC = {  # name: (slice l, t, r, b), bleed - the spec's recommended numbers
    "panel": ((36, 36, 36, 36), 12), "selection": ((12, 10, 12, 10), 4), "heading": ((12, 6, 12, 6), 0),
    "key": ((16,) * 4, 4), "key_function": ((16,) * 4, 4), "key_lit": ((16,) * 4, 4),
    "key_selected": ((16,) * 4, 4), "field": ((16,) * 4, 4)}


def nine(img, scale, sl, bleed, box_w, box_h):
    """Draw a frame into a box the way ab_gui does: the image covers the box grown by the bleed; corners 1:1,
    edges stretched along, the centre both ways. Returns an RGBA of (box + 2*bleed) at `scale`."""
    l, t, r, b = [v * scale for v in sl]
    W, H = img.size
    ow, oh = (box_w + 2 * bleed) * scale, (box_h + 2 * bleed) * scale
    out = Image.new("RGBA", (ow, oh), (0, 0, 0, 0))
    xs_src, xs_dst = [0, l, W - r, W], [0, l, ow - r, ow]
    ys_src, ys_dst = [0, t, H - b, H], [0, t, oh - b, oh]
    for i in range(3):
        for j in range(3):
            sx0, sx1, sy0, sy1 = xs_src[i], xs_src[i + 1], ys_src[j], ys_src[j + 1]
            dx0, dx1, dy0, dy1 = xs_dst[i], xs_dst[i + 1], ys_dst[j], ys_dst[j + 1]
            if sx1 <= sx0 or sy1 <= sy0 or dx1 <= dx0 or dy1 <= dy0:
                continue
            piece = img.crop((sx0, sy0, sx1, sy1)).resize((dx1 - dx0, dy1 - dy0), Image.BILINEAR)
            out.alpha_composite(piece, (dx0, dy0))
    return out


def put(screen, frames, name, x, y, w, h, scale=1):
    sl, bleed = SPEC[name]
    im = nine(frames[name](scale), scale, sl, bleed, w, h)
    screen.alpha_composite(im.resize(((w + 2 * bleed), (h + 2 * bleed)), Image.LANCZOS) if scale != 1 else im,
                           (x - bleed, y - bleed))


def fonts():
    base = os.path.join(THEME, "font")
    med = os.path.join(base, "RedHatText-Medium.ttf")
    bold = os.path.join(base, "RedHatText-SemiBold.ttf")
    return (lambda px: ImageFont.truetype(med, px)), (lambda px: ImageFont.truetype(bold, px))


def background():
    bg = Image.open(os.path.join(DESIGN, "bg-proc", "bg-p5.png")).convert("RGBA")
    return Image.alpha_composite(bg, Image.new("RGBA", bg.size, (0, 0, 0, 110)))  # the code's dim behind a panel


def options_screen(frames, label):
    MED, BOLD = fonts()
    s = background()
    px, py, pw, ph = 30, 20, 1220, 660
    put(s, frames, "panel", px, py, pw, ph)
    d = ImageDraw.Draw(s)
    d.text((px + 24, py + 18), "Options", font=BOLD(28), fill=(240, 248, 250))
    d.line([(px + 24, py + 66), (px + pw - 24, py + 66)], fill=CYAN + (110,), width=1)
    rows = [("h", "Display"), ("r", "Theme", "ab2.0.0"), ("r", "Show covers", "On"), ("r", "Aspect ratio", "4:3"),
            ("h", "Sound"), ("r", "Background music", "On"), ("r", "Menu sounds", "On"), ("h", "System"),
            ("r", "Language", "Polski"), ("r", "Font", "Red Hat Text"), ("r", "Online box art", "Off")]
    y, sel = py + 74, 5
    for i, row in enumerate(rows):
        if row[0] == "h":
            put(s, frames, "heading", px + 1, y, pw - 2, 28)
            d = ImageDraw.Draw(s)
            d.text((px + 32, y + 14), row[1].upper(), font=BOLD(15), fill=CYAN, anchor="lm")
            y += 32
            continue
        if i == sel:
            put(s, frames, "selection", px + 1, y, pw - 2, 32)
            d = ImageDraw.Draw(s)
        on = i == sel
        d.text((px + 32, y + 16), row[1], font=MED(20), fill=(240, 248, 250) if on else (180, 192, 204), anchor="lm")
        d.text((px + pw - 24, y + 16), row[2], font=MED(20), fill=(240, 248, 250) if on else (140, 152, 166),
               anchor="rm")
        y += 36
    fy = py + ph - 54
    d.line([(px + 24, fy), (px + pw - 24, fy)], fill=CYAN + (110,), width=1)
    d.text((px + 24, fy + 27), "(X) Change    (O) Back    L2/R2 Page", font=MED(18), fill=(200, 210, 220), anchor="lm")
    d.text((px + 12, 700), label, font=BOLD(16), fill=(255, 255, 255))
    return s


def keyboard_screen(frames, label):
    MED, BOLD = fonts()
    s = background()
    px, py, pw, ph = 30, 20, 1220, 660
    put(s, frames, "panel", px, py, pw, ph)
    d = ImageDraw.Draw(s)
    d.text((px + 24, py + 18), "Wi-Fi password", font=BOLD(28), fill=(240, 248, 250))
    d.line([(px + 24, py + 66), (px + pw - 24, py + 66)], fill=CYAN + (110,), width=1)
    fx, fy, fw = px + 54, py + 96, pw - 108
    put(s, frames, "field", fx, fy, fw, 48)
    d = ImageDraw.Draw(s)
    d.text((fx + 16, fy + 24), "autobleem-2", font=MED(22), fill=(240, 248, 250), anchor="lm")
    tw = d.textlength("autobleem-2", font=MED(22))
    d.rectangle([fx + 16 + tw + 2, fy + 12, fx + 16 + tw + 3, fy + 36], fill=(240, 248, 250))
    rows = ["1234567890", "qwertyuiop", "asdfghjkl-", "zxcvbnm.@_"]
    kw, kh, gap = 96, 64, 8
    kx0 = px + (pw - (10 * kw + 9 * gap)) // 2
    ky = fy + 48 + 28
    for r, keys in enumerate(rows):
        for c, ch in enumerate(keys):
            x, y = kx0 + c * (kw + gap), ky + r * (kh + gap)
            name = "key_selected" if (r, c) == (1, 4) else "key"
            put(s, frames, name, x, y, kw, kh)
            ImageDraw.Draw(s).text((x + kw / 2, y + kh / 2), ch, font=MED(24), fill=(240, 248, 250), anchor="mm")
    y = ky + 4 * (kh + gap)
    x = kx0
    for label2, cols, name in (("Shift", 2, "key_lit"), ("#+=", 1, "key_function"), ("Space", 4, "key_function"),
                               ("Back", 2, "key_function"), ("Done", 1, "key_function")):
        w = cols * kw + (cols - 1) * gap
        put(s, frames, name, x, y, w, kh)
        ImageDraw.Draw(s).text((x + w / 2, y + kh / 2), label2, font=BOLD(20), fill=(240, 248, 250), anchor="mm")
        x += w + gap
    ImageDraw.Draw(s).text((px + 12, 700), label, font=BOLD(16), fill=(255, 255, 255))
    return s


def main():
    variants = [("outline", "glow"), ("outline", "flat"), ("fill", "glow"), ("fill", "flat")]
    names = {"outline": "zaznaczenie: ramka", "fill": "zaznaczenie: tlo", "glow": "z poswiata", "flat": "plaskie"}
    opt, kb = [], []
    for sel, glow in variants:
        fr = build(sel, glow)
        d = os.path.join(OUT, f"{sel}-{glow}", "frames")
        os.makedirs(d, exist_ok=True)
        for n, fn in fr.items():
            fn(1).save(os.path.join(d, f"{n}.png"))
            fn(2).save(os.path.join(d, f"{n}@2x.png"))
        lab = f"{names[sel]}, {names[glow]}"
        opt.append(options_screen(fr, lab))
        kb.append(keyboard_screen(fr, lab))
    for name, shots in (("frames-options.png", opt), ("frames-keyboard.png", kb)):
        sheet = Image.new("RGB", (2 * 1280 + 24, 2 * 720 + 24), (30, 30, 30))
        for i, im in enumerate(shots):
            sheet.paste(im.convert("RGB"), (8 + (i % 2) * 1288, 8 + (i // 2) * 728))
        sheet.resize((sheet.width // 2, sheet.height // 2), Image.LANCZOS).save(os.path.join(OUT, name))
        for i, im in enumerate(shots):
            im.convert("RGB").save(os.path.join(OUT, name.replace(".png", f"-{variants[i][0]}-{variants[i][1]}.png")))
    print("written:", OUT)


if __name__ == "__main__":
    main()
