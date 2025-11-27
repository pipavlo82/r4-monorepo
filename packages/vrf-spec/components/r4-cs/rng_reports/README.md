# 🧪 R4-CS Stream — RNG Validation Reports

This directory contains **independent validation reports** for the `r4-cs` stream used in the VRF / client-side components.

The goal is to show that not only the sealed core, but also the exported, VRF-facing stream behaves as a statistically sound RNG.

---

## 📂 Contents

- `nist_sts_finalAnalysisReport.txt`  
  Final report for **NIST SP 800-22**.

- `practrand_summary.txt`  
  Summary of PractRand tests for both 32-bit and 64-bit stdin streams.

- `r4cs_dieharder.txt`, `r4cs_dieharder_retest_*.txt`  
  Dieharder full run and targeted re-tests for the most sensitive test IDs.

- `r4cs_dieharder_retest_summary.txt`  
  Consolidated summary of the re-tests.

- `testu01_crush_summary.txt`  
  Summary of TestU01 Crush results for the `re4_stream_le32` stream.

---

## ✅ TestU01 Crush (r4-cs)

- **Battery**: Crush (TestU01 1.2.3)  
- **Generator**: `re4_stream_le32` (r4-cs stream)  
- **Statistics**: 144  
- **Result**: `All tests were passed`  
- **Artifact**:  
  - `testu01_crush_summary.txt`

This confirms that the VRF-side stream has no detectable linear or structural biases under the Crush battery.

---

## ✅ Dieharder + Targeted Re-Tests

- **Tool**: Dieharder 3.31.1  
- **Mode**: `stdin_input_raw`  
- **Generator**: r4-cs stream  
- **Result**:  
  - Full run: all tests **PASSED**, no WEAK / FAILED  
  - Targeted re-tests for known high-sensitivity IDs:
    - `11 = diehard_2dsphere` → PASSED (p ≈ 0.657)  
    - `102 = sts_serial` → all subtests PASSED  
    - `203 = rgb_lagged_sum` → PASSED (p ≈ 0.992)  

Targeting these tests is important because they frequently reveal issues in weaker RNGs. In our case, they confirm that no such weaknesses are present.

---

## ✅ PractRand (r4-cs streams)

- **Tool**: PractRand 0.95  
- **Streams**:
  - `RNG_stdin32`:  
    - 1 GiB (2^30 bytes) — no anomalies in 194 test results  
    - 2 GiB (2^31 bytes) — no anomalies in 205 test results  
  - `RNG_stdin64`:  
    - 1 GiB (2^30 bytes) — no anomalies in 246 test results  
- **Artifact**:  
  - `practrand_summary.txt`

This shows that both 32-bit and 64-bit representations of the r4-cs stream behave as high-quality random streams over gigabyte-scale outputs.

---

## ✅ NIST SP 800-22 (NIST STS)

- **Input**: `data/epsilon` (r4-cs bitstream)  
- **Sample size**:
  - 80 sequences for most tests  
  - 45 sequences for Random Excursions / Variant  

All tests satisfy **both** NIST criteria:

1. **Global p-value** for the uniformity of p-values is well above 0.0001.  
2. **Pass rate** per test is above the required minimum:
   - For 80 sequences: all tests ≥ 77/80 (minimum threshold ≈ 76/80)  
   - For 45 sequences: all RandomExcursions / Variant tests ≥ 43/45 (minimum threshold ≈ 42/45)

Key tests include:

- Frequency, BlockFrequency, CumulativeSums, Runs, LongestRun, Rank, FFT  
- Hundreds of NonOverlappingTemplate instances  
- OverlappingTemplate, Universal, ApproximateEntropy  
- RandomExcursions, RandomExcursionsVariant  
- Serial (2×), LinearComplexity  

**Result**: NIST SP 800-22 battery — **full pass** for the r4-cs stream.

---

## ▶ Reproducibility

The reports in this directory are generated from controlled runs against the r4-cs binary stream.

For full reproducibility, store your own raw bitstreams and re-run:

- TestU01 Crush  
- Dieharder (including the targeted re-tests)  
- PractRand  
- NIST STS

using the same parameters as documented in the logs.
