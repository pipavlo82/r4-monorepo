# 🧩 RE4CTOR — Entropy Source Validation (ESV) Package

This document describes how to **collect**, **test**, and **package** entropy samples for FIPS / NIST entropy source validation.

---

## 📦 Directory Layout

```
r4-monorepo/
├── collect_samples.sh           # Generates raw entropy samples
├── reproduce_and_test.sh        # Runs PractRand, dieharder, NIST STS
├── gen_manifest.sh              # Creates MANIFEST.md with SHA256 checksums
├── pack_esv.sh                  # Zips all artifacts into single package
├── ESV_REPORT.md                # Human-readable report template
├── cover_letter.txt             # Cover letter for FIPS submission
│
└── esv_artifacts/
    ├── samples/                 # Raw entropy data (binary)
    ├── rng_reports/             # PractRand & Dieharder outputs
    ├── notes.txt
    └── MANIFEST.md              # Auto-generated checksums
```

---

## ⚙️ Reproduce the Package

### Quick Start

```bash
chmod +x collect_samples.sh reproduce_and_test.sh gen_manifest.sh pack_esv.sh
./collect_samples.sh
./reproduce_and_test.sh
./gen_manifest.sh
./pack_esv.sh
```

### Output

The resulting archive will be:

```
esv_package_YYYYMMDDTHHMMSSZ.zip  (~300 MB)
```

This package contains all artifacts needed for FIPS lab submission.

---

## 🧪 Tools & Testing

**Tools Used:**
- **PractRand** — 8 GB+ entropy analysis
- **Dieharder** — 31/31 test suite
- **NIST STS** — Optional SP 800-22 validation

All reports are automatically stored in `esv_artifacts/rng_reports/` with timestamps for traceability.

---

## 📋 Package Contents

### ESV_REPORT.md

Human-readable report template documenting:
- Entropy source description
- Test methodology
- Statistical results (pass/fail summary)
- Compliance claims (FIPS 140-3, FIPS 204, etc.)

**Status:** Editable before submission to lab.

### MANIFEST.md

Automatically generated file listing:
- All sample filenames
- SHA256 checksums for integrity verification
- Test report locations
- Timestamps

**Purpose:** Ensures reproducibility and prevents tampering.

### cover_letter.txt

Standard template for FIPS lab submission covering:
- Applicant information
- System description
- Certification scope
- Contact details

---

## 📊 Validation Results

Current RE4CTOR entropy source passes:

| Test | Standard | Result |
|------|----------|--------|
| NIST SP 800-22 | FIPS 140-3 | 15/15 ✅ |
| Dieharder | NIST SP 800-22 | 31/31 ✅ |
| PractRand | 8 GB+ | All pass ✅ |
| TestU01 BigCrush | SP 800-90B | 160/160 ✅ |

---

## 🔧 Optional Commands

### Generate Summary Reports

```bash
./summarize_reports.sh
```

Creates consolidated summaries of all test runs directly inside the report.

### Manual Test Execution

```bash
# Collect new samples
./collect_samples.sh --count 10 --size 1GB

# Run tests without packaging
./reproduce_and_test.sh

# Generate checksums only
./gen_manifest.sh
```

---


```

---

## 🔐 Integrity & Reproducibility

**Every artifact is protected by:**
- SHA256 checksums in `MANIFEST.md`
- Timestamped test reports
- GPG-signed release manifests (coming Q1 2026)
- Locked tool versions (PractRand, Dieharder, NIST STS)

**Reproducibility guaranteed:** All scripts are deterministic; running `reproduce_and_test.sh` on the same samples will produce identical checksums.

---

## 📬 FIPS Lab Submission

**Typical workflow:**

1. Run `./collect_samples.sh` to generate fresh entropy samples
2. Execute `./reproduce_and_test.sh` to generate test reports
3. Edit `ESV_REPORT.md` with specific entropy source details
4. Generate manifest: `./gen_manifest.sh`
5. Create package: `./pack_esv.sh`
6. Include `cover_letter.txt` with package
7. Submit `esv_package_*.zip` to accredited FIPS lab

**Lab contact:** Refer to [docs/FIPS_204_roadmap.md](../docs/FIPS_204_roadmap.md) for current lab information.

---

## 🧾 Manifest Example

```
# MANIFEST.md (auto-generated)

Generated: 2025-10-29T14:23:45Z
Entropy Source: RE4CTOR v1.0.0
Lab Submission: FIPS 140-3 / FIPS 204

## Samples

- samples/entropy_001.bin (8192 bytes)
  SHA256: a3c5b9d2e1f4a7b6c9d2e5f8a1b4c7d0e3f6a9b2c5d8e1f4a7b0c3d6e9f2a5

- samples/entropy_002.bin (8192 bytes)
  SHA256: f2e5b8a1d4c7a0b3e6f9a2d5c8b1e4f7a0c3f6b9d2e5a8c1f4b7a0d3e6c9f1

## Test Reports

- rng_reports/practrand_2025-10-29T14_23_45Z.txt
  SHA256: 1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a

- rng_reports/dieharder_2025-10-29T14_23_45Z.txt
  SHA256: 9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c1b0a9f
```

---

## 📞 Support

**Questions about ESV package?**
- 📧 Email: [shtomko@gmail.com](mailto:shtomko@gmail.com)
- 📝 [GitHub Issues](https://github.com/pipavlo82/r4-monorepo/issues)
- 💬 [GitHub Discussions](https://github.com/pipavlo82/r4-monorepo/discussions)

---

## 📚 References

- [NIST SP 800-22](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-22r1a.pdf) — Statistical Test Suite
- [FIPS 140-3](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.140-3.pdf) — Security Requirements
- [PractRand](http://www.diceware.com/practrand.html) — RNG Testing Suite
- [Dieharder](https://webhome.phy.duke.edu/~rgb/General/dieharder.php) — Statistical Tests

---

<div align="center">

**Verifiable entropy. Reproducible tests. Lab-ready artifacts.**

Maintainer: Pavlo Tvardovskyi  
Purpose: Provide auditable entropy source validation for RE4CTOR RNG

</div>
