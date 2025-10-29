☢️ RE4CTOR — The Nuclear Core of Randomness

Provable entropy • Post-quantum trust • Verified fairness










🧠 Overview

Re4ctor (R4) — high-assurance entropy appliance + post-quantum verifiable randomness platform.

It includes:

🔒 Entropy Core (8080) — sealed binary re4_dump, Dieharder / PractRand / BigCrush validated

🔐 PQ-VRF Node (8081) — ECDSA & Dilithium3 (FIPS 204) signatures

💠 On-chain Verifier — Solidity contracts verifying R4 signatures

🧬 Python SDK (r4sdk) — available on PyPI

🚀 One-Command Demo
./run_full_demo.sh


Runs both nodes (8080 + 8081), fetches signed randomness, performs stress-tests, runs Solidity tests, and proves a fair lottery draw.

Expected output:

✅ 8080 entropy OK
✅ 8081 PQ/VRF OK
✅ 200 req/sec no errors
✅ Hardhat tests: 5 passing
✅ LotteryR4: fair winner verified

🐳 Docker Quickstart
docker run -d -p 8080:8080 \
  -e API_KEY=demo \
  pipavlo/r4-local-test:latest


Health:

curl http://127.0.0.1:8080/health


Random bytes:

curl -H "x-api-key: demo" \
  "http://127.0.0.1:8080/random?n=32&fmt=hex"

🐍 Python SDK (r4sdk)

Install:

pip install r4sdk


Use:

from r4sdk import R4Client
client = R4Client(api_key="demo", host="http://localhost:8080")
print(client.get_random(16).hex())


Signed randomness:

import requests, json
r = requests.get("http://localhost:8081/random_pq?sig=ecdsa",
                 headers={"X-API-Key":"demo"}).json()
print(json.dumps(r, indent=2))

🔐 API Reference
Node	Port	Signature	Endpoint examples
Core	8080	none	/health, /version, /random?n=32
PQ-VRF	8081	ECDSA / Dilithium	/random_pq?sig=ecdsa, /random_pq?sig=dilithium
📊 Security & Compliance
Test	Result
NIST SP 800-22	✅ 15 / 15 passed
Dieharder	✅ 31 / 31
PractRand	✅ 8 GB, no anomalies
TestU01 BigCrush	✅ 160 / 160

Proofs live under packages/core/proof/
.
Each release ships with sha256, gpg, and SBOM.spdx.json.

⚙️ Performance
Metric	Value
Throughput	~950 k req/s
Latency (p99)	~1 ms
Entropy bias	< 10⁻⁶
Max req	1 MB
📅 Roadmap 2025
Quarter	Milestone	Status
Q1	Dilithium 3 PQ signatures	✅ Done
Q2	Kyber KEM integration	✅ Done
Q3	Solidity audit / testnet	✅ Done
Q4	FIPS 140-3 / 204 lab submission	🚀 In progress
🧪 MVP Status
Feature	Status	Notes
Entropy core	✅	FIPS self-test
PQ node (8081)	✅	ECDSA + Dilithium
Hardhat tests	✅	5/5 passing
Stress tools	✅	stress_core.sh, stress_vrf.py
SDK on PyPI	✅	r4sdk v0.1.5
Docker image	✅	pipavlo/r4-local-test
📊 Quick Comparison
Feature	R4	Chainlink VRF	drand	API3 QRNG	AWS HSM
Post-Quantum Ready	✅ Dilithium + Kyber	❌	❌	❌	⚠️ Partial
Latency	< 1 ms	30–120 s	30 s	20 s	10–50 ms
Cost Model	Self-hosted	Pay per req	Free	dAPI	$$$
On-chain Verify	✅ Solidity	✅	⚠️ External	✅	❌
Auditability	✅ Open	✅	✅	⚠️	❌
FIPS 204 Path	🚀 In progress	❌	❌	❌	✅

Full comparison: docs/COMPETITORS.md

🧬 Architecture
┌──────────────┐
│ Core 8080    │
│ /random      │
└─────┬────────┘
      ↓
┌──────────────┐
│ PQ VRF 8081  │
│ /random_pq   │
└─────┬────────┘
      ↓
┌──────────────┐
│ Solidity VRF │
│ Verifier & LotteryR4 │
└──────────────┘

🧭 Repository Map
r4-monorepo/
├── packages/core/          # sealed entropy binary + proofs
├── api/                    # FastAPI 8080
├── pq-api/                 # PQ/VRF node 8081
├── sdk_py_r4/              # Python SDK (PyPI)
├── vrf-spec/               # Solidity + Hardhat tests
├── docs/                   # comparison, deployment, proof
├── stress_core.sh / stress_vrf.py
└── run_full_demo.sh

🏷️ Release Tag

v1.0.0-demo — complete end-to-end reproducible demo (core → PQ/VRF → Solidity).

📬 Contact & Support

Maintainer: Pavlo Tvardovskyi
📧 shtomko@gmail.com

🐙 github.com/pipavlo82

🐳 hub.docker.com/r/pipavlo/r4-local-test

📦 PyPI r4sdk

🧠 Mission Statement

R4 is the fastest, cheapest way to get verifiable randomness for blockchain, gaming, and validator rotation — self-hosted, FIPS-tested, post-quantum-ready.

© 2025 Re4ctoR Project • Built with ⚡ for provable entropy and verifiable fairness.
