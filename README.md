# autobleem-themes

The UI themes for [AutoBleem](https://github.com/autobleem2/autobleem): `ab2`, `aergb`, `autobleem`,
`default` and `evolution`, each a folder under `Themes/` with a `theme.json` and the files it names.

## Installing

Copy a theme's folder to the stick's `Themes/<name>/` (or unpack a release tarball there - it already
has that layout). AutoBleem picks it up from the Options menu.

## Format

A theme's `theme.json` layout, and how a value or file falls back to the `default` theme when a theme
doesn't set it, is documented in the launcher's own `docs/theme-format.md`.

## Releases

`themes-<version>.tar.gz` on this repository's [releases page](../../releases) - a plain `Themes/` folder,
unpack it wherever you keep themes. `nightly` is the rolling build of `develop`.

## Licence

GPL-3.0-or-later (`LICENSE`). The AutoBleem name, logo and this theme artwork are not covered by it. Each
theme's fonts are under the Open Font License (see its own `OFL.txt`); `ab2`'s `ab.ogg` and `evolution`'s
music track are their authors' own work, credited in that theme's `credit.txt`.
