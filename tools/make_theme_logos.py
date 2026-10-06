"""The AutoBleem 2 logo in the 16:9 art of aergb, default, evolution and Legacy of 2018 (the owner, 2026-10-06: the
new logo, coloured to fit each style, everywhere but ab2.0.0, which has its own as launcher.logo). The logos come
coloured from autobleem-design (themes/ab2.0.0/tools/make_logo_theme_colours.py -> design/logo-ab2/logo-*@2x.png);
the art they go into is the art as it was before (design/logo-ab2/<theme>-<background|footer>.orig.png), so a rerun
starts from the same pixels:

  aergb, default   the old stacked "Auto Bleem" painted out of the background's foot (OpenCV's Telea fill over the
                   pixels that are not the navy), the new logo (arc colours) in its place, 340 px wide
  evolution        the old logo on the console's lid painted out of launcher_footer.png (the lid's own grey under the
                   footer's transparent top rows, so the fill does not pull black), the new one engraved on the lid
                   (evo-silver), 206 px wide
  Legacy of 2018   no logo before: the new one (white) top-right, 285 px wide, above the side covers

Writes Themes/<theme>/images/launcher_background.png (and evolution's launcher_footer.png). The 4:3 pictures are
tools/make_4x3_backgrounds.py's (they cut from the .orig art and set the logo again in the 4:3 box).
Needs Pillow, numpy and opencv-python.  Run: python tools/make_theme_logos.py
"""
import os

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
THEMES = os.path.join(HERE, "..", "Themes")
SRC = os.path.join(HERE, "..", "design", "logo-ab2")

OLD_ARC_LOGO = (70, 515, 350, 712)          # aergb / default: the old logo in the 1280x720 background
ARC_LOGO = (30, 614, 340)                   # the new one: x, its vertical centre, width (clear of the hint swoosh)
EVO_OLD = (236, 8, 326, 70)                 # evolution: the old logo on the lid, in launcher_footer.png (1280x100)
EVO_LID = (280, 46, 206)                    # the new one: its centre on the lid, width
LEGACY_LOGO = (30, 16, 285)                 # Legacy: right margin, top, width


def logo(palette, width):
    lg = Image.open(os.path.join(SRC, "logo-%s@2x.png" % palette)).convert("RGBA")
    return lg.resize((width, round(lg.height * width / lg.width)), Image.LANCZOS)


def orig(name, kind):
    return Image.open(os.path.join(SRC, "%s-%s.orig.png" % (name.replace(" ", "-"), kind)))


def paint_out(im, box, mask):
    """OpenCV's Telea fill over mask (box-sized, 0/255), a little widened for the anti-aliased edges"""
    a = cv2.cvtColor(np.asarray(im.convert("RGB")), cv2.COLOR_RGB2BGR)
    m = np.zeros(a.shape[:2], np.uint8)
    x0, y0, x1, y1 = box
    m[y0:y1, x0:x1] = mask
    m = cv2.dilate(m, np.ones((5, 5), np.uint8), iterations=2)
    return Image.fromarray(cv2.cvtColor(cv2.inpaint(a, m, 12, cv2.INPAINT_TELEA), cv2.COLOR_BGR2RGB))


def arc(name):
    bg = orig(name, "background").convert("RGB")
    x0, y0, x1, y1 = OLD_ARC_LOGO
    a = np.asarray(bg)[y0:y1, x0:x1].astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    lum = (r * 3 + g * 6 + b) // 10
    navy = (b > r + 25) & (b > g + 8) & (lum > 14) & (lum < 90)          # the background; the rest is the old logo
    out = paint_out(bg, OLD_ARC_LOGO, np.where(navy, 0, 255).astype(np.uint8)).convert("RGBA")
    x, cy, w = ARC_LOGO
    lg = logo("arc", w)
    out.alpha_composite(lg, (x, cy - lg.height // 2))
    out.convert("RGB").save(os.path.join(THEMES, name, "images", "launcher_background.png"), optimize=True)


def evolution():
    ft = orig("evolution", "footer").convert("RGBA")
    f = np.asarray(ft.convert("RGB")).astype(np.float64)
    smooth = cv2.GaussianBlur(f, (0, 0), 9)
    x0, y0, x1, y1 = EVO_OLD
    dev = (np.abs(f - smooth).max(2) > 10)[y0:y1, x0:x1]                 # the engraving's edges
    sat = (f.max(2) - f.min(2) > 40)[y0:y1, x0:x1]                       # its small rainbow arc
    dark = (f.mean(2) < smooth.mean(2) - 12)[y0:y1, x0:x1]               # its shadowed "2"
    flat = Image.new("RGBA", ft.size, (150, 150, 152, 255))
    flat.alpha_composite(ft)
    out = paint_out(flat, EVO_OLD, np.where(dev | sat | dark, 255, 0).astype(np.uint8)).convert("RGBA")
    out.putalpha(ft.getchannel("A"))
    cx, cy, w = EVO_LID
    lg = logo("evo-silver", w)
    out.alpha_composite(lg, (cx - lg.width // 2, cy - lg.height // 2))
    out.save(os.path.join(THEMES, "evolution", "images", "launcher_footer.png"), optimize=True)


def legacy():
    bg = orig("Legacy of 2018", "background").convert("RGBA")
    m, top, w = LEGACY_LOGO
    lg = logo("legacy", w)
    bg.alpha_composite(lg, (bg.width - m - w, top))
    bg.convert("RGB").save(os.path.join(THEMES, "Legacy of 2018", "images", "launcher_background.png"), optimize=True)


def main():
    arc("aergb")
    arc("default")
    evolution()
    legacy()
    print("ok")


if __name__ == "__main__":
    main()
