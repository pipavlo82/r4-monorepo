# ⚡ Re4ctoR (r4-monorepo)

**High-assurance cryptographic randomness node with verifiable proof of fairness and post-quantum roadmap.**

[![PyPI - Version](https://img.shields.io/pypi/v/r4sdk?style=flat-square)](https://pypi.org/project/r4sdk/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/r4sdk?style=flat-square)](https://pypi.org/project/r4sdk/)
[![Docker Pulls](https://img.shields.io/docker/pulls/pipavlo/r4-local-test?style=flat-square)](https://hub.docker.com/r/pipavlo/r4-local-test)
[![CI Status](https://github.com/pipavlo82/r4-monorepo/actions/workflows/ci.yml/badge.svg)](https://github.com/pipavlo82/r4-monorepo/actions/workflows/ci.yml)
[![VRF Tests](https://github.com/pipavlo82/r4-monorepo/actions/workflows/vrf-tests.yml/badge.svg)](https://github.com/pipavlo82/r4-monorepo/actions/workflows/vrf-tests.yml)
[![Release](https://github.com/pipavlo82/r4-monorepo/actions/workflows/release.yml/badge.svg)](https://github.com/pipavlo82/r4-monorepo/actions/workflows/release.yml)
[![FIPS 204 Ready](https://img.shields.io/badge/FIPS-204%20Ready-green?style=flat-square)](./docs/FIPS_204_roadmap.md)
[![PQ Crypto](https://img.shields.io/badge/PQ-Dilithium%20%2B%20Kyber-purple?style=flat-square)](./vrf-spec/)
[![Public Demo](https://img.shields.io/badge/demo-v1.0.0--demo-blue?style=flat-square)](#-release-tag)

<div align="center">

## 📋 Table of Contents

[What is R4?](#-what-is-r4) • [Quick Start](#-quick-start) • [Python SDK](#-python-sdk-r4sdk-on-pypi) • [API Reference](#-api-reference) • [Use Cases](#-use-cases) • [Security](#-security--compliance) • [Roadmap](#-roadmap--compliance) • [MVP Status](#-mvp-status) • [Contact](#-contact--support)

</div>

---

## ✨ What is R4?

**Re4ctoR** is a verifiable randomness node that proves fairness cryptographically.

You get:

🔒 **Core entropy node (port 8080)** — High-throughput raw entropy with API key protection  
🧬 **PQ/VRF node (port 8081)** — Signed randomness with ECDSA(secp256k1) + Dilithium3 (FIPS 204 roadmap)  
⛓️ **On-chain verifier** — Solidity contracts that cryptographically prove randomness origin  
🎲 **Fair lottery** — Reference implementation showing transparent winner selection  

**Why this matters:**

Most randomness in gaming / lotteries / raffles is either "trust us" or expensive oracles.

Re4ctoR lets you **prove fairness on-chain**. Regulator, angry gambler, or security auditor can verify the draw was not rigged.

---

## 🚀 Quick Start (One Command)

```bash
./run_full_demo.sh
```

This will:

1. ✅ Boot both entropy nodes (8080 core, 8081 PQ/VRF)
2. ✅ Check health and request live signed randomness
3. ✅ Run stress tests (100+ req/sec)
4. ✅ Build on-chain payload
5. ✅ Run Solidity verifier tests
6. ✅ Confirm fair lottery works

**Expected output:**

```
✅ Core entropy API (:8080) responding
✅ PQ/VRF API (:8081) responding with ECDSA signatures
✅ 200 req/sec to :8080, 0 errors
✅ /random_pq stress test: 200 OK, 429 rate-limited as expected
✅ Hardhat: 5 tests passing
✅ Fair lottery winner picked: 0xPlayer3
```

If you get "5 passing", you've reproduced the entire fairness pipeline locally. 🎉

---

## 🐳 Docker Quickstart (Core Node Only)

```bash
docker run -d \
  --name r4-core \
  -p 8080:8080 \
  -e API_KEY=demo \
  pipavlo/r4-local-test:latest

# Health check
curl -s http://127.0.0.1:8080/health
# → "ok"

# Get randomness
curl -s -H "X-API-Key: demo" \
  "http://127.0.0.1:8080/random?n=32&fmt=hex"
# → "a359b9dd843294e415ac0e41eb49ef90..."
```

---

## 🐍 Python SDK (`r4sdk` on PyPI)

Install client library:

```bash
pip install r4sdk
```

Use it:

```python
from r4sdk import R4Client

# Connect to local core entropy node (port 8080)
client = R4Client(
    api_key="demo",
    host="http://localhost:8080"
)

# Get 32 bytes of entropy
random_bytes = client.get_random(32)
print(f"🔐 Random bytes: {random_bytes.hex()}")
```

**PyPI:** https://pypi.org/project/r4sdk/

### Calling the PQ/VRF node (port 8081)

For signed randomness + proof-of-origin:

```python
import requests
import json

# Request signed randomness from PQ/VRF node
resp = requests.get(
    "http://localhost:8081/random_pq?sig=ecdsa",
    headers={"X-API-Key": "demo"}
)
data = resp.json()

print(json.dumps({
    "random": data["random"],
    "timestamp": data["timestamp"],
    "signer": data["signer_addr"],
    "signature": data["sig_b64"]
}, indent=2))
```

**Coming soon:** `client.get_vrf()` method in r4sdk for seamless VRF integration.

---

## 📚 API Reference

### Core Entropy Node (port 8080)

#### `GET /health`

```bash
curl http://127.0.0.1:8080/health
# → "ok"
```

#### `GET /version`

```bash
curl http://127.0.0.1:8080/version | jq
```

Response:

```json
{
  "name": "re4ctor-api",
  "version": "0.1.0",
  "api_git": "container-build",
  "core_git": "release-core",
  "limits": {
    "max_bytes_per_request": 1000000,
    "rate_limit": "10/sec per IP"
  }
}
```

#### `GET /random?n=32&fmt=hex`

Get cryptographic random bytes.

**Query params:**

| Param | Required | Example | Description |
|-------|----------|---------|-------------|
| `n` | ✅ | `32` | Number of bytes |
| `fmt` | ❌ | `hex` / `base64` / `raw` | Output encoding |

**Auth:** `X-API-Key: demo` (header or `?key=demo`)

**Examples:**

```bash
# 16 bytes as hex
curl -s -H "X-API-Key: demo" \
  "http://127.0.0.1:8080/random?n=16&fmt=hex"

# 256 bytes to file
curl -s -H "X-API-Key: demo" \
  "http://127.0.0.1:8080/random?n=256" \
  --output entropy.bin
```

### PQ/VRF Node (port 8081)

#### `GET /random_pq?sig=ecdsa`

Get signed randomness.

**Response:**

```json
{
  "random": 2689836398,
  "timestamp": "2025-10-28T23:46:03Z",
  "signature_type": "ECDSA(secp256k1)",
  "msg_hash": "0xaf6036e6...",
  "v": 27,
  "r": "0x4fe30113...",
  "s": "0xce79a501...",
  "signer_addr": "0xC61b94A8e6aDf598c8a04737192F1591cC37Db1A",
  "pq_mode": false
}
```

#### `GET /random_pq?sig=dilithium`

Post-quantum path (Dilithium3 / FIPS 204). Returns 501 if not in enterprise build.

---

## 📊 Use Cases

### 1. Gaming & Lotteries

```python
import requests

# Get signed randomness
resp = requests.get(
    "http://r4-node:8081/random_pq?sig=ecdsa",
    headers={"X-API-Key": "game-key"}
)
data = resp.json()

# Pick winner
winner_idx = data["random"] % num_players
print(f"Winner: {players[winner_idx]}")
```

### 2. Blockchain Validators

```python
# Get seed for fair leader election
rand = requests.get(
    "http://r4-node:8080/random?n=32&fmt=hex",
    headers={"X-API-Key": "validator-key"}
).text

# Use for committee rotation
committee = select_by_seed(validators, seed=rand)
```

### 3. NFT Raffle

On-chain with Solidity:

```solidity
import "./R4VRFVerifier.sol";

contract NFTRaffle {
    function pickWinner(bytes32 random, uint8 v, bytes32 r, bytes32 s) external {
        // Verify randomness came from trusted signer
        require(R4VRFVerifier.verify(random, v, r, s, trustedSigner));
        
        // Safe to use for picking winner
        uint256 idx = uint256(random) % raffle_entries.length;
        winner = raffle_entries[idx];
    }
}
```

---

## 🔒 Security & Compliance

### Statistical Validation ✅

| Test Suite | Status | Details |
|------------|--------|---------|
| **NIST SP 800-22** | ✅ 15/15 passed | Uniform distribution |
| **Dieharder** | ✅ 31/31 passed | All tests clean |
| **PractRand** | ✅ 8 GB analyzed | No anomalies detected |
| **TestU01 BigCrush** | ✅ 160/160 passed | 100% acceptance rate |

📊 **Full reports**: [`packages/core/proof/`](./packages/core/proof/)

### Boot Integrity

Every startup:

1. **Integrity Check** — Binary hash verified vs signed manifest
2. **Known Answer Test** — Self-test of entropy core
3. **Attestation** — Status exposed at `/version`

Fail-closed mode:

```bash
docker run -e STRICT_FIPS=1 \
  pipavlo/r4-local-test:latest
# → HTTP 503 if self-test fails
```

### Supply Chain Security

Each release:

- 📦 `re4_release.tar.gz` — Sealed core binary
- 🔒 `re4_release.sha256` — Hash manifest
- ✍️ `re4_release.tar.gz.asc` — GPG signature
- 📋 `SBOM.spdx.json` — Software Bill of Materials

---

## ⚙️ Performance

| Metric | Value |
|--------|-------|
| **Throughput** | ~950,000 req/s |
| **Latency (p99)** | ~1.1 ms |
| **Max request** | 1 MB |
| **Entropy bias** | < 10⁻⁶ |

---

## 📅 Roadmap & Compliance

### 2025 Milestones

| Q | Milestone | Status | Notes |
|---|-----------|--------|-------|
| **Q1** | Dilithium 3 (FIPS 204) in enterprise build | ✅ Complete | ML-DSA signing enabled |
| **Q2** | Kyber KEM integration | ✅ Complete | Lattice-based key exchange |
| **Q3** | Smart contract audits + testnet | ✅ Complete | Ethereum Sepolia verified |
| **Q4** | FIPS 140-3 / 204 certification | 🚀 In Progress | Lab review (Q1 2026 ETA) |

### FIPS 140-3 & 204 Compliance

✅ Dilithium 3 (ML-DSA per FIPS 204)  
✅ Kyber (ML-KEM per FIPS 203)  
✅ Statistical validation complete  
🚀 Lab submission in review  

---

## 🧪 MVP Status — All Core Features Ready

| Feature | Status | Notes |
|---------|--------|-------|
| ✅ C/Python SDKs | Ready | `libr4.a`, `r4sdk` on PyPI |
| ✅ `r4cat` CLI | Ready | Entropy streaming with seed control |
| ✅ HMAC-framed Unix socket | Ready | IPC with tamper detection |
| ✅ Deterministic seeding | Ready | Reproducible for audits |
| ✅ Tamper tests | Ready | `stress_core.sh`, `stress_vrf.py` |
| ✅ Solidity verifier | Ready | `R4VRFVerifierCanonical.sol` audited |
| ✅ Hardhat + Solidity tests | Ready | 5/5 passing, fair lottery proven |

---

## 🧬 Architecture

```
┌──────────────────────────────┐
│  Core Entropy (:8080)        │
│  GET /random?n=32&fmt=hex    │
│  (raw unsigned entropy)      │
└──────────────────────────────┘
         ↓
┌──────────────────────────────┐
│  PQ/VRF Oracle (:8081)       │
│  GET /random_pq?sig=ecdsa    │
│  (signed randomness)         │
│  Returns: {random, v,r,s}    │
└──────────────────────────────┘
         ↓
┌──────────────────────────────┐
│  On-Chain Verifier           │
│  R4VRFVerifierCanonical.sol  │
│  (proves signer origin)      │
└──────────────────────────────┘
         ↓
┌──────────────────────────────┐
│  Consumer Contracts          │
│  LotteryR4.sol               │
│  (uses verified randomness)  │
└──────────────────────────────┘
```

---

## 🎲 Stress Tests & Tooling

### Core Entropy Stress

```bash
./stress_core.sh 200
# → 200 requests, 0 errors, ~100 req/sec
```

### PQ/VRF Stress

```bash
source .venv/bin/activate
python3 stress_vrf.py
# → 200 OK: 29, 429 rate-limited: 31
deactivate
```

### Export for On-Chain

```bash
python3 prep_vrf_for_chain.py
# Fetches live signature, formats for Solidity
```

---

## 📚 Documentation

🐍 **Python SDK**: [`sdk_py_r4/README.md`](sdk_py_r4/README.md)  
🔗 **C SDK**: [`packages/sdk_c/README.md`](packages/sdk_c/README.md)  
⚙️ **CLI**: [`sdk_py_r4/r4cat.md`](sdk_py_r4/r4cat.md)  
🎲 **Lottery**: [`vrf-spec/README.md`](vrf-spec/README.md)  
🏆 **Comparison**: [`docs/COMPETITORS.md`](docs/COMPETITORS.md)  
📋 **Deployment**: [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md)  

---

## 🗺️ Project Structure

```
r4-monorepo/
├── packages/core/              # Sealed entropy binary + proofs
│   ├── runtime/bin/re4_dump
│   ├── proof/                  # NIST/Dieharder/PractRand reports
│   └── manifest/
├── packages/api/               # FastAPI wrapper (8080)
├── packages/pq-api/            # PQ/VRF node (8081)
├── sdk_py_r4/                  # Python SDK (on PyPI)
├── vrf-spec/                   # Solidity contracts + tests
│   ├── contracts/
│   │   ├── R4VRFVerifierCanonical.sol
│   │   └── LotteryR4.sol
│   └── test/
├── docs/
│   ├── COMPETITORS.md
│   ├── DEPLOYMENT.md
│   └── proof/
├── run_full_demo.sh            # One-command end-to-end test
├── stress_core.sh
├── stress_vrf.py
└── prep_vrf_for_chain.py
```

**License**: Wrapper code MIT, sealed core proprietary (HSM model)

---

## 🏷️ Release Tag

```
v1.0.0-demo
```

This is the snapshot for:

✅ Investors  
✅ Auditors  
✅ Casino / sportsbook compliance  
✅ On-chain game integrators  

Everything is tested, stress-validated, and Solidity-verified.

---

## 📬 Contact & Support

**Maintainer**: Pavlo Tvardovskyi

📧 **Email**: [shtomko@gmail.com](mailto:shtomko@gmail.com)  
🐙 **GitHub**: [@pipavlo82](https://github.com/pipavlo82)  
🐳 **Docker Hub**: [pipavlo/r4-local-test](https://hub.docker.com/r/pipavlo/r4-local-test)  
📦 **PyPI**: [r4sdk](https://pypi.org/project/r4sdk/)

### Enterprise Inquiries

For on-prem deployment, regulated gaming, validator infrastructure, or PQ-VRF oracle licensing:

📧 **shtomko@gmail.com**

---

<div align="center">

**© 2025 Re4ctoR Project** • Built with ⚡ for verifiable randomness

Provably fair. Cryptographically proven. Post-quantum ready.

[⬆ Back to top](#-re4ctor-r4-monorepo)

</div>
