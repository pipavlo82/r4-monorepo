# ⚡ r4-monorepo

**High-assurance cryptographic randomness API with post-quantum VRF roadmap**

[![Docker Pulls](https://img.shields.io/docker/pulls/pipavlo/r4-local-test?style=flat-square)](https://hub.docker.com/r/pipavlo/r4-local-test)
[![Docker Image Size](https://img.shields.io/docker/image-size/pipavlo/r4-local-test/latest?style=flat-square)](https://hub.docker.com/r/pipavlo/r4-local-test)
[![CI Status](https://github.com/pipavlo82/r4-monorepo/actions/workflows/ci.yml/badge.svg)](https://github.com/pipavlo82/r4-monorepo/actions/workflows/ci.yml)
[![Sanity Check](https://img.shields.io/badge/sanity--check-passing-brightgreen?style=flat-square)](https://github.com/pipavlo82/r4-monorepo/actions/workflows/public-sanity.yml)
[![VRF Tests](https://github.com/pipavlo82/r4-monorepo/actions/workflows/vrf-tests.yml/badge.svg)](https://github.com/pipavlo82/r4-monorepo/actions/workflows/vrf-tests.yml)
[![Release](https://github.com/pipavlo82/r4-monorepo/actions/workflows/release.yml/badge.svg)](https://github.com/pipavlo82/r4-monorepo/actions/workflows/release.yml)

---

## 📋 Table of Contents

- [What is R4?](#-what-is-r4)
- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [API Reference](#-api-reference)
- [On-Chain VRF](#-on-chain-verification-vrf)
- [Use Cases](#-use-cases)
- [Security & Compliance](#-security--compliance)
- [Deployment](#-production-deployment)
- [Roadmap](#-pq-vrf-roadmap)
- [Project Structure](#-whats-inside)
- [R4 vs Competitors](./docs/COMPETITION.md) 

---

## 🎯 What is R4?

**r4** is an enterprise-grade entropy appliance delivering **cryptographically secure randomness** via HTTP API.

### Core Features

🔒 **Sealed Entropy Core (`re4_dump`)**
- Closed-source, statistically verified
- NIST SP 800-22, Dieharder, PractRand, TestU01 BigCrush certified
- Shipped as signed binary with integrity verification
- FIPS 140-3 ready

🌐 **Hardened FastAPI Layer**
- Key-protected `/random` endpoint
- Rate-limited, audit-logged
- Docker or systemd deployment
- Production-ready security

🔐 **On-Chain Verification (VRF)**
- ECDSA signature verification for off-chain randomness
- Reference Solidity contracts included
- Post-quantum roadmap (Dilithium + Kyber)

### Designed For

| Use Case | Application |
|----------|-------------|
| 🔑 **Cryptography** | TLS certificates, signing keys, secrets |
| 🎲 **Gaming & Lotteries** | Provably fair randomness |
| ⛓️ **Blockchain** | Validator rotation, leader election, PoS |
| 🏦 **Finance** | Key generation, random sampling |
| 🔐 **Enterprise** | HSM-grade entropy appliance |

---

## 🚀 Quick Start

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

# Get version + integrity status
curl http://127.0.0.1:8080/version | jq
```

**Expected response:**

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
# 32 bytes as hex
curl -H "x-api-key: demo" \
  "http://127.0.0.1:8080/random?n=32&fmt=hex"

# 256 bytes as base64
curl -H "x-api-key: demo" \
  "http://127.0.0.1:8080/random?n=256&fmt=base64"

# 64 raw bytes to file
curl -H "x-api-key: demo" \
  "http://127.0.0.1:8080/random?n=64" \
  --output random.bin
```

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────┐
│  FastAPI (Rate-limited HTTP API)                    │
│  /health  /version  /random                         │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│  Sealed Entropy Core (re4_dump)                     │
│  • FIPS 140-3 self-test on boot                     │
│  • Integrity-verified binary                        │
│  • Statistical validation (NIST/Dieharder/etc)      │
└─────────────────────────────────────────────────────┘
```

**Trust Model**: HSM-style sealed core + transparent API wrapper + continuous attestation

### Data Flow

```
[ Client ] 
    ↓
[ HTTP Request + API Key ]
    ↓
[ FastAPI Authentication ]
    ↓
[ Rate Limiter ]
    ↓
[ Re4ctoR Entropy Core ]
    ↓
[ Format Converter (hex/base64/raw) ]
    ↓
[ Audit Log ]
    ↓
[ HTTP Response ]
```

---

## 📘 API Reference

### `GET /health`

Simple liveness check.

```bash
curl http://127.0.0.1:8080/health
```

**Response**: `"ok"` (200 OK)

---

### `GET /version`

Build info, integrity status, and self-test results.

```bash
curl http://127.0.0.1:8080/version | jq
```

**Response fields:**

```json
{
  "name": "re4ctor-api",
  "version": "0.1.0",
  "integrity": "verified",
  "selftest": "pass",
  "mode": "sealed"
}
```

| Field | Values | Meaning |
|-------|--------|---------|
| `integrity` | `"verified"` / `"failed"` | Binary hash matches signed manifest |
| `selftest` | `"pass"` / `"degraded"` / `"fail"` | Startup Known Answer Test result |
| `mode` | `"sealed"` / `"fallback"` / `"blocked"` | Current operational state |

---

### `GET /random`

Core entropy endpoint. Returns cryptographically secure random bytes.

```bash
curl -H "x-api-key: YOUR_API_KEY" \
  "http://127.0.0.1:8080/random?n=32&fmt=hex"
```

**Query Parameters:**

| Parameter | Required | Type | Example | Description |
|-----------|----------|------|---------|-------------|
| `n` | ✅ | int | `32` | Number of bytes (1–1,000,000) |
| `fmt` | ❌ | string | `hex` / `base64` / `raw` | Output encoding (default: raw binary) |
| `x-api-key` | ✅ | string | `demo` | API key (header or query param) |

**Examples:**

```bash
# 16 bytes as hexadecimal
curl -H "x-api-key: prod-key" \
  "http://127.0.0.1:8080/random?n=16&fmt=hex"
# → "a3f7b2c1d8e4f9a5..."

# 256 bytes as base64
curl -H "x-api-key: prod-key" \
  "http://127.0.0.1:8080/random?n=256&fmt=base64"
# → "o7f8Qx9K2L5M8N1P..."

# Raw binary to file
curl -H "x-api-key: prod-key" \
  "http://127.0.0.1:8080/random?n=1024" \
  --output seed.bin
```

**Error Responses:**

```bash
# Missing API key
curl "http://127.0.0.1:8080/random?n=16"
# → HTTP/1.1 401 Unauthorized

# Invalid API key
curl -H "x-api-key: WRONG" \
  "http://127.0.0.1:8080/random?n=16"
# → HTTP/1.1 401 Unauthorized

# Request too large
curl -H "x-api-key: demo" \
  "http://127.0.0.1:8080/random?n=2000000"
# → HTTP/1.1 413 Payload Too Large

# Rate limit exceeded
curl -H "x-api-key: demo" \
  "http://127.0.0.1:8080/random?n=16"
# (after many requests)
# → HTTP/1.1 429 Too Many Requests
```

---

## 🔐 On-Chain Verification (VRF)

### What is VRF?

A **Verifiable Random Function** proves that random bytes were:
1. Generated by the trusted Re4ctoR node
2. Not manipulated in transit
3. Deterministic for the same input

This is cryptographic proof, not just a promise.

### Smart Contracts

Located in `vrf-spec/contracts/`:

#### **R4VRFVerifier.sol**

Verifies ECDSA signatures on randomness.

```solidity
function verify(
    bytes32 randomness,
    bytes calldata signature,
    address trustedSigner
) external returns (bool)
```

**Features:**
- Standard ECDSA recovery
- Emits `RandomnessVerified` event
- Reusable across dApps

#### **LotteryR4.sol**

Reference on-chain lottery using verified randomness.

```solidity
function enterLottery() external
function drawWinner(bytes32 randomness, bytes calldata signature) external
```

**Features:**
- Players register on-chain
- Deterministic winner selection
- Signature verification
- Complete event audit trail

### Run Tests

```bash
cd vrf-spec
npm install
npx hardhat compile
npx hardhat test
```

**Expected output:**

```
LotteryR4
  ✔ picks a deterministic fair winner using verified randomness (425ms)
  ✔ reverts if signature is invalid (218ms)

R4VRFVerifier
  ✔ verifies a valid signature from the signer (424ms)
  ✔ emits event on submitRandom() (185ms)

4 passing (1.2s)
```

### Integration Example

```javascript
// Off-chain: Get randomness from Re4ctoR
const response = await fetch('http://r4-node:8080/random?n=32&fmt=hex', {
  headers: { 'x-api-key': 'your-key' }
});
const randomness = await response.text();

// Sign it (simulating Re4ctoR signing)
const signature = await signer.signMessage(randomness);

// On-chain: Verify and use
await lottery.drawWinner(randomness, signature);

// Listen for winner
lottery.on('WinnerSelected', (winner, index, rand) => {
  console.log(`Winner: ${winner} at index ${index}`);
});
```

---

## 📊 Use Cases

### 1. Blockchain Validators

```python
import requests

# Get seed for leader election
response = requests.get(
    "http://r4-node:8080/random?n=32&fmt=hex",
    headers={"x-api-key": "validator-secret"}
)
seed = response.text
# Use for committee selection, rotation
```

### 2. Key Generation

```bash
# Generate 256-bit AES encryption key
curl -H "x-api-key: prod" \
  "http://r4-internal:8080/random?n=32&fmt=base64" \
  | base64 -d > aes256.key

# Generate ECDSA signing key
curl -H "x-api-key: prod" \
  "http://r4-internal:8080/random?n=32" \
  --output signing_key.bin
```

### 3. Gaming & Lotteries

```javascript
// Fair dice roll 1-100
const response = await fetch(
  'http://r4-api:8080/random?n=8&fmt=hex',
  { headers: { 'x-api-key': process.env.R4_KEY } }
);
const hex = await response.text();
const roll = (parseInt(hex.substring(0, 8), 16) % 100) + 1;
console.log(`You rolled: ${roll}`);
```

### 4. ZK-Rollup Seeding

```solidity
// Get randomness from Re4ctoR
bytes32 seed = IRe4ctoR(r4Node).requestRandom(32);
// Use for sequencer selection, prover assignment
```

### 5. NFT Raffle

```solidity
// On-chain lottery using LotteryR4
lottery.enterLottery{value: rafflePrice}();
// Later, when randomness is available:
lottery.drawWinner(randomness, signature);
```

---

## 🔒 Security & Compliance

### Statistical Validation ✅

All output verified against industry-standard test suites:

| Test Suite | Status | Details |
|------------|--------|---------|
| **NIST SP 800-22** | ✅ 15/15 | `p ≈ 0.5` uniformity |
| **Dieharder** | ✅ 31/31 | All tests pass |
| **PractRand** | ✅ 8 GB | No anomalies |
| **TestU01 BigCrush** | ✅ 160/160 | 100% acceptance |

📊 **Full reports**: [`packages/core/proof/`](./packages/core/proof/)

### Boot Integrity & Self-Test

Every container startup:

1. **Integrity Check** — Binary hash vs. signed manifest (fail → block)
2. **Known Answer Test (KAT)** — Core self-test (fail → degraded/block)
3. **Attestation** — Status exposed at `/version`

**Enable strict mode:**

```bash
docker run -d \
  -e STRICT_FIPS=1 \
  pipavlo/r4-local-test:latest
# → HTTP 503 if selftest ≠ "pass"
```

### Supply Chain Security

Each release includes:

- 📦 `re4_release.tar.gz` — Sealed core binary
- 🔒 `re4_release.sha256` — Hash manifest
- ✍️ `re4_release.tar.gz.asc` — GPG signature
- 📋 `SBOM.spdx.json` — Software Bill of Materials

**Verify before use:**

```bash
# Check integrity
sha256sum -c re4_release.sha256

# Verify GPG signature
gpg --verify re4_release.tar.gz.asc

# Review dependencies
cat SBOM.spdx.json | jq '.packages'
```

---

## ⚙️ Performance

| Metric | Value |
|--------|-------|
| **Throughput** | ~950,000 req/s |
| **Latency (p99)** | ~1.1 ms |
| **Max request** | 1 MB (1,000,000 bytes) |
| **Entropy bias** | < 10⁻⁶ deviation |

📈 **Detailed benchmarks**: [`docs/proof/benchmarks_summary.md`](./docs/proof/benchmarks_summary.md)

---

## 🏭 Production Deployment

### Docker + systemd

Create `/etc/systemd/system/r4-entropy.service`:

```ini
[Unit]
Description=R4 Entropy API
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
Restart=always
RestartSec=5s

# Load API key from vault/env file
EnvironmentFile=/etc/r4-entropy.env

ExecStart=/usr/bin/docker run --rm \
  --name r4-entropy \
  -p 8080:8080 \
  -e API_KEY=${R4_API_KEY} \
  -e STRICT_FIPS=${R4_STRICT:-1} \
  --log-driver json-file \
  --log-opt max-size=100m \
  --log-opt max-file=10 \
  pipavlo/r4-local-test:latest

ExecStop=/usr/bin/docker stop r4-entropy

[Install]
WantedBy=multi-user.target
```

**Create env file:**

```bash
echo "R4_API_KEY=your-secure-api-key-here" | sudo tee /etc/r4-entropy.env
sudo chmod 600 /etc/r4-entropy.env
```

**Enable and start:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable r4-entropy
sudo systemctl start r4-entropy
sudo systemctl status r4-entropy
```

### Best Practices

✅ **Reverse proxy** — Run behind nginx/traefik/API gateway  
✅ **API key management** — Use vault (Hashicorp, AWS Secrets Manager)  
✅ **Monitoring** — Poll `/version` for integrity drift  
✅ **Rate limiting** — Configure at reverse proxy level  
✅ **Network isolation** — Internal-only, no public internet exposure  
✅ **Logging** — Centralize logs (ELK, CloudWatch, Splunk)  
✅ **Health checks** — Configure automated restarts  
✅ **Backups** — Keep audit logs for compliance  

### Example: Docker Compose

```yaml
version: '3.8'
services:
  r4-entropy:
    image: pipavlo/r4-local-test:latest
    environment:
      API_KEY: ${R4_API_KEY}
      STRICT_FIPS: "1"
    ports:
      - "8080:8080"
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "10"

  nginx-proxy:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - r4-entropy
```

---

## 🔭 PQ VRF Roadmap

**Target**: Q1–Q2 2025  
**Endpoint**: `/vrf` (Verifiable Random Function with post-quantum crypto)

### Planned Response

```json
{
  "random": "<32_bytes_hex>",
  "signature": "<dilithium_signature>",
  "public_key": "<node_public_key>",
  "verified": true,
  "timestamp": "2025-01-15T12:34:56Z"
}
```

### Post-Quantum Cryptography

🔐 **Dilithium-3** — NIST-standardized signature scheme  
🔒 **Kyber-1024** — Key encapsulation mechanism (lattice-based)

### Features

✅ Resistant to quantum computer attacks  
✅ Verifiable by anyone (public key cryptography)  
✅ Low latency compared to classical VRFs  
✅ On-chain verification support (Solidity)  

### Use Cases Enabled

| Industry | Application |
|----------|-------------|
| **Blockchain** | Quantum-resistant validator rotation |
| **ZK-Rollups** | Sequencer seed, prover selection |
| **Gaming** | Anti-cheat randomness, loot drops |
| **Lotteries** | Provably fair draws |
| **IoT** | Distributed randomness for sensors |

📋 **Specification draft**: [`vrf-spec/`](./vrf-spec/)

---

## 🧰 What's Inside

```
r4-monorepo/
├── packages/
│   ├── core/                           # Sealed entropy core
│   │   ├── runtime/bin/re4_dump        # Compiled binary
│   │   ├── proof/                      # Statistical validation reports
│   │   │   ├── nist_sp800_22.txt
│   │   │   ├── dieharder_results.txt
│   │   │   └── practrand_results.txt
│   │   └── manifest/
│   │       ├── re4_release.sha256      # Hash of binary
│   │       └── re4_release.tar.gz.asc  # GPG signature
│   │
│   └── api/                            # FastAPI wrapper (open-source)
│       ├── main.py                     # FastAPI application
│       ├── requirements.txt
│       └── Dockerfile
│
├── vrf-spec/                           # Post-quantum VRF specification
│   ├── contracts/
│   │   ├── R4VRFVerifier.sol           # Signature verification
│   │   └── LotteryR4.sol               # Reference lottery
│   ├── test/
│   │   ├── lottery.js
│   │   └── verify.js
│   ├── hardhat.config.js
│   └── package.json
│
├── docs/
│   ├── USAGE.md                        # API usage guide
│   ├── DEPLOYMENT.md                   # Production deployment
│   ├── SECURITY.md                     # Security considerations
│   └── proof/
│       └── benchmarks_summary.md
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── vrf-tests.yml
│       └── release.yml
│
├── SBOM.spdx.json                      # Software Bill of Materials
├── LICENSE                             # Proprietary core + MIT wrapper
└── README.md                           # This file
```
### Competitive Landscape

See [R4 vs Competitors](./docs/COMPETITION.md) for a deep comparison vs Chainlink VRF, drand, AWS CloudHSM, Thales HSM, and others.

**License**: Wrapper code MIT, sealed core proprietary (HSM model)

---

## 🧪 Testing

### Entropy Core Tests

```bash
# Run statistical validation suite
cd packages/core
make test-fips
make test-dieharder
make test-practrand
```

### VRF Smart Contracts

```bash
cd vrf-spec
npm install
npx hardhat compile
npx hardhat test

# With gas reporting
REPORT_GAS=true npx hardhat test
```

### Integration Tests

```bash
# Start local R4 instance
docker run -d -p 8080:8080 -e API_KEY=test pipavlo/r4-local-test:latest

# Run integration tests
npm run test:integration
```

---

## 📈 Monitoring & Observability

### Health Check

```bash
# Continuous monitoring
watch -n 5 'curl -s http://127.0.0.1:8080/version | jq .'
```

### Prometheus Metrics (Roadmap)

Future support for `/metrics` endpoint with:
- Request count
- Request latency
- Integrity check status
- Entropy core health

### Logging

Container logs include:
- Request timestamp
- API key (hash)
- Response size
- Response time
- Error details

```bash
docker logs r4test | tail -100
```

---

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit changes (`git commit -am 'Add feature'`)
4. Push to branch (`git push origin feature/my-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone and install dependencies
git clone https://github.com/pipavlo82/r4-monorepo
cd r4-monorepo
npm install

# Run tests
npm test

# Build Docker image locally
docker build -f packages/api/Dockerfile -t r4-local:dev .
```

---

## 📬 Contact & Support

**Maintainer**: Pavlo Tvardovskyi

- 📧 **Email**: [shtomko@gmail.com](mailto:shtomko@gmail.com)
- 🐙 **GitHub**: [@pipavlo82](https://github.com/pipavlo82)
- 🐳 **Docker Hub**: [pipavlo/r4-local-test](https://hub.docker.com/r/pipavlo/r4-local-test)

### Enterprise Inquiries

For custom deployments, SLA agreements, regulatory audits, or PQ-VRF early access:

📧 **shtomko@gmail.com**

---

## 📚 Additional Resources

- [API Usage Guide](./docs/USAGE.md)
- [Deployment Guide](./docs/DEPLOYMENT.md)
- [Security Model](./docs/SECURITY.md)
- [Statistical Proofs](./packages/core/proof/)
- [VRF Specification](./vrf-spec/)

---

## 🏷️ Tags

`#entropy` `#rng` `#fips` `#pqcrypto` `#verifiable` `#docker` `#hsm` `#blockchain` `#web3` `#cryptography` `#randomness`

---

<div align="center">

**© 2025 Re4ctoR Project**

Built with ⚡ for high-assurance randomness

[⬆ Back to top](#-r4-monorepo)

</div>
