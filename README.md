[![CI](https://github.com/pipavlo82/r4-cs/actions/workflows/ci.yml/badge.svg)](https://github.com/pipavlo82/r4-cs/actions/workflows/ci.yml)
# R4-CS (MVP): HKDF-SHA256 → ChaCha20 DRBG with optional external entropy (`re4_stream`)

![CI](https://github.com/pipavlo82/r4-cs/actions/workflows/ci.yml/badge.svg)


**Status:** MVP for demonstrations. Ships a C library (`-lr4cs` via `pkg-config`), a CLI tool (`r4cs_cat`), and real test logs (PractRand / Dieharder / NIST STS / TestU01 Crush) in `rng_reports/`.

## ⚠️ Security disclaimer
Passing statistical test suites is **not** a proof of cryptographic security. A proper independent audit is required before any production use.

---

## What’s in the repo
- **Library:** C API (`r4cs.h`), link with `pkg-config --cflags --libs r4cs`.
- **CLI:** `r4cs_cat` – dumps raw/hex bytes to stdout.
- **Demo:** `demo.c` – prints 32 random bytes (hex).
- **Logs:** `rng_reports/` – raw/summary outputs of the runs below.

---

## Quick start (Linux)

### Use the library (`pkg-config`)
```bash
gcc -O2 -std=c11 demo.c $(pkg-config --cflags --libs r4cs) -o demo
./demo    # 32 hex bytes


## TestU01 BigCrush (v1.2.3)

- Generator: **R4-CS_DRBG**  
- Number of statistics: **160**  
- Result: **All tests were passed**  
- Total CPU time: ~14h on my machine  
- Logs: `rng_reports/testu01/bigcrush_summary.txt` (brief).  
  Full raw BigCrush log is excluded from the repo to keep it lean.

> Note: Passing statistical batteries (PractRand / Dieharder / NIST STS / TestU01) does **not** prove cryptographic security. A formal independent audit is still required before production use.

## TestU01 BigCrush (v1.2.3)

- Generator: **R4-CS_DRBG**  
- Number of statistics: **160**  
- Result: **All tests were passed**  
- Total CPU time: ~14h on my machine  
- Logs: `rng_reports/testu01/bigcrush_summary.txt` (brief).  
  Full raw BigCrush log is excluded from the repo to keep it lean.

> Passing PractRand / Dieharder / NIST STS / TestU01 does **not** prove cryptographic security. A formal independent audit is still required before production use.

---

## Test results (reproducible)

- **PractRand v0.95**
  - stdin32: 1 GiB (2^30) — no anomalies
  - stdin64: 1 GiB (2^30) — no anomalies
  - stdin32: 2 GiB (2^31) — no anomalies
  - Smoke 64 MiB (2^26) — no anomalies  
  Logs: `rng_reports/r4cs_pr32_tl30_32.txt`, `r4cs_pr64_tl30_32.txt`, `r4cs_pr32_tl31_33.txt`.

- **Dieharder v3.31.1 (`-a`)**
  - Initial full battery: all PASSED; three WEAKs observed (2dsphere, sts_serial k=5, rgb_lagged_sum t=30).
  - Targeted re-tests (`-p 100`): **no WEAK/FAILED**.  
  Logs: `rng_reports/r4cs_dieharder.txt`, `r4cs_dieharder_retest.txt`.

- **NIST STS 2.1.2**
  - 80 bitstreams × 1,000,000 bits (ASCII). Pass ratios within thresholds for N=80.  
  Logs: `rng_reports/nist_sts_summary.txt` (and STS output).

- **TestU01 (Crush & BigCrush)**
  - **Crush**: All tests were passed.
  - **BigCrush**: All tests were passed.  
  Logs: `rng_reports/testu01/crush.txt`, `rng_reports/testu01/bigcrush.txt`, summary excerpt: `rng_reports/testu01/bigcrush_summary.txt`.

> ⚠️ Statistical suites ≠ crypto proof. Independent audit required before production.

### Dieharder targeted re-tests
See `rng_reports/r4cs_dieharder_retest_summary.txt` (IDs 11/102/203). No WEAK/FAILED observed.

## Test results (reproducible)

**Note:** Passing statistical batteries does *not* prove cryptographic security. This is a DRBG MVP; an independent audit is required before any production use.

- PractRand v0.95:
  - stdin32: 1 GiB (2^30) — no anomalies  
  - stdin64: 1 GiB (2^30) — no anomalies  
  - stdin32: 2 GiB (2^31) — no anomalies  
  - Smoke: 64 MiB — no anomalies  
  See: `rng_reports/r4cs_pr32_tl30_32.txt`, `rng_reports/r4cs_pr64_tl30_32.txt`, `rng_reports/r4cs_pr32_tl31_33.txt`.

- Dieharder v3.31.1 (full `-a`): initial run showed **WEAK** in 3 tests (2dsphere, sts_serial(k=5), rgb_lagged_sum(t=30)); targeted re-tests with `-p 100`: **no WEAK/FAILED**.  
  See: `rng_reports/r4cs_dieharder.txt`, `rng_reports/r4cs_dieharder_retest_*.txt`.

- NIST STS 2.1.2: 80 streams × 1,000,000 bits; pass rates within the expected thresholds for N=80.  
  See STS summary under `rng_reports/`.

- TestU01 v1.2.3:
  - **Crush**: *All tests were passed*.  
    See: `rng_reports/testu01_crush_summary.txt`
  - **BigCrush**: *All tests were passed*.  
    See: `rng_reports/testu01/bigcrush_summary.txt`

