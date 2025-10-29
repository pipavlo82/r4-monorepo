# 🚀 Deployment Guide — RE4CTOR / R4 entropy node

This guide shows how to run RE4CTOR in different environments:
- local dev
- prod Docker
- systemd service
- behind reverse proxy

You are deploying **two services**:
- `:8080` Core entropy API (raw crypto bytes, unsigned)
- `:8081` PQ/VRF API (randomness + signature for on-chain verification)

> In minimal deployments you can run only `:8080`.

---

## 1. Quick local run (Docker)

Prereqs:
- Docker installed
- Port 8080 free

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
You should see:

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
2. Security / Auth
The API requires a key for /random.

You can send it:

as header → X-API-Key: <your-key>

or as query → ?key=<your-key>

In Docker you pass it as env:

bash
Copy code
docker run -d \
  --name r4-prod \
  -p 8080:8080 \
  -e API_KEY="super-secret-prod-key" \
  pipavlo/r4-local-test:latest
Never ship with API_KEY=demo in prod.

3. Recommended production layout
Edge / reverse proxy → R4 container (8080)

R4 is not supposed to be exposed publicly to the whole internet

Put it behind nginx / traefik / API gateway

Enforce IP allowlist + rate limit up front

Example nginx (very simple sketch):

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
Why reverse proxy?

per-IP throttling

TLS termination

audit logging

you can completely block /version from external if you want

4. systemd service (hosted long-running node)
If you're not using Kubernetes and you just want “run this forever on a box” — use systemd that wraps Docker.

Create (for example) /etc/systemd/system/r4-entropy.service:

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

# Hardening suggestions (host-level)
ProtectSystem=strict
ProtectHome=true
NoNewPrivileges=true
MemoryDenyWriteExecute=true

[Install]
WantedBy=multi-user.target
Then:

bash
Copy code
sudo systemctl daemon-reload
sudo systemctl enable r4-entropy
sudo systemctl start r4-entropy
sudo systemctl status r4-entropy
Put the secret in /etc/default/r4-entropy or /etc/environment:

bash
Copy code
export R4_API_KEY="your-prod-key-here"
5. Running PQ/VRF node (:8081)
The PQ/VRF node exposes signed randomness and is what you feed into smart contracts.

Typical call:

bash
Copy code
curl -H "X-API-Key: demo" \
  "http://localhost:8081/random_pq?sig=ecdsa" | jq
Example response:

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
Use v,r,s + signer_addr in Solidity to prove fairness on-chain.

Enterprise build supports ?sig=dilithium, returning Dilithium3 / FIPS 204 post-quantum signature.

⚠ This node should definitely not be internet-public without auth + rate limiting. Treat its signer key like infrastructure private key.

6. Health, monitoring, compliance
You should scrape:

/health (liveness)

/version (attestation)

reverse proxy logs (who requested randomness, rate, burst events)

The /version response is also your “this box booted clean, self-test passed, hash matches signed manifest” evidence for your auditors.

7. Checklist for production
 You changed API_KEY from default

 Service is NOT directly exposed to the open internet

 Reverse proxy has rate limiting

 /version output logged somewhere (compliance trail)

 You ran stress_core.sh on your hardware at least once

 You backed up SBOM + signed manifest from packages/core/manifest/

 You locked who can access :8081 (PQ/VRF signer node)

8. TL;DR
docker run ... is fine for dev

systemd unit is fine for “prod on bare metal”

you MUST protect access with API keys + proxy

PQ/VRF signer node is sensitive infra (treat it like validator key)
