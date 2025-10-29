#!/usr/bin/env bash
set -Eeuo pipefail
DEST="esv_artifacts/MANIFEST.md"
echo "# ESV Artifacts Manifest" > "$DEST"
echo "" >> "$DEST"
echo "Generated (UTC): $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$DEST"
echo "" >> "$DEST"
echo "## Files" >> "$DEST"
echo "" >> "$DEST"
while IFS= read -r -d '' f; do
  sz=$(stat -c%s "$f")
  sha=$(sha256sum "$f" | awk '{print $1}')
  echo "- \`$f\` — $sz bytes — sha256: \`$sha\`" >> "$DEST"
done < <(find esv_artifacts -type f -print0 | sort -z)
echo "" >> "$DEST"
echo "## Notes" >> "$DEST"
echo "- Samples produced on host: $(hostname -s)" >> "$DEST"
echo "- Tooling present: dieharder=$(command -v dieharder >/dev/null && echo yes || echo no), PractRand=$(command -v RNG_test >/dev/null && echo yes || echo no)" >> "$DEST"
echo "Manifest written to $DEST"
