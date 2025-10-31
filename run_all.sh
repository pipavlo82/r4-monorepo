#!/usr/bin/env bash
set -Eeuo pipefail

CORE_HOST="${CORE_HOST:-http://localhost:8080}"
CORE_KEY="${CORE_KEY:-local-demo}"

PQ_HOST="${PQ_HOST:-http://localhost:8081}"
PQ_KEY="${PQ_KEY:-demo}"

JQ=$(command -v jq || true)
CURL="curl --fail --show-error --silent --location --max-time 5"

log()  { echo -e "$*"; }
sep()  { printf "%s\n" "=============================="; }
ok()   { log "✅ $*"; }
err()  { log "❌ $*" >&2; }
warn() { log "⚠️  $*"; }

# request helper: try with key, then without
req() {
  local url=$1
  local key=$2
  local out=${3:-}
  local hdr=()
  [[ -n "$key" ]] && hdr=( -H "X-API-Key: ${key}" )
  if [[ -n "$out" ]]; then
    if ! ${CURL} "${url}" "${hdr[@]}" -o "${out}"; then
      warn "auth failed for ${url}, retrying without key…"
      ${CURL} "${url}" -o "${out}"
    fi
  else
    if ! ${CURL} "${url}" "${hdr[@]}"; then
      warn "auth failed for ${url}, retrying without key…"
      ${CURL} "${url}"
    fi
  fi
}

PASS=0
FAIL=0
step() {
  local name="$1"
  shift
  if "$@"; then
    ok "$name"
    ((PASS++)) || true
  else
    err "$name"
    ((FAIL++)) || true
  fi
}

sep; log "🔎 Checking CORE entropy node (8080)"; sep

# /version
step "CORE /version" bash -c '
  req "'"${CORE_HOST}"'/version" "'"${CORE_KEY}"'" /tmp/r4_core_version.json
  if [[ -n "'"${JQ}"'" ]]; then jq . /tmp/r4_core_version.json; else cat /tmp/r4_core_version.json; fi >/dev/null
'

echo
log "→ CORE /random (16 bytes HEX)"
step "CORE /random?n=16&fmt=hex" bash -c '
  req "'"${CORE_HOST}"'/random?n=16&fmt=hex" "'"${CORE_KEY}"'" /tmp/r4_core_random_hex.txt
  cat /tmp/r4_core_random_hex.txt; echo
'

echo
sep; log "🔐 Checking PQ / VRF node (8081)"; sep

# /version
step "PQ /version" bash -c '
  req "'"${PQ_HOST}"'/version" "'"${PQ_KEY}"'" /tmp/r4_pq_version.json
  if [[ -n "'"${JQ}"'" ]]; then jq . /tmp/r4_pq_version.json; else cat /tmp/r4_pq_version.json; fi >/dev/null
'

echo
log "→ PQ /random"
step "PQ /random" bash -c '
  req "'"${PQ_HOST}"'/random" "'"${PQ_KEY}"'" /tmp/r4_pq_random.json
  if [[ -n "'"${JQ}"'" ]]; then jq . /tmp/r4_pq_random.json; else cat /tmp/r4_pq_random.json; fi >/dev/null
'

echo
log "→ PQ /random_pq?sig=ecdsa"
step "PQ /random_pq (ecdsa)" bash -c '
  req "'"${PQ_HOST}"'/random_pq?sig=ecdsa" "'"${PQ_KEY}"'" /tmp/vrf_dual.json
  if [[ -n "'"${JQ}"'" ]]; then jq . /tmp/vrf_dual.json; else head -c 400 /tmp/vrf_dual.json; fi >/dev/null
'

echo
log "→ PQ /random_pq?sig=dilithium (enterprise builds only)"
step "PQ /random_pq (dilithium)" bash -c '
  # цей ендпойнт може бути відсутній у community; не вважаємо за фатальну помилку
  if req "'"${PQ_HOST}"'/random_pq?sig=dilithium" "'"${PQ_KEY}"'" /tmp/vrf_dual_pq.json; then
    if [[ -n "'"${JQ}"'" ]]; then jq . /tmp/vrf_dual_pq.json; fi >/dev/null
    exit 0
  else
    warn "dilithium endpoint not available on this build"
    exit 0
  fi
'

echo
# Опційна локальна перевірка ECDSA (якщо є тул)
if [[ -f tools/verify_vrf_msg_hash.py ]]; then
  log "→ Verifying ECDSA locally (tools/verify_vrf_msg_hash.py)"
  step "ECDSA verify tool" bash -c '
    PYTHONPATH="$PWD" python3 tools/verify_vrf_msg_hash.py /tmp/vrf_dual.json | tee /tmp/vrf_verify_out.json
    # перевіряємо expected == recovered та hash_ok=true
    [[ -n "'"${JQ}"'" ]] && jq -e ".hash_ok == true and .ecdsa_ok == true" /tmp/vrf_verify_out.json >/dev/null
  '
else
  warn "ECDSA verifier script not found (tools/verify_vrf_msg_hash.py) — skipping local verification"
fi

sep
if (( FAIL == 0 )); then
  ok "All checks passed. (${PASS} OK)"
  exit 0
else
  err "Some checks failed. PASS=${PASS} FAIL=${FAIL} (див. /tmp/* для логів)"
  exit 1
fi
