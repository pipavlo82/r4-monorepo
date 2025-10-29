#!/usr/bin/env bash
set -Eeuo pipefail
OUT="esv_artifacts/rng_reports"
DEST="ESV_REPORT.md"

echo -e "\n## Auto Summary (PractRand & dieharder)\n" >> "$DEST"

find "$OUT" -type f -name "*_dieharder.txt" | sort | while read -r f; do
  echo -e "\n### $(basename "$f")\n" >> "$DEST"
  tail -n 10 "$f" >> "$DEST"
done

find "$OUT" -type f -name "*_practrand.txt" | sort | while read -r f; do
  echo -e "\n### $(basename "$f")\n" >> "$DEST"
  tail -n 15 "$f" >> "$DEST"
done

echo -e "\n(End of auto summary)\n" >> "$DEST"
echo "Appended summaries to $DEST"
