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
# Build the image from this repo
docker build -t re4ctor-api:dev .

# Run the container
docker run -d \
  --name r4api \
  -p 8081:8081 \
  re4ctor-api:dev

# Test the API
curl http://localhost:8081/random
Example output:

json
Copy code
{
  "random_hex": "b1c8e76e737fe93ba347e6850ee3fe6693fb1f87402c6af397f9b3fe29c5b2b5",
  "timestamp": "2025-10-26 20:27:26"
}
Custom port if 8081 is busy:

bash
Copy code
docker run -d \
  --name r4api_alt \
  -p 9090:8081 \
  re4ctor-api:dev

curl http://localhost:9090/random
Override runtime limits / API key:

bash
Copy code
docker run -d \
  --name r4api_prod \
  -p 8081:8081 \
  -e RATE_LIMIT="60/minute" \
  -e API_KEY="your-secret-key" \
  re4ctor-api:dev
Option 2: Local development (WSL / Linux)
bash
Copy code
python3 -m pip install --user -r api/requirements.txt
python3 -m uvicorn api.app:app --host 0.0.0.0 --port 8081
In another terminal:

bash
Copy code
curl http://localhost:8081/version
curl http://localhost:8081/random
curl http://localhost:8081/metrics
.env file (not committed, ignored by .gitignore):

bash
Copy code
API_KEY=demo
RATE_LIMIT=30/minute
PORT=8081
Option 3: Python SDK
python
Copy code
from clients.python.re4ctor_client.api import Client

# Connect to local node (default http://localhost:8081)
client = Client()

print(client.get_status())
print(client.get_random())
print(client.get_metrics())

# Or point to a remote node (future public HTTPS endpoint)
client_prod = Client(base_url="https://demo.re4ctor.net")
print(client_prod.get_random())
📘 API Reference
GET /version
Purpose: Health check and build metadata
Auth: none
Rate limit: 10/minute

Response:

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
Auth: API key (planned)
Rate limit: default 30/minute per IP

Response:

json
Copy code
{
  "random_hex": "b1c8e76e737fe93ba347e6850ee3fe6693fb1f87402c6af397f9b3fe29c5b2b5",
  "timestamp": "2025-10-26 20:27:26"
}
If you exceed rate limit:

json
Copy code
{"detail":"Rate limit exceeded: 30 per 1 minute"}
GET /metrics
Purpose: Operational metrics (Prometheus-ready in future)
Auth: none
Rate limit: 60/minute

Response:

json
Copy code
{
  "service": "re4ctor-api",
  "uptime_stub": "ok",
  "requests_per_minute_allowed": "30/minute"
}
🐍 Python SDK
File: clients/python/re4ctor_client/api.py

python
Copy code
import os
import requests

class Client:
    """
    Lightweight client for Re4ctoR API.
    Default base_url = http://localhost:8081
    """

    def __init__(self, base_url=None):
        self.base_url = (
            base_url
            or os.getenv("R4_BASE_URL")
            or "http://localhost:8081"
        )

    def get_status(self):
        r = requests.get(f"{self.base_url}/version", timeout=5)
        r.raise_for_status()
        return r.json()

    def get_random(self):
        r = requests.get(f"{self.base_url}/random", timeout=5)
        r.raise_for_status()
        return r.json()

    def get_metrics(self):
        r = requests.get(f"{self.base_url}/metrics", timeout=5)
        r.raise_for_status()
        return r.json()
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
✅	Python SDK	Minimal client usable in 3 lines
✅	Docker deployment	Single-container service on port 8081
🔄	ECDSA signing in /random	Signed randomness + public key for verification
🔄	Smart contract R4VRFVerifier.sol	On-chain verification (ECDSA first, PQ after)
🔄	Prometheus metrics	Real operational counters via /metrics
🔜	HTTPS public node	https://demo.re4ctor.net behind nginx + rate limit
🔜	PQ VRF	Dilithium/Kyber-backed post-quantum randomness

Legend: ✅ Done · 🔄 In progress · 🔜 Planned

🔒 Security
Current:

Uses Python secrets (cryptographically strong)

Per-IP rate limiting

Hex output of 256-bit entropy

Timestamped responses

Planned:

ECDSA signatures for /random

API key auth

HTTPS via nginx reverse proxy

Audit logging for compliance / fairness proofs

📬 Contact & Support
Maintainer: Pavlo Tvardovskyi
Email: shtomko@gmail.com
GitHub: https://github.com/pipavlo82

For integration / infra / investor demos:
Email with subject Re4ctoR.

<div align="center">
© 2025 Pavlo Tvardovskyi — Re4ctoR Project
Built with ⚡ for secure randomness

⬆ Back to top

</div> ```
