# ☢️ RE4CTOR — The Nuclear Core of Randomness

### **FIPS-204 Ready • Post-Quantum VRF • Cryptographically Verifiable Fairness**

> **The fastest self-hosted verifiable randomness engine (20–30 ms).**  
> **The only 2025 solution with ECDSA + ML-DSA-65 dual signatures and a sealed FIPS-grade entropy core.**

[![Status: Q4 2025](https://img.shields.io/badge/status-Q4_2025-blue?style=for-the-badge)](#-roadmap--current-status)
[![FIPS 204 Ready](https://img.shields.io/badge/FIPS_204-ready-brightgreen?style=for-the-badge)](docs/FIPS_204_roadmap.md)
[![PyPI](https://img.shields.io/pypi/v/r4sdk?label=r4sdk&style=for-the-badge)](https://pypi.org/project/r4sdk/)
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

- **☢️ Entropy Core (port 8080)**  
  Sealed FIPS-grade binary → `/random` endpoint

- **🔐 PQ/VRF Node (port 8081)**  
  - Public build: ECDSA signatures
  - Enterprise build: ECDSA + ML-DSA-65 (FIPS-204 post-quantum)

- **📜 Solidity Verifiers**  
  `R4VRFVerifierCanonical.sol` for on-chain verification

- **🎲 LotteryR4**  
  Provably fair on-chain lottery reference implementation

- **🐍 Python SDK**  
  Available via `pip install r4sdk`

- **🌐 Production Stack**  
  [r4-prod](https://github.com/pipavlo82/r4-prod) for hardened deployments

---

## 🎯 Strategic Focus: Defense + Crypto

RE4CTOR is engineered for two of the most demanding sectors in the world.

### 1️⃣ Defense & National Security

Defense demands:

- Predictable **20–30 ms** latency
- Attested boot + integrity manifest
- FIPS-grade entropy core
- ML-DSA-65 (PQ, FIPS-204 profile)
- SBOM + KAT startup tests
- Zero-trust RNG monitoring (RCT/APT)

**Use cases:**
- PQ migration for government/defense systems
- Secure comms, key transport, KEM systems
- National lotteries & regulated randomness
- Zero-trust distributed systems
- Classified systems requiring sealed entropy

> **Goal:** Become the first fully self-hosted FIPS-204 entropy appliance.

### 2️⃣ Crypto & Web3 Infrastructure

Blockchain requires:

- ⚡ **20–30 ms verifiable randomness**
- 🔐 Dual signatures (ECDSA + ML-DSA-65)
- 🧩 Solidity verification on-chain
- 🎲 Deterministic fair selection
- 🚀 100k–300k req/s throughput

**Use cases:**
- L2 sequencer fairness
- Casinos/iGaming/sportsbooks
- NFT mints & raffles
- ZK-rollup entropy seeding
- DAO random governance

> **Impact:** ~1000× faster than Chainlink VRF.  
> The only PQ-ready randomness pipeline in production (2025).

---

## 🚀 Unified 2025–2026 Strategy

| Phase | Target | Description |
|-------|--------|-------------|
| **Phase 1 — Crypto** | 10 protocols | L2s, casinos, NFT platforms |
| **Phase 2 — Defense Prep** | FIPS-ready | Full compliance package |
| **Phase 3 — Defense Launch** | 3–5 contracts | Post-certification rollout |

---

## ☁️ SaaS Gateway (Demo)

🔗 **Live:** https://r4-saas-api.onrender.com  
📦 **Source:** https://github.com/pipavlo82/r4-saas-api

### ⚠️ Latency Notice

- Demo (free-tier hosting): **~1481 ms**
- Real VPS: **20–30 ms p99**

> **Demo slow ≠ product slow.**  
> Production is **50–70× faster**.

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

**Production latency: 20–30 ms p99**

---

## 🚀 One-Command Local Demo

```bash
./run_full_demo.sh
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

## 🐍 Python SDK

```bash
pip install r4sdk
```

```python
from r4sdk import R4Client

client = R4Client(api_key="demo", host="http://localhost:8080")
random_bytes = client.get_random(32)
print(random_bytes.hex())
```

---

## 🔐 PQ/VRF Node (Port 8081)

### Public Build (ECDSA)

```bash
curl -H "X-API-Key: demo" \
  "http://localhost:8081/random_dual?sig=ecdsa"
```

### Enterprise Build (ML-DSA-65)

```bash
curl "http://localhost:8081/random_dual?sig=dilithium"
```

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

## 🛡️ Security, Proofs & FIPS

### Included

- Integrity manifest (SHA-256)
- Startup KAT (ChaCha20)
- RCT/APT continuous RNG tests
- SBOM.spdx.json
- GPG-signed release archives
- Dieharder / PractRand / BigCrush logs

### Strict FIPS Mode

```bash
docker run \
  -e R4_STRICT_FIPS=1 \
  -p 8081:8081 \
  r4-fips-vrf:latest
```

---

## 📊 Statistical Validation

| Suite | Result |
|-------|--------|
| NIST SP 800-22 | 15/15 ✅ |
| Dieharder | 31/31 ✅ |
| PractRand | 8 GB ✅ |
| TestU01 BigCrush | 160/160 ✅ |

### Performance Metrics

- **Latency:** 20–30 ms (p99)
- **Throughput:** 950k req/s
- **Entropy bias:** < 1e-6

---

## 🥊 R4 vs Competitors

| Feature | R4 | Chainlink VRF | drand | AWS HSM |
|---------|----|----|----|----|
| Latency | 20–30 ms | 30–120 s | 3–30 s | 10–50 ms |
| PQ Ready | Yes (ML-DSA-65) | No | No | Partial |
| Cost | $0/call | $1–3M / 1M calls | Free | $$$$ |
| On-Chain Proof | Yes | Yes | Limited | No |
| Self-hosted | Easy | No | Medium | Hard |
| Throughput | 100k/s | 1–10k/s | 1–5k/s | 50k/s |

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
├── sdk_py_r4/
│   ├── r4sdk/
│   └── PyPI packaging
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
- **Email:** shtomko@gmail.com
- **GitHub:** https://github.com/pipavlo82
- **Docker Hub:** https://hub.docker.com/r/pipavlo/r4-local-test
- **PyPI:** https://pypi.org/project/r4sdk/
- **Production:** https://github.com/pipavlo82/r4-prod

---

<div align="center">

### ⚛️ RE4CTOR

**Fairness you can prove. On-chain. Cryptographically.**

[GitHub](https://github.com/pipavlo82/r4-monorepo) • [Docker](https://hub.docker.com/r/pipavlo/r4-local-test) • [PyPI](https://pypi.org/project/r4sdk/) • [r4-prod](https://github.com/pipavlo82/r4-prod)

</div>
