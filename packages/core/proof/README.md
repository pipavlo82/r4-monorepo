# 🧪 Re4ctoR Core — Statistical Validation Proofs

This directory contains **formal statistical validation artifacts** for the Re4ctoR core entropy stream (`re4_dump`).

All tests were executed on the binary stream produced by the sealed core (little-endian 32/64-bit words), using standard, widely accepted test batteries.

---

## 📂 Layout

- `bigcrush/`  
  Full TestU01 BigCrush logs and helper code.

- `dieharder/`  
  Raw Dieharder logs (if needed; compressed logs are under `packages/core/artifacts`).

- `practrand/`  
  Raw PractRand logs (ditto).

- `fips_selftest.py`, `fips_selftest_core.py`  
  Internal self-test harness used for quick startup validation.

- `bigcrush_summary.txt`  
- `dieharder_summary.txt`  
- `practrand_summary.txt`  

These three summary files are the **canonical high-level proof** used in Re4ctoR documentation.

---

## ✅ TestU01 BigCrush

- **Battery**: BigCrush (TestU01 1.2.3)  
- **Generator**: `re4_stream_le32` (core stream)  
- **Number of tests**: 160  
- **Result**: `160 / 160` PASSED  
- **Suspicious / catastrophic p-values**: none  
- **Artifact**:  
  - Full log (gzipped):  
    - `packages/core/artifacts/bigcrush_full_20251020_140456.txt.gz`  
  - Summary:  
    - `packages/core/proof/bigcrush_summary.txt`

BigCrush is the most demanding battery in TestU01. A **full pass** with no suspicious p-values is a very strong indication of statistical robustness.

---

## ✅ Dieharder 3.31.1

- **Tool**: Dieharder 3.31.1  
- **Mode**: `stdin_input_raw`  
- **Generator**: `re4_dump`  
- **Total tests**: 114  
- **Result**:  
  - `PASSED`: 114  
  - `WEAK`:   0  
  - `FAILED`: 0  
- **Artifact**:  
  - Full log (gzipped):  
    - `packages/core/artifacts/dieharder_20251020_125859.txt.gz`  
  - Summary:  
    - `packages/core/proof/dieharder_summary.txt`

In particular, all high-sensitivity tests such as `diehard_birthdays`, `diehard_rank_32x32`, `diehard_bitstream`, and `sts_serial` show well-distributed p-values with no anomalies.

---

## ✅ PractRand v0.95

- **Tool**: PractRand 0.95 (`RNG_test`)  
- **Generator**: `RNG_stdin64` (core stream, 64-bit)  
- **Test set**: `core`, folding = `standard (64 bit)`  
- **Length tested**: up to `2^32` bytes (4 GiB)  
- **Result**:  
  - "**no anomalies**" reported at each tested length  
- **Artifact**:  
  - `packages/core/artifacts/practrand_20251020_133922.txt.gz`  
  - `packages/core/proof/practrand_summary.txt`

PractRand is extremely sensitive to subtle correlations over large data volumes. No anomalies up to 4 GiB is a very strong indicator that the core stream behaves as high-quality cryptographic randomness.

---

## ▶ How to Reproduce (Developer Notes)

From the repository root:

```bash
cd packages/core

# BigCrush (requires TestU01 installed)
./scripts/run_bigcrush.sh > ../artifacts/bigcrush_$(date +%Y%m%d_%H%M%S).log

# Dieharder (requires dieharder)
./scripts/run_dieharder.sh > ../artifacts/dieharder_$(date +%Y%m%d_%H%M%S).log

# PractRand (requires PractRand RNG_test)
./scripts/run_practrand.sh > ../artifacts/practrand_$(date +%Y%m%d_%H%M%S).log
These scripts are the only supported way to reproduce the statistical proof for the core stream in a consistent environment.

🔒 Security Note

These statistical tests validate randomness quality but do not verify:

Supply-chain integrity (see GPG signatures, SHA-256 manifests)

Side-channel resistance (requires separate audit)

Cryptographic security assumptions (see WHITEPAPER.md)

For compliance and audit purposes, these reports should be combined with:

SBOM (Software Bill of Materials)

Binary signature verification

Security audit reports

📚 References

TestU01: P. L'Ecuyer and R. Simard, "TestU01: A C library for empirical testing of random number generators," ACM Trans. Math. Softw. 33(4), Article 22 (2007)

Dieharder: Robert G. Brown, "Dieharder: A Random Number Test Suite" (https://webhome.phy.duke.edu/~rgb/General/dieharder.php
)

PractRand: Chris Doty-Humphrey, "PractRand" (http://pracrand.sourceforge.net/
)

NIST SP 800-22: A. Rukhin et al., "A Statistical Test Suite for Random and Pseudorandom Number Generators for Cryptographic Applications," NIST Special Publication 800-22 Rev. 1a (2010)
