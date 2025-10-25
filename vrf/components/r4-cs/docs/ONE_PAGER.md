# R4-CS — Deterministic RNG (MVP)

**What it is.** A DRBG that derives a key with HKDF-SHA256 and expands with ChaCha20. Optional external entropy feeder (`re4_stream`) can be mixed in at init/reseed.

**Why it matters.**
- Simple, auditable construction (HKDF + stream cipher).
- Strong statistical quality: PractRand, Dieharder, NIST STS, TestU01 Crush & BigCrush (all passed in our runs).
- Drop-in C library + tiny CLI (`r4cs_cat`).

**Key claims (current status).**
- **Stat suites:**  
  - PractRand v0.95: up to 2 GiB (stdin32/64) — no anomalies.  
  - Dieharder v3.31.1 (`-a`): initial WEAKs, targeted re-tests `-p 100` — **no WEAK/FAILED**.  
  - NIST STS 2.1.2: 80×1e6 bits — pass ratios within expected thresholds.  
  - **TestU01 Crush & BigCrush:** **All tests were passed** (logs attached).
- **Security disclaimer:** statistical tests ≠ cryptographic proof. A formal audit is required before production.

**Architecture (MVP).**
- Seed: HKDF-SHA256( entropy || optional `re4_stream` ), derive `key, nonce`.
- Generate: ChaCha20 keystream → bytes.
- Reseed API (optional): mix new entropy via HKDF, re-derive state.

**Interfaces.**
- C API: `int r4cs_init(...); void r4cs_random(uint8_t*, size_t); void r4cs_close(void);`
- CLI: `./r4cs_cat -n <bytes> [-hex]`.

**Reproducibility:** see `rng_reports/` and README for exact commands.

**License:** MIT. **Status:** MVP for demos; not audited.

**Contact:** Pavlo Tvardovskyi — GitHub: @pipavlo82
