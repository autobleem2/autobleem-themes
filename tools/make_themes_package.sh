#!/usr/bin/env bash
# Package Themes/ as dist/themes-<version>.tar.gz. The archive's own top-level folder is plain Themes/
# (no version in it, like a processor's or extension's package) - it unpacks straight over a stick's
# Themes/, or wherever an appliance/installer stages it; only the file name carries the version.
#
#   AB_VERSION=1.0.0 tools/make_themes_package.sh
#
# AB_VERSION defaults to `git describe --tags --always --dirty` for a local run; CI always sets it
# (see .github/workflows/build.yml - a v* tag's own version, else the nightly scheme every autobleem2
# repository uses for a develop build).
# The folders listed in tools/unshipped_themes.txt (ab2) stay in the repository but are left out of the package;
# `tools/make_themes_package.sh --unshipped` prints their names, one per line (the CI check reads them).
set -euo pipefail
cd "$(dirname "$0")/.."

unshipped() {
    local name
    while IFS= read -r name || [ -n "$name" ]; do
        name="${name%$'\r'}"
        case "$name" in ''|'#'*) continue ;; esac
        printf '%s\n' "$name"
    done < tools/unshipped_themes.txt
}
if [ "${1:-}" = "--unshipped" ]; then unshipped; exit 0; fi

version="${AB_VERSION:-$(git describe --tags --always --dirty 2>/dev/null || echo 0.0.0)}"
out="dist"

rm -rf "$out"
mkdir -p "$out"
excludes=()
while IFS= read -r name; do excludes+=(--exclude="Themes/$name"); done < <(unshipped)
tar -czf "$out/themes-$version.tar.gz" "${excludes[@]}" Themes

echo "wrote $out/themes-$version.tar.gz (not shipped: $(unshipped | tr '\n' ' '))"
