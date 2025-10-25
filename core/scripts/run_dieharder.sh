#!/usr/bin/env bash
set -euo pipefail
BUILD=build
cmake -S . -B "$BUILD" -DCMAKE_BUILD_TYPE=Release >/dev/null
cmake --build "$BUILD" -j >/dev/null
mkdir -p proof
OUT="proof/dieharder_$(date +%Y%m%d_%H%M%S).txt"
"$BUILD/re4_dump" | dieharder -a -g 200 2>&1 | tee "$OUT" || true
echo -e "\nSaved: $OUT"
