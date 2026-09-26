# autobleem-themes - developer context

The source of AutoBleem's UI themes (autobleem-main's `docs/decisions.md`: "Themes and samples have their
own source repositories"). Five themes ship today: `ab2`, `aergb`, `autobleem`, `default`, `evolution`.

## Layout

```
Themes/<name>/theme.json          the theme, in the format the launcher reads - see below
Themes/<name>/...                 the files theme.json names: images, fonts, sounds, music, credits
```

Each theme is exactly what `<launcher>/payload/Themes/<name>/` used to hold. The **format** - what
`theme.json` can say, what a key or file falling back to `Themes/default` means, the layout inside a
theme folder - is documented in the launcher's own `docs/theme-format.md`, since the code that reads it
(`ableem::ThemeSpec`, `Theme::load()`) lives there; this repository does not restate it.

## Adding or updating a theme

Edit the files under `Themes/<name>/` directly. A binary asset (png/jpg/ttf/otf/ogg/wav) is committed as
is; `theme.json` and any `.txt` credit/licence file are LF (`.gitattributes` enforces this - do not let a
Windows editor turn them back to CRLF). Keep every theme's own licence facts with it: a theme's fonts are
OFL (its own `OFL.txt`/`LICENSE`), `ab2`'s `ab.ogg` and `evolution`'s track are their authors' own work
(each theme's `credit.txt`/`OFL.txt` says so - do not remove or thin these out). `default`'s sounds,
images and music are generated - `tools/make_theme_sounds.py`, `tools/make_theme_images.py`,
`tools/make_theme_music.py`; `ab2`'s launcher menu icons and on/off switch by `tools/make_ab2_icons.py`.
Re-run the relevant script and commit its output when you touch what it draws.

A new theme is a new `Themes/<name>/` folder with at least a `theme.json` (everything else falls back to
`default`) - see `docs/theme-format.md` in the launcher for the minimum that makes sense to ship.

## Packaging and release

`tools/make_themes_package.sh` (`AB_VERSION=x.y.z tools/make_themes_package.sh`) writes
`dist/themes-<version>.tar.gz`: the archive's own top-level folder is plain `Themes/` (no version in it,
like a scanner processor's or extension's package) - it unpacks straight over a stick's `Themes/`, or
wherever a consuming project stages it.

`.github/workflows/build.yml`, gated by the repository variable `AB_CI_ENABLED` like every autobleem2
repository: packages and diffs the archive back against `Themes/` on every push and pull request; a `v*`
tag publishes a GitHub release with the tarball attached, and every push to `develop` replaces the rolling
`nightly` pre-release's asset (`autobleem2/autobleem-build`'s `nightly-release` action - the same scheme
`proc_unzip`, `ext_store` and the console tools use). No build image is needed: there is nothing to
compile.

## Consumers

The launcher and autobleem-appliance take a themes release the way they take any other component's (a
tag or `nightly`, staged into the package being assembled) - see autobleem-main's `docs/todo.md` D5 for
where that stands. Until that lands, the launcher's own `payload/Themes/` is still what ships; this
repository is the themes' source of truth and the launcher's copy should be treated as downstream of it.

## Licence

GPL-3.0-or-later (`LICENSE`), matching the launcher. The theme artwork and the AutoBleem name/logo are not
covered by it (`TRADEMARKS.md`-equivalent language lives in the launcher's CLAUDE.md "Licence" section);
third-party assets inside a theme (fonts, `ab2/ab.ogg`, `evolution`'s track) keep their own licence, named
in that theme's own credit/licence file.
