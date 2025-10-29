#!/usr/bin/env bash
set -Eeuo pipefail

OUT_DIR="esv_artifacts/rng_reports/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$OUT_DIR"
echo "Reproduce & test -> $OUT_DIR"

SAMPLES_DIR="esv_artifacts/samples"
if [ ! -d "$SAMPLES_DIR" ]; then
  echo "No samples in $SAMPLES_DIR. Run collect_samples.sh first." >&2
  exit 1
fi

for f in "$SAMPLES_DIR"/*.bin; do
  name=$(basename "$f")
  echo "--- Testing $name ---"
  # PractRand (RNG_test) if present
  if command -v RNG_test >/dev/null 2>&1; then
    echo "Running PractRand on $name..."
    ./RNG_test "$f" -tlmax 34 > "$OUT_DIR/${name}_practrand.txt" 2>&1 || true
  else
    echo "PractRand (RNG_test) not found; skipping."
  fi

  # dieharder if present
  if command -v dieharder >/dev/null 2>&1; then
    echo "Running dieharder on $name..."
    cat "$f" | dieharder -g 200 -a > "$OUT_DIR/${name}_dieharder.txt" 2>&1 || true
  else
    echo "dieharder not found; skipping."
  fi

  # NIST STS if present (sts-2.1.2 assumed)
  if [ -d "./sts-2.1.2" ]; then
    echo "Running NIST STS on $name (will create folder per file)..."
    outsub="$OUT_DIR/${name}_nist_sts"
    mkdir -p "$outsub"
    # Convert to bits file expected by STS if needed (use existing tools), here copy
    cp "$f" "$outsub/input.bin"
    # user should run STS tests manually if installed; note in log
    echo "NIST STS: input at $outsub/input.bin (run sts manually if installed)" > "$OUT_DIR/${name}_nist_sts_instructions.txt"
  else
    echo "NIST STS not present; skipping."
  fi

  echo "Done $name"
done

echo "Reproduce & test finished. Reports in $OUT_DIR"

