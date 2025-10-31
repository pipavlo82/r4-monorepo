<div align="center">

# ⚡ Re4ctoR API

**Developer Preview — Cryptographically Secure Randomness as a Service**

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.x-green?style=flat-square)](https://fastapi.tiangolo.com/)
[![Docker Ready](https://img.shields.io/badge/docker-ready-2496ED?style=flat-square&logo=docker)](https://www.docker.com/)

*Entropy is the foundation of security — Re4ctoR brings it to the cloud.*

[Features](#-features) • [Quick Start](#-quick-start) • [API Docs](#-api-reference) • [SDK](#-python-sdk) • [Roadmap](#-roadmap)

</div>

---

## 🎯 What is Re4ctoR API?

Re4ctoR delivers **cryptographically secure randomness** through a simple HTTP API. Built for developers who need:

- 🎲 Unpredictable randomness — blockchain oracles, gaming, simulations  
- 🔒 Cryptographic strength — key generation, secure tokens, nonces  
- 🚀 Easy integration — REST API + Python SDK  
- 🐳 Deploy anywhere — Docker-ready, self-hosted or cloud  

### Architecture

```text
┌──────────────────────────────────────┐
│     FastAPI + Rate Limiting          │
│  /version  /random  /metrics         │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  Cryptographically Secure RNG        │
│  • 256-bit entropy per request       │
│  • Built-in rate limiting (slowapi)  │
│  • Future: digital signatures        │
└──────────────────────────────────────┘
✨ Features
✅ Dual-mode randomness: classical (ECDSA) + post-quantum (Dilithium3)
✅ 256-bit cryptographic randomness per request
✅ Per-IP rate limiting (default: 30 requests/minute)
✅ Docker deployment (single container, port 8081)
✅ Python SDK client with 3-line usage
✅ /metrics endpoint (Prometheus-ready placeholder)
✅ Simple .env config for API_KEY / RATE_LIMIT / PORT

🚀 Quick Start
Option 1: Docker (recommended)
bash
Copy code
docker build -t re4ctor-api:dev .
docker run -d \
  --name r4api \
  -p 8081:8081 \
  re4ctor-api:dev

curl http://localhost:8081/random
Example output:

json
Copy code
{
  "random_hex": "b1c8e76e737fe93ba347e6850ee3fe6693fb1f87402c6af397f9b3fe29c5b2b5",
  "timestamp": "2025-10-26 20:27:26"
}
Custom port:

bash
Copy code
docker run -d -p 9090:8081 re4ctor-api:dev
curl http://localhost:9090/random
Override runtime limits / API key:

bash
Copy code
docker run -d \
  -p 8081:8081 \
  -e RATE_LIMIT="60/minute" \
  -e API_KEY="your-secret-key" \
  re4ctor-api:dev
Option 2: Local development
bash
Copy code
python3 -m pip install --user -r api/requirements.txt
python3 -m uvicorn api.app:app --host 0.0.0.0 --port 8081
Test:

bash
Copy code
curl http://localhost:8081/version
curl http://localhost:8081/random
curl http://localhost:8081/metrics
.env file:

bash
Copy code
API_KEY=demo
RATE_LIMIT=30/minute
PORT=8081
Option 3: Python SDK
📦 PyPI: r4sdk

python
Copy code
from clients.python.re4ctor_client.api import Client

client = Client()
print(client.get_status())
print(client.get_random())
print(client.get_metrics())
📘 API Reference
GET /version
Purpose: Health check and build metadata
Auth: none
Rate limit: 10/minute

json
Copy code
{
  "version": "v1.0.0",
  "build": "r4-demo",
  "rate_limit": "30/minute",
  "api_key": "demo",
  "timestamp": "2025-10-26 20:27:26"
}
GET /random
Purpose: 256-bit cryptographic randomness (hex-encoded)
Rate limit: 30/minute per IP

json
Copy code
{
  "random_hex": "b1c8e76e737fe93ba347e6850ee3fe6693fb1f87402c6af397f9b3fe29c5b2b5",
  "timestamp": "2025-10-26 20:27:26"
}
Rate limit exceeded:

json
Copy code
{"detail":"Rate limit exceeded: 30 per 1 minute"}
GET /metrics
Purpose: Operational metrics (Prometheus-ready)
Rate limit: 60/minute

json
Copy code
{
  "service": "re4ctor-api",
  "uptime_stub": "ok",
  "requests_per_minute_allowed": "30/minute"
}
🧩 Post-Quantum Mode (Dilithium3)
Re4ctoR API now supports optional post-quantum signatures via CRYSTALS-Dilithium3
(FIPS 204 ML-DSA-ready).

Port 8081 provides classical entropy plus PQ-signed randomness:

bash
Copy code
curl "http://localhost:8081/random_pq?n=32&fmt=hex" | jq
Example response:

json
Copy code
{
  "random": "6a1ef5b7...",
  "signature": "dilithium3:abf8...",
  "public_key": "R4PQ_pub_dilithium3",
  "verified": true,
  "algorithm": "Dilithium3",
  "timestamp": "2025-10-27T12:00:00Z"
}
Verification:

bash
Copy code
curl -X POST http://localhost:8081/verify_pq \
  -H "Content-Type: application/json" \
  -d '{"random":"6a1ef5b7...","signature":"dilithium3:abf8..."}'
# → {"verified": true}
Latency: ~1.5 ms per request
Signature size: ~2700 bytes
Compliance: FIPS 204 ML-DSA (Dilithium3) ready

🐍 Python SDK
File: clients/python/re4ctor_client/api.py

python
Copy code
import os, requests

class Client:
    """Lightweight client for Re4ctoR API."""
    def __init__(self, base_url=None):
        self.base_url = base_url or os.getenv("R4_BASE_URL") or "http://localhost:8081"

    def get_status(self): return requests.get(f"{self.base_url}/version").json()
    def get_random(self): return requests.get(f"{self.base_url}/random").json()
    def get_metrics(self): return requests.get(f"{self.base_url}/metrics").json()
Usage:

python
Copy code
from clients.python.re4ctor_client.api import Client
c = Client()
print(c.get_status())
print(c.get_random())
print(c.get_metrics())
🔭 Roadmap
Status	Milestone	Description
✅	Entropy API Core	/random live and serving 256-bit entropy
✅	Rate limiting	Per-IP throttle using slowapi
✅	Python SDK	Minimal 3-line client
✅	Docker deployment	Single-container on port 8081
🔄	ECDSA signing	Signed randomness for VRF proof
🔄	Solidity verifier	On-chain ECDSA + PQ validation
🔄	Prometheus metrics	Operational counters in /metrics
🔜	HTTPS public node	https://demo.re4ctor.net
🔜	PQ VRF	Dilithium/Kyber-based VRF

🔒 Security
Current:

Python secrets for entropy

Per-IP rate limiting

Hex-encoded 256-bit output

Timestamped responses

Planned:

ECDSA signatures for /random

API key authentication

HTTPS (nginx proxy)

Full audit logging

📬 Contact & Support
Maintainer: Pavlo Tvardovskyi
Email: shtomko@gmail.com
GitHub: @pipavlo82

For enterprise or investor demos — email with subject “Re4ctoR”.

<div align="center">
© 2025 Pavlo Tvardovskyi — Re4ctoR Project
Built with ⚡ for secure randomness

⬆ Back to top

</div> ```
