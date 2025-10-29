# FIPS 140-3 / FIPS 204 Roadmap

## Current Status

The RE4CTOR entropy core runs as a sealed module that:
- performs a Known Answer Test (KAT) at startup,
- checks its runtime binary hash against a signed manifest,
- refuses service (`STRICT_FIPS=1`) if self-tests fail,
- exposes attestation via `/version`,
- ships with SBOM (`SBOM.spdx.json`) and statistical test reports (`packages/core/proof/`).

This matches the pre-cert behavior expected by FIPS 140-3 style modules (startup self-test, fail-closed, integrity attestation).

## Post-Quantum Algorithms

- **Dilithium3 (ML-DSA)** — used for post-quantum signing mode in the PQ/VRF node (`:8081`).  
- **Kyber (ML-KEM)** — used for post-quantum key exchange / session bootstrapping.

These map to the NIST post-quantum standards that are being profiled under:
- FIPS 204 (ML-DSA)
- FIPS 203 (ML-KEM)

## Timeline

- **Q4 2025**  
  Hardening completed:
  - deterministic startup self-test
  - integrity manifest
  - tamper-evident release bundle (SBOM + GPG-signed tarball)

- **Q1 2026**  
  Submission of the sealed module (binary + manifest + SBOM + KAT logs + statistical proofs) to an accredited lab for FIPS 140-3 / FIPS 204 validation.

- **2026**  
  Pending certification decision from the lab / NIST channel.

## Disclaimer

"FIPS 204 Ready" means:
- post-quantum primitives (Dilithium3, Kyber) are implemented,
- the module enforces KAT + integrity + fail-closed,
- artifacts required for lab testing exist.

It does **not** mean "already FIPS-certified". Certification review is in progress, targeting 2026.


