# R4-CS DRBG — Whitepaper (Outline)

1. Abstract & Scope
2. Construction
   - Entropy model & seeding
   - HKDF-SHA256 for KDF (extract/expand)
   - ChaCha20 as expander
   - Optional external stream mixing
3. Security Discussion
   - Backtracking resistance & forward secrecy (what we guarantee / open questions)
   - Reseed policy
   - State handling, zeroization
   - Side-channel considerations (high-level)
4. Statistical Testing
   - PractRand, Dieharder, NIST STS, TestU01 (Crush/BigCrush) — methodology & results
5. Performance Notes (future work to benchmark)
6. Limitations & Non-Goals
7. Threat Model & Intended Use
8. Reproducibility (exact commands, environment)
9. Roadmap to Audit & Certification (FIPS-140-3 readiness plan)
