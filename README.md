# ☢️ RE4CTOR — The Nuclear Core of Randomness

**Verifiable entropy • Post-quantum VRF • On-chain fairness you can prove**

[![PyPI](https://img.shields.io/pypi/v/r4sdk?label=r4sdk%20on%20PyPI&style=flat-square)](https://pypi.org/project/r4sdk/)
[![Docker Pulls](https://img.shields.io/docker/pulls/pipavlo/r4-local-test?style=flat-square)](https://hub.docker.com/r/pipavlo/r4-local-test)
[![VRF Tests](https://github.com/pipavlo82/r4-monorepo/actions/workflows/vrf-tests.yml/badge.svg)](https://github.com/pipavlo82/r4-monorepo/actions/workflows/vrf-tests.yml)
[![CI Status](https://github.com/pipavlo82/r4-monorepo/actions/workflows/ci.yml/badge.svg)](https://github.com/pipavlo82/r4-monorepo/actions/workflows/ci.yml)
[![FIPS 204 Ready](https://img.shields.io/badge/FIPS-204%20Ready-green?style=flat-square)](docs/FIPS_204_roadmap.md)
[![Release](https://img.shields.io/github/v/release/pipavlo82/r4-monorepo?include_prereleases&style=flat-square)](https://github.com/pipavlo82/r4-monorepo/releases)

<div align="center">

## 📋 Table of Contents

[Overview](#-overview) • [One-Command Demo](#-one-command-demo) • [Docker Quickstart](#-docker-quickstart-8080) • [Python SDK](#-python-sdk) • [PQ/VRF Node](#-pqvrf-node-8081) • [On-Chain Verifier](#-on-chain-verifier) • [Security](#-security--proofs) • [Roadmap](#-roadmap-2025) • [Competition](#-r4-vs-competitors) • [Contributing](#contributing) • [Contact](#-contact)

</div>

---

## 🧠 Overview

RE4CTOR is a **sealed entropy appliance + verifiable randomness pipeline**.

- ☢️ **Core entropy node (:8080)** — FIPS-verified sealed binary via FastAPI `/random`
- 🔐 **PQ/VRF node (:8081)** — ECDSA + Dilithium3 signed randomness  
- 🧬 **Solidity verifiers** — `R4VRFVerifierCanonical.sol` proves origin on-chain
- 🎲 **LotteryR4.sol** — Fair lottery reference implementation
- 🐍 **Python SDK** — `pip install r4sdk` for backends/validators/bots

**Use cases:** Casinos, sportsbooks, NFT raffles, validator rotation, ZK-rollup seeding, "prove to regulators we didn't rig this."

---

## 🚀 One-Command Demo

```bash
./run_full_demo.sh
```

Boots both nodes, stress-tests them, exports signed randomness, runs Solidity verification. You'll see:

```
✅ Core entropy API (:8080) alive
✅ PQ/VRF API (:8081) returning ECDSA signatures
✅ 100 req/sec to :8080, 0 errors
✅ :8081 stress showing 200 OK vs 429 rate-limited
✅ Hardhat: 5 tests passing
✅ LotteryR4 picks winner on-chain
```

If you see "5 passing", you've proven fairness locally. 🎉

---

## 🐳 Docker Quickstart (:8080)

```bash
docker run -d \
  --name r4-core \
  -p 8080:8080 \
  -e API_KEY=demo \
  pipavlo/r4-local-test:latest

# Health check
curl http://127.0.0.1:8080/health
# → "ok"

# Get randomness
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

```bash
curl -H "X-API-Key: demo" \
  "http://localhost:8081/random_pq?sig=ecdsa" | jq
```

**Response:**
```json
{
  "random": 2689836398,
  "timestamp": "2025-10-28T23:46:03Z",
  "v": 27,
  "r": "0x4fe30113...",
  "s": "0xce79a501...",
  "signer_addr": "0xC61b94A8e6aDf598c8a04737192F1591cC37Db1A",
  "pq_mode": false
}
```

Enterprise build (`?sig=dilithium`) returns Dilithium3/ML-DSA (FIPS 204) signatures.

---

## 🧱 On-Chain Verifier

Solidity contracts under `vrf-spec/contracts/`:

**R4VRFVerifierCanonical.sol** — Verifies ECDSA signature + signer address  
**LotteryR4.sol** — Fair lottery using verified randomness

```bash
cd vrf-spec
npx hardhat test
# → 5 passing
```

Demonstrates:
- ✅ Valid signed randomness → winner picked
- ❌ Tampered randomness → reverted

---

## 🛡️ Security & Proofs

**Statistical validation** (packages/core/proof/):
- NIST SP 800-22: 15/15 ✅
- Dieharder: 31/31 ✅
- PractRand: 8 GB analyzed ✅
- TestU01 BigCrush: 160/160 ✅

**Performance** (docs/proof/benchmarks_summary.md):
- Throughput: ~950,000 req/s
- Latency p99: ~1.1 ms
- Entropy bias: <10⁻⁶

**Startup hardening:**
- Binary hash verified against signed manifest
- Known-answer self-test must pass
- STRICT_FIPS=1 → fail-closed mode

**Supply chain:**
- re4_release.tar.gz
- re4_release.sha256
- re4_release.tar.gz.asc (GPG)
- SBOM.spdx.json

---

## 📅 Roadmap 2025

| Q | Milestone | Status |
|---|-----------|--------|
| Q1 | Dilithium3 (ML-DSA / FIPS 204) signing | ✅ Done |
| Q2 | Kyber KEM integration | ✅ Done |
| Q3 | Solidity audits + testnet | ✅ Done |
| Q4 | FIPS 140-3 / 204 lab submission | 🚀 In progress |

---

## 🥊 R4 vs Competitors

Full breakdown: [docs/COMPETITORS.md](docs/COMPETITORS.md)

| Feature | R4 | Chainlink | drand | AWS HSM |
|---------|----|---------|----|---------|
| **Post-Quantum** | ✅ Dilithium3 | ❌ | ❌ | ⚠️ |
| **Latency** | **<1ms** | 30-120s | 3-30s | 10-50ms |
| **Cost** | self-hosted | pay-per-req | free | $$$$ |
| **On-chain Verify** | ✅ | ✅ | ⚠️ | ❌ |
| **Self-hosted** | ✅ | ❌ | ✅ | ⚠️ |
| **Throughput** | 950k/s | limited | limited | 50k/s |

**Decision:** Need speed + verifiable proof? → **R4**. Need decentralization? → **Chainlink/drand**.

---

## 🗺️ Repo Map

```
r4-monorepo/
├── README.md                     (← you are here)
├── CONTRIBUTING.md              (how to help)
├── SPONSORS.md                  (enterprise)
├── run_full_demo.sh             (one-command test)
├── stress_core.sh               (load test :8080)
├── stress_vrf.py                (load test :8081)
│
├── packages/core/
│   ├── runtime/bin/re4_dump     (sealed entropy core)
│   ├── proof/                   (Dieharder/PractRand/BigCrush results)
│   └── manifest/                (sha256, GPG sig, SBOM)
│
├── vrf-spec/
│   ├── contracts/
│   │   ├── R4VRFVerifierCanonical.sol
│   │   └── LotteryR4.sol
│   ├── test/
│   │   ├── lottery.js
│   │   ├── verify.js
│   │   └── verify_r4_canonical.js
│   ├── hardhat.config.js
│   └── package.json
│
├── sdk_py_r4/
│   ├── r4sdk/                   (Python client)
│   ├── test_r4sdk.py
│   └── setup.py
│
└── docs/
    ├── USAGE.md
    ├── DEPLOYMENT.md
    ├── COMPETITORS.md           (← positioning)
    ├── FIPS_204_roadmap.md
    └── proof/benchmarks_summary.md
```

---

## 📬 Contact

**Maintainer:** Pavlo Tvardovskyi  
📧 **Email:** [shtomko@gmail.com](mailto:shtomko@gmail.com)  
🐙 **GitHub:** [@pipavlo82](https://github.com/pipavlo82)  
🐳 **Docker Hub:** [pipavlo/r4-local-test](https://hub.docker.com/r/pipavlo/r4-local-test)  
📦 **PyPI:** [r4sdk](https://pypi.org/project/r4sdk/)

### Enterprise / Regulated Gaming / Validator Rotation

→ Email `shtomko@gmail.com` with subject **"R4 ENTERPRISE"**

---

## 📚 Resources

- [Contributing Guide](CONTRIBUTING.md)
- [Sponsorship Tiers](SPONSORS.md)
- [Competitive Analysis](docs/COMPETITORS.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [API Usage](docs/USAGE.md)
- [Performance Benchmarks](docs/proof/benchmarks_summary.md)

---

<div align="center">

**Tag:** `v1.0.0-demo` — Full-stack reproducible demo  
**Status:** Production-ready with FIPS 204 roadmap

[⬆ Back to top](#-re4ctor--the-nuclear-core-of-randomness)

</div>
