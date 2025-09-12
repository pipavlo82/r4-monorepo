# Re4ctoR-RNG — Results

## TL;DR (2025-09-08)
- **PractRand:** *no anomalies* up to **8 GB** (latest runs after reseed/nonce fixes).
  - Older builds (2025-09-04, 2025-09-07) showed *suspicious/very suspicious* — these were pre-fix binaries.
- **TestU01 / BigCrush:** *All tests were passed* (two independent runs).
- **NIST STS:** proportions ≥ required minima; a few low p-values (~**0.018–0.006**) in isolated sub-tests, but **overall PASS** (proportions within acceptable ranges).

## Details

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
