# Direction A - work in progress (CONSOLE-14)

The design source for one new look across the whole system: "a dark premium console" - graphite and navy,
one cyan accent, soft light, a calm centre behind the game row and a dark lower third for Play and the menu.
Elements are made and approved one at a time; nothing here is a theme yet and nothing here is packaged
(`tools/make_themes_package.sh` takes `Themes/` only).

| File | What | Made by |
|---|---|---|
| `bg-direction-a-01.png` | the background, 1280x720 | FLUX.1-schnell (Apache-2.0); prompt and seed in `bg-direction-a-01.prompt.txt` |
| `play_*-direction-a-02.png` | the Play button: the pill, the triangle + "PLAY", both together (1x, @2x) | `tools/make_direction_a_play.py` |
| `preview_play_on_bg-02.png` | the button at 2x on the background's lower third | the same script |

Rules for what follows: backgrounds are generated (prompt and seed kept beside each file; no text, logos
or third-party marks in them); the logo, Play and the icons are drawn as vectors by a script in `tools/`;
the small button icons stay the default theme's.

Still to draw: the launcher's panels and footer, the logo, the game-menu icons, the splash screens, the
Pi/PC-stick boot splash (plymouth, GRUB), the installer's screens and, later, the site's banner.
