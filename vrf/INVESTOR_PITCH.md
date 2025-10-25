# Re4ctor — Verifiable RNG Platform (Investor 1-Pager)

## Problem
Real-money apps (games, fintech, lotteries, on-chain apps) need RNG that is:
- Verifiable (provably fair / auditable), 
- High-throughput and low-latency,
- Operationally simple (multi-tenant, keys, quotas),
- Tamper-resistant (no “fake entropy” at edges).

## Solution
Split the stack:
- **Core**: r4-cs (HKDF→ChaCha20 DRBG) — **closed-source**, optimized.
- **Transport**: HMAC-framed IPC server (re4ctor-ipc) with per-tenant keys.
- **SDKs**: C & Python clients (`r4cat`, `libr4.a`) + commit-reveal & audit helpers.
- **Determinism option**: reproducible seeds for audits & simulations.

## Why Now
- On-chain & regulated workloads require transparent RNG.
- Enterprise games/fintech moving to provable fairness + audit trails.
- “Roll-your-own RNG” incidents keep happening; compliance pressure grows.

## Proof / Traction
- PractRand / NIST STS / TestU01 runs (summaries public).
- Tamper tests (HMAC required) — clients reject unauthenticated frames.
- Deterministic reproducibility for investigation & simulation.

## Business Model
- **Binaries/SaaS**: paid plans by throughput & SLAs, per-tenant keys, signed outputs.
- **Enterprise**: private deployments, HSM integration, custom attestations.
- **Add-ons**: VRF module for on-chain verification, formal verification reports.

## Go-To-Market
- Design partners: gaming platforms, fintech backends, oracles.
- Publish public wrapper + spec + VRF demo for devs.
- Certifications path: FIPS-friendly configuration & SOC 2 processes.

## Ask
Pre-seed/seed to:
1) Ship VRF (verifiable proofs), 
2) Formalize spec & audits, 
3) Pilot with 2–3 design partners.

## Team
- Builder with crypto/RNG, systems, CI hardening background; proven test results and secure IPC design.
