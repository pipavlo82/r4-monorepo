# 🚀 Deployment Guide — RE4CTOR / R4 Entropy Node

This guide explains how to deploy RE4CTOR in various environments:
- local development
- production Docker
- systemd service
- behind a reverse proxy

You are deploying **two services**:
- `:8080` — Core entropy API (raw crypto bytes, unsigned)
- `:8081` — PQ/VRF API (randomness + signature for on-chain verification)

> Minimal deployments can run only `:8080`.

---

## 1️⃣ Quick Local Run (Docker)

**Requirements:**
- Docker installed  
- Port `8080` available

```bash
docker run -d \
  --name r4-core \
  -p 8080:8080 \
  -e API_KEY=demo \
  pipavlo/r4-local-test:latest
Health check

bash
Copy code
curl -s http://127.0.0.1:8080/health
# → "ok"
Version / build attestation

bash
Copy code
curl -s http://127.0.0.1:8080/version | jq
Example output:

json
Copy code
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
Get random bytes

bash
Copy code
curl -s -H "X-API-Key: demo" \
  "http://127.0.0.1:8080/random?n=32&fmt=hex"
# → "a359b9dd843294e415ac0e41eb49ef90..."
2️⃣ Security / Auth
The API requires a key for /random.

Auth options:

Header → X-API-Key: <your-key>

Query → ?key=<your-key>

Pass it to Docker via env var:

bash
Copy code
docker run -d \
  --name r4-prod \
  -p 8080:8080 \
  -e API_KEY="super-secret-prod-key" \
  pipavlo/r4-local-test:latest
⚠️ Never deploy with API_KEY=demo in production.

3️⃣ Recommended Production Layout
Architecture:

java
Copy code
Internet → Reverse Proxy → R4 container (:8080)
RE4CTOR should not be exposed directly to the public Internet.

Use a reverse proxy (nginx / traefik / API gateway) to:

enforce IP allowlist

apply rate limits

handle TLS termination

log requests for audits

Example (nginx)

nginx
Copy code
server {
    listen 443 ssl;
    server_name entropy.example.com;

    location /random {
        proxy_pass http://127.0.0.1:8080/random;
        limit_req zone=r4 burst=10 nodelay;
        add_header X-Source r4-core;
    }

    location /health {
        proxy_pass http://127.0.0.1:8080/health;
    }

    location /version {
        proxy_pass http://127.0.0.1:8080/version;
    }
}
You can block /version from external access if desired — it’s mainly for internal attestation.

4️⃣ systemd Service (Long-Running Node)
If not using Kubernetes, use systemd to keep the Docker container always running.

Create service file:
/etc/systemd/system/r4-entropy.service

ini
Copy code
[Unit]
Description=R4 entropy API (:8080)
After=network-online.target
Wants=network-online.target

[Service]
Restart=always
RestartSec=2
ExecStart=/usr/bin/docker run --rm \
  --name r4-entropy \
  -p 8080:8080 \
  -e API_KEY=${R4_API_KEY} \
  pipavlo/r4-local-test:latest
ExecStop=/usr/bin/docker stop r4-entropy

# Hardening (recommended)
ProtectSystem=strict
ProtectHome=true
NoNewPrivileges=true
MemoryDenyWriteExecute=true

[Install]
WantedBy=multi-user.target
Enable & start:

bash
Copy code
sudo systemctl daemon-reload
sudo systemctl enable r4-entropy
sudo systemctl start r4-entropy
sudo systemctl status r4-entropy
Store your secret in /etc/default/r4-entropy or /etc/environment:

bash
Copy code
export R4_API_KEY="your-prod-key-here"
5️⃣ Running PQ/VRF Node (:8081)
The PQ/VRF node produces signed randomness — to be verified on-chain.

Example request:

bash
Copy code
curl -s -H "X-API-Key: demo" \
  "http://localhost:8081/random_pq?sig=ecdsa" | jq
Response:

json
Copy code
{
  "random": 2689836398,
  "timestamp": "2025-10-28T23:46:03Z",
  "v": 27,
  "r": "0x4fe30113...",
  "s": "0xce79a501...",
  "signer_addr": "0xC61b94A8e6aDf598c8a04737192F1591cC37Db1A",
  "pq_mode": false
}
Use (v,r,s) + signer_addr in Solidity (R4VRFVerifierCanonical) to prove fairness.

Enterprise builds:
?sig=dilithium → returns Dilithium3 (FIPS-204 / ML-DSA) post-quantum signatures.

⚠️ Never expose :8081 publicly.
Treat the PQ/VRF signer’s private key as critical infrastructure (like a validator key).

6️⃣ Health, Monitoring, Compliance
You should monitor and log:

/health → liveness

/version → integrity & attestation

Reverse proxy logs → IP, rate, bursts

/version response acts as:

boot attestation

hash verification

“self-test passed” statement for audit trails

Archive /version output after each restart as evidence of clean FIPS startup.

7️⃣ Production Checklist ✅
 API_KEY changed from default

 Service not exposed to open Internet

 Reverse proxy has rate limiting

 /version output logged for compliance

 stress_core.sh run on target hardware

 SBOM + signed manifest from packages/core/manifest/ backed up

 Access to :8081 limited (only internal trusted systems)

8️⃣ TL;DR
docker run ... → fine for dev

systemd → fine for bare-metal prod

Always protect access with API keys + proxy

PQ/VRF signer node = sensitive cryptographic infrastructure
