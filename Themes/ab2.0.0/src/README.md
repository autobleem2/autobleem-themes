# ab2.0.0 - AutoBleem 2's new look (CONSOLE-14), the trial theme

`Themes/ab2.0.0/` is a **first build** of the new look, on today's `theme.json` format: everything the
format can already carry. `src/` holds its sources: every script that draws the pictures (`src/tools/`), the
mockups and design sources (`src/design/`), and this file - the decisions and the exact code changes the
mockups need. The theme's name is **ab2.0.0** (the owner, 2026-09-29); "Direction A" / "direction-a" in the
scripts' and design files' names is the look's working name from the design rounds.

## Decisions (the owner, 2026-09-29)

| What | Decision | Where it is drawn |
|---|---|---|
| Style | **v02b**: every tile, panel, badge and button has **cut corners** (top right + bottom left - the memory card's shape); **cyan** (`#36d9e0`) lines and frames on graphite (`#2e3742` -> `#212831`); **magenta** (`#ff46aa`) marks the **focused/selected** item only (Play, the selected cover's glow, the selected row). v01 (rounded, all cyan) was "too generic"; four variants were compared (`design/mockup/launcher-variants-02.png`) | `tools/make_direction_a_variants.py` (variant `b`) |
| Logo | **C3**: "AUTO" (steel) + "BLEEM" (white, bold) + the "2" in a cut-corner capsule with a magenta rim, **underlined in magenta** under the 2, a cyan bar fading right under the word | `tools/make_direction_a_logo3.py`, `design/logo/logo-c3*.png` |
| Background | **p5 "mozaika"**: dark cut-corner tiles, filled (no outlines), a soft cyan light up right, a faint magenta one low left, the middle third calmer and the bottom third darker for the UI; drawn procedurally - **no lines, stripes or brushed metal** (the owner disliked those) | `tools/make_direction_a_bg_proc.py` (`p5_mosaic`), `design/bg-proc/bg-p5.png` |
| Font | **Red Hat Text everywhere** - the launcher, the classic screens, the Store, the emulator's menu **and the Linux installers**; medium (500) for text, semibold (600) for titles. OFL 1.1, no reserved font name, so static cuts of the variable font may ship. Chinese stays on Noto Sans SC. 14 OFL fonts were compared (`design/fonts/fonts-1..3.png`, `zoom-redhat-vs-opensans.png`) | `tools/make_direction_a_fonts.py`, `make_direction_a_font_zoom.py` |
| Plymouth | the logo on **black** with a soft glow (the boot script paints black around it) - OK | `tools/make_direction_a_screens_v2.py` (`plymouth`) |
| Small button glyphs | the pad's button icons (cross, circle, square, triangle, Start, Select, L/R) **stay default's** | - |
| No Sony marks | no PlayStation logo, no button-symbol shapes in the art | - |

Not decided yet: the theme's final name; whether it replaces `default` or ships beside it as the new default;
new music/sounds or default's; the splash tagline ("RETRO GAME LAUNCHER" is a placeholder).

## What the trial theme has (no code change needed)

`theme.json` (format 1) with: the launcher background (p5), the footer strip (a cut-corner panel behind the
hint bar, `hintBar` 360,642 900x68 to sit in it), Play (`play_button.png` 200x68 = the magenta frame,
`play_text.png` 262x68 = triangle + "PLAY" - the launcher centres the text's 262-wide canvas on x 640 and
draws the button at x 540, both at y 428), the four game-menu icons (the resume icon's picture window kept at
25,33 68x52), the pad glyph (`meta_panel.png`), the cover arrow, the memory card manager's grid and pencil,
**Red Hat Text as `launcher.fonts`** (the launcher's own text - `ThemeAssets::fixedFonts()` - takes it:
the game's details, the menus, the hints, the panels), `launcher.colors` (text, secondary, hint,
`selection` magenta for the resume-slot picker); for the classic UI: background (p5), logo C3 (`ab.png`),
graphite menu panel/status bar/keyboard/label colours, the cut-corner on/off switch. Everything else (hint
icons, the other button glyphs, sounds, music, the settings panel) falls back to `Themes/default`.

