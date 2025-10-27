# ⚡ r4-monorepo

Entropy appliance and verifiable randomness API with **post-quantum cryptography**.

[![Docker Pulls](https://img.shields.io/docker/pulls/pipavlo/r4-local-test?style=flat-square)](https://hub.docker.com/r/pipavlo/r4-local-test)
[![Docker Size](https://img.shields.io/docker/image-size/pipavlo/r4-local-test/latest?style=flat-square)](https://hub.docker.com/r/pipavlo/r4-local-test)
[![CI](https://github.com/pipavlo82/r4-monorepo/actions/workflows/ci.yml/badge.svg)](https://github.com/pipavlo82/r4-monorepo/actions)
[![VRF Tests](https://github.com/pipavlo82/r4-monorepo/actions/workflows/vrf-tests.yml/badge.svg)](https://github.com/pipavlo82/r4-monorepo/actions)
[![FIPS 204 Ready](https://img.shields.io/badge/FIPS-204%20Ready-green?style=flat-square)](./docs/FIPS_204_roadmap.md)
[![PQ Crypto](https://img.shields.io/badge/PQ-Dilithium%20%2B%20Kyber-purple?style=flat-square)](./vrf-spec/)

---

## 🧠 Overview

**r4** delivers high-entropy randomness via HTTP API with enterprise-grade post-quantum cryptography.

**Ships two components:**

🔒 **Sealed entropy core (`re4_dump`)**  
Closed-source, statistically verified (Dieharder / PractRand / BigCrush), shipped as signed binary

🌐 **Hardened HTTP API (`/random`)**  
Rate-limited, key-protected, production-ready (Docker or systemd)

**NEW: Post-Quantum Extension (Port 8081)**  
✅ Dilithium 3 (FIPS 204) signatures  
✅ Kyber KEM integration  
✅ Audited Solidity verifiers  

**Includes reference implementation:**

🎲 **On-chain lottery** (`vrf-spec/`) with cryptographic fairness proof

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

### Verify

```bash
# Health check
curl http://127.0.0.1:8080/health
# → "ok"

# Version + build info
curl http://127.0.0.1:8080/version | jq

# Request random bytes
curl -H "x-api-key: demo" \
  "http://127.0.0.1:8080/random?n=32&fmt=hex"
```

---

## 📘 API Reference

### `GET /health`

Simple liveness check.

```bash
curl http://127.0.0.1:8080/health
# → "ok"
```

---

### `GET /version`

Metadata about running instance (for audit / fleet inventory).

```bash
curl http://127.0.0.1:8080/version | jq
```

**Response:**

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

---

### `GET /random`

Request cryptographically secure random bytes.

**Query Parameters:**

| Param | Required | Example | Description |
|-------|----------|---------|-------------|
| `n` | ✅ | `32`, `1024` | Number of bytes |
| `fmt` | ❌ | `hex` / (raw) | Output format |

**Auth:**
- Header: `x-api-key: demo`
- Query: `?key=demo`

**Examples:**

```bash
# 16 bytes, hex-encoded
curl -H "x-api-key: demo" \
  "http://127.0.0.1:8080/random?n=16&fmt=hex"

# 64 raw bytes to file
curl -H "x-api-key: demo" \
  "http://127.0.0.1:8080/random?n=64" \
  --output sample.bin
```

**Error example:**

```bash
curl -i -H "x-api-key: WRONG" \
  "http://127.0.0.1:8080/random?n=16"
# → HTTP/1.1 401 Unauthorized
```

---

## 🔐 Auth Model

The API requires a key for `/random`.

Two ways to pass it:
- Header: `x-api-key: demo`
- Query: `?key=demo`

**Example production run:**

```bash
docker run -d \
  --name r4prod \
  -p 8080:8080 \
  -e API_KEY="my-super-secret" \
  pipavlo/r4-local-test:latest
```

Then call:

```bash
curl -H "x-api-key: my-super-secret" \
  "http://127.0.0.1:8080/random?n=64&fmt=hex"
```

---

## 🧰 What's Inside the Container

The published image `pipavlo/r4-local-test:latest` bundles:

- `/app/runtime/bin/re4_dump` — high-entropy generator binary
- FastAPI + Uvicorn REST layer (`/health`, `/version`, `/random`)
- Rate limiting, request logging, IP metadata hints

**Runtime config (env vars):**
- `API_KEY` — required for `/random`
- `API_HOST` / `PORT` — default `0.0.0.0:8080`

**No external entropy source** — randomness never leaves container except via HTTP.

---

## 🔭 Roadmap Progress — 2025

| Quarter | Milestone | Status | Notes |
|---------|-----------|--------|-------|
| **Q1 2025** | Dilithium 3 (PQ signatures) enabled in enterprise build | ✅ **Complete** | ML-DSA (FIPS 204) signing now available |
| **Q2 2025** | Kyber KEM integration for VRF key exchange | ✅ **Complete** | Lattice-based KEM added to PQ-VRF layer |
| **Q3 2025** | Smart contract audits & public testnet launch | ✅ **Complete** | Solidity verifiers audited on Ethereum Sepolia |
| **Q4 2025** | FIPS 140-3 / 204 certification submission | 🚀 **In Progress** | Lab validation under review (Q1 2026 ETA) |

### Summary

✅ PQ signatures (Dilithium 3) live in enterprise build (port 8081)  
✅ Kyber KEM operational for VRF exchange  
✅ Audited contracts deployed to testnet  
🚧 FIPS submission pipeline active  

**R4 now enters the certification phase for FIPS 140-3 and 204.**

---

## 🧬 Post-Quantum Extension (Port 8081)

The **R4PQ module** extends R4 with verifiable signed randomness and post-quantum signatures.

### Dual-Node Architecture

| Port | Purpose | Signature Type |
|------|---------|----------------|
| **8080** | Classic entropy core | Unsigned |
| **8081** | PQ API layer | ECDSA + Dilithium 3 |

Run side-by-side:

```bash
docker build -t r4pq:latest .
docker run -d \
  --name r4pq \
  -p 8081:8081 \
  -e API_KEY=demo \
  -e RATE_LIMIT="30/minute" \
  r4pq:latest
```

### Endpoints (Port 8081)

| Endpoint | Description |
|----------|-------------|
| `GET /version` | Service metadata |
| `GET /random` | Raw entropy |
| `GET /random_pq?sig=ecdsa` | ECDSA-signed randomness |
| `GET /random_pq?sig=dilithium` | Dilithium 3 (FIPS 204 PQ signature) |
| `POST /verify_pq` | Signature verification |
| `GET /metrics_pq` | Uptime & FIPS status |

### Example Response (ECDSA Mode)

```json
{
  "random": 1875835980,
  "timestamp": "2025-10-27T12:36:50Z",
  "signature_type": "ECDSA(secp256k1)",
  "pq_mode": false
}
```

### Example Response (Dilithium Mode — Enterprise Build)

```json
{
  "random": "a3f7b2c1d8e4f9a5...",
  "signature": "<dilithium_3_signature>",
  "public_key": "<node_pq_key>",
  "timestamp": "2025-10-27T12:36:50Z",
  "signature_type": "Dilithium3(FIPS204)",
  "verified": true,
  "pq_mode": true
}
```

**Enterprise build enables real Dilithium signatures** for provably fair use cases (gaming, lotteries, validator rotation).

---

## 🮨 Trust / Audit / Compliance

This acts as an entropy appliance.

We ship:
- `re4_release.tar.gz` — release tarball
- `re4_release.sha256` — SHA-256 manifest
- `re4_release.tar.gz.asc` — detached GPG signature
- `SBOM.spdx.json` — Software Bill of Materials

We run statistical batteries:
- **Dieharder** — 31/31 passed
- **PractRand** — 8 GB analyzed, no anomalies
- **TestU01 BigCrush** — 160/160 passed
- **NIST SP 800-22** — 15/15 passed

**Human-readable summaries** live under `packages/core/proof/`. Full multi-GB raw logs archived offline and shared under NDA.

**Sealed core (HSM model):**
- You can measure output quality
- You can verify supply-chain integrity (hash + signature + SBOM)
- You cannot clone the internal core

### FIPS 140-3 & 204 Compliance

📋 **Status**: Certification in progress (Q1 2026 ETA)

- ✅ Dilithium 3 (ML-DSA per FIPS 204)
- ✅ Kyber (ML-KEM per FIPS 203)
- ✅ Statistical validation complete
- 🚀 Lab submission in review

---

## 🏭 Production Deployment

### Two supported modes:

#### 🐳 Docker (Recommended)

Run behind a reverse proxy (nginx / traefik / API gateway). Expose `/random` only internally. Keep `API_KEY` secret. Monitor `/version` for expected `core_git`.

**Example systemd unit:**

```ini
[Unit]
Description=R4 entropy API container
After=network-online.target
Wants=network-online.target

[Service]
Restart=always
ExecStart=/usr/bin/docker run --rm \
  -p 8080:8080 \
  -e API_KEY=prod-secret-here \
  --name r4-entropy \
  pipavlo/r4-local-test:latest
ExecStop=/usr/bin/docker stop r4-entropy

[Install]
WantedBy=multi-user.target
```

#### ⚙️ Bare Metal / systemd

Run uvicorn + `re4_dump` directly under systemd as non-root with sandboxing:

```ini
ProtectSystem=strict
ProtectHome=true
MemoryDenyWriteExecute=true
```

See:
- `packages/core/docs/USAGE.md`
- `packages/core/docs/re4ctor-api.service.example`

---

## 🔭 Post-Quantum Roadmap

**Current state (✅ Complete):**
- `/random` returns high-quality entropy bytes
- You authenticate with API key
- You trust we're not biasing output

**Next phase (🚀 In Progress):**
Provable randomness for consensus / staking. The `vrf-spec/` package tracks milestones:

- ✅ Attach post-quantum identity (Dilithium / Kyber)
- ✅ Sign each randomness response
- ✅ Allow external verifiers to prove:
  - The bytes came from an authorized node
  - The operator couldn't re-roll for a "better" outcome

**Planned `/vrf` response shape:**

```json
{
  "random": "<entropy_bytes>",
  "signature": "<dilithium_sig>",
  "public_key": "<node_key>",
  "verified": true,
  "timestamp": "2025-01-15T12:34:56Z"
}
```

**Intended consumers:**
- Validator set rotation in PoS
- zk-rollup sequencers / prover seeds
- On-chain lotteries / airdrops / mint fairness
- Anti-manipulation randomness feeds

**Positioning:**
- `/random` = fast local entropy
- `/vrf` = attestable randomness with cryptographic accountability

---

## 📦 Status

This repo is **public**. The core entropy code is not.

**Public Docker image:**

```bash
docker pull pipavlo/r4-local-test:latest
```

**Enough to:**
- Integrate into backend services
- Generate keys/secrets
- Feed offline systems needing strong RNG
- Demo to infra / security / validator teams

---

## 📄 License / NOTICE

See `LICENSE` and `NOTICE`.

**Summary:**
- Wrapper code, API logic, docs → public & reviewable
- Entropy core → compiled & signed binary (reproducible build)
- Internal DRBG/entropy combiner → private (HSM model)

You can test output quality, verify signatures and SBOM, but not access the private core.

---

## 🤝 Contact & Support

**Maintainer**: Pavlo Tvardovskyi

📧 **Email**: [shtomko@gmail.com](mailto:shtomko@gmail.com)  
🐙 **GitHub**: [@pipavlo82](https://github.com/pipavlo82)  
🐳 **Docker Hub**: [pipavlo/r4-local-test](https://hub.docker.com/r/pipavlo/r4-local-test)

### Enterprise Inquiries

For enterprise access, on-prem deployments, validator beacons, SLA agreements, or PQ-signed `/vrf` services:

📧 **shtomko@gmail.com**

---

<div align="center">

**© 2025 Re4ctoR Project**

Built with ⚡ for high-assurance randomness in the post-quantum era

[⬆ Back to top](#-r4-monorepo)

</div>
