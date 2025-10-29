#!/usr/bin/env bash
set -Eeuo pipefail

OUT_DIR="esv_artifacts/samples"
mkdir -p "$OUT_DIR"
TS=$(date -u +"%Y%m%dT%H%M%SZ")
# sizes in MB - редагуй за потреби
SIZES_MB=(100 100 100)

echo "Collector starting at $TS -> $OUT_DIR"

for i in "${!SIZES_MB[@]}"; do
  SIZE_MB=${SIZES_MB[i]}
  OUT="$OUT_DIR/sample_${SIZE_MB}MB_${i}_${TS}.bin"
  echo "- producing $OUT ($SIZE_MB MB)"

  # 1) спробувати внутрішній python-генератор (якщо є)
  if command -v python3 >/dev/null 2>&1 && [ -f ./quantum_safe_rng_v1577_v13.py ]; then
    python3 ./quantum_safe_rng_v1577_v13.py gen --bytes $((SIZE_MB*1024*1024)) > "$OUT" 2>/dev/null || true
  fi

  # 2) або наявний власний бинар (re4_dump)
  if [ ! -s "$OUT" ] && [ -x ./re4_dump ]; then
    ./re4_dump "$OUT" $((SIZE_MB*1024*1024)) || true
  fi

  # 3) fallback: /dev/urandom (тільки як резерв)
  if [ ! -s "$OUT" ]; then
    echo "WARNING: fallback to /dev/urandom for $OUT" >> esv_artifacts/notes.txt
    head -c $((SIZE_MB*1024*1024)) /dev/urandom > "$OUT"
  fi

  ls -lh "$OUT"
done

echo "Collector finished"
