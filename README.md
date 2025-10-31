☢️ RE4CTOR — The Nuclear Core of Randomness

Verifiable entropy • Post-quantum VRF • Attested boot • On-chain fairness you can prove
> **Verifiable entropy • Post-quantum VRF • Attested boot • On-chain fairness you can prove**

[![PyPI](https://img.shields.io/pypi/v/r4sdk?label=r4sdk%20on%20PyPI&style=flat-square)](https://pypi.org/project/r4sdk/)
[![Docker Pulls](https://img.shields.io/docker/pulls/pipavlo/r4-local-test?style=flat-square)](https://hub.docker.com/r/pipavlo/r4-local-test)
[![VRF Tests](https://github.com/pipavlo82/r4-monorepo/actions/workflows/vrf-tests.yml/badge.svg)](https://github.com/pipavlo82/r4-monorepo/actions/workflows/vrf-tests.yml)
[![CI Status](https://github.com/pipavlo82/r4-monorepo/actions/workflows/ci.yml/badge.svg)](https://github.com/pipavlo82/r4-monorepo/actions/workflows/ci.yml)
[![FIPS 204 Ready](https://img.shields.io/badge/FIPS%20204%20Ready-brightgreen?style=flat-square)](docs/FIPS_204_roadmap.md)
[![Release](https://img.shields.io/github/v/release/pipavlo82/r4-monorepo?include_prereleases&style=flat-square)](https://github.com/pipavlo82/r4-monorepo/releases)

## 📋 Table of Contents

- [Overview](#-overview)
- [One-Command Demo](#-one-command-demo)
- [Docker Quickstart (:8080)](#-docker-quickstart-8080)
- [Python SDK](#-python-sdk)
- [Dual VRF API (:8083)](#-dual-vrf-api-8083)
- [On-Chain Verifier](#-on-chain-verifier)
- [Security & ESV](#-security--esv)
- [Roadmap 2025](#-roadmap-2025)
- [R4 vs Competitors](#-r4-vs-competitors)
- [LotteryR4 (reference)](#-lotteryr4-reference)
- [Repository Structure](#-repository-structure)
- [Contributing](#contributing)
- [Support](#-support)
- [Contact](#-contact)

---
# RE4CTOR 🧠

**A sealed entropy appliance + verifiable randomness pipeline for post-quantum, FIPS-compliant, and on-chain-verifiable randomness.**

[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-green)](https://www.python.org/)
[![Docker Ready](https://img.shields.io/badge/docker-ready-blue)](https://hub.docker.com/r/pipavlo/r4-local-test)

## Features

- **Post-Quantum Cryptography** — ML-DSA-65 (Dilithium3) + ML-KEM (Kyber512) signatures
- **FIPS-Compliant** — FIPS 204 certification roadmap with rigorous entropy validation
- **On-Chain Verifiable** — Solidity verifiers for transparent randomness verification
- **Sub-millisecond Latency** — <1ms response times for ultra-fast RNG
- **Self-Hosted** — No external dependencies or API subscriptions required
- **Dual VRF Node** — ECDSA (EIP-191) + optional post-quantum signatures

## Quick Start

### Docker (Fastest)

```bash
docker run -d \
  --name r4-core \
  -p 8080:8080 \
  -e API_KEY=demo \
  pipavlo/r4-local-test:latest

# Health check
curl http://127.0.0.1:8080/health

# Get 32 bytes of random data
curl -H "X-API-Key: demo" \
  "http://127.0.0.1:8080/random?n=32&fmt=hex"
```

### Full Demo

```bash
./run_full_demo.sh
```

Starts both APIs, runs stress tests, validates entropy, and executes Solidity unit tests.

Expected output:
- ✅ Core API (:8080) online
- ✅ Dual VRF (:8083) with ECDSA + PQ signatures
- ✅ Hardhat: 6/6 tests passing
- ✅ LotteryR4 picks deterministic winner

### Python SDK

```bash
pip install r4sdk
```

```python
from r4sdk import R4Client

client = R4Client(api_key="demo", host="http://localhost:8080")
data = client.get_random(32)
print(f"Random: {data.hex()}")
```

## Architecture

### Core Components

**☢️ Core API (:8080)**  
FastAPI service providing FIPS-checked entropy with strict self-tests and rate limiting.

**🔐 Dual VRF Node (:8083)**  
Outputs ECDSA (EIP-191) + optional ML-DSA (Dilithium3) post-quantum signatures with full auditability.

**🧬 Solidity Verifiers**  
On-chain signature verification supporting both ECDSA and post-quantum schemes.

**🎲 LotteryR4**  
Reference implementation of a provably fair on-chain lottery using RE4CTOR randomness.

## API Usage

### Get Random Entropy

```bash
curl -H "X-API-Key: demo" \
  "http://localhost:8080/random?n=32&fmt=hex"
```

### Dual VRF with Signature

```bash
curl -sS -H "X-API-Key: demo" \
  http://localhost:8083/random_dual | jq
```

Response includes randomness, ECDSA signature (EIP-191), and optional post-quantum signature:

```json
{
  "random": 1116700701,
  "timestamp": "2025-10-31T18:17:17Z",
  "hash_alg": "SHA-256",
  "signature_type": "ECDSA(secp256k1) + ML-DSA-65",
  "v": 27,
  "r": "0x...",
  "s": "0x...",
  "msg_hash": "0x...",
  "signer_addr": "0x1C901e3b...",
  "sig_pq_b64": "...",
  "pq_pubkey_b64": "...",
  "pq_scheme": "ML-DSA-65"
}
```

### Verify Signature Locally

```bash
python3 tools/verify_vrf_msg_hash.py /tmp/vrf_dual.json
# Output: which_hash="eip191", hash_ok=true, ecdsa_ok=true
```

## Post-Quantum Cryptography

RE4CTOR integrates FIPS 204 algorithms for future-proofing against quantum threats:

| Algorithm | Purpose | Status |
|-----------|---------|--------|
| ML-DSA-65 (Dilithium3) | VRF signature | ✅ Implemented |
| ML-KEM (Kyber512) | Key exchange | ✅ Implemented |
| SHAKE256 / BLAKE2s | Whitening | ✅ Implemented |
| ChaCha20 | Entropy whitening | ✅ Implemented |

**Runtime Detection:** The API automatically detects `liboqs` availability and enables dual-signing (ECDSA + ML-DSA-65). Falls back gracefully to ECDSA-only if unavailable.

## On-Chain Verification

### Solidity Verifiers

Located in `vrf-spec/contracts/`:

- **R4VRFVerifierCanonical.sol** — Standard ECDSA (EIP-191) verifier
- **LotteryR4.sol** — Reference fair-lottery implementation

### Build & Test

```bash
cd vrf-spec
npm ci
npx hardhat compile
npx hardhat test
# ✅ 6/6 tests passing
```

### Verifier Interface

```solidity
function verify(
    bytes32 randomness,
    uint8 v,
    bytes32 r,
    bytes32 s,
    address expectedSigner
) external pure returns (bool);
```

## Security & Entropy Validation

### FIPS-Style Self-Tests

- **Integrity** — SHA-256 verification of sealed binary
- **Known-Answer Test** — ChaCha20 validation
- **Statistical Tests** — Repetition, Adaptive Proportion, Continuous RNG
- **Strict Mode** — `R4_STRICT_FIPS=1` enables fail-closed startup

### Statistical Validation Results

| Test Suite | Result |
|-----------|--------|
| NIST SP 800-22 | 15/15 ✅ |
| Dieharder | 31/31 ✅ |
| PractRand | 8 GiB ✅ |
| TestU01 BigCrush | 160/160 ✅ |

See `packages/core/proof/` for detailed artifacts and `docs/ESV_README.md` for technical details.

## Roadmap

| Quarter | Milestone | Status |
|---------|-----------|--------|
| Q1 2025 | ML-DSA-65 (Dilithium3) signing | ✅ Shipped |
| Q2 2025 | Kyber KEM integration | ✅ Shipped |
| Q3 2025 | Solidity verifier audit + testnet | ✅ Complete |
| Q4 2025 | Attestation & self-test hardening | ✅ Complete |
| Q1 2026 | FIPS 140-3 / 204 lab submission | 🚀 In Progress |
| 2026 | Certification decision | ⏳ Pending |

## Comparison

| Feature | RE4CTOR | Chainlink VRF | drand | AWS HSM |
|---------|---------|---------------|-------|---------|
| Post-Quantum | ✅ Dilithium | ❌ | ❌ | ⚠️ |
| Latency | <1 ms | 30-120 s | 3-30 s | 10-50 ms |
| Cost | Self-hosted | Pay-per-req | Free | $$$$ |
| On-chain verify | ✅ | ✅ | ⚠️ | ❌ |
| Self-hosted | ✅ | ❌ | ✅ | ⚠️ |

## Use Cases

- **Casinos & Gaming** — Provably fair randomness with regulatory audit trails
- **NFT Raffles** — Deterministic winner selection with on-chain verification
- **Validator Rotation** — Fair validator selection for PoS networks
- **Regulatory Compliance** — Verifiable randomness for compliance audits
- **ZK Applications** — Seed generation for zero-knowledge proofs
- **Web3 Oracles** — Trustless random data feeds

## Repository Structure

```
r4-monorepo/
├── run_full_demo.sh              # Complete demo script
├── api/
│   ├── app.py                    # Core API (:8080)
│   ├── app_dual.py               # Dual VRF API (:8083)
│   ├── sign_ecdsa.py             # ECDSA signing
│   └── sign_pq.py                # Post-quantum signing
├── vrf-spec/
│   ├── contracts/
│   │   ├── R4VRFVerifierCanonical.sol
│   │   └── LotteryR4.sol
│   ├── test/
│   │   ├── lottery.js
│   │   ├── verify.js
│   │   └── verify_r4_canonical.js
│   └── hardhat.config.js
├── packages/core/
│   ├── runtime/bin/re4_dump
│   └── proof/
├── docs/
│   ├── USAGE.md
│   ├── DEPLOYMENT.md
│   ├── FIPS_204_roadmap.md
│   └── proof/benchmarks_summary.md
└── tools/verify_vrf_msg_hash.py
```

## Documentation

- [Usage Guide](docs/USAGE.md) — API usage and integration patterns
- [Deployment Guide](docs/DEPLOYMENT.md) — Production setup and configuration
- [FIPS 204 Roadmap](docs/FIPS_204_roadmap.md) — Certification timeline
- [Performance Benchmarks](docs/proof/benchmarks_summary.md) — Latency and throughput metrics
- [Competition Analysis](docs/COMPETITION.md) — Detailed comparison with competitors

## Contributing

We welcome contributions! Areas of interest:

- New VRF verifiers for alternative EVMs and L2 solutions
- Additional test coverage and edge case validation
- Performance optimization scripts and benchmarks
- Documentation improvements and examples

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Support & Community

- **GitHub Issues** — Bug reports and feature requests
- **GitHub Discussions** — Questions and community support
- **Benchmarks** — Performance metrics and comparisons
- **Enterprise Contact** — shtomko@gmail.com (subject: R4 ENTERPRISE)

See [SPONSORS.md](SPONSORS.md) for enterprise support options.

## Contact

**Maintainer:** Pavlo Tvardovskyi

- 📧 Email: [shtomko@gmail.com](mailto:shtomko@gmail.com)
- 🐙 GitHub: [@pipavlo82](https://github.com/pipavlo82)
- 🐳 Docker Hub: [pipavlo/r4-local-test](https://hub.docker.com/r/pipavlo/r4-local-test)
- 📦 PyPI: [r4sdk](https://pypi.org/project/r4sdk/)

## License

MIT License — See [LICENSE](LICENSE) file for details.

---

<div align="center">

### Fairness you can prove. On-chain. Cryptographically.

**[Getting Started](docs/USAGE.md) • [Deploy](docs/DEPLOYMENT.md) • [Contribute](CONTRIBUTING.md)**

</div>
