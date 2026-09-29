"""Direction A (CONSOLE-14): the candidate fonts (all OFL, Google Fonts) on the launcher and the emulator menu.

Each family is cut to two static weights with fontTools (medium 500 for text, semibold/bold for titles and
headings), then the v02b launcher Games screen (background p5) and the v02b emulator menu are drawn in it,
with a diacritics sample (Polish, Czech, Romanian, Turkish) - the launcher's languages minus Chinese, which
stays on Noto. Writes design/direction-a/fonts/fonts-1.png, fonts-2.png.
Run: python tools/make_direction_a_fonts.py --launcher ../../../repos/autobleem --fonts ../../../tmp/fonts
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

LAUNCHER = sys.argv[sys.argv.index("--launcher") + 1]
FONTS = sys.argv[sys.argv.index("--fonts") + 1]
PART = sys.argv[sys.argv.index("--part") + 1] if "--part" in sys.argv else None
sys.argv = [sys.argv[0], "--font-dir", os.path.join(LAUNCHER, "src", "resources", "fonts")]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_direction_a_screens_v2 as sc  # noqa: E402
import make_direction_a_variants as va  # noqa: E402
import make_direction_a_emu_v2 as emu  # noqa: E402

SAMPLE = "Zażółć gęślą jaźń · Příliš žluťoučký · Șir țară · Türkçe ığş · 0123456789"


def static(path, out, axes):
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    if os.path.isfile(out):
        return out
    f = TTFont(path)
    if "fvar" in f:
        present = {a.axisTag for a in f["fvar"].axes}
        instancer.instantiateVariableFont(f, {k: v for k, v in axes.items() if k in present}, inplace=True)
    f.save(out)
    return out


def family(name, med_src, bold_src, med_w=500, bold_w=650):
    d = os.path.join(FONTS, "static")
    os.makedirs(d, exist_ok=True)
    base = {"opsz": 14, "wdth": 100}
    return (name, static(os.path.join(FONTS, med_src), os.path.join(d, f"{name}-med.ttf"), dict(base, wght=med_w)),
            static(os.path.join(FONTS, bold_src), os.path.join(d, f"{name}-bold.ttf"), dict(base, wght=bold_w)))


def main():
    lf = os.path.join(LAUNCHER, "src", "resources", "fonts")
    fams = [("Open Sans (dzis)", os.path.join(lf, "OpenSans-Medium.ttf"), os.path.join(lf, "OpenSans-Bold.ttf")),
            family("Inter", "inter/Inter[opsz,wght].ttf", "inter/Inter[opsz,wght].ttf"),
            family("Manrope", "manrope/Manrope[wght].ttf", "manrope/Manrope[wght].ttf", 500, 700),
            family("Barlow", "barlow/Barlow-Medium.ttf", "barlow/Barlow-SemiBold.ttf"),
            family("Barlow Semi Condensed", "barlowsemicondensed/BarlowSemiCondensed-Medium.ttf",
                   "barlowsemicondensed/BarlowSemiCondensed-SemiBold.ttf"),
            family("Exo 2", "exo2/Exo2[wght].ttf", "exo2/Exo2[wght].ttf"),
            family("Oxanium", "oxanium/Oxanium[wght].ttf", "oxanium/Oxanium[wght].ttf"),
            family("IBM Plex Sans", "ibmplexsans/IBMPlexSans[wdth,wght].ttf",
                   "ibmplexsans/IBMPlexSans[wdth,wght].ttf", 500, 600),
            family("Titillium Web", "titilliumweb/TitilliumWeb-Regular.ttf", "titilliumweb/TitilliumWeb-SemiBold.ttf")]
    # partia 2: OFL fonts from their authors (GitHub releases; Red Hat Text via Google Fonts)
    o = "other/"
    fams += [family("Geist", o + "geist-font-v1.7.2/geist-font/Geist/ttf/Geist-Medium.ttf",
                    o + "geist-font-v1.7.2/geist-font/Geist/ttf/Geist-SemiBold.ttf"),
             family("Mona Sans", o + "mona-sans-variable-v2.0.27/fonts/variable/MonaSansVF[opsz,wght].ttf",
                    o + "mona-sans-variable-v2.0.27/fonts/variable/MonaSansVF[opsz,wght].ttf", 500, 650),
             family("Hubot Sans", o + "Hubot-Sans/Hubot Sans/TTF/HubotSans-Medium.ttf",
                    o + "Hubot-Sans/Hubot Sans/TTF/HubotSans-SemiBold.ttf"),
             family("Source Sans 3", o + "VF-source-sans-3.052R/VF/SourceSans3VF-Upright.ttf",
                    o + "VF-source-sans-3.052R/VF/SourceSans3VF-Upright.ttf", 500, 650),
             family("Red Hat Text", o + "RedHatText[wght].ttf", o + "RedHatText[wght].ttf", 500, 650)]
    out = os.path.join(va.A, "fonts")
    os.makedirs(out, exist_ok=True)
    bg = Image.open(os.path.join(va.A, "bg-proc", "bg-p5.png")).convert("RGBA")
    art = sc.emu(bg)
    tw, th, rowh = 640, 360, 360 + 80
    label_font = ImageFont.truetype(os.path.join(lf, "OpenSans-Bold.ttf"), 24)
    only = PART
    for part, chunk in enumerate((fams[:5], fams[5:9], fams[9:])):
        if only and str(part + 1) != only:
            continue
        sheet = Image.new("RGB", (2 * tw + 48, len(chunk) * rowh + 16), (12, 15, 20))
        d = ImageDraw.Draw(sheet)
        for i, (name, med, bold) in enumerate(chunk):
            v = dict(va.VARIANTS["b"], heading=bold)
            evo = va.render("b", v, bold, med, bg=bg, label=False)
            va.SAIRA = bold  # the emulator mockup's headings and title
            emu_fonts = os.path.join(out, "_emu_fonts")
            os.makedirs(emu_fonts, exist_ok=True)
            for src, dst in ((bold, "OpenSans-Bold.ttf"), (med, "OpenSans-Medium.ttf")):
                with open(src, "rb") as a, open(os.path.join(emu_fonts, dst), "wb") as b:
                    b.write(a.read())
            menu = emu.menu_v2(art, emu_fonts)
            y = 16 + i * rowh
            d.text((16, y), name, font=label_font, fill=(54, 217, 224))
            d.text((16, y + 34), SAMPLE, font=ImageFont.truetype(med, 22), fill=(230, 236, 242))
            sheet.paste(evo.resize((tw, th), Image.LANCZOS), (16, y + 70))
            sheet.paste(menu.resize((tw, th), Image.LANCZOS), (16 + tw + 16, y + 70))
            print(name, flush=True)
        sheet.save(os.path.join(out, f"fonts-{part + 1}.png"))
    print("written:", out)


if __name__ == "__main__":
    main()