**Not checked on a device yet** - it needs a launcher build with this theme on the VM/Pi (Options -> theme).

## What needs code to look like the mockups

Mockups: `design/mockup/launcher-games-direction-a-02b.png` (the launcher), `design/bg-proc/bg-screens-1.png`
(p5 on the launcher and the emulator), `design/emu/emu-menu-v2-p5.png` (the emulator's menu),
`design/screens-c3.png` (splash, plymouth, emulator art). Paths are per repository.

### autobleem (the launcher)

1. **The small EvolutionUI icons from the theme** (todo UIREV-30). Today they are fixed files:
   `src/code/evoui/controls/evoui_meta.cpp:109-119` (usb, sd/hd, lock/unlock, cd, favorite, lightgun,
   lightgun2 - `curPath + "evoimg/..."`), the tab icons and the d-pad hint arrows (`evoimg/tab_*.png`,
   `evoimg/dpad_*.png`, see `tools/make_evoimg_icons.py`), `carousel_game.cpp:88,94` and
   `gui_game_editor_ra_menu.cpp:19` (the cover placeholders). Change: look the name up in the theme first
   (a `launcher.icons` block in `theme.json`, or an `evoimg/` folder in the theme), then `Themes/default`,
   then the built-in file; document it in `docs/theme-format.md` (`ThemeSpec` in core). The Direction A
   versions: `design/evoimg/<name>-direction-a-01.png` (same canvases). ps1.png and ra.png stay (third-party
   marks).
2. **The "Showing: ..." banner** (top right) and the **notification bubble**
   (`src/code/evoui/controls/evoui_notification_bubble.cpp`, drawn from `evoui_launcher_screen.cpp`): a
   graphite panel with cut corners and a cyan rim instead of today's dark rectangle - through PanelStyle
   (core, below) so every theme gets its own.
3. **The selected cover's glow in the focus colour** (magenta) - the carousel's selection highlight in
   `src/code/evoui/` (carousel drawing); today it has no colour of its own. Needs a theme colour
   (`launcher.colors.focus`, or UIREV-29's colour roles).
4. **Covers as CD jewel cases** (spine, plastic sheen, slight perspective on the side covers) - optional, the
   mockup's look; the carousel draws flat squares today.
5. **The Play outline**: `makePlayOutline()` (`evoui_launcher_screen.cpp:749-760`) draws a dark outline
   around the Play images when `textShadow` is on - check it against the glow of the new frame; if it muddies
   it, a theme switch for the outline alone.
6. **The classic screens' font** (todo UIREV-31): `classic.font` is not read since 2026-09-29 - the classic
   UI uses Open Sans Medium 20 or the user's Options font (`autobleem-core/src/code/gui/theme_assets.cpp`,
   `classicFont`). For "Red Hat Text everywhere": ship Red Hat Text in `src/resources/fonts` as the default
   pair (replacing Open Sans, with its OFL.txt, in `THIRD_PARTY_NOTICES.md`), or let a theme's
   `launcher.fonts` also be the classic default.
7. **The splash** `src/resources/splash/autobleem.jpg` -> the C3 splash (`design/splash/splash-c3.jpg`,
   re-drawn on p5 by `make_direction_a_screens_v2.py` once the background is final there).

### autobleem-core (the shared UI)

8. **PanelStyle** (`src/code/gui/panel_style.cpp`: `fromTheme()` l.20, `sheet()` l.43, `selection()` l.73,
   `label()` l.84, `rule()` l.54, `footer()` l.269/330) - the Quick menu, the System menu and every new
   panel: a **cut-corner shape** (a theme switch: rounded | chamfer, and the cut size) for the sheet and the
   selection; the sheet's rim in the line colour (cyan); the selection as a **magenta rim** on a slightly
   lighter graphite instead of a filled bar; headings in the line colour. The colours come from UIREV-29's
   colour-role block (in progress - `theme.json` keys to be agreed there before this theme sets them).
9. **The classic list windows** (`gui_menu_base.h`: Options, Game Manager, editors): the same selection and
   heading colours as PanelStyle (UIREV-29).

### ext_store (the Store)

10. Its screens draw through core's PanelStyle and the theme's fonts - they follow 8 and the fonts once
    those land; check its own colour constants (`src/gui_store.cpp`).

### pcsx-abnxt (the emulator's in-game menu) - todo EMU-16, **only in an owner session** (emulator freeze)

11. `frontend/ab/ab_menu.c:361-368` - the colour constants: `ab_col_panel` `#041230` -> graphite `#212831`,
    `ab_col_row` `#1a7ec4` (the selected row's fill) -> a magenta `#ff46aa` rim on graphite `#2e3742`,
    `ab_col_accent` `#4fc3f7` -> cyan `#36d9e0` for headings, `ab_col_dim` stays for values.
12. `ab_ui_fill(...)` (rounded boxes, `ab_ui.c`) -> a cut-corner fill + a rim for the panel (l.860) and the
    selected row (l.900); section headings drawn in the accent colour with a thin rule after them.
13. `skin/ui.ttf` (Selawik) -> Red Hat Text (medium for rows, semibold for the title/headings), with OFL.txt.
14. `skin/ab_background.jpg` -> the Direction A art: p5 + logo C3 bottom left + the cut-corner hint bar
    (`design/emu/ab_background-c3.jpg`, re-drawn on p5); the hints are written on it from x 490, y 647.
    Mockup: `design/emu/emu-menu-v2-p5.png`. Check fps before/after (a menu only, but the rule stands).

### autobleem-appliance (boot and the Linux installers) - todo PLATFORM-15

15. `payload_linux/system/plymouth/splash.png` -> `design/splash/plymouth-c3.png`.
16. `payload_linux/system/autobleem-install-ui.py` (the first-boot installer on the framebuffer): its
    colours -> graphite panels, cyan lines, magenta for the selected item, the logo C3; it can only draw **PSF
    console fonts** (a fresh Lite image has no FreeType) - convert Red Hat Text to PSF2 at the sizes it asks
    for (`find_font`: 16/20/24/32 px) and ship them with the installer (its `--fonts` option) plus the OFL
    notice. The text backend (whiptail colours) can keep its palette.

### autobleem-themes (this repository)

17. **Packaging**: `tools/make_themes_package.sh` packs all of `Themes/` - this theme's `src/` (~45 MB of
    mockups and sources) would ship on every stick. Before this theme is released, either leave `src/` out of
    the package (and out of the CI's archive-vs-`Themes/` diff) or move it back to `design/`.

## How to rebuild

From the repository root, given a launcher checkout (`--launcher`) and a folder of the downloaded fonts
(`--fonts`: the OFL files from Google Fonts / the authors' GitHub releases; Red Hat Text is read from
`<fonts>/other/RedHatText[wght].ttf` and `<fonts>/other/RedHat-OFL.txt`):

```
python Themes/ab2.0.0/src/tools/make_direction_a_theme.py --launcher <launcher checkout> --fonts <fonts folder>
```

The other scripts draw the design sheets (each says how to run it in its docstring):
`make_direction_a_icons.py` / `_evoimg.py` (icons), `_logo.py` / `_logo2.py` / `_logo3.py` (logos),
`_bg_proc.py` (backgrounds p1-p10), `_variants.py` (the four launcher mockups), `_v2_assets.py` (the theme's
images in v02b), `_screens_v2.py` (splash, plymouth, emulator art), `_emu_v2.py` (the emulator menu mockup),
`_bg_screens.py`, `_fonts.py`, `_font_zoom.py` (comparison sheets), `_play.py`, `_splash.py`, `_mockup.py`
(earlier v01 steps), `deband.py` (smoothing + dither for gradients).
