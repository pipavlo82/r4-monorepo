#!/usr/bin/env bash
set -euo pipefail
BUILD=build
cmake -S . -B "$BUILD" -DCMAKE_BUILD_TYPE=Release >/dev/null
cmake --build "$BUILD" -j >/dev/null
mkdir -p proof

# Вибираємо RNG_test (спершу 0.95, тоді 0.94, тоді з PATH)
RNG_TEST_CAND=( "$HOME/PractRand-0.95/RNG_test" "$HOME/PractRand_094/RNG_test" RNG_test )
for x in "${RNG_TEST_CAND[@]}"; do
  if command -v "$x" &>/dev/null || [ -x "$x" ]; then RNG_TEST="$x"; break; fi
done
if [ -z "${RNG_TEST:-}" ]; then
  echo "❌ PractRand RNG_test не знайдено. Встанови/зібрай PractRand."; exit 1
fi

OUT="proof/practrand_$(date +%Y%m%d_%H%M%S).txt"
echo "Using: $RNG_TEST" | tee "$OUT"

# Пробуємо stdin64, при краші — fallback на stdin
set +e
"$BUILD/re4_dump" | "$RNG_TEST" stdin64 -tlmin 28 -tlmax 32 2>&1 | tee -a "$OUT"
RC=${PIPESTATUS[1]}
set -e
if [ $RC -ne 0 ]; then
  echo -e "\n⚠️ Fallback: stdin (8-bit)" | tee -a "$OUT"
  "$BUILD/re4_dump" | "$RNG_TEST" stdin -tlmin 28 -tlmax 32 2>&1 | tee -a "$OUT" || true
fi

echo -e "\nSaved: $OUT"
