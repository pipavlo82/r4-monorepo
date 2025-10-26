# Re4ctoR API — Developer Preview

**Re4ctoR** delivers **cryptographically secure randomness as a service**.

This repository contains:
- A public HTTP API (`/random`, `/version`, `/metrics`)
- Built-in **rate limiting** (via `slowapi`)
- A lightweight **Python SDK client**
- A **Dockerfile** for easy deployment

---

## 1. API Endpoints

### `GET /version`
Health check + build metadata.

**Example response:**
```json
{
  "version": "v1.0.0",
  "build": "r4-demo",
  "rate_limit": "30/minute",
  "api_key": "demo",
  "timestamp": "2025-10-26 20:27:26"
}
GET /random
Returns 256 bits of cryptographically secure randomness in hexadecimal form.

Example response:

json
Copy code
{
  "random_hex": "b1c8e76e737fe93ba347e6850ee3fe6693fb1f87402c6af397f9b3fe29c5b2b5",
  "timestamp": "2025-10-26 20:27:26"
}
GET /metrics
System metrics placeholder — future-ready for Prometheus / Grafana monitoring.

Example response:

json
Copy code
{
  "service": "re4ctor-api",
  "uptime_stub": "ok",
  "requests_per_minute_allowed": "30/minute"
}
2. Local Development (Linux / WSL)
bash
Copy code
python3 -m pip install --user -r api/requirements.txt
python3 -m uvicorn api.app:app --host 0.0.0.0 --port 8081
Then test the endpoints:

bash
Copy code
curl http://localhost:8081/version
curl http://localhost:8081/random
curl http://localhost:8081/metrics
Configuration is stored in .env (⚠️ do not commit this file):

bash
Copy code
API_KEY=demo
RATE_LIMIT=30/minute
PORT=8081
3. Docker Deployment
Build the image:
bash
Copy code
docker build -t re4ctor-api:dev .
Run the container:
bash
Copy code
docker run -d \
  --name r4api_dev \
  -p 8081:8081 \
  re4ctor-api:dev
Now test:

bash
Copy code
curl http://localhost:8081/random
If port 8081 is already in use:

bash
Copy code
docker run -d \
  --name r4api_alt \
  -p 9090:8081 \
  re4ctor-api:dev

curl http://localhost:9090/random
4. Python SDK Client
File: clients/python/re4ctor_client/api.py

python
Copy code
from clients.python.re4ctor_client.api import Client

# Local dev node (default: http://localhost:8081)
c = Client()
print(c.get_status())
print(c.get_random())
print(c.get_metrics())

# or use a public node
c = Client(base_url="https://demo.re4ctor.net")
print(c.get_random())
5. Technical Roadmap
Milestone	Description
✅ Entropy API (Core)	Public FastAPI endpoint with rate limiting
✅ Python SDK	Easy client integration for developers
🧩 Dockerized Deployment	Ready-to-run container image
🔒 ECDSA Signing	Add digital signature to /random
🔗 Smart Contract (R4VRFVerifier.sol)	On-chain verification of randomness
📈 Prometheus Metrics	Real-time monitoring via /metrics
🌐 Nginx HTTPS Gateway	Public node under https://demo.re4ctor.net

6. About
Re4ctoR is a high-entropy randomness infrastructure designed for:

Blockchain oracles and VRFs

Post-quantum cryptography

Secure gaming, lotteries, and simulations

Research and verification environments

“Entropy is the foundation of security — Re4ctoR brings it to the cloud.”

© 2025 Pavlo Tvardovskyi — Re4ctoR Project
