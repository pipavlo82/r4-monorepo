# R4 Runtime / Deployment Guide

This document describes how to launch and verify the two operational components of **Re4ctoR (R4)**:  
- the **Core Entropy API (port 8080)**  
- and the **R4PQ / VRF API (port 8081)**

Both services are now functional and can be demonstrated live via a single command (`./run_all.sh`).

---

## ⚙️ 1. Port 8080 – Core Entropy API

### Purpose
- Provides high-quality cryptographic entropy directly from the local binary `re4_dump`.  
- Protected by an API key (`X-API-Key` header).  
- Designed for **FIPS 140-3 readiness**, secure custody, wallet seed generation, or HSM integration.  
- Works entirely offline.

### Launch
Script:
```bash
~/re4ctor-local/re4ctor-api/api_start.sh start
Environment file ~/re4ctor-local/re4ctor-api/.env contains:

ini
Copy code
API_KEY=local-demo
API_GIT=main
CORE_GIT=release-core
Endpoints
GET /version

json
Copy code
{"core_git":"release-core","api_git":"main"}
GET /random?n=16&fmt=raw
(requires header X-API-Key: local-demo)

nginx
Copy code
f15ac31f8b612703f1ce2a69cd61fab6
→ 16 bytes of raw entropy (hex)

🔐 2. Port 8081 – R4PQ / VRF API
Purpose
Delivers verifiable randomness with cryptographic signatures.

Designed for casinos, on-chain games, audits, and regulators.

Supports both classic ECDSA (secp256k1) and post-quantum Dilithium3 (FIPS 204 ML-DSA).

PQ-mode is declared but disabled in the demo build (returns 501 Enterprise notice).

Launch
Script:

bash
Copy code
~/re4ctor-local/pq-api/pq_start.sh start
Application: api.app:app (from ~/r4-monorepo/api/app.py)
Virtual env: ~/r4-monorepo/.venv/

Env variables:

ini
Copy code
API_KEY=demo
RATE_LIMIT=30/minute
PORT=8081
Key Endpoints
GET /version
json
Copy code
{
  "version": "v1.0.0",
  "build": "r4-demo",
  "rate_limit": "30/minute",
  "api_key": "demo",
  "timestamp": "2025-10-28 02:04:26"
}
GET /random
json
Copy code
{
  "random_hex": "543d3690742ad0149ffc80f74e41d96a3edca89fddbe43d69c657b83bcb7e24a",
  "timestamp": "2025-10-28 02:04:26"
}
GET /random_pq?sig=ecdsa
Verifiable randomness (ECDSA signature + public key):

json
Copy code
{
  "random": 264154896,
  "timestamp": "2025-10-28T02:04:26Z",
  "signature_type": "ECDSA(secp256k1)",
  "sig_b64": "raZi9AwyAEl5+E9wdhfSSiLgV+6uCUvgOywh+lbIIEpow95QMfem+LsL2ptNX66/z4FxJ5cOcalN6y/z+O1iGw==",
  "pubkey_b64": "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0K...LS0tLQo=",
  "hash_alg": "SHA-256",
  "pq_mode": false
}
✅ Compatible with Ethereum/Bitcoin curves.
Can be verified on-chain or off-chain.

GET /random_pq?sig=dilithium
Enterprise / FIPS 204 tier (post-quantum signature).
In the demo build returns 501:

json
Copy code
{
  "error": "Dilithium3 signature not available on this build",
  "pq_required": true,
  "status": 501,
  "hint": "Enterprise / FIPS 204 build required"
}
GET /metrics_pq
json
Copy code
{
  "service": "re4ctor-pq-api",
  "uptime_seconds": 403,
  "modes_supported": ["ecdsa","dilithium(unavailable)"],
  "fips_status": {
    "rng_core": "FIPS 140-3 ready",
    "pq_signature": "Not enabled in this build"
  },
  "note": "Use /random_pq for signed randomness and /verify_pq for audit."
}
🚀 3. One-Command Health Check
run_all.sh performs a full diagnostic of both nodes:

bash
Copy code
cd ~/r4-monorepo
./run_all.sh
Expected output:

text
Copy code
==============================
🔎 Checking CORE entropy node (8080)
==============================
{"core_git":"release-core","api_git":"main"}

→ /random (16 bytes hex)
f15ac31f8b612703f1ce2a69cd61fab6

==============================
🔐 Checking PQ / VRF node (8081)
==============================
{"version":"v1.0.0","build":"r4-demo","rate_limit":"30/minute","api_key":"demo","timestamp":"..."}

→ /random
{"random_hex":"543d3690742ad0149ffc80f74e41d96a3edca89fddbe43d69c657b83bcb7e24a","timestamp":"..."}

→ /random_pq?sig=ecdsa
{"random":264154896,"timestamp":"...","signature_type":"ECDSA(secp256k1)","sig_b64":"...","pubkey_b64":"...","hash_alg":"SHA-256","pq_mode":false}

→ /random_pq?sig=dilithium
{"error":"Dilithium3 signature not available on this build","pq_required":true,"status":501,"hint":"Enterprise / FIPS 204 build required"}

✅ done.
🧩 4. Service Control Scripts
Core Entropy API (8080)
bash
Copy code
~/re4ctor-local/re4ctor-api/api_start.sh {start|status|log|stop}
PQ / VRF API (8081)
bash
Copy code
~/re4ctor-local/pq-api/pq_start.sh {start|status|log|stop}
💼 5. Key Value Proposition
Layer	Purpose	Standard
8080 Core Entropy	Secure offline RNG for custody and HSM feeds	FIPS 140-3 ready
8081 R4PQ / VRF	Verifiable fairness / casino oracle / on-chain randomness	ECDSA(secp256k1), Dilithium3(FIPS 204 ML-DSA)

🟢 ./run_all.sh demonstrates both tiers live: local entropy + signed randomness.
The FIPS 204 /PQ mode is already declared and acts as your enterprise upgrade path.

Re4ctoR — Nuclear-grade entropy. Verifiable randomness. Post-quantum ready.
