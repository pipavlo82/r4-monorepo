#!/usr/bin/env bash
set -Eeuo pipefail

CORE_HOST="http://localhost:8080"
CORE_KEY="local-demo"

PQ_HOST="http://localhost:8081"
PQ_KEY="demo"

echo "=============================="
echo "🔎 Checking CORE entropy node (8080)"
echo "=============================="
curl -s "${CORE_HOST}/version" -H "X-API-Key: ${CORE_KEY}" || echo "[!] /version failed"
echo
echo

echo "→ /random (16 bytes hex)"
curl -s "${CORE_HOST}/random?n=16&fmt=raw" -H "X-API-Key: ${CORE_KEY}" || echo "[!] /random failed"
echo
echo

echo "=============================="
echo "🔐 Checking PQ / VRF node (8081)"
echo "=============================="

curl -s "${PQ_HOST}/version" -H "X-API-Key: ${PQ_KEY}" || curl -s "${PQ_HOST}/version" || echo "[!] /version failed"
echo
echo

echo "→ /random"
curl -s "${PQ_HOST}/random" -H "X-API-Key: ${PQ_KEY}" || curl -s "${PQ_HOST}/random" || echo "[!] /random failed"
echo
echo

echo "→ /random_pq?sig=ecdsa"
curl -s "${PQ_HOST}/random_pq?sig=ecdsa" -H "X-API-Key: ${PQ_KEY}" || curl -s "${PQ_HOST}/random_pq?sig=ecdsa" || echo "[!] /random_pq ecdsa failed"
echo
echo

echo "→ /random_pq?sig=dilithium"
curl -s "${PQ_HOST}/random_pq?sig=dilithium" -H "X-API-Key: ${PQ_KEY}" || curl -s "${PQ_HOST}/random_pq?sig=dilithium" || echo "[!] /random_pq dilithium failed"
echo
echo

echo "✅ done."
