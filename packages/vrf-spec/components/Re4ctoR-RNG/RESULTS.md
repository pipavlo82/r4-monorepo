# Re4ctoR-RNG — Results

## TL;DR (2025-09-08)
- **PractRand:** *no anomalies* up to **8 GB** (latest runs after reseed/nonce fixes).
  - Older builds (2025-09-04, 2025-09-07) showed *suspicious/very suspicious* — these were pre-fix binaries.
- **TestU01 / BigCrush:** *All tests were passed* (two independent runs).
- **NIST STS:** proportions ≥ required minima; a few low p-values (~**0.018–0.006**) in isolated sub-tests, but **overall PASS** (proportions within acceptable ranges).

## Details

### Dieharder

- **Version:** 3.31.1  
- **Mode:** stdin (`-g 201`), with additional reruns using higher `psamples`  
- **Logs:** `rng_reports/20250908_223744_consolidated/*.txt`  
- **Seeds observed in logs:** 984015027, 2878240219, 1575189660

**Final status:** **PASS** — **0 FAILED**, **0 WEAK** (after reruns).

**Initially weak results (all cleared after increasing `psamples`):**

| Test                          | Condition    | Initial p-value @100 psamples | Rerun p-value / psamples        | Final  |
|-------------------------------|--------------|-------------------------------:|----------------------------------|--------|
| `diehard_dna`                 | default      | 0.99553273 (WEAK)             | 0.49593590 @200; 0.10987154 @400 | PASSED |
| `sts_serial` (m=11)           | default      | 0.99781550 (WEAK)             | passed at 200 psamples           | PASSED |
| `rgb_bitdist` (m=10)          | default      | 0.99962963 (WEAK)             | 0.89567568 @200                  | PASSED |
| `rgb_lagged_sum` (k=3)        | default      | 0.99691170 (WEAK)             | 0.79153456 @200                  | PASSED |
| `rgb_lagged_sum` (k=6)        | default      | 0.99606002 (WEAK)             | 0.57318073 @200                  | PASSED |

_Notes:_ “WEAK” on default settings can occur due to sampling variance; increasing `psamples` improved statistical power and all tests passed on rerun.


### PractRand
- Date: 2025-09-08  
- Volume: **up to 8 GB**  
- Result: **no anomalies**  
- Note: earlier pre-fix builds (2025-09-04, 2025-09-07) produced *suspicious/very suspicious*.

### TestU01 (BigCrush)
- Runs: **2**  
- Result: **All tests were passed**  
- Logs/configs: see [`rng_reports/`](rng_reports/).

### NIST STS
.### NIST Statistical Test Suite (STS)

- **Suite:** NIST STS v2.1.2  
- **Input:** `quantum_safe_rng_v1577_v13_1024mb.bin` (200 sequences)  
- **Result:** **PASS** — all tests meet the NIST minimum pass-rate criterion (≥ 193 / 200 for non-excursion tests).

**Pass-rate (highlights):**
- Frequency: **197/200**
- BlockFrequency: **199/200**
- CumulativeSums (forward/backward): **197/200**, **197/200**
- Runs: **198/200**
- LongestRun: **199/200** *(lowest p ≈ 0.0185)*
- Rank: **199/200**
- FFT: **198/200**
- NonOverlapping Template (multiple templates): **min 194/200**, typical **196–200/200**
- OverlappingTemplate: **200/200**
- Universal: **199/200**
- ApproximateEntropy: **198/200**
- Serial (two parameters): **198/200** *(p ≈ 0.0064)*, **199/200**
- LinearComplexity: **198/200**
- RandomExcursions / RandomExcursionsVariant: p-values span **~0.04–0.97**; proportions **119–123 / 123**

**Notes:** A few low p-values (e.g., Serial **p≈0.0064**, LongestRun **p≈0.0185**, some NonOverlapping Template cases **p≈0.009–0.03**) are expected due to the large number of subtests. Since overall pass-rates are within NIST thresholds, the suite outcome is considered a **pass** with no evidence of systematic bias.

Results — OQS demo runs (2025-09-10)

Environment: OQS Python env (python3 quantum_safe_rng_v1577_v13.py demo), Linux (WSL).

Run A — default demo

VRF

VRF Value: 2bf83fea106f00794123abe125642216a6c6c533dd53c72a64d6e857feae1ba2

VRF Verified: True

Token seed (hex): 591d37ebfcf288e8e024798111564315103888791bfb63aac71d6525efa3aa29

10 MB output

File: /home/pavlo/quantum_safe_rng_v1577_v13_10mb.bin

Time: 0.17 s → ~58.82 MB/s

Integrity: Verified: True

100 MB output

File: /home/pavlo/quantum_safe_rng_v1577_v13_100mb.bin

Time: 1.65 s → ~60.61 MB/s

Duplicate-check (10×10MB chunks): no duplicates (all SHA-256 unique)

Integrity: Verified: True

Run B — neutrino mode (--neutrino --mean-free-path 12000)

VRF

VRF Value: d0939612e90cbcbc3bc8633353344b7fd2e22eeb0021885118cef02becbebf85

VRF Verified: True

Token seed (hex): 5c64074ff038d541cc0b65b9ffabb6cc531fd8e19dadb49924ff1cbe3edc19b0

10 MB output

File: /home/pavlo/quantum_safe_rng_v1577_v13_10mb.bin

Time: 0.15 s → ~66.67 MB/s

Integrity: Verified: True

100 MB output

File: /home/pavlo/quantum_safe_rng_v1577_v13_100mb.bin

Time: 1.62 s → ~61.73 MB/s

Duplicate-check (10×10MB chunks): no duplicates (all SHA-256 unique)

Integrity: Verified: True

Notes

The numbers above are end-to-end (generation + I/O to disk) from the demo pipeline.

The internal custom_rng_bytes steps show ~0.01 s per call in logs (very fast); total wall-clock depends on Python, VRF/reseed steps, and disk I/O.

Prior micro-benchmarks of the core generator reached 90+ MB/s; the demo runs here show ~59–67 MB/s end-to-end on this machine/config.


## Artifacts
- Logs folder: [`rng_reports/`](rng_reports/) (subfolders per date, e.g., `2025-09-08/`).
- Each run contains raw logs + a short README on how it was produced.

> For the Ukrainian narrative, see [RESULTS.uk.md](RESULTS.uk.md).
