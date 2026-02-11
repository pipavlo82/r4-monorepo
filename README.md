# ☢️ RE4CTOR — The Nuclear Core of Randomness

### **FIPS-204 Aligned • Post-Quantum VRF • Cryptographically Verifiable Fairness**

> **Low-latency self-hosted verifiable randomness engine (tens of ms in typical setups).**  
> **One of the few self-hosted stacks combining ECDSA + ML-DSA-65 dual-signing and a sealed entropy core.**

[![Proofs: 2025Q4](https://img.shields.io/badge/proofs-2025Q4-blue)](https://github.com/pipavlo82/r4-monorepo/releases/download/v2025.4-proofs/re4ctor_proofs_2025Q4.tar.gz)
[![Status: Q4 2025](https://img.shields.io/badge/status-Q4_2025-blue?style=for-the-badge)](#-roadmap--current-status)
[![FIPS 204 Aligned](https://img.shields.io/badge/FIPS_204-aligned-brightgreen?style=for-the-badge)](docs/FIPS_204_roadmap.md)
[![Docker Pulls](https://img.shields.io/docker/pulls/pipavlo/r4-local-test?style=for-the-badge)](https://hub.docker.com/r/pipavlo/r4-local-test)
[![CI](https://github.com/pipavlo82/r4-monorepo/actions/workflows/ci.yml/badge.svg?style=for-the-badge)](https://github.com/pipavlo82/r4-monorepo/actions/workflows/ci.yml)

---

## ⚖️ Licensing

- **Apache 2.0** — API, VRF node, SDKs, infrastructure
- **Proprietary** — sealed entropy core (`re4_dump`)  
  → see [LICENSE-CORE.md](LICENSE-CORE.md)

**Open where it matters. Closed where security demands it.**

---

## 🧠 Overview

RE4CTOR is a **sealed entropy appliance + fully verifiable randomness pipeline**.

### Core Components

- **☢️ Entropy Core (default 8080)**  
  Sealed compliance-oriented binary → `/random` endpoint

- **🔐 PQ/VRF Node (default 8081)**  
  - Public build: ECDSA signatures
  - Enterprise build: ECDSA + ML-DSA-65 (FIPS-204 post-quantum)

- **📜 Solidity Verifiers**  
  `R4VRFVerifierCanonical.sol` for on-chain verification

- **🎲 LotteryR4**  
  Provably fair on-chain lottery reference implementation

- **🌐 Production Stack**  
  [r4-prod](https://github.com/pipavlo82/r4-prod) for hardened deployments

**Port notes (WSL/Windows):**  
Default local ports: core 8080, vrf 8081, gateway 8082  
WSL/Windows note: if 8080 is busy (often wslrelay.exe), run core on 8089 and update CORE_BASE.

---

## Statistical Validation (2025Q4)

Re4ctoR Core (`re4_dump`) successfully passed:

- **TestU01 BigCrush** — 160/160 passed  
- **Dieharder 3.31.1** — 114/114 passed, 0 weak  
- **PractRand 0.95** — up to 2^32 bytes, no anomalies  
- **NIST STS** — all tests in acceptable range  
- **TestU01 Crush / SmallCrush** (VRF-side) — full pass  

Proof bundle:
[Download Proof Bundle (2025Q4)](https://github.com/pipavlo82/r4-monorepo/releases/download/v2025.4-proofs/re4ctor_proofs_2025Q4.tar.gz)

---

## 🎯 Strategic Focus: Defense + Crypto

RE4CTOR is engineered for two of the most demanding sectors in the world.

### 1️⃣ Defense & National Security

Defense demands:

- Predictable low-latency operation
- Attested boot + integrity manifest
- Compliance-oriented entropy core
- ML-DSA-65 (PQ, FIPS-204 profile)
- SBOM + KAT startup tests
- Zero-trust RNG monitoring (RCT/APT)

**Use cases:**
- PQ migration for government/defense systems
- Secure comms, key transport, KEM systems
- National lotteries & regulated randomness
- Zero-trust distributed systems
- Classified systems requiring sealed entropy

> **Goal:** Become a leading self-hosted FIPS-204 aligned entropy appliance.

### 2️⃣ Crypto & Web3 Infrastructure

Blockchain requires:

- ⚡ Low-latency verifiable randomness
- 🔐 Dual signatures (ECDSA + ML-DSA-65)
- 🧩 Solidity verification on-chain
- 🎲 Deterministic fair selection
- 🚀 High-throughput design

**Use cases:**
- L2 sequencer fairness
- Casinos/iGaming/sportsbooks
- NFT mints & raffles
- ZK-rollup entropy seeding
- DAO random governance

---

## 🚀 Unified 2025–2026 Strategy

| Phase | Target | Description |
|-------|--------|-------------|
| **Phase 1 — Crypto** | 10 protocols | L2s, casinos, NFT platforms |
| **Phase 2 — Defense Prep** | FIPS-aligned | Full compliance package |
| **Phase 3 — Defense Launch** | 3–5 contracts | Post-certification rollout |

---

## 🌐 RE4CTOR Hosted API Gateway

**Hosted gateway in front of RE4CTOR Core RNG and VRF.**

- **API Base URL:** `https://api.re4ctor.com`
- **Docs (Swagger):** `https://api.re4ctor.com/docs`
- **OpenAPI:** `https://api.re4ctor.com/openapi.json`

### Authentication

Requests require `X-API-Key`.

- **Public playground key (temporary):** `demo`  
  Intended for the website playground only. It will be disabled once pricing + key issuance are live.

### Quickstart (hosted)

```bash
# health
curl -sS "https://api.re4ctor.com/v1/health"

# core RNG
curl -sS -H "X-API-Key: demo" \
  "https://api.re4ctor.com/v1/random?n=16&fmt=hex"

# VRF (dual-signed mode depends on deployment build)
curl -sS -H "X-API-Key: demo" \
  "https://api.re4ctor.com/v1/vrf?sig=ecdsa" | jq .
```

### Local dev

When running the production-style stack locally, the services are typically:
- `r4-core` on `127.0.0.1:8080`
- `r4-vrf` on `127.0.0.1:8081`
- `r4-gateway` on `127.0.0.1:8082`
- `caddy` on `:80/:443`

```bash
curl -sS -H "X-API-Key: demo" \
  "http://127.0.0.1:8082/v1/random?n=16&fmt=hex"
```

### Security posture (production)

- Core/VRF/Gateway ports are bound to localhost; only HTTPS via Caddy is public.
- Debug endpoints are blocked at the edge.
- Public/demo keys are temporary and will be removed once billing + key issuance are deployed.

---

## 🧱 Production Deployment — r4-prod (Official)

For stable, hardened, reproducible production deployments:

**🔗 [r4-prod Repository](https://github.com/pipavlo82/r4-prod)**

Contains:

- Production-ready Dockerfiles
- Hardened API Gateway
- r4-prod environment templates
- Nginx reverse proxy configs
- Rate limiting & key protection
- Logging, auditing, key rotation
- Enterprise PQ build support

### Deploy Production

```bash
git clone https://github.com/pipavlo82/r4-prod
cd r4-prod
docker compose up -d
```

Brings up:

- `r4-core` (8080) — entropy appliance
- `r4-vrf` (8081) — verifiable randomness
- `r4-gateway` (443, TLS) — HTTPS API gateway

---

## 🚀 One-Command Local Demo

```bash
./run_full_demo.sh
```

**Custom ports (WSL/Windows):**
```bash
CORE_BASE=http://127.0.0.1:8089 VRF_BASE=http://127.0.0.1:8081 \
CORE_KEY=demo VRF_KEY=demo MODE=local ./run_full_demo.sh
```

Expected output:

```
:8080 Core → OK
:8081 VRF → OK
Stress tests → OK
Hardhat → 6 passing
LotteryR4 → deterministic winner
```

---

## 🐳 Docker Quickstart

```bash
docker run -d \
  --name r4-core \
  -p 8080:8080 \
  -e API_KEY=demo \
  pipavlo/r4-local-test:latest
```

### Get Random Bytes

```bash
curl -H "X-API-Key: demo" \
  "http://127.0.0.1:8080/random?n=32&fmt=hex"
```

---

## 🔐 PQ/VRF Node (Default 8081)

### Canonical VRF endpoint

```bash
# ECDSA signature (public build)
curl -H "X-API-Key: demo" \
  "http://localhost:8081/random_dual?sig=ecdsa"

# ML-DSA-65 signature (enterprise build)
curl -H "X-API-Key: demo" \
  "http://localhost:8081/random_dual?sig=dilithium"
```

**Legacy endpoint:** `/random_pq` (compatibility)

### Public Build Output (requesting PQ)

```json
{
  "error": "ML-DSA signature not available on this build",
  "status": 501,
  "pq_required": true
}
```

---

## 📜 On-Chain VRF Verification

```bash
cd vrf-spec
npm ci
npx hardhat test
```

Expected: **6 passing**

### Included Contracts

- **R4VRFVerifierCanonical.sol** — ECDSA v,r,s recovery
- **LotteryR4.sol** — Provably fair winner selection

Features:

- ✅ ECDSA signature verification
- ✅ Tampering detection & revert
- ✅ Deterministic fair winner selection

---

## 🛡️ Security, Proofs & Compliance

### Included

- Integrity manifest (SHA-256)
- Startup KAT (ChaCha20)
- RCT/APT continuous RNG tests
- SBOM.spdx.json
- GPG-signed release archives
- Dieharder / PractRand / BigCrush logs

### Compliance Mode

```bash
docker run \
  -e R4_COMPLIANCE_MODE=1 \
  -p 8081:8081 \
  r4-compliance-vrf:latest
```

**Note:** Compliance mode enables startup KATs, manifests, and continuous tests. Not FIPS 140-3 certified.

---

## 📊 Statistical Validation & Proof Bundle

Re4ctoR's core entropy stream (re4_dump) and the VRF-side stream (r4-cs) have successfully passed the full suite of heavy statistical test batteries.
A consolidated proof bundle is provided for auditors, integrators, and security teams.

### Included test suites

**Core (re4_dump):**

- **TestU01 BigCrush (v1.2.3)**  
  - Generator: `re4_stream_le32`  
  - Result: **160 / 160 tests PASSED**  
  - No suspicious or catastrophic p-values  
  - Artifacts:
    - `packages/core/proof/bigcrush_summary.txt`
    - `packages/core/artifacts/bigcrush_full_20251020_140456.txt.gz`

- **Dieharder 3.31.1**  
  - Mode: `stdin_input_raw`  
  - Tests: **114**  
  - Result: **114 PASSED, 0 WEAK, 0 FAILED**  
  - Artifacts:
    - `packages/core/proof/dieharder_summary.txt`
    - `packages/core/artifacts/dieharder_20251020_125859.txt.gz`

- **PractRand v0.95 (`RNG_test`)**  
  - RNG: `RNG_stdin64`  
  - Test set: `core`, folding = `standard (64 bit)`  
  - Length: up to **2^32 bytes (4 GiB)**  
  - Result: **"no anomalies"** at all tested lengths  
  - Artifacts:
    - `packages/core/proof/practrand_summary.txt`
    - `packages/core/artifacts/practrand_20251020_133922.txt.gz`

**VRF-side / r4-cs:**

- **NIST SP 800-22 (STS)**  
  - Final report:
    - `packages/vrf-spec/components/r4-cs/rng_reports/nist_sts_finalAnalysisReport.txt`
- **Dieharder targeted re-tests**  
  - `diehard_2dsphere`, `sts_serial`, `rgb_lagged_sum`  
  - All **PASSED** after retest  
  - Reports:
    - `packages/vrf-spec/components/r4-cs/rng_reports/r4cs_dieharder*.txt`
- **TestU01 SmallCrush / Crush / BigCrush (r4-cs stream)**  
  - Summaries:
    - `packages/vrf-spec/components/r4-cs/rng_reports/testu01/smallcrush_summary.txt`
    - `packages/vrf-spec/components/r4-cs/rng_reports/testu01/crush_summary.txt`
    - `packages/vrf-spec/components/r4-cs/rng_reports/testu01/bigcrush_summary.txt`

### 📦 Proof bundle (auditor-friendly)

A complete archive containing all statistical artifacts is available:

- Local path:  
  `proofs/re4ctor_proofs_2025Q4.tar.gz`

The archive contains:

- `packages/core/proof/` (README + BigCrush/Dieharder/PractRand summaries + self-tests)
- `packages/core/artifacts/` (full logs BigCrush, Dieharder, PractRand)
- `packages/vrf-spec/components/r4-cs/rng_reports/` (NIST STS, Dieharder retests, TestU01 SmallCrush/Crush/BigCrush)

To reproduce the bundle locally:

```bash
cd ~/r4-monorepo
PROOF_TAG=2025Q4 ./scripts/make_proof_bundle.sh
```

---

## 🎲 LotteryR4 (Reference Implementation)

```bash
cd vrf-spec
npm ci
npx hardhat compile
npx hardhat test
```

---

## 🗂️ Repository Structure

```
r4-monorepo/
├── README.md
├── LICENSE / LICENSE-CORE.md / NOTICE.md
├── run_full_demo.sh / stress_core.sh / stress_vrf.py
│
├── packages/core/
│   ├── runtime/bin/re4_dump
│   ├── proof/ (Dieharder/PractRand/BigCrush)
│   └── manifest/ (SHA256, GPG, SBOM)
│
├── vrf-spec/
│   ├── contracts/
│   ├── test/
│   ├── scripts/
│   └── README.md
│
├── api/
│   ├── app.py (8080)
│   ├── app_dual.py (8081)
│   ├── Dockerfile
│
└── docs/
    ├── USAGE.md
    ├── DEPLOYMENT.md
    ├── COMPETITION.md
    ├── FIPS_204_roadmap.md
    └── ESV_README.md
```

---

## 📞 Contact

- **Maintainer:** Pavlo Tvardovskyi
- **GitHub:** https://github.com/pipavlo82
- **Docker Hub:** https://hub.docker.com/r/pipavlo/r4-local-test
- **Production:** https://github.com/pipavlo82/r4-prod

---

<div align="center">

### ⚛️ RE4CTOR

**Fairness you can prove. On-chain. Cryptographically.**

[GitHub](https://github.com/pipavlo82/r4-monorepo) • [Docker](https://hub.docker.com/r/pipavlo/r4-local-test) • [r4-prod](https://github.com/pipavlo82/r4-prod)

</div>
