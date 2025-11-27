Licensing: Apache 2.0 (API/VRF/SDK); Proprietary for sealed entropy core (see LICENSE-CORE.md).
> Licensing: Apache 2.0 for API/VRF; proprietary for sealed entropy core (see LICENSE).
# ☢️ RE4CTOR — The Nuclear Core of Randomness

> **Verifiable entropy • Post-quantum VRF • Attested boot • On-chain fairness you can prove**

[![Status: End of 2025](https://img.shields.io/badge/status-as_of_2025_Q4-blue?style=flat-square)](#-roadmap--current-status-as-of-november-2025)
[![FIPS 204 Ready](https://img.shields.io/badge/FIPS%20204%20Ready-brightgreen?style=flat-square)](docs/FIPS_204_roadmap.md)
[![PyPI](https://img.shields.io/pypi/v/r4sdk?label=r4sdk%20on%20PyPI&style=flat-square)](https://pypi.org/project/r4sdk/)
[![Docker Pulls](https://img.shields.io/docker/pulls/pipavlo/r4-local-test?style=flat-square)](https://hub.docker.com/r/pipavlo/r4-local-test)
[![VRF Tests](https://github.com/pipavlo82/r4-monorepo/actions/workflows/vrf-tests.yml/badge.svg)](https://github.com/pipavlo82/r4-monorepo/actions/workflows/vrf-tests.yml)
[![CI Status](https://github.com/pipavlo82/r4-monorepo/actions/workflows/ci.yml/badge.svg)](https://github.com/pipavlo82/r4-monorepo/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/pipavlo82/r4-monorepo?include_prereleases&style=flat-square)](https://github.com/pipavlo82/r4-monorepo/releases)

**Licensing:** Apache 2.0 for API/VRF; proprietary for sealed entropy core (see [LICENSE-CORE](LICENSE-CORE.md)).

---

## 📋 Table of Contents

- [Overview](#-overview)
- [One-Command Demo](#-one-command-demo)
- [Docker Quickstart](#-docker-quickstart-8080)
- [Python SDK](#-python-sdk)
- [PQ/VRF Node](#-pqvrf-node-8081)
- [On-Chain Verifier](#-on-chain-verifier)
- [Security & Proofs](#-security--proofs)
- [Roadmap & Status](#-roadmap--current-status-as-of-november-2025)
- [Competitive Analysis](#-r4-vs-competitors)
- [LotteryR4](#-lotteryr4--provably-fair-on-chain-lottery)
- [Repository Structure](#-repository-structure)
- [Contributing](#contributing)
- [Support](#-support)
- [Contact](#-contact)
- [Resources](#-resources)

---

## 🧠 Overview

RE4CTOR is a **sealed entropy appliance + verifiable randomness pipeline**.

- **☢️ Core entropy node (:8080)** — sealed core binary via FastAPI `/random`
- **🔐 PQ/VRF node (:8081)** — ECDSA + (enterprise) ML-DSA-65 signed randomness
- **🧬 Solidity verifiers** — `R4VRFVerifierCanonical.sol` to prove origin on-chain
- **🎲 LotteryR4.sol** — fair lottery reference implementation
- **🐍 Python SDK** — `pip install r4sdk` for servers/validators/bots

**Typical use cases:** casinos & sportsbooks, NFT raffles, validator rotation, ZK-rollup seeding, "prove to regulators we didn't rig this."

> 💡 **Need a hosted HTTPS API instead of running the full stack?**  
> Check out **R4 SaaS API Gateway** → [github.com/pipavlo82/r4-saas-api](https://github.com/pipavlo82/r4-saas-api)

---

## 🚀 One-Command Demo

```bash
./run_full_demo.sh
```

What you should see:

- ✅ :8080 Core API up
- ✅ :8081 PQ/VRF API returning ECDSA signatures (public build)
- ✅ 100 req/sec to :8080, zero errors
- ✅ :8081 stress: 200 OK vs 429 rate-limited
- ✅ Hardhat tests: 6 passing
- ✅ LotteryR4 picks a winner on-chain

If you see "6 passing", you've proven local fairness. 🎉

---

## 🐳 Docker Quickstart (:8080)

Run:

```bash
docker run -d \
  --name r4-core \
  -p 8080:8080 \
  -e API_KEY=demo \
  pipavlo/r4-local-test:latest
```

Health check:

```bash
curl http://127.0.0.1:8080/health
# → "ok"
```

Get randomness:

```bash
curl -H "X-API-Key: demo" \
  "http://127.0.0.1:8080/random?n=32&fmt=hex"
# → "a359b9dd843294e415ac0e41eb49ef90..."
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
print(f"🔐 Random: {random_bytes.hex()}")
```

📦 **PyPI:** https://pypi.org/project/r4sdk/

---

## 🔐 PQ/VRF Node (:8081)

Returns randomness + signature proof for on-chain verification.
Public image exposes ECDSA; Enterprise build enables ML-DSA-65 (FIPS-204 profile).

Run:

```bash
docker run -d \
  --name r4-vrf \
  -p 8081:8081 \
  -e API_KEY=demo \
  pipavlo/r4-local-test:latest
```

**ECDSA (public):**

```bash
curl -sS -H "X-API-Key: demo" \
  "http://localhost:8081/random_dual?sig=ecdsa" | jq .
```

Example response:

```json
{
  "random": 3108117130,
  "timestamp": "2025-11-06T22:59:37Z",
  "hash_alg": "SHA-256",
  "signature_type": "ECDSA(secp256k1) + ML-DSA-65",
  "v": 27,
  "r": "0xce2d9acb1a9955c5521994112fa7d5c4b02b7912385c3df705ed611ae6f6455c",
  "s": "0x5468dcc38a472bbcbc6b6deac0469aae76ff8690ba2baeaa9381b81b0b4aa477",
  "msg_hash": "0xc93f71c19c0845950a3cd4d56ab95b4f6ce28f95955e5ed5b0e7cc2beee11c01",
  "signer_addr": "0x1C901e3bd997BD46a9AE3967F8632EFbDFe72293",
  "pq_scheme": "ML-DSA-65"
}
```

**Enterprise PQ (ML-DSA-65):**

```bash
# Enterprise build only; public image returns 501
curl -sS -H "X-API-Key: demo" \
  "http://localhost:8081/random_dual?sig=dilithium" | jq .
```

Public image expected response:

```json
{
  "error": "ML-DSA (Dilithium) signature not available on this build",
  "pq_required": true,
  "status": 501,
  "hint": "Enterprise / FIPS 204 build required"
}
```

---

## 🧱 On-Chain Verifier

Contracts (under `vrf-spec/contracts/`):

- **R4VRFVerifierCanonical.sol** — verifies ECDSA v,r,s & trusted signer
- **LotteryR4.sol** — fair lottery using verified randomness

Run tests:

```bash
cd vrf-spec
npx hardhat test
# → 6 passing
```

Demonstrates:

- ✅ Valid signed randomness → deterministic winner
- ❌ Tampered randomness → revert

---

## 🛡️ Security & Proofs

### FIPS 140-3 / FIPS 204 Path

Sealed entropy core ships with:

- Startup KAT (ChaCha20 vector)
- Integrity hash vs pinned manifest
- Fail-closed option (`R4_STRICT_FIPS=1`)
- SBOM (SBOM.spdx.json) for supply-chain
- Statistical bundles (Dieharder, PractRand, BigCrush) under `packages/core/proof/`

Submission package for lab includes:

- `re4_release.tar.gz`
- `re4_release.sha256`
- `re4_release.tar.gz.asc` (GPG)
- `SBOM.spdx.json`
- KAT and health-test logs

### Boot Integrity & Startup Attestation

At container boot:

1. **Integrity check** (SHA-256)
2. **KAT** (ChaCha20)
3. **Health tests** — RCT / APT / Continuous RNG
4. **Attestation output** (stdout)

**Strict-FIPS mode:**

```bash
docker run -e R4_STRICT_FIPS=1 -p 8081:8081 r4-fips-vrf:latest
```

### Statistical Validation

| Suite | Result |
|-------|--------|
| NIST SP 800-22 | 15/15 ✅ |
| Dieharder | 31/31 ✅ |
| PractRand | 8 GB ✅ |
| TestU01 BigCrush | 160/160 ✅ |
## 📊 Statistical Validation & Proof Bundle

Re4ctoR’s core entropy stream (re4_dump) and the VRF-side stream (r4-cs) have successfully passed the full suite of heavy statistical test batteries.
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
- `packages/core/artifacts/` (повні логи BigCrush, Dieharder, PractRand)
- `packages/vrf-spec/components/r4-cs/rng_reports/` (NIST STS, Dieharder ретести, TestU01 SmallCrush/Crush/BigCrush)

To reproduce the bundle locally:

```bash
cd ~/r4-monorepo
PROOF_TAG=2025Q4 ./scripts/make_proof_bundle.sh

**Performance** (see [docs/proof/benchmarks_summary.md](docs/proof/benchmarks_summary.md)):

- Throughput: ~950k req/s
- Latency p99: ~1.1 ms
- Entropy bias: < 1e-6

---

## 📅 Roadmap & Current Status (as of November 2025)

2025 wrap-up: all technical milestones complete; enterprise build is frozen for FIPS pre-submission.

| Quarter | Milestone | Status |
|---------|-----------|--------|
| Q1 2025 | ML-DSA-65 (FIPS-204) signing integrated into PQ node | ✅ Shipped |
| Q2 2025 | Kyber KEM handshake added to VRF key-exchange layer | ✅ Shipped |
| Q3 2025 | Solidity verifier audited + public testnet (Sepolia) launched | ✅ Complete |
| Q4 2025 | Attestation pipeline + integrity self-test hardening | ✅ Complete |
| Q1 2026 (target) | Package submission to FIPS lab (sealed core + SBOM + KAT logs) | 🟨 Ready for submission |
| Mid-2026 (expected) | FIPS 140-3 / FIPS 204 certification decision (lab) | ⏳ Pending (External) |

**Summary:**

- ✅ ECDSA, ML-DSA-65, Kyber KEM implemented & documented
- 🧩 Self-tests stable across Docker/native builds
- 🧾 FIPS bundle frozen awaiting lab hand-off
- 🌐 Public Docker = ECDSA + PQ metadata; Enterprise = full ML-DSA-65 signing

---

## 🥊 R4 vs Competitors
# RE4CTOR vs Competitors: Honest Comparison


| Feature | R4 | Chainlink | drand | AWS HSM |
|---------|-----|-----------|--------|---------|
| **Latency** | **20–30 ms** | 30–120 s | 3–30 s | 10–50 ms |
| **Post-Quantum** | ✅ ML-DSA-65 | ❌ | ❌ | ⚠️ |
| **Cost** | self-hosted | pay/req | free | $$$$ |
| **On-chain verify** | ✅ | ✅ | ⚠️ | ❌ |
| **Self-hosted** | ✅ | ❌ | ✅ | ⚠️ |
| **Throughput** | ~100k/s | limited | limited | ~50k/s |
| **FIPS 204 Ready** | ✅ Q1 2026 | ❌ | ❌ | ❌ |

---

## Detailed Breakdown

### Latency Comparison

| Service | Actual | Notes |
|---------|--------|-------|
| **RE4CTOR** | 20–30 ms | HTTP + crypto proof (live tested Nov 11, 2025) |
| **AWS HSM** | 10–50 ms | Hardware + TLS (config dependent) |
| **drand** | 3–30 s | Beacon finality + network |
| **Chainlink VRF** | 30–120 s | Oracle network + blockchain confirmation |

**Verdict:** RE4CTOR comparable to AWS HSM, 1000x faster than Chainlink/drand

---

### Post-Quantum Readiness

| Service | Status | Timeline |
|---------|--------|----------|
| **RE4CTOR** | ✅ ML-DSA-65 implemented | Already in production (2025) |
| **AWS HSM** | ⚠️ Planning | Unknown |
| **Chainlink** | ❌ No roadmap | Not prioritized |
| **drand** | ❌ No roadmap | Not prioritized |

**Verdict:** RE4CTOR only production-ready PQ RNG (2025)

---

### Cost Analysis

| Service | Model | 1M Calls/Month |
|---------|-------|-------------|
| **RE4CTOR** | Self-hosted | ~$500 (1 server) |
| **Chainlink VRF** | Pay-per-request | $1M–5M |
| **drand** | Free | $0 |
| **AWS HSM** | Monthly rental | $5k–50k |

**Verdict:** RE4CTOR 1000x cheaper than Chainlink for volume users

---

### On-Chain Verification

| Service | On-Chain Verify | Method |
|---------|-----------------|--------|
| **RE4CTOR** | ✅ Yes | ECDSA (EIP-191) + ML-DSA-65 |
| **Chainlink** | ✅ Yes | Oracle callback |
| **drand** | ⚠️ Limited | Beacon only |
| **AWS HSM** | ❌ No | Offline, no proof |

**Verdict:** RE4CTOR and Chainlink support on-chain verification

---

### Self-Hosted Capability

| Service | Self-Host | Difficulty |
|---------|-----------|-----------|
| **RE4CTOR** | ✅ Yes | Easy (Docker Compose) |
| **drand** | ✅ Yes | Medium (setup + relay) |
| **AWS HSM** | ⚠️ Hybrid | Hard (AWS management) |
| **Chainlink** | ❌ No | Centralized network |

**Verdict:** RE4CTOR easiest to deploy

---

### Throughput

| Service | Measured | Notes |
|---------|----------|-------|
| **RE4CTOR** | ~100k/s | Tested; scales to 300k/s concurrent |
| **AWS HSM** | ~50k/s | Hardware-limited |
| **Chainlink** | ~1–10k/s | Blockchain finality bottleneck |
| **drand** | ~1–5k/s | Beacon finality bottleneck |

**Verdict:** RE4CTOR highest throughput

RE4CTOR: 20–30ms Verifiable Randomness

The only FIPS 204-ready, post-quantum RNG 
you can self-host today.

Performance:
  • 20–30ms latency (comparable to AWS HSM)
  • 1000x faster than Chainlink VRF
  • ~100k req/s throughput
  
Security:
  • ECDSA + ML-DSA-65 dual signatures
  • FIPS 204 certification ready (Q1 2026)
  • On-chain verification included
  
Cost:
  • Self-hosted: $0 per call
  • vs Chainlink: $1–5 per call
  • 90% cost savings for volume users

Use Cases:
  ✅ Gaming & Casinos
  ✅ Defense/Government (FIPS 204)
  ✅ DeFi Protocols
  ✅ Enterprise Systems
```

---

## Quick Reference Table

| Dimension | R4 | Chainlink | AWS HSM | drand |
|-----------|-----|-----------|---------|-------|
| **Speed** | 20–30ms ⚡ | 30–120s 🐢 | 10–50ms 📦 | 3–30s 📊 |
| **Cost** | $0/call | $1–5/call | $$$$$ | Free |
| **Post-Quantum** | ✅ | ❌ | ❌ | ❌ |
| **Self-Hosted** | ✅ Easy | ❌ | ⚠️ Hard | ✅ Medium |
| **On-Chain Proof** | ✅ | ✅ | ❌ | ⚠️ |
| **Best For** | Gaming, Defense, DeFi | Decentralization | Enterprise | Beacon |

**Decision:** need speed + verifiable proof → **R4**. Need decentralization → **Chainlink/drand**.
[docs/COMPETITION.md](docs/COMPETITION.md)


---

## 🎲 LotteryR4 — Provably Fair On-Chain Lottery

Reference Solidity implementation using RE4CTOR randomness.

**Workflow:**

1. Register players → `enterLottery()`
2. Fetch signed randomness from :8081
3. On-chain verify via `R4VRFVerifierCanonical.verify()`
4. Deterministic winner selection: `winnerIndex = uint256(randomness) % players.length`
5. Full audit trail via events

**Quick start:**

```bash
cd vrf-spec
npm ci
npx hardhat compile
npx hardhat test   # expect 6 passing
```

**Key features:**

- ✅ Players register on-chain
- ✅ Operator fetches signed randomness (off-chain)
- ✅ Signature verified on-chain (no trust needed)
- ✅ Winner picked deterministically & transparently
- ✅ Audit trail immutable forever

See [vrf-spec/README.md](vrf-spec/README.md) for full integration guide.

---

## 🗺️ Repository Structure

```
r4-monorepo/
├── README.md                          # ← You are here
├── LICENSE                            # Apache 2.0 (wrapper code)
├── LICENSE-CORE.md                    # Proprietary (sealed entropy)
├── NOTICE.md                          # IP ownership statement
├── CONTRIBUTING.md
├── SPONSORS.md
├── run_full_demo.sh
├── stress_core.sh
├── stress_vrf.py
│
├── packages/core/
│   ├── runtime/bin/re4_dump           # sealed entropy core binary
│   ├── proof/                         # Dieharder/PractRand/BigCrush logs
│   │   ├── dieharder.log
│   │   ├── practrand.log
│   │   └── bigcrush.log
│   └── manifest/                      # sha256, GPG sig, SBOM
│       ├── re4_release.sha256
│       ├── re4_release.tar.gz.asc
│       └── SBOM.spdx.json
│
├── vrf-spec/
│   ├── contracts/
│   │   ├── R4VRFVerifierCanonical.sol  # on-chain ECDSA verification
│   │   └── LotteryR4.sol               # reference lottery
│   ├── test/
│   │   ├── lottery.js
│   │   ├── verify.js
│   │   └── verify_r4_canonical.js
│   ├── scripts/
│   │   └── deploy.js
│   ├── hardhat.config.js
│   ├── package.json
│   └── README.md
│
├── api/
│   ├── app.py                         # :8080 core API
│   ├── app_dual.py                    # :8081 PQ/VRF endpoint
│   ├── dual_router.py
│   ├── sign_ecdsa.py
│   ├── sign_pq.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── sdk_py_r4/
│   ├── r4sdk/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   └── types.py
│   ├── test_r4sdk.py
│   ├── setup.py
│   └── README.md
│
├── tools/
│   ├── verify_vrf_msg_hash.py
│   └── (other utilities)
│
├── docker/
│   ├── Dockerfile
│   ├── .dockerignore
│   └── stubs/re4_dump                 # stub for CI testing
│
├── docs/
│   ├── USAGE.md
│   ├── DEPLOYMENT.md
│   ├── COMPETITION.md
│   ├── FIPS_204_roadmap.md
│   ├── ESV_README.md
│   └── proof/benchmarks_summary.md
│
└── .github/workflows/
    ├── ci.yml
    └── vrf-tests.yml
```

---

## Contributing

We welcome PRs for:

- New verifier contracts (L2s, alt-EVMs)
- Hardhat/Huff audits
- Reproducible benchmark scripts
- Documentation improvements

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📞 Support

**Documentation:**

- [API Usage](docs/USAGE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Performance Benchmarks](docs/proof/benchmarks_summary.md)
- [FIPS 204 Roadmap](docs/FIPS_204_roadmap.md)
- [Competitive Analysis](docs/COMPETITION.md)
- [Entropy Source Validation](docs/ESV_README.md)

**Community:**

- 💬 [GitHub Issues](https://github.com/pipavlo82/r4-monorepo/issues) — bug reports & features
- 💭 [GitHub Discussions](https://github.com/pipavlo82/r4-monorepo/discussions) — integration Q&A

**Enterprise & Regulated Gaming:**

- 📧 Email: [shtomko@gmail.com](mailto:shtomko@gmail.com) (subject: **"R4 ENTERPRISE"**)
- 🤝 Sponsorship tiers: see [SPONSORS.md](SPONSORS.md)

---

## 📬 Contact

**Maintainer:** Pavlo Tvardovskyi

- 📧 Email: [shtomko@gmail.com](mailto:shtomko@gmail.com)
- 🐙 GitHub: [@pipavlo82](https://github.com/pipavlo82)
- 🐳 Docker Hub: [pipavlo/r4-local-test](https://hub.docker.com/r/pipavlo/r4-local-test)
- 📦 PyPI: [r4sdk](https://pypi.org/project/r4sdk/)

---

## 📚 Resources

- [Contributing Guide](CONTRIBUTING.md)
- [Sponsorship Tiers](SPONSORS.md)
- [Competitive Analysis](docs/COMPETITION.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [API Usage](docs/USAGE.md)
- [Performance Benchmarks](docs/proof/benchmarks_summary.md)
- [Entropy Source Validation](docs/ESV_README.md)

---

<div align="center">

### Fairness you can prove. On-chain. Cryptographically.

**[GitHub](https://github.com/pipavlo82/r4-monorepo) • [PyPI](https://pypi.org/project/r4sdk/) • [Docker Hub](https://hub.docker.com/r/pipavlo/r4-local-test)**

v1.0.0-demo | [⬆ Back to top](#-re4ctor--the-nuclear-core-of-randomness)

</div>

---


---

## 🌐 RE4CTOR SaaS API Gateway

**Hosted gateway in front of RE4CTOR Core RNG and VRF.**
If you don’t want to run the full monorepo stack locally, you can use the hosted SaaS endpoint.

- 🔗 GitHub: https://github.com/pipavlo82/r4-saas-api
- 🌍 Endpoint: `https://api.re4ctor.xyz` (dev: `http://localhost:8082`)
- 🔑 Auth: `X-API-Key: demo` (dev)

### Quickstart (local dev)

```bash
git clone https://github.com/pipavlo82/r4-saas-api.git
cd r4-saas-api
cp .env.example .env
docker compose up -d --build

curl -s http://127.0.0.1:8082/v1/health
curl -s -H "X-API-Key: demo" "http://127.0.0.1:8082/v1/random?n=16&fmt=hex"
curl -s -H "X-API-Key: demo" "http://127.0.0.1:8082/v1/vrf?sig=ecdsa" | jq .
The SaaS gateway exposes:

GET /v1/health

GET /v1/random

GET /v1/vrf?sig=ecdsa

POST /v1/verify (ECDSA signature verification helper)
