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
- Proportions met required minima.  
- Few isolated low p-values (**0.018–0.006**); **overall status: PASS**.

## Artifacts
- Logs folder: [`rng_reports/`](rng_reports/) (subfolders per date, e.g., `2025-09-08/`).
- Each run contains raw logs + a short README on how it was produced.

> For the Ukrainian narrative, see [RESULTS.uk.md](RESULTS.uk.md).
