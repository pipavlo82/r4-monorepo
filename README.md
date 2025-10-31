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


🧠 Overview

RE4CTOR is a sealed entropy appliance + verifiable randomness pipeline, designed for post-quantum, FIPS-compliant, and on-chain-verifiable randomness.

☢️ Core API (:8080) — FastAPI service providing FIPS-checked entropy.

🔐 Dual VRF Node (:8083) — Outputs ECDSA (EIP-191) + optional ML-DSA (Dilithium3) post-quantum signatures.

🧬 Solidity Verifiers — On-chain signature verification (ECDSA and PQ-ready).

🎲 LotteryR4 — A provably fair on-chain lottery demo.

🐍 Python SDK (r4sdk) — Simplified access for backends, validators, or bots.

Use cases: Casinos, NFT raffles, validator rotation, provable randomness for regulators, ZK-seed generation, or Web3 oracles.

🚀 One-Command Demo
./run_full_demo.sh


Starts both APIs, performs stress tests, verifies entropy, and runs Solidity unit tests.

Expected output:

✅ Core API (:8080) online
✅ Dual VRF (:8083) ECDSA + PQ signatures
✅ Hardhat: 6 tests passing
✅ LotteryR4 picks deterministic winner

🐳 Docker Quickstart (:8080)
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

🐍 Python SDK
pip install r4sdk

from r4sdk import R4Client

client = R4Client(api_key="demo", host="http://localhost:8080")
data = client.get_random(32)
print(f"Random: {data.hex()}")


📦 PyPI → r4sdk

🔐 Dual VRF API (:8083)

The /random_dual endpoint returns randomness + proof (ECDSA + PQ if available).

curl -sS -H "X-API-Key: demo" http://127.0.0.1:8083/random_dual | jq


Response:

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
  "sig_pq_b64": "...",       // optional
  "pq_pubkey_b64": "...",    // optional
  "pq_scheme": "ML-DSA-65"
}

✅ Verify locally (EIP-191)
python3 tools/verify_vrf_msg_hash.py /tmp/vrf_dual.json
# → which_hash="eip191", hash_ok=true, ecdsa_ok=true

🧩 Post-Quantum Layer (FIPS-204 / ML-DSA / Kyber)

RE4CTOR ships with a post-quantum security layer, automatically enabled when liboqs is present.

Algorithm	Purpose	Status
ML-DSA-65 (Dilithium3)	VRF signature (FIPS 204)	✅ implemented
ML-KEM (Kyber512)	Key exchange for node-to-node comms	✅ implemented
SHAKE256 / BLAKE2s	Whitening / hash mixing	✅ implemented
ChaCha20	Entropy whitening inside the sealed core	✅ implemented
How it works

The API detects liboqs at runtime.

If available → dual-signs with ECDSA + ML-DSA-65.

If not → gracefully falls back to ECDSA-only, keeping CI and Docker builds simple.

Example PQ fields
{
  "sig_pq_b64": "Base64-encoded Dilithium signature",
  "pq_pubkey_b64": "Base64-encoded Dilithium public key",
  "pq_scheme": "ML-DSA-65"
}

FIPS 204 Roadmap

Q1 2025 — ML-DSA-65 integrated into Dual VRF

Q2 2025 — Kyber KEM key exchange

Q1 2026 — FIPS 140-3 / FIPS 204 submission

📘 See docs/FIPS_204_roadmap.md

🧱 On-Chain Verifier

Solidity contracts in vrf-spec/contracts/:

R4VRFVerifierCanonical.sol — canonical ECDSA (EIP-191) verifier

LotteryR4.sol — reference fair-lottery implementation

cd vrf-spec
npm ci
npx hardhat compile
npx hardhat test
# ✅ 6 passing


Verifier interface:

function verify(
    bytes32 randomness,
    uint8 v,
    bytes32 r,
    bytes32 s,
    address expectedSigner
) external pure returns (bool);

🛡️ Security & Entropy Source Validation (ESV)
FIPS-Style Self-Tests

Integrity SHA-256 of sealed binary

Known-Answer Test (ChaCha20)

