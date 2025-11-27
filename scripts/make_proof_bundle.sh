#!/usr/bin/env bash
set -Eeuo pipefail

# Detect repo root
ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT_DIR"

echo "[*] Re4ctoR proof bundle builder"
echo "    ROOT_DIR = $ROOT_DIR"

# Output directory for bundles
OUT_DIR="${ROOT_DIR}/proofs"
mkdir -p "$OUT_DIR"

# Timestamp + optional tag (e.g. PROOF_TAG=2025Q4)
TS="$(date +%Y%m%d_%H%M%S)"
TAG="${PROOF_TAG:-$TS}"
ARCHIVE_NAME="re4ctor_proofs_${TAG}.tar.gz"
ARCHIVE_PATH="${OUT_DIR}/${ARCHIVE_NAME}"

echo "[*] Output archive: ${ARCHIVE_PATH}"

# List of files / directories to include
INCLUDE_ITEMS=(
  # Core proof summaries + self-tests
  "packages/core/proof/README.md"
  "packages/core/proof/bigcrush_summary.txt"
  "packages/core/proof/dieharder_summary.txt"
  "packages/core/proof/practrand_summary.txt"
  "packages/core/proof/fips_selftest.py"
  "packages/core/proof/fips_selftest_core.py"

  # Core heavy logs (BigCrush / PractRand / Dieharder)
  "packages/core/artifacts/bigcrush_full_20251020_140456.txt.gz"
  "packages/core/artifacts/practrand_20251020_133922.txt.gz"
  "packages/core/artifacts/dieharder_20251020_125859.txt.gz"

  # VRF-side / r4-cs RNG reports (NIST, Dieharder, PractRand, TestU01)
  "packages/vrf-spec/components/r4-cs/rng_reports"
)

echo "[*] Verifying inputs..."

MISSING=0
for item in "${INCLUDE_ITEMS[@]}"; do
  if [ ! -e "$item" ]; then
    echo "  [!] MISSING: $item"
    MISSING=1
  else
    echo "  [+] OK:      $item"
  fi
done

if [ "$MISSING" -ne 0 ]; then
  echo
  echo "[!] One or more expected proof files are missing."
  echo "    Please fix the paths or regenerate the artifacts before bundling."
  exit 1
fi

echo
echo "[*] Creating tarball..."

tar czf "$ARCHIVE_PATH" \
  --transform 's|^|re4ctor_proofs/|' \
  "${INCLUDE_ITEMS[@]}"

echo "[*] Done."
echo "    Bundle: $ARCHIVE_PATH"
