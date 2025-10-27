# ⚡ r4-monorepo

Entropy appliance and verifiable randomness API with **post-quantum cryptography**.

[![Docker Pulls](https://img.shields.io/docker/pulls/pipavlo/r4-local-test?style=flat-square)](https://hub.docker.com/r/pipavlo/r4-local-test)
[![Docker Size](https://img.shields.io/docker/image-size/pipavlo/r4-local-test/latest?style=flat-square)](https://hub.docker.com/r/pipavlo/r4-local-test)
[![CI](https://github.com/pipavlo82/r4-monorepo/actions/workflows/ci.yml/badge.svg)](https://github.com/pipavlo82/r4-monorepo/actions/workflows/ci.yml)
[![Sanity Check](https://img.shields.io/badge/sanity--check-passing-brightgreen?style=flat-square)](https://github.com/pipavlo82/r4-monorepo/actions/workflows/public-sanity.yml)
[![VRF Tests](https://github.com/pipavlo82/r4-monorepo/actions/workflows/vrf-tests.yml/badge.svg)](https://github.com/pipavlo82/r4-monorepo/actions/workflows/vrf-tests.yml)
[![Release](https://github.com/pipavlo82/r4-monorepo/actions/workflows/release.yml/badge.svg)](https://github.com/pipavlo82/r4-monorepo/actions/workflows/release.yml)
[![FIPS 204 Ready](https://img.shields.io/badge/FIPS-204%20Ready-green?style=flat-square)](./docs/FIPS_204_roadmap.md)
[![PQ Crypto](https://img.shields.io/badge/PQ-Dilithium%20%2B%20Kyber-purple?style=flat-square)](./vrf-spec/)

---

## 🧠 Overview

**r4** is a high-entropy appliance and verifiable randomness API.

It delivers:
- 🔒 **Sealed entropy core (`re4_dump`)** — closed-source, statistically verified via Dieharder / PractRand / BigCrush, shipped as a signed binary.  
- 🌐 **Hardened FastAPI layer** — key-protected `/random` endpoint for secure entropy distribution over HTTP (Docker or systemd).
- 🧬 **Post-Quantum Extension** — Dilithium 3 (FIPS 204) signatures and Kyber KEM integration on port 8081.

The repo also tracks the **Post-Quantum VRF roadmap** (`vrf-spec/`) — future attested randomness for proof-of-stake rotation, zk-rollup seeding, and lotteries.

---

## 🚀 Quickstart (Docker)

You can run the whole service with one Docker command.

### Prereqs

- 🐳 Docker Desktop (Windows/macOS) or Docker Engine (Linux)
- 🔌 Port 8080 free

### Run the container

```bash
docker run -d \
  --name r4test \
  -p 8080:8080 \
  -e API_KEY=demo \
  pipavlo/r4-local-test:latest
```

### Health check

```bash
curl -s http://127.0.0.1:8080/health
```

### Version / build info

```bash
curl -s http://127.0.0.1:8080/version | jq
```

**Expected response:**

```json
{
  "name": "re4ctor-api",
  "version": "0.1.0",
  "api_git": "container-build",
  "core_git": "release-core",
  "limits": {
    "max_bytes_per_request": 1000000,
    "rate_limit": "10/sec per IP (enforced in prod by reverse proxy)"
  }
}
```

### Request cryptographic random bytes

```bash
curl -s -H "x-api-key: demo" \
  "http://127.0.0.1:8080/random?n=32&fmt=hex"
```

**What happens here:**
- `re4_dump` is executed in the container
- The API enforces `API_KEY`
- Output is served over HTTP with basic rate limiting
- No external network calls — randomness is generated locally in your container

---

## 🔐 Auth Model

The API requires a key for `/random`.

Two ways to pass it:
- Header: `x-api-key: demo`
- Query: `?key=demo`

By default, the container ships with:
```
-e API_KEY=demo
```

**Change this in production.**

### Example production run

```bash
docker run -d \
  --name r4prod \
  -p 8080:8080 \
  -e API_KEY="my-super-secret" \
  pipavlo/r4-local-test:latest
```

Then call:

```bash
curl -s -H "x-api-key: my-super-secret" \
  "http://127.0.0.1:8080/random?n=64&fmt=hex"
```

---

## 📚 API Reference

### `GET /health`

Returns `"ok"` if the API is alive.

```bash
curl http://127.0.0.1:8080/health
```

---

### `GET /version`

Returns metadata about this running instance:
- `core_git` – build/commit tag of the entropy core
- `api_git` – build tag for the API layer
- `limits` – rate limit and max request size

Designed for audit / fleet inventory / compliance dashboards.

```bash
curl http://127.0.0.1:8080/version | jq
```

---

### `GET /random`

Request random bytes.

**Query params:**

| Param | Required | Example | Description |
|-------|----------|---------|-------------|
| `n` | ✅ | `32`, `1024` | Number of bytes |
| `fmt` | ❌ | `hex` / (unset) | Output format |

**Auth:**
- Header: `x-api-key:`
- Query: `?key=`

**Examples:**

16 bytes, hex-encoded:
```bash
curl -s -H "x-api-key: demo" \
  "http://127.0.0.1:8080/random?n=16&fmt=hex"
```

64 raw bytes saved to file:
```bash
curl -s -H "x-api-key: demo" \
  "http://127.0.0.1:8080/random?n=64" \
  --output sample.bin
hexdump -C sample.bin | head
```

Error example (invalid key):
```bash
curl -i -s -H "x-api-key: WRONG" \
  "http://127.0.0.1:8080/random?n=16&fmt=hex"
# → HTTP/1.1 401 Unauthorized
# → {"detail": "invalid api key"}
```

---

## 🧰 What's Inside the Container

The published image `pipavlo/r4-local-test:latest` bundles:

- `/app/runtime/bin/re4_dump` — the high-entropy generator binary (only component allowed to emit randomness)
- FastAPI + Uvicorn REST layer exposing `/health`, `/version`, `/random`
- Rate limiting, request logging, and IP metadata hints

**Runtime config (env vars):**
- `API_KEY` — required for `/random`
- `API_HOST` / `PORT` — default `0.0.0.0:8080`

**No external entropy source is pulled at request time** — randomness never leaves the container except via your HTTP call.

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

## 🧮 Trust / Audit / Compliance

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

Human-readable summaries live under `packages/core/proof/`. Full multi-GB raw logs are not committed — archived offline and shared under NDA.

The internal DRBG/entropy core is intentionally not open-sourced, following an HSM / Secure Enclave model:
- you can measure output quality
- you can verify supply-chain integrity (hash + signature + SBOM)
- you cannot clone the internal core

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

## 🔭 Post-Quantum VRF Roadmap

**Today:**
- `/random` returns high-quality entropy bytes
- You authenticate with API key
- You trust we're not biasing output

**Next: provable randomness for consensus / staking.** The `vrf-spec/` package tracks the next milestone:

- ✅ Attach post-quantum identity (Dilithium / Kyber class keys)
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

## 🎲 Provably Fair Lottery (LotteryR4.sol)

We include a reference on-chain lottery contract:
**`vrf-spec/contracts/LotteryR4.sol`**

How it works:
1. Players join via `enterLottery()`
2. Re4ctoR node generates 32 bytes of randomness and signs it with its private key
3. The contract verifies the ECDSA signature (via `R4VRFVerifier`)
4. A winner is selected on-chain:
   `winnerIndex = uint256(randomness) % players.length`
5. We emit `WinnerSelected(winner, index, randomness)`

Hardhat test (`vrf-spec/test/lottery.js`) proves:
- ✅ honest randomness → valid draw
- 🔐 forged / attacker randomness → revert

This is a blueprint for:
- on-chain casinos
- NFT mints / raffles
- transparent loot drops
- validator / committee elections

---

## 📦 Status

This repo is public. The core entropy code is not.

**Public Docker image:**

```bash
docker pull pipavlo/r4-local-test:latest
```

**Enough to:**
- integrate into backend services
- generate keys/secrets
- feed offline systems needing strong RNG
- demo to infra / security / validator teams

---

## 📄 License / NOTICE

See `LICENSE` and `NOTICE`.

**Summary:**
- Wrapper code, API logic, docs → public & reviewable
- Entropy core → compiled & signed binary (reproducible build)
- Internal DRBG/entropy combiner → private (HSM model)

You can test output quality, verify signatures and SBOM, but not access the private core.

---

## 🤝 Contact / Sponsors

For enterprise access, on-prem deployments, validator beacons, or PQ-signed `/vrf` services (enterprise / auditors / rollup / staking infra):

**Maintainer**: Pavlo Tvardovskyi

📧 **Email**: [shtomko@gmail.com](mailto:shtomko@gmail.com)  
🐙 **GitHub**: [@pipavlo82](https://github.com/pipavlo82)  
🐳 **Docker Hub**: [pipavlo/r4-local-test](https://hub.docker.com/r/pipavlo/r4-local-test)

---

<div align="center">

**© 2025 Re4ctoR Project**

Built with ⚡ for high-assurance randomness in the post-quantum era

[⬆ Back to top](#-r4-monorepo)

</div>
