#!/usr/bin/env bash
set -euo pipefail

BUILD=build
OUT="proof/bigcrush_$(date +%Y%m%d_%H%M%S).txt"
BIN="${BIGCRUSH_BIN:-$HOME/sts_linux/TestU01-1.2.3/examples/bigcrush_file}"
SIZE_BYTES=$((2*1024*1024*1024))  # 2 GiB (можеш збільшити до 4 GiB)

if [ ! -x "$BIN" ]; then
  echo "❌ BigCrush binary не знайдено: $BIN" | tee "$OUT"
  exit 1
fi

echo "Using (file): $BIN" | tee "$OUT"
TMP="proof/bigcrush_input_$(date +%Y%m%d_%H%M%S).bin"
echo "Generating $((SIZE_BYTES/1024/1024)) MiB to $TMP ..." | tee -a "$OUT"
./build/re4_dump | head -c "$SIZE_BYTES" > "$TMP"

echo "Running BigCrush on file..." | tee -a "$OUT"
"$BIN" "$TMP" 2>&1 | tee -a "$OUT" || true
echo -e "\nSaved: $OUT"
