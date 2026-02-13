#!/usr/bin/env bash
set -euo pipefail
BASE="${1:-http://127.0.0.1:8081}"
KEY="${2:-demo}"

echo "[1/4] health"
curl -sS "$BASE/health" | jq .

echo "[2/4] version"
curl -sS "$BASE/version" | jq .

echo "[3/4] random_dual?sig=ecdsa"
curl -sS -H "X-API-Key: $KEY" "$BASE/random_dual?sig=ecdsa" | jq .

echo "[4/4] random_dual_full?sig=dual"
curl -sS -H "X-API-Key: $KEY" "$BASE/random_dual_full?sig=dual" | jq .
