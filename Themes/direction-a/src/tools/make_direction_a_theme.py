"""Direction A (CONSOLE-14): assemble the trial theme Themes/direction-a/ from the design sources.

A first build on today's theme.json format (the owner, 2026-09-29): what the format can already carry. What
needs code changes is listed in ../README.md. Writes, next to src/:
  theme.json
  images/  launcher_background.png (background p5), launcher_footer.png, play_button.png, play_text.png,
           menu_settings/guide/memcard/resume.png, meta_panel.png, arrow.png, memcard_grid.png,
           memcard_pencil.png                                 (v02b: cut corners, cyan lines, magenta focus)
  background.jpg, ab.png (logo C3), on.png, off.png           the classic UI
  font/    RedHatText-Medium.ttf, RedHatText-SemiBold.ttf     static cuts of Red Hat Text (OFL, no reserved
           name) + OFL.txt
  credit.txt
Anything not here (hint icons, the other button glyphs, sounds, music, the settings panel) falls back to
Themes/default, as the format says.
Run: python src/tools/make_direction_a_theme.py --launcher ../../../repos/autobleem --fonts ../../../tmp/fonts
     (from the repository root)
"""
import json
import os
import shutil
import sys

LAUNCHER = sys.argv[sys.argv.index("--launcher") + 1]
FONTS = sys.argv[sys.argv.index("--fonts") + 1]
sys.argv = [sys.argv[0], "--font-dir", os.path.join(LAUNCHER, "src", "resources", "fonts")]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image  # noqa: E402

import make_direction_a_icons as ic  # noqa: E402
import make_direction_a_variants as va  # noqa: E402

THEME = os.path.join(va.REPO, "Themes", "direction-a")
DESIGN = va.A


def fonts():
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    src = os.path.join(FONTS, "other", "RedHatText[wght].ttf")
    d = os.path.join(THEME, "font")
    os.makedirs(d, exist_ok=True)
    out = {}
    for name, w in (("Medium", 500), ("SemiBold", 600)):
        f = TTFont(src)
        instancer.instantiateVariableFont(f, {"wght": w}, inplace=True)
        p = os.path.join(d, f"RedHatText-{name}.ttf")
        f.save(p)
        out[name] = p
    shutil.copyfile(os.path.join(FONTS, "other", "RedHat-OFL.txt"), os.path.join(d, "OFL.txt"))
    return out


def main():
    os.makedirs(os.path.join(THEME, "images"), exist_ok=True)
    f = fonts()
    va.VARIANTS["b"]["heading"] = f["SemiBold"]  # the PLAY label in the theme's own font
    import make_direction_a_v2_assets as v2  # noqa: E402  (after the heading is set)

    img = lambda n: os.path.join(THEME, "images", n)  # noqa: E731
    for k in ("settings", "guide", "memcard", "resume"):
        va.menu_icon(k, v2.V).save(img(f"menu_{k}.png"))
    btn, txt = v2.play_parts()
    btn.save(img("play_button.png"))
    txt.save(img("play_text.png"))
    v2.meta_panel().save(img("meta_panel.png"))
    v2.footer().save(img("launcher_footer.png"))
    ic.icon_arrow().save(img("arrow.png"))
    ic.memcard_grid().save(img("memcard_grid.png"))
    ic.memcard_pencil().save(img("memcard_pencil.png"))
    bg = Image.open(os.path.join(DESIGN, "bg-proc", "bg-p5.png")).convert("RGB")
    bg.save(img("launcher_background.png"))
    bg.save(os.path.join(THEME, "background.jpg"), quality=92, subsampling=0)
    shutil.copyfile(os.path.join(DESIGN, "logo", "logo-c3.png"), os.path.join(THEME, "ab.png"))
    v2.switch(True).save(os.path.join(THEME, "on.png"))
    v2.switch(False).save(os.path.join(THEME, "off.png"))

    spec = {
        "format": 1,
        "classic": {
            "background": "background.jpg",
            "logo": {"file": "ab.png", "x": 400, "y": 160, "w": 480, "h": 360},
            "menuLines": 12,
            "menuPanel": {"x": 30, "y": 10, "w": 1220, "h": 615, "color": "#1a212b", "alpha": 215},
            "statusBar": {"x": 30, "y": -670, "w": 1220, "h": 33, "color": "#1a212b", "alpha": 215, "textY": 662},
            "textColor": "#f0f8fa",
            "textShadow": True,
            "keyboardKey": {"color": "#3a4654", "alpha": 215},
            "labelColor": "#28313d",
            "freeSpaceText": {"x": 180, "y": 35},
            "buttons": {"cross": "cross.png", "circle": "circle.png", "square": "square.png",
                        "triangle": "triangle.png", "start": "start.png", "select": "select.png",
                        "l1": "l1.png", "r1": "r1.png", "l2": "l2.png", "r2": "r2.png",
                        "check": "on.png", "uncheck": "off.png", "esc": "esc.png", "enter": "enter.png",
                        "tab": "tab.png"},
        },
        "launcher": {
            "background": "images/launcher_background.png",
            "footer": "images/launcher_footer.png",
            "playButton": "images/play_button.png",
            "playText": "images/play_text.png",
            "metaPanel": "images/meta_panel.png",
            "metaPanelSlides": True,
            "textShadow": True,
            "arrow": "images/arrow.png",
            "hintBar": {"x": 360, "y": 642, "w": 900, "h": 68},
            "menuIcons": {"settings": "images/menu_settings.png", "guide": "images/menu_guide.png",
                          "memcard": "images/menu_memcard.png", "resume": "images/menu_resume.png",
                          "resumePicture": {"x": 25, "y": 33, "w": 68, "h": 52}},
            "memcardManager": {"grid": "images/memcard_grid.png", "pencil": "images/memcard_pencil.png"},
            "fonts": {"medium": "font/RedHatText-Medium.ttf", "bold": "font/RedHatText-SemiBold.ttf"},
            "colors": {"text": "#f0f8fa", "secondary": "#96a4b2", "hint": "#c8d2dc", "selection": "#ff46aa"},
        },
    }
    with open(os.path.join(THEME, "theme.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(spec, fh, indent=2)
        fh.write("\n")
    with open(os.path.join(THEME, "credit.txt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("direction-a - a trial of AutoBleem 2's new look (CONSOLE-14).\n"
                 "Images: drawn by src/tools/*.py (vectors and a procedural background); no photographs, no AI\n"
                 "pictures. Font: Red Hat Text, SIL Open Font License 1.1 (font/OFL.txt), static cuts of the\n"
                 "variable font. Sounds, music and the button glyphs come from the default theme.\n")
    print("theme written:", THEME)


if __name__ == "__main__":
    main()
