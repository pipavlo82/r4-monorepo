# R4-CS (MVP): HKDF-SHA256 → ChaCha20 DRBG (optional external entropy: `re4_stream`)

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
