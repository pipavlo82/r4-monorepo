#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VER="${1:-}"; [ -n "$VER" ] || { echo "usage: tools/release.sh vX.Y.Z"; exit 1; }
cd "$ROOT"

# Збірка (якщо є Makefile)
[ -f Makefile ] && make -B || true

# Перевірка бінарника (CLI потрібен для демонстрації)
if [ ! -x bin/r4cat ]; then
  echo "ERROR: bin/r4cat missing (build failed). Provide CLI in repository."
  exit 1
fi

PKG="re4ctor-${VER}-linux-x86_64"
DST="dist/${PKG}"
rm -rf "$DST" && mkdir -p "$DST"

# Укладаємо артефакти
install -m0755 bin/r4cat "$DST/"
[ -f lib/libr4.a ]     && install -m0644 lib/libr4.a "$DST/" || true
[ -f include/r4.h ]    && install -m0644 include/r4.h "$DST/" || true
[ -f bindings/python/r4.py ] && install -m0644 bindings/python/r4.py "$DST/" || true
[ -f README.md ]       && install -m0644 README.md "$DST/" || true

# Документація (якщо є)
mkdir -p "$DST/docs"
[ -f docs/SPEC-R4CS.md ]   && cp -f docs/SPEC-R4CS.md "$DST/docs/" || true
[ -f docs/API.md ]         && cp -f docs/API.md "$DST/docs/" || true

# ZIP + checksum
cd dist
ZIP="${PKG}.zip"
rm -f "$ZIP" checksums.txt
zip -r "$ZIP" "$PKG" >/dev/null
sha256sum "$ZIP" > checksums.txt
echo "Created dist/$ZIP"
