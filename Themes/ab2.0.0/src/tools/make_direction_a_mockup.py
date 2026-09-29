"""Direction A (CONSOLE-14): a mockup of the EvolutionUI launcher's Games screen with every Direction A piece.

v01 (2026-09-29). Layout taken from the launcher's screenshots (1280x720): the carousel with the selected
cover in the middle, the game's details and meta row to its right, the Play button under it, the game
menu's icons below, the hint bar at the bottom right, the "Showing" banner at the top right, the logo at
the bottom left. The covers are made-up placeholders (no real box art).
Uses design/direction-a/ (background, Play v02, logo B4, icons/, evoimg/) and the default theme's button
hints (small button icons stay default's).
Run: python tools/make_direction_a_mockup.py --launcher ../../../repos/autobleem
"""
import argparse
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
A = os.path.join(REPO, "Themes", "ab2.0.0", "src", "design")
DEF = os.path.join(REPO, "Themes", "default")

CYAN = (54, 217, 224)
WHITE = (240, 248, 250)
GREY = (150, 164, 178)
PANEL_TOP = (40, 48, 58)
PANEL_BOT = (26, 32, 40)


def img(*p):
    return Image.open(os.path.join(*p)).convert("RGBA")


def panel(w, h, radius, glow=True, alpha=235):
    """A graphite panel with a thin cyan top edge, like the Play pill's body."""
    ss = 3
    size = (w * ss, h * ss)
    body = Image.new("RGBA", size)
    d = ImageDraw.Draw(body)
    for y in range(size[1]):
        t = y / size[1]
        d.line([(0, y), (size[0], y)], fill=tuple(round(PANEL_TOP[i] + (PANEL_BOT[i] - PANEL_TOP[i]) * t)
                                                  for i in range(3)) + (alpha,))
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius * ss, fill=255)
    body.putalpha(Image.eval(m, lambda v: v * alpha // 255))
    edge = Image.new("L", size, 0)
    ImageDraw.Draw(edge).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius * ss,
                                           outline=255, width=2 * ss)
    top = Image.new("L", size, 0)
    ImageDraw.Draw(top).rectangle([0, 0, size[0], size[1] // 2], fill=255)
    top = top.filter(ImageFilter.GaussianBlur(size[1] // 4))
    edge = Image.eval(Image.composite(edge, Image.new("L", size, 0), top), lambda v: v)
    ec = Image.new("RGBA", size, CYAN + (0,))
    ec.putalpha(edge)
    out = Image.alpha_composite(body, ec)
    return out.resize((w, h), Image.LANCZOS)


def cover(w, h, c1, c2, title, font):
    """A made-up box: a diagonal two-tone gradient, a big shape, a title band."""
    im = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=tuple(round(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)) + (255,))
    d.ellipse([w * 0.18, h * 0.22, w * 0.82, h * 0.86], fill=tuple(min(255, v + 40) for v in c2) + (255,))
    d.rectangle([0, 0, w, h * 0.2], fill=(15, 15, 20, 255))
    f = ImageFont.truetype(font, max(10, int(h * 0.1)))
    d.text((w / 2, h * 0.1), title, font=f, fill=(250, 250, 250, 255), anchor="mm")
    d.rectangle([0, 0, w * 0.06, h], fill=(20, 20, 24, 255))  # the jewel case's spine
    return im


def reflect(im, frac=0.35, strength=0.3):
    h = int(im.height * frac)
    r = im.transpose(Image.FLIP_TOP_BOTTOM).crop((0, 0, im.width, h))
    grad = Image.linear_gradient("L").resize((im.width, h)).point(lambda v: int((255 - v) * strength))
    a = r.getchannel("A")
    r.putalpha(Image.eval(Image.merge("L", [a]), lambda v: v).point(lambda v: v))
    r.putalpha(Image.composite(grad, Image.new("L", r.size, 0), a))
    return r


def shadow(im, blur=10, alpha=0.6):
    a = im.getchannel("A").filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * alpha))
    s = Image.new("RGBA", im.size, (0, 0, 0, 0))
    s.putalpha(a)
    return s


def text(d, xy, s, font, fill, anchor="la", shadow_=True):
    if shadow_:
        d.text((xy[0] + 1, xy[1] + 2), s, font=font, fill=(0, 0, 0, 150), anchor=anchor)
    d.text(xy, s, font=font, fill=fill, anchor=anchor)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--launcher", required=True)
    a = ap.parse_args()
    fonts = os.path.join(a.launcher, "src", "resources", "fonts")
    bold, med = os.path.join(fonts, "OpenSans-Bold.ttf"), os.path.join(fonts, "OpenSans-Medium.ttf")

    scr = img(A, "bg-direction-a-01-smooth.png").resize((1280, 720))
    d = ImageDraw.Draw(scr)

    # --- the carousel: covers to the right, faded ones to the left, the selected one in the middle ---------
    games = [("NEON RUN", (20, 60, 120), (60, 190, 230)), ("STAR KNIGHT", (90, 20, 60), (230, 90, 120)),
             ("DEEP ORBIT", (10, 30, 40), (40, 160, 140)), ("IRON FIST", (60, 40, 10), (220, 150, 40)),
             ("PIXEL QUEST", (40, 20, 90), (140, 90, 230)), ("TURBO KART", (80, 10, 10), (240, 70, 40)),
             ("SKY PATROL", (10, 50, 80), (120, 200, 240)), ("GHOST TOWN", (30, 30, 30), (130, 130, 140))]
    x = 785
    for k, (t, c1, c2) in enumerate(games[1:]):
        size = 118 - k * 4
        cv = cover(size, size, c1, c2, t, bold)
        scr.alpha_composite(shadow(cv, 6), (x + 3, 100 + 4))
        scr.alpha_composite(cv, (x, 100))
        scr.alpha_composite(reflect(cv, 0.3, 0.25), (x, 100 + size + 2))
        x += size - 40
    # the games already passed: a mirrored stack, dimmed, the nearest drawn last
    left = [("RETRO RALLY", (50, 70, 20), (170, 210, 60)), ("MOON BASE", (20, 20, 50), (90, 110, 200)),
            ("LAVA LAND", (90, 30, 0), (250, 120, 30)), ("ICE PALACE", (20, 60, 80), (170, 230, 250))]
    for k in reversed(range(len(left))):
        t, c1, c2 = left[k]
        size = 110 - k * 4
        cv = cover(size, size, c1, c2, t, bold)
        cv.putalpha(cv.getchannel("A").point(lambda v: v * 50 // 100))
        scr.alpha_composite(cv, (530 - 30 - size - k * 62, 104))
    sel = cover(220, 220, *games[0][1:], games[0][0], bold)
    glow = Image.new("RGBA", (300, 300), CYAN + (0,))
    gm = Image.new("L", (300, 300), 0)
    ImageDraw.Draw(gm).rectangle([40, 40, 260, 260], fill=255)
    glow.putalpha(gm.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * 0.45)))
    scr.alpha_composite(glow, (530 - 40, 93 - 40))
    scr.alpha_composite(sel, (530, 93))
    scr.alpha_composite(reflect(sel, 0.3, 0.3), (530, 93 + 222))

    # --- the game's details and the meta row ---------------------------------------------------------------
    d = ImageDraw.Draw(scr)
    text(d, (786, 218), "Neon Run", ImageFont.truetype(bold, 28), WHITE)
    f = ImageFont.truetype(med, 15)
    text(d, (787, 258), "Made-up Studio, 1997", f, GREY)
    text(d, (787, 278), "Serial: SLUS-00000, Region: USA", f, GREY)
    text(d, (787, 298), "Last played: yesterday", f, GREY)
    ev = lambda n: img(A, "evoimg", f"{n}-direction-a-01.png")  # noqa: E731
    my = 322
    scr.alpha_composite(img(A, "icons", "meta_panel-direction-a-01.png"), (784, my))
    text(d, (818, my + 15), "1 Player", ImageFont.truetype(bold, 15), WHITE, anchor="lm")
    xx = 900
    for n, extra in (("cd", "1"), ("favorite", None), ("sd", None), ("lock", None)):
        icon = ev(n)
        scr.alpha_composite(icon, (xx, my + (30 - icon.height) // 2))
        xx += icon.width + 6
        if extra:
            text(d, (xx - 2, my + 15), extra, ImageFont.truetype(bold, 15), WHITE, anchor="lm")
            xx += 16
        xx += 6

    # --- Play, the game menu's icons ---------------------------------------------------------------------
    play = img(A, "play_full-direction-a-02.png")
    scr.alpha_composite(play, (640 - play.width // 2, 405))
    for k, n in enumerate(("menu_settings", "menu_guide", "menu_memcard", "menu_resume")):
        icon = img(A, "icons", f"{n}-direction-a-01.png").resize((96, 96), Image.LANCZOS)
        scr.alpha_composite(icon, (640 - 48 + k * 118 - 1 * 0, 500))

    # --- the "Showing" banner ------------------------------------------------------------------------------
    b = panel(420, 46, 10)
    scr.alpha_composite(b, (1280 - 16 - 420, 16))
    d = ImageDraw.Draw(scr)
    text(d, (1280 - 16 - 420 + 18, 16 + 23), "Showing: All games (24)", ImageFont.truetype(bold, 19), WHITE,
         anchor="lm")

    # --- the hint bar -----------------------------------------------------------------------------------------
    hb = panel(840, 76, 14)
    hx, hy = 1280 - 16 - 840, 720 - 12 - 76
    scr.alpha_composite(hb, (hx, hy))
    d = ImageDraw.Draw(scr)
    hf = ImageFont.truetype(med, 19)

    def hint_row(y, items):
        widths = []
        for icon, label in items:
            widths.append(icon.width + 6 + d.textlength(label, font=hf))
        gap = 34
        total = sum(widths) + gap * (len(items) - 1)
        x0 = hx + (840 - total) / 2
        for (icon, label), w_ in zip(items, widths):
            scr.alpha_composite(icon, (int(x0), int(y - icon.height / 2)))
            text(d, (x0 + icon.width + 6, y), label, hf, WHITE, anchor="lm", shadow_=False)
            x0 += w_ + gap

    def keycap(label):
        f2 = ImageFont.truetype(bold, 12)
        w_ = int(d.textlength(label, font=f2)) + 12
        k = Image.new("RGBA", (w_, 22), (0, 0, 0, 0))
        kd = ImageDraw.Draw(k)
        kd.rounded_rectangle([0, 0, w_ - 1, 21], radius=4, fill=(70, 82, 96, 255))
        kd.text((w_ / 2, 11), label, font=f2, fill=WHITE, anchor="mm")
        return k

    small = lambda im: im.resize((24, 24), Image.LANCZOS)  # noqa: E731
    hint_row(hy + 24, [(img(DEF, "images", "hint_cross.png"), "Play"), (small(ev("dpad_down")), "Game menu"),
                       (small(ev("dpad_up")), "Quick menu")])
    hint_row(hy + 54, [(keycap("SELECT"), "Games shown"), (keycap("START"), "Random"),
                       (img(DEF, "images", "hint_triangle.png"), "Guide"), (keycap("L2+R2"), "System")])

    # --- the logo ---------------------------------------------------------------------------------------------
    logo = img(A, "logo", "logo-b4.png")
    logo = logo.resize((int(logo.width * 0.72), int(logo.height * 0.72)), Image.LANCZOS)
    scr.alpha_composite(logo, (6, 720 - logo.height + 38))

    out = os.path.join(A, "mockup")
    os.makedirs(out, exist_ok=True)
    scr.convert("RGB").save(os.path.join(out, "launcher-games-direction-a-01.png"))
    print("written:", out)


if __name__ == "__main__":
    main()
