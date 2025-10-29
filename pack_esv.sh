#!/usr/bin/env bash
set -Eeuo pipefail
TS=$(date -u +"%Y%m%dT%H%M%SZ")
OUT="esv_package_${TS}.zip"
mkdir -p esv_artifacts
zip -r "$OUT" esv_artifacts ESV_REPORT.md cover_letter.txt collect_samples.sh reproduce_and_test.sh || true
echo "Packed -> $OUT"
