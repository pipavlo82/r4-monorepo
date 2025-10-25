# 🔐 Re4ctoR Cryptographic Audit Overview

Repository: https://github.com/pipavlo82/r4-monorepo  
Maintainer: Pavlo Tvardovskyi (Re4ctoR Project)  
Audit Scope: entropy core / VRF layer / API surface / release integrity  
Planned Audit Window: Q2 2026

---

## Architecture Overview

Re4ctoR provides a deterministic, high-throughput entropy core and a roadmap for post-quantum verifiable randomness (VRF).  
The low-level DRBG / entropy core logic is private, shipped as a signed binary. The API layer and proof outputs are public and testable.

Directory layout:

packages/
core/ → entropy engine, DRBG glue, health monitor, SP800-90B estimator,
FastAPI /random service, SBOM, signed release bundle
vrf-spec/ → post-quantum VRF design, roadmap, investor & protocol briefs
The security model is similar to a hardware RNG / HSM:  
you are allowed to consume, benchmark and continuously test the output stream,  
but the internal mixing logic is not published.

---

## Audit Goals

| Area            | Objective                                                                 |
|-----------------|---------------------------------------------------------------------------|
| Entropy Core    | Statistical soundness, backtracking resistance, health/entropy checks     |
| Crypto Primitives | Correct use of DRBG, HMAC-style framing, SP800-90B style estimators     |
| API Security    | Key auth, rate limiting, request logging, no accidental entropy leakage   |
| Build Integrity | SBOM, SHA256, GPG detached signatures, reproducibility of shipped bundle  |
| Threat Model    | Replay / tamper resistance, abuse surface, privilege boundaries           |

---

## Evidence Provided to Auditors

- PractRand summaries (multi-GB streams, PASS)
- Dieharder summaries (including WEAK cases; expected even for /dev/urandom-class RNGs)
- TestU01 BigCrush summary
- Release bundle:
  - `re4_release.tar.gz`
  - `re4_release.sha256`
  - `re4_release.tar.gz.asc`
- SBOM (SPDX 2.3): `packages/core/release/SBOM.spdx.json`
- Systemd hardening example with sandboxing, non-root user, memory write/exec denied

Full raw logs (multi-GB PractRand / BigCrush runs) are archived offline and can be shared privately under NDA.

---

## Post-Quantum VRF Roadmap

Goal: verifiable randomness endpoint (`/vrf`) that returns:

```json
{
  "random": "<N bytes>",
  "signature": "<post-quantum signature>",
  "public_key": "<node PQ public key>",
  "verified": true
}
Intended uses:

validator / committee selection in Proof-of-Stake

L2 / rollup fairness, sequencer rotation

zk proving seeds / transcript seeding

on-chain lotteries / airdrops / anti-reroll guarantees

Planned primitives: Dilithium / Kyber class (post-quantum secure).

Audit Partners (Planned)
Trail of Bits → cryptographic review of entropy/VRF design

Cure53 → API surface / auth / rate limiting / isolation

Halborn → blockchain / validator / oracle integration review

Contact / Responsible Disclosure
Security contact: security@re4ctor.dev
GPG Fingerprint: ED5B 0368 114D A3AE 355E 4C61 6605 6461 E00D 386B

If you believe you found a weakness (bias, repeatability, predictable state, API abuse vector), please DO NOT open a public GitHub issue.
Instead email security@re4ctor.dev with details. A public summary can be coordinated after triage.
