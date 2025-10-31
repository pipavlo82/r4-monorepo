#!/usr/bin/env bash
set -Eeuo pipefail

cd "$HOME/r4-monorepo"
source .venv/bin/activate

API_KEY="${API_KEY:-demo}"
VRF_URL="${VRF_URL:-http://127.0.0.1:8083}"

# 1) тягнемо свіжий пакет
curl -sS -H "X-API-Key: $API_KEY" "$VRF_URL/random_pq?sig=ecdsa" -o /tmp/vrf.json

# 2) перевіряємо підпис Python’ом (без node/jq)
python3 tools/verify_vrf_local.py /tmp/vrf.json