Repetition / Adaptive Proportion / Continuous RNG tests

R4_STRICT_FIPS=1 → fail-closed startup mode

Statistical Validation
Suite	Result
NIST SP 800-22	15/15 ✅
Dieharder	31/31 ✅
PractRand	8 GiB ✅
TestU01 BigCrush	160/160 ✅

Artifacts in packages/core/proof/
Details in ESV_README.md

📅 Roadmap 2025
Quarter	Milestone	Status
Q1 2025	ML-DSA-65 (Dilithium3) signing	✅ Shipped
Q2 2025	Kyber KEM integration	✅ Shipped
Q3 2025	Solidity verifier audit + public testnet	✅ Complete
Q4 2025	Attestation & self-test hardening	✅ Complete
Q1 2026	FIPS 140-3 / 204 lab submission	🚀 In progress
2026	Certification decision window	⏳ Pending
🥊 R4 vs Competitors
Feature	R4	Chainlink VRF	drand	AWS HSM
Post-Quantum	✅ Dilithium	❌	❌	⚠️
Latency	<1 ms	30-120 s	3-30 s	10-50 ms
Cost	self-hosted	pay-per-req	free	$$$$
On-chain verify	✅	✅	⚠️	❌
Self-hosted	✅	❌	✅	⚠️
🎲 LotteryR4 (reference)

A transparent on-chain lottery showing how RE4CTOR randomness drives verifiable fairness.

Tests (vrf-spec/test):

✅ Valid signatures pass

✅ Invalid ones revert

✅ Deterministic winner selection

✅ Audit events emitted

✅ 6/6 tests passing

Workflow:

Players enter via enterLottery()

Backend calls /random_dual to obtain randomness + signature

Contract verifies with R4VRFVerifierCanonical

drawWinner() selects deterministic winner

Emitted event enables regulator audit

🗺️ Repository Structure
r4-monorepo/
├── README.md
├── run_full_demo.sh
├── tools/verify_vrf_msg_hash.py
├── api/
│   ├── app.py               # core :8080
│   ├── app_dual.py          # dual VRF :8083
│   ├── dual_router.py
│   ├── sign_ecdsa.py
│   └── sign_pq.py
├── vrf-spec/
│   ├── contracts/
│   │   ├── R4VRFVerifierCanonical.sol
│   │   └── LotteryR4.sol
│   ├── test/
│   │   ├── lottery.js
│   │   ├── verify.js
│   │   └── verify_r4_canonical.js
│   ├── scripts/deploy.js
│   ├── hardhat.config.js
│   └── package.json
├── packages/core/
│   ├── runtime/bin/re4_dump
│   ├── proof/
│   └── manifest/
├── docs/
│   ├── USAGE.md
│   ├── DEPLOYMENT.md
│   ├── COMPETITION.md
│   ├── FIPS_204_roadmap.md
│   └── proof/benchmarks_summary.md
└── docker/stubs/re4_dump

🤝 Contributing

We welcome PRs for:

New VRF verifiers (alt EVMs, L2s)

Additional test coverage

Performance scripts and benchmarks

See CONTRIBUTING.md
.

📞 Support

API Usage

Deployment Guide

Performance Benchmarks

FIPS 204 Roadmap

Competition Analysis

Community: GitHub Issues / Discussions
Enterprise Contact: 📧 shtomko@gmail.com
 (subject: R4 ENTERPRISE)
See SPONSORS.md

📬 Contact

Maintainer: Pavlo Tvardovskyi
📧 shtomko@gmail.com

🐙 @pipavlo82

🐳 Docker Hub

📦 PyPI

<div align="center">

Fairness you can prove. On-chain. Cryptographically.

</div>
✅ Next Step

Save as README.md, then commit:

git switch -c docs/final-readme
git add README.md
git commit -m "docs: unified English README (FIPS-204 PQ layer, dual VRF, 6/6 tests)"
git push -u origin docs/final-readme


Would you like me to also generate a shorter GitHub Description (2-line tagline) and About section (for repo header)?
Example:

“FIPS-ready verifiable randomness engine — ECDSA + Dilithium3 VRF, provably fair entropy appliance.”
