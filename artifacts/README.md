# 📂 RE4CTOR Statistical Proof Artifacts

This directory contains **raw generator test logs** for the sealed entropy core.

These logs are produced by running the internal RNG output through standard statistical batteries under controlled conditions.  
They are published so auditors, validators, regulators, and casino compliance teams can independently review output quality.

### 1. BigCrush full output
- [bigcrush_full_20251020_140456.txt.gz](https://github.com/pipavlo82/re4ctor-core/blob/main/artifacts/bigcrush_full_20251020_140456.txt.gz)
- Full output from **TestU01 BigCrush**
- Result: **PASS**

### 2. Dieharder full output
- [dieharder_20251020_125859.txt.gz](https://github.com/pipavlo82/re4ctor-core/blob/main/artifacts/dieharder_20251020_125859.txt.gz)
- Result: **PASS (31/31)**

### 3. PractRand full output
- [practrand_20251020_133922.txt.gz](https://github.com/pipavlo82/re4ctor-core/blob/main/artifacts/practrand_20251020_133922.txt.gz)
- Run: ~8+ GB, **no anomalies**



---

## How to interpret

We also ship short human-readable summaries under  
[`packages/core/proof/`](../packages/core/proof/).

Those summaries include:
- `dieharder_summary.txt`
- `practrand_summary.txt`
- `bigcrush_summary.txt`

and an overview `README.md` explaining methodology and environment.

This `artifacts/` directory is for the **full raw logs**, not just summaries.

---

## Integrity / Reproducibility

Every RE4CTOR release bundle includes:
- Sealed core binary (`re4_dump`)
- SHA-256 manifest
- GPG signature (`.asc`)
- SBOM (`SBOM.spdx.json`)
- These statistical logs

You can:
1. Pull the Docker image,
2. Run the self-test harness,
3. Reproduce fresh logs,
4. Compare with ours.

This is part of the FIPS 140-3 / FIPS 204 certification path (target submission: Q1 2026).

---

## Notes

- Some full logs are large (tens of MB). They are compressed as `.txt.gz`.
- If you are a regulator / auditor and need the uncompressed originals, email `shtomko@gmail.com` with subject `RE4CTOR FULL PROOF REQUEST`.
- For casino / gaming / sportsbook compliance: we provide signed per-round randomness + on-chain verifiers, not just statistics.

**Status:** artifacts are provided as-is for transparency. They are not a FIPS certificate.
