# ⚡ r4-monorepo — entropy appliance & verifiable randomness API

[![docker pulls](https://img.shields.io/docker/pulls/pipavlo/r4-local-test?style=flat-square)](https://hub.docker.com/r/pipavlo/r4-local-test)
[![image size](https://img.shields.io/docker/image-size/pipavlo/r4-local-test/latest?style=flat-square)](https://hub.docker.com/r/pipavlo/r4-local-test)
[![re4ctor-ci](https://github.com/pipavlo82/r4-monorepo/actions/workflows/ci.yml/badge.svg)](https://github.com/pipavlo82/r4-monorepo/actions/workflows/ci.yml)
[![sanity-check](https://img.shields.io/badge/sanity--check-passing-brightgreen?style=flat-square)](https://github.com/pipavlo82/r4-monorepo/actions/workflows/public-sanity.yml)
[![VRF Contract Tests](https://github.com/pipavlo82/r4-monorepo/actions/workflows/vrf-tests.yml/badge.svg)](https://github.com/pipavlo82/r4-monorepo/actions/workflows/vrf-tests.yml)
---

## 🧠 Overview

**r4** is a high-entropy appliance and verifiable randomness API.

It delivers:
- 🔒 **Sealed entropy core (`re4_dump`)** — closed-source, statistically verified via Dieharder / PractRand / BigCrush, shipped as a signed binary.  
- 🌐 **Hardened FastAPI layer** — key-protected `/random` endpoint for secure entropy distribution over HTTP (Docker or systemd).

The repo also tracks the **Post-Quantum VRF roadmap** (`vrf-spec/`) — future attested randomness for proof-of-stake rotation, zk-rollup seeding, and lotteries.

<div align="center">

# ⚡ R4 Entropy Appliance

**High-assurance cryptographic randomness API with post-quantum VRF roadmap**

[![Docker Hub](https://img.shields.io/badge/docker-pipavlo%2Fr4--local--test-blue?logo=docker)](https://hub.docker.com/r/pipavlo/r4-local-test)
[![License](https://img.shields.io/badge/license-Proprietary%20Core-red)](./LICENSE)
[![FIPS Ready](https://img.shields.io/badge/FIPS-140--3%20Ready-green)](./packages/core/proof/)
[![PQ Crypto](https://img.shields.io/badge/PQ-Kyber%20%2B%20Dilithium-purple)](./vrf-spec/)

[Quickstart](#-quickstart) • [API Docs](#-api-reference) • [Security](#-security--compliance) • [Roadmap](#-pq-vrf-roadmap) • [Contact](#-contact)

</div>

---

## 🎯 What is R4?

**R4** is a hardened entropy service delivering cryptographically secure randomness through a simple HTTP API. Designed for:

- 🔑 **Key generation** — TLS certificates, signing keys, secrets
- 🎲 **Gaming & Lotteries** — Provably fair randomness
- ⛓️ **Blockchain validators** — Leader election, PoS rotation
- 🔐 **High-security systems** — HSM-grade entropy appliance

### Architecture

```
┌─────────────────────────────────────┐
│   FastAPI (Rate-limited HTTP API)   │
│   /health  /version  /random        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Sealed Entropy Core (re4_dump)    │
│   • FIPS self-test on boot          │
│   • Integrity-verified binary       │
│   • Statistical validation passed   │
└─────────────────────────────────────┘
```

**Trust Model**: HSM-style sealed core + transparent API wrapper + continuous attestation

---

## 🚀 Quickstart

### Prerequisites
- 🐳 Docker (Desktop or Engine)
- 🔌 Port 8080 available

### Run in 30 seconds

```bash
docker run -d \
  --name r4test \
  -p 8080:8080 \
  -e API_KEY=demo \
  pipavlo/r4-local-test:latest
```

### Verify it works

```bash
# Health check
curl http://127.0.0.1:8080/health
# → "ok"

# Get version + integrity status
curl http://127.0.0.1:8080/version | jq
```

**Expected output:**
```json
{
  "name": "re4ctor-api",
  "version": "0.1.0",
  "integrity": "verified",
  "selftest": "pass",
  "mode": "sealed"
}
```

### Request random bytes

```bash
# 32 bytes as hex (64 hex chars)
curl -H "x-api-key: demo" \
  "http://127.0.0.1:8080/random?n=32&fmt=hex"

# 64 raw bytes to file
curl -H "x-api-key: demo" \
  "http://127.0.0.1:8080/random?n=64" \
  --output random.bin
```

---

## 📘 API Reference

### `GET /health`
**Returns**: `"ok"` if service is alive

```bash
curl http://127.0.0.1:8080/health
```

---

### `GET /version`
**Returns**: Build info, integrity status, self-test results

```bash
curl http://127.0.0.1:8080/version
```

**Response fields:**
- `integrity`: `"verified"` → binary hash matches signed manifest
- `selftest`: `"pass"` | `"degraded"` | `"fail"` → startup KAT result
- `mode`: `"sealed"` | `"fallback"` | `"blocked"` → operational state

---

### `GET /random`
**Returns**: Cryptographically secure random bytes

| Parameter | Required | Example | Description |
|-----------|----------|---------|-------------|
| `n` | ✅ | `32` | Number of bytes (max 1,000,000) |
| `fmt` | ❌ | `hex` / `base64` | Output encoding (default: raw) |
| `x-api-key` | ✅ | `demo` | API key (header or query `?key=`) |

**Examples:**

```bash
# 16 bytes as hex
curl -H "x-api-key: demo" \
  "http://127.0.0.1:8080/random?n=16&fmt=hex"

# 256 bytes as base64
curl -H "x-api-key: demo" \
  "http://127.0.0.1:8080/random?n=256&fmt=base64"
```

**Error handling:**
```bash
# Invalid key
curl -i -H "x-api-key: WRONG" \
  "http://127.0.0.1:8080/random?n=16"
# → HTTP/1.1 401 Unauthorized
```

---

## 🔗 On-chain Verification (VRF Path)

Re4ctoR is not just "here's some random bytes."  
It also includes an **on-chain verification pipeline (VRF)**.

This repo ships a reference Solidity contract:  
**`vrf-spec/contracts/R4VRFVerifier.sol`**

### What it does

**1. `verify(randomness, signature, signer)`**
   - Recomputes the signed message hash  
   - Recovers the signer via ECDSA  
   - Confirms that the randomness was produced by the expected Re4ctoR node  

**2. `submitRandom(randomness)`**
   - Emits an event `RandomnessVerified(sender, randomness)`  
   - Lets consumer contracts (lotteries, games, DeFi apps) react to verified randomness  

### Included Hardhat Test

**`vrf-spec/test/verify.js`**

This test:
- Generates a random value (`bytes32`)
- Signs it with a local Ethereum key (simulating Re4ctoR)
- Verifies it on-chain via the Solidity contract
- Confirms the event emission

### Run Locally

```bash
cd vrf-spec
npm install
npx hardhat compile
npx hardhat test
```

**✅ Result:**

```
R4VRFVerifier
  ✔ verifies a valid signature from the signer (424ms)
  ✔ emits event on submitRandom()

2 passing (448ms)
```

Re4ctoR can now generate randomness off-chain  
and **prove on-chain** that it was produced by a trusted signer.

This forms the **MVP of the Re4ctoR VRF**:

```
Off-chain entropy → ECDSA signature → On-chain verification
```

## 🔐 Security & Compliance

### Statistical Validation ✅

| Test Suite | Status | Details |
|------------|--------|---------|
| **NIST SP 800-22** | ✅ 15/15 passed | `p ≈ 0.5` uniformity |
| **Dieharder** | ✅ 31/31 passed | All tests clean |
| **PractRand** | ✅ 8 GB analyzed | No anomalies detected |
| **TestU01 BigCrush** | ✅ 160/160 passed | 100% acceptance rate |

📊 **Full reports**: [`packages/core/proof/`](./packages/core/proof/)

---

### Boot Integrity & Self-Test

Every container startup performs:

1. **Integrity Check**  
   Binary hash verified against signed manifest. Mismatch → service blocked.

2. **Known Answer Test (KAT)**  
   Entropy core executed with timeout. Failure → degraded mode or block.

3. **Attestation**  
   Current state exposed at `/version` for remote monitoring.

**Fail-closed mode:**
```bash
docker run -d -e STRICT_FIPS=1 \
  pipavlo/r4-local-test:latest
# → HTTP 503 if selftest ≠ "pass"
```

---

### Supply Chain Security

Each release includes:

- 📦 `re4_release.tar.gz` — Sealed core binary
- 🔒 `re4_release.sha256` — Hash manifest
- ✍️ `re4_release.tar.gz.asc` — GPG signature
- 📋 `SBOM.spdx.json` — Software Bill of Materials

**Verify release:**
```bash
sha256sum -c re4_release.sha256
gpg --verify re4_release.tar.gz.asc
```

---

## ⚙️ Performance

| Metric | Value |
|--------|-------|
| **Throughput** | ~950,000 req/s |
| **Latency (p99)** | ~1.1 ms |
| **Max request size** | 1 MB |
| **Entropy bias** | < 10⁻⁶ deviation |

📈 **Benchmarks**: [`docs/proof/benchmarks_summary.md`](./docs/proof/benchmarks_summary.md)

---

## 🏭 Production Deployment

### Docker + systemd

```ini
[Unit]
Description=R4 Entropy API
After=network-online.target

[Service]
Restart=always
ExecStart=/usr/bin/docker run --rm \
  -p 8080:8080 \
  -e API_KEY=${R4_API_KEY} \
  --name r4-entropy \
  pipavlo/r4-local-test:latest
ExecStop=/usr/bin/docker stop r4-entropy

[Install]
WantedBy=multi-user.target
```

### Best Practices

✅ Run behind reverse proxy (nginx, traefik, API gateway)  
✅ Use strong `API_KEY` from secure vault  
✅ Monitor `/version` endpoint for integrity drift  
✅ Rate limit per IP at reverse proxy level  
✅ Internal-only exposure (no public internet)  

---

## 🔭 PQ VRF Roadmap

**Target**: Q1–Q2 2025  
**Endpoint**: `/vrf` (Verifiable Random Function)

### Planned Response

```json
{
  "random": "<entropy_bytes>",
  "signature": "<dilithium_sig>",
  "public_key": "<node_pubkey>",
  "verified": true,
  "timestamp": "2025-01-15T12:34:56Z"
}
```

### Features

- 🔐 **Post-quantum signatures** (Dilithium-3)
- 🔒 **Key encapsulation** (Kyber-1024)
- ✅ **Verifiable by anyone** — prove non-manipulation
- ⚡ **Low latency** — beat Chainlink VRF on speed

### Use Cases

| Industry | Application |
|----------|-------------|
| **Blockchain** | Validator rotation, leader election |
| **ZK-Rollups** | Sequencer seed, prover selection |
| **Gaming** | Anti-cheat randomness, loot drops |
| **Lotteries** | Provably fair draws, NFT mints |

📋 **Spec draft**: [`vrf-spec/`](./vrf-spec/)

---

## 🧰 What's Inside

```
r4-monorepo/
├── packages/
│   ├── core/               # Sealed entropy binary + proofs
│   │   ├── runtime/bin/re4_dump
│   │   └── proof/          # Statistical validation reports
│   └── api/                # FastAPI wrapper (open-source)
├── vrf-spec/               # Post-quantum VRF specification
├── docs/
│   ├── USAGE.md
│   └── DEPLOYMENT.md
├── SBOM.spdx.json
└── LICENSE
```

**License**: Wrapper code public, sealed core proprietary (HSM model)

---

## 📊 Use Cases

### 1. Blockchain Validators
```python
import requests

response = requests.get(
    "http://r4-node:8080/random?n=32&fmt=hex",
    headers={"x-api-key": "validator-secret"}
)
seed = response.text
# Use for leader election, committee selection
```

### 2. Key Generation
```bash
# Generate 256-bit AES key
curl -H "x-api-key: prod" \
  "http://r4-internal:8080/random?n=32&fmt=base64" \
  | base64 -d > aes256.key
```

### 3. Gaming RNG
```javascript
const response = await fetch(
  'http://r4-api:8080/random?n=8&fmt=hex',
  { headers: { 'x-api-key': process.env.R4_KEY } }
);
const hex = await response.text();
const roll = parseInt(hex.substring(0, 8), 16) % 100 + 1;
// Fair dice roll: 1-100
```

---

## 📬 Contact

**Maintainer**: Pavlo Tvardovskyi  
**Email**: [shtomko@gmail.com](mailto:shtomko@gmail.com)  
**GitHub**: [@pipavlo82](https://github.com/pipavlo82)  
**Docker Hub**: [pipavlo/r4-local-test](https://hub.docker.com/r/pipavlo/r4-local-test)

### Enterprise Inquiries

For custom deployments, SLA agreements, or PQ-VRF early access:  
📧 **shtomko@gmail.com**

---

## 🏷️ Tags

`#entropy` `#fips` `#pqcrypto` `#rng` `#verifiable` `#docker` `#hsm` `#cybersecurity` `#blockchain` `#web3`

---

<div align="center">

**© 2025 Re4ctoR Project** • Built with ⚡ for high-assurance randomness

[⬆ Back to top](#-r4-entropy-appliance)

</div>
