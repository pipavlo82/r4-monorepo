# 🧩 RE4CTOR — Entropy Source Validation (ESV) Package

This document describes how to **collect**, **test**, and **package** entropy samples for FIPS / NIST entropy source validation.

---

## 📦 Directory layout

r4-monorepo/
├── collect_samples.sh # Generates raw entropy samples
├── reproduce_and_test.sh # Runs PractRand, dieharder, (optionally NIST STS)
├── gen_manifest.sh # Creates MANIFEST.md with SHA256 checksums
├── pack_esv.sh # Zips all artifacts into a single package
├── ESV_REPORT.md # Human-readable report template
├── cover_letter.txt # Cover letter for FIPS submission
└── esv_artifacts/
├── samples/ # Raw entropy data (binary)
├── rng_reports/ # PractRand & Dieharder outputs
├── notes.txt
└── MANIFEST.md

yaml
Copy code

---

## ⚙️ Reproduce the package

```bash
chmod +x collect_samples.sh reproduce_and_test.sh gen_manifest.sh pack_esv.sh
./collect_samples.sh
./reproduce_and_test.sh
./gen_manifest.sh
./pack_esv.sh
The resulting archive will look like:

python
Copy code
esv_package_YYYYMMDDTHHMMSSZ.zip  (~300 MB)
🧪 Tools used
PractRand

Dieharder

NIST STS (optional)

All reports are stored in esv_artifacts/rng_reports/ with timestamps.

🧾 Report & Manifest
ESV_REPORT.md — structure for human-readable report (editable).

MANIFEST.md — automatically generated file listing all artifact checksums.

cover_letter.txt — standard template for FIPS lab submission.

🔗 Integration
Later, link to this document from the main README:

markdown
Copy code
For entropy source validation and test reproduction, see [ESV_README.md](./ESV_README.md)
🧰 Optional commands
Generate summaries directly inside the report:

bash
Copy code
./summarize_reports.sh
Maintainer: Pavlo Tvardovskyi
Purpose: Provide verifiable artifacts for RE4CTOR RNG entropy source validation.
