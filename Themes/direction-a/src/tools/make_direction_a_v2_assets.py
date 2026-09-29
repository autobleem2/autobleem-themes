"""Direction A (CONSOLE-14): the theme's launcher images in the chosen v02b style (the owner, 2026-09-29).

Cut corners (the memory card's shape), cyan lines, magenta for the focused item. Same file names and
canvases as the default theme, written into design/direction-a/v2/ (not into Themes/ yet):
  menu_settings/guide/memcard/resume.png  118x118
  play_button.png  200x68  the chamfered frame alone (magenta - Play is the focused item)
  play_text.png    262x68  the triangle and "PLAY" alone (262 wide: the launcher centres it on x 640)
  meta_panel.png   30x30   the pad glyph on a small chamfered tile
  launcher_footer.png 1280x88  a chamfered panel behind the hint bar (hintBar 360,632 900x56 -> the
                   panel spans x 348..1268 of the strip)
  on.png / off.png 60x30   the classic UI's switch, chamfered, "on" in cyan
plus a preview on the background.
Run: python tools/make_direction_a_v2_assets.py
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_direction_a_icons as ic  # noqa: E402
import make_direction_a_variants as va  # noqa: E402

V = va.VARIANTS["b"]
OUT = os.path.join(va.A, "v2")
LAUNCHER = os.path.normpath(os.path.join(va.REPO, "..", "..", "..", "repos", "autobleem"))


def play_parts():
    w, h = 200, 68
    box = (12, 12, 188, 56)
    s = va.SS
    btn = va.frame(w, h, box, V, edge=V["focus"], stroke=2, glow_px=6, glow_a=0.6).resize((w, h), Image.LANCZOS)
    size = (w * s, h * s)
    txt = Image.new("RGBA", size, (0, 0, 0, 0))
    f = ImageFont.truetype(V["heading"], 25 * s)
    tw = f.getbbox("PLAY", anchor="lm")
    tw = (tw[2] - tw[0]) / s
    tri_h, gap = 19, 9
    gx = (box[0] + box[2]) / 2 - (tri_h * 0.87 + gap + tw) / 2
    cy = (box[1] + box[3]) / 2
    tri = Image.new("L", size, 0)
    ImageDraw.Draw(tri).polygon([(gx * s, (cy - tri_h / 2) * s), (gx * s, (cy + tri_h / 2) * s),
                                 ((gx + tri_h * 0.87) * s, cy * s)], fill=255)
    txt = va.lines(txt, tri, V["focus"], V)
    ImageDraw.Draw(txt).text(((gx + tri_h * 0.87 + gap) * s, cy * s), "PLAY", font=f, fill=va.WHITE + (255,),
                             anchor="lm")
    # the launcher draws playText at x = 640 - 262/2 and playButton at x = 540 (evoui_launcher_screen.cpp):
    # the text's canvas is 262 wide, so the 200-wide content goes 31 px in to sit on the button
    wide = Image.new("RGBA", (262, h), (0, 0, 0, 0))
    wide.alpha_composite(txt.resize((w, h), Image.LANCZOS), (31, 0))
    return btn, wide


def meta_panel():
    base = va.frame(30, 30, (3, 5, 27, 25), V, stroke=1, glow_px=2, glow_a=0.6)
    p = ic.pad_mask(30, 30, 15, 15.5, 17, 10)
    return va.lines(base, p, V["line"], V, glow_px=1, glow_a=0.6).resize((30, 30), Image.LANCZOS)


def footer():
    w, h = 1280, 88
    return va.frame(w, h, (348, 6, 1268, 84), V, stroke=2, body_alpha=225, glow_px=5, glow_a=0.35,
                    ss=2).resize((w, h), Image.LANCZOS)


def switch(on):
    w, h = 60, 30
    box = (6, 7, 54, 23)
    edge = V["line"] if on else (110, 124, 138)
    base = va.frame(w, h, box, V if on else dict(V, glow=0), edge=edge, stroke=1.5)
    s = va.SS
    if on:
        fill = va.shape_mask(w, h, box, V["shape"], inset=3)
        base = va.lines(base, fill, V["line"], dict(V, glow=0))
    kx = 45 if on else 15
    knob = Image.new("L", base.size, 0)
    c = 3
    x0, x1, y0, y1 = (kx - 7) * s, (kx + 7) * s, 10 * s, 20 * s
    ImageDraw.Draw(knob).polygon([(x0, y0), (x1 - c * s, y0), (x1, y0 + c * s), (x1, y1), (x0 + c * s, y1),
                                  (x0, y1 - c * s)], fill=255)
    base = Image.alpha_composite(base, va.solid(base.size, (240, 248, 250) if on else (150, 162, 175), knob))
    return base.resize((w, h), Image.LANCZOS)


def main():
    os.makedirs(OUT, exist_ok=True)
    files = {f"menu_{k}": va.menu_icon(k, V) for k in ("settings", "guide", "memcard", "resume")}
    files["play_button"], files["play_text"] = play_parts()
    files["meta_panel"] = meta_panel()
    files["launcher_footer"] = footer()
    files["on"], files["off"] = switch(True), switch(False)
    for n, im in files.items():
        im.save(os.path.join(OUT, n + ".png"))
    # preview: everything on the background at its screen spot
    scr = Image.open(os.path.join(va.A, "bg-direction-a-01-smooth.png")).convert("RGBA").resize((1280, 720))
    scr.alpha_composite(files["launcher_footer"], (0, 632))
    scr.alpha_composite(files["play_button"], (540, 400))
    scr.alpha_composite(files["play_text"], (540, 400))
    for k, n in enumerate(("settings", "guide", "memcard", "resume")):
        scr.alpha_composite(files[f"menu_{n}"], (400 + k * 130, 480))
    scr.alpha_composite(files["meta_panel"], (960, 420))
    scr.alpha_composite(files["on"], (1010, 420))
    scr.alpha_composite(files["off"], (1080, 420))
    scr.convert("RGB").save(os.path.join(OUT, "preview-v2.png"))
    print("written:", OUT)


if __name__ == "__main__":
    main()
