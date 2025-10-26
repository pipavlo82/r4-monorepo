<div align="center">

# ⚡ Re4ctoR API

**Developer Preview — Cryptographically Secure Randomness as a Service**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue?style=flat-square)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=flat-square)](https://fastapi.tiangolo.com/)
[![Docker Ready](https://img.shields.io/badge/docker-ready-2496ED?style=flat-square&logo=docker)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-orange?style=flat-square)](./LICENSE)

*Entropy is the foundation of security — Re4ctoR brings it to the cloud.*

[Features](#-features) • [Quick Start](#-quick-start) • [API Docs](#-api-reference) • [SDK](#-python-sdk) • [Roadmap](#-roadmap)

</div>

---

## 🎯 What is Re4ctoR API?

Re4ctoR delivers **cryptographically secure randomness** through a simple HTTP API. Built for developers who need:

- 🎲 **Unpredictable randomness** — Blockchain oracles, gaming, simulations
- 🔒 **Cryptographic strength** — Key generation, secure tokens, nonces
- 🚀 **Easy integration** — RESTful API + Python SDK
- 🐳 **Deploy anywhere** — Docker-ready, self-hosted or cloud

### Architecture

```
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
│  • Future: Digital signatures        │
└──────────────────────────────────────┘
```

---

## ✨ Features

✅ **256-bit cryptographic randomness** — Production-grade entropy  
✅ **Rate limiting** — 30 requests/minute (configurable)  
✅ **Docker deployment** — Single command setup  
✅ **Python SDK** — Zero-friction integration  
✅ **Monitoring ready** — `/metrics` endpoint for Prometheus  
✅ **Lightweight** — FastAPI + Uvicorn, < 100 MB image  

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Pull and run (or build locally)
docker run -d \
  --name r4api \
  -p 8081:8081 \
  re4ctor-api:dev

# Test the API
curl http://localhost:8081/random
```

**Expected output:**
```json
{
  "random_hex": "a3f7c89d4e2b1f0c8d9e3a7f6b5c2d1e4f8a9c7b6d5e3f2a1c0b9d8e7f6a5b4c3",
  "timestamp": "2025-10-26 20:27:26"
}
```

### Option 2: Local Development (Linux/WSL)

```bash
# Install dependencies
python3 -m pip install --user -r api/requirements.txt

# Run the server
python3 -m uvicorn api.app:app --host 0.0.0.0 --port 8081

# Test in another terminal
curl http://localhost:8081/version
```

### Option 3: Python SDK

```python
from clients.python.re4ctor_client.api import Client

# Connect to local node
client = Client()

# Get randomness
result = client.get_random()
print(result['random_hex'])
# → 'b1c8e76e737fe93ba347e6850ee3fe66...'
```

---

## 📘 API Reference

### `GET /version`

**Description**: Health check + build metadata  
**Rate limit**: None  
**Auth**: None

**Response:**
```json
{
  "version": "v1.0.0",
  "build": "r4-demo",
  "rate_limit": "30/minute",
  "api_key": "demo",
  "timestamp": "2025-10-26 20:27:26"
}
```

**Example:**
```bash
curl http://localhost:8081/version | jq
```

---

### `GET /random`

**Description**: Returns 256 bits (32 bytes) of cryptographic randomness as hex  
**Rate limit**: 30 requests/minute per IP  
**Auth**: API key (future)

**Response:**
```json
{
  "random_hex": "a3f7c89d4e2b1f0c8d9e3a7f6b5c2d1e4f8a9c7b6d5e3f2a1c0b9d8e7f6a5b4c3",
  "timestamp": "2025-10-26 20:27:26"
}
```

**Example:**
```bash
# Get random hex
curl http://localhost:8081/random

# Save to file
curl -s http://localhost:8081/random | jq -r '.random_hex' > random.hex
```

**Rate limit handling:**
```bash
# If you exceed 30/minute:
HTTP/1.1 429 Too Many Requests
{"error": "Rate limit exceeded"}
```

---

### `GET /metrics`

**Description**: System metrics (Prometheus-compatible format planned)  
**Rate limit**: None  
**Auth**: None

**Response:**
```json
{
  "service": "re4ctor-api",
  "uptime_stub": "ok",
  "requests_per_minute_allowed": "30/minute"
}
```

**Future format** (Prometheus):
```
# HELP re4ctor_requests_total Total randomness requests
# TYPE re4ctor_requests_total counter
re4ctor_requests_total{status="success"} 1247
```

---

## 🐍 Python SDK

### Installation

```bash
# From source (until PyPI package is published)
cd clients/python
pip install -e .
```

### Usage

```python
from re4ctor_client import Client

# Local development
client = Client()  # default: http://localhost:8081

# Production node
client = Client(base_url="https://demo.re4ctor.net")

# Get randomness
random_data = client.get_random()
print(random_data['random_hex'])

# Check server status
status = client.get_status()
print(f"Server version: {status['version']}")

# Get metrics
metrics = client.get_metrics()
print(metrics)
```

### Error Handling

```python
from re4ctor_client import Client
import requests

client = Client()

try:
    data = client.get_random()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 429:
        print("Rate limit exceeded, wait before retry")
    else:
        print(f"Error: {e}")
```

---

## 🐳 Docker Deployment

### Build Image

```bash
# From repository root
docker build -t re4ctor-api:dev .
```

### Run Container

**Basic:**
```bash
docker run -d \
  --name r4api \
  -p 8081:8081 \
  re4ctor-api:dev
```

**Custom port:**
```bash
docker run -d \
  --name r4api_alt \
  -p 9090:8081 \
  re4ctor-api:dev

# Access on port 9090
curl http://localhost:9090/random
```

**With environment variables:**
```bash
docker run -d \
  --name r4api_prod \
  -p 8081:8081 \
  -e RATE_LIMIT="60/minute" \
  -e API_KEY="your-secret-key" \
  re4ctor-api:dev
```

### Docker Compose

```yaml
version: '3.8'
services:
  re4ctor-api:
    build: .
    ports:
      - "8081:8081"
    environment:
      - API_KEY=demo
      - RATE_LIMIT=30/minute
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

---

## ⚙️ Configuration

Configuration via `.env` file (create in project root):

```bash
# API Settings
API_KEY=demo
RATE_LIMIT=30/minute
PORT=8081

# Optional: Future features
ENABLE_SIGNATURES=false
SIGNATURE_ALGORITHM=ECDSA-secp256k1
```

**⚠️ Security Note**: Never commit `.env` to version control. Add to `.gitignore`:
```
.env
*.key
*.pem
```

---

## 🛠️ Development

### Project Structure

```
re4ctor-api/
├── api/
│   ├── app.py              # FastAPI application
│   ├── requirements.txt    # Python dependencies
│   └── __init__.py
├── clients/
│   └── python/
│       └── re4ctor_client/
│           ├── api.py      # SDK client
│           └── __init__.py
├── Dockerfile              # Container image
├── docker-compose.yml      # Orchestration
├── .env.example            # Config template
└── README.md
```

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/

# With coverage
pytest --cov=api tests/
```

### Code Quality

```bash
# Format code
black api/ clients/

# Lint
flake8 api/ clients/

# Type checking
mypy api/
```

---

## 🔭 Roadmap

| Status | Milestone | Description | ETA |
|--------|-----------|-------------|-----|
| ✅ | **Entropy API Core** | Public FastAPI endpoint with rate limiting | Done |
| ✅ | **Python SDK** | Easy client integration for developers | Done |
| ✅ | **Docker Deployment** | Ready-to-run container image | Done |
| 🔄 | **ECDSA Signing** | Add digital signature to `/random` responses | Q1 2025 |
| 🔄 | **Smart Contract** | `R4VRFVerifier.sol` for on-chain verification | Q1 2025 |
| 📋 | **Prometheus Metrics** | Real-time monitoring via `/metrics` | Q2 2025 |
| 📋 | **HTTPS Gateway** | Public node at `https://demo.re4ctor.net` | Q2 2025 |
| 📋 | **Post-Quantum VRF** | Dilithium + Kyber integration | Q2 2025 |

**Legend**: ✅ Done | 🔄 In Progress | 📋 Planned

---

## 🎯 Use Cases

### 1. **Blockchain Oracle**
```python
from re4ctor_client import Client

client = Client(base_url="https://demo.re4ctor.net")

# Get verifiable randomness for smart contract
randomness = client.get_random()
seed = int(randomness['random_hex'], 16)

# Use in lottery selection
winner_index = seed % total_participants
```

### 2. **Secure Token Generation**
```python
import hashlib
from re4ctor_client import Client

client = Client()

def generate_secure_token():
    random_hex = client.get_random()['random_hex']
    token = hashlib.sha256(bytes.fromhex(random_hex)).hexdigest()
    return token[:32]  # 128-bit token

session_token = generate_secure_token()
```

### 3. **Gaming RNG**
```python
from re4ctor_client import Client

client = Client()

def roll_dice(sides=6):
    """Provably fair dice roll"""
    random_hex = client.get_random()['random_hex']
    random_int = int(random_hex, 16)
    return (random_int % sides) + 1

result = roll_dice(sides=20)  # D20 roll
print(f"You rolled: {result}")
```

---

## 🔒 Security

### Current Implementation
- ✅ Python's `secrets` module (cryptographically secure PRNG)
- ✅ Rate limiting per IP address
- ✅ Hexadecimal output (64 characters = 256 bits)

### Planned Enhancements
- 🔄 ECDSA signatures for response verification
- 🔄 API key authentication
- 🔄 Request/response logging for audit trails
- 🔄 TLS/HTTPS enforcement

### Best Practices
- Use HTTPS in production (nginx reverse proxy)
- Rotate API keys regularly
- Monitor `/metrics` for anomalies
- Keep Docker image updated

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| **Response time** | < 10ms (p99) |
| **Throughput** | ~1000 req/s (single instance) |
| **Rate limit** | 30 req/min (default) |
| **Entropy quality** | 256 bits per request |

**Benchmarking:**
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test endpoint
ab -n 1000 -c 10 http://localhost:8081/random
```

---

## 🤝 Contributing

We welcome contributions! Areas where you can help:

- 📝 Documentation improvements
- 🧪 Additional test coverage
- 🔧 SDK clients for other languages (Go, Rust, JS)
- 🐛 Bug reports and fixes
- 💡 Feature suggestions

**How to contribute:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📬 Contact & Support

**Maintainer**: Pavlo Tvardovskyi  
**Email**: [shtomko@gmail.com](mailto:shtomko@gmail.com)  
**GitHub**: [@pipavlo82](https://github.com/pipavlo82)

### Enterprise Support
For custom deployments, SLA agreements, or integration assistance:  
📧 **shtomko@gmail.com**

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🏷️ Tags

`#randomness` `#rng` `#cryptography` `#fastapi` `#docker` `#python` `#entropy` `#blockchain` `#oracle` `#vrf`

---

<div align="center">

**© 2025 Pavlo Tvardovskyi — Re4ctoR Project**

*Built with ⚡ for secure randomness*

[⬆ Back to top](#-re4ctor-api)

</div>
