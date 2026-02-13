Minimal public-facing FastAPI service exposing a **dual-signature random** endpoint:
- ECDSA (secp256k1) signer included (demo-only key via env).
- ML-DSA-65 is currently a **stub** in this public repo (placeholder to keep API shape stable).

## Quickstart (local)

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements-public.txt

export PYTHONPATH=$PWD
export VRF_KEY=demo
# Optional demo-only ECDSA private key (DO NOT use in production)
export ECDSA_PRIVKEY=0x59c6995e998f97a5a0044966f094538b292a2e2b0f1b9b7a0f6f4b9b9b2e8d4a

python -m uvicorn api.app:app --host 0.0.0.0 --port 8081
Auth
All randomness endpoints require X-API-Key.

Example demo key:

X-API-Key: demo

Endpoints
GET /health

GET /version

GET /random_dual?sig=ecdsa

GET /random_dual_full?sig=dual

Example calls
curl -sS http://127.0.0.1:8081/health | jq .
curl -sS http://127.0.0.1:8081/version | jq .

curl -sS -H "X-API-Key: demo" \
  "http://127.0.0.1:8081/random_dual?sig=ecdsa" | jq .

curl -sS -H "X-API-Key: demo" \
  "http://127.0.0.1:8081/random_dual_full?sig=dual" | jq .
OpenAPI
Swagger UI: http://127.0.0.1:8081/docs

OpenAPI JSON: http://127.0.0.1:8081/openapi.json

Notes
ML-DSA-65 is a stub here (placeholder only).

ECDSA_PRIVKEY is demo-only. Never use a shared/private key in production.
