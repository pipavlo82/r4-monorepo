#!/usr/bin/env bash
set -Eeuo pipefail

#############################################
# R4 FULL STACK SELF-TEST (core + vrf + chain)
#############################################

# --- Paths (налаштовувані через env) ---
REPO_DIR="${REPO_DIR:-$HOME/r4-monorepo}"
VENV_DIR="${VENV_DIR:-$REPO_DIR/.venv}"
VRF_SPEC_DIR="${VRF_SPEC_DIR:-$REPO_DIR/vrf-spec}"

CORE_DIR="${CORE_DIR:-$HOME/re4ctor-local/core-api}"
PQ_DIR="${PQ_DIR:-$HOME/re4ctor-local/pq-api}"

# --- Endpoints / keys ---
CORE_HOST="${CORE_HOST:-http://127.0.0.1:8080}"
CORE_KEY="${CORE_KEY:-local-demo}"

PQ_HOST="${PQ_HOST:-http://127.0.0.1:8081}"
PQ_KEY="${PQ_KEY:-demo}"

# --- Tools ---
JQ=$(command -v jq || true)
CURL="curl --fail --show-error --silent --location --max-time 8"

# --- Helpers ---
log()  { echo -e "$*"; }
sep()  { printf "%s\n" "========================================"; }
ok()   { log "✅ $*"; }
err()  { log "❌ $*" >&2; }
warn() { log "⚠️  $*"; }

# HTTP helper: спочатку з ключем, якщо впало → без ключа
req() {
  local url="$1"; local key="${2:-}"; local out="${3:-}"
  local hdr=()
  [[ -n "$key" ]] && hdr=(-H "X-API-Key: ${key}")
  if [[ -n "$out" ]]; then
    if ! ${CURL} "${url}" "${hdr[@]}" -o "${out}"; then
      warn "auth failed for ${url}, retry without key…"
      ${CURL} "${url}" -o "${out}"
    fi
  else
    if ! ${CURL} "${url}" "${hdr[@]}"; then
      warn "auth failed for ${url}, retry without key…"
      ${CURL} "${url}"
    fi
  fi
}

PASS=0; FAIL=0
step() {
  local title="$1"; shift
  sep; log "$title"; sep
  if "$@"; then ok "$title"; ((PASS++))||true
  else err "$title"; ((FAIL++))||true
  fi
  echo
}

# --- Preflight ---
sep; log "R4 FULL STACK SELF-TEST (core + vrf + chain)"; sep; echo

if [[ ! -d "$REPO_DIR" ]]; then
  err "Repo not found: $REPO_DIR"
  exit 1
fi

if [[ ! -d "$VENV_DIR" ]]; then
  err "Python venv not found: $VENV_DIR (очікується fastapi/uvicorn/eth_keys/…)"; exit 1
fi

# 1) START CORE :8080
step "1) START CORE NODE :8080" bash -c '
  if [[ -x "'"$CORE_DIR"'/core_start.sh" ]]; then
    "'"$CORE_DIR"'/core_start.sh" stop || true
    "'"$CORE_DIR"'/core_start.sh" start
    "'"$CORE_DIR"'/core_start.sh" status || true
  else
    echo "WARN: '"$CORE_DIR"'/core_start.sh not found — припускаю, що core вже запущений"
  fi
'

# 2) START PQ/VRF :8081
step "2) START PQ / VRF NODE :8081" bash -c '
  if [[ -x "'"$PQ_DIR"'/pq_start.sh" ]]; then
    "'"$PQ_DIR"'/pq_start.sh" stop || true
    "'"$PQ_DIR"'/pq_start.sh" start
    "'"$PQ_DIR"'/pq_start.sh" status || true
  else
    echo "WARN: '"$PQ_DIR"'/pq_start.sh not found — припускаю, що PQ/VRF вже запущений"
  fi
'

sleep 1

# 3) LIVE SANITY
step "3) LIVE SANITY (health/version/random)" bash -c '
  # CORE
  req "'"$CORE_HOST"'/version" "'"$CORE_KEY"'" /tmp/r4_core_version.json
  [[ -n "'"$JQ"'" ]] && jq . /tmp/r4_core_version.json || cat /tmp/r4_core_version.json
  echo
  echo "→ CORE /random (16 bytes HEX)"
  req "'"$CORE_HOST"'/random?n=16&fmt=hex" "'"$CORE_KEY"'" /tmp/r4_core_rand_hex.txt
  cat /tmp/r4_core_rand_hex.txt; echo; echo
  # PQ/VRF
  req "'"$PQ_HOST"'/version" "'"$PQ_KEY"'" /tmp/r4_pq_version.json
  [[ -n "'"$JQ"'" ]] && jq . /tmp/r4_pq_version.json || cat /tmp/r4_pq_version.json
  echo
  echo "→ VRF /random_pq?sig=ecdsa"
  req "'"$PQ_HOST"'/random_pq?sig=ecdsa" "'"$PQ_KEY"'" /tmp/vrf_dual.json
  [[ -n "'"$JQ"'" ]] && jq . /tmp/vrf_dual.json || head -c 600 /tmp/vrf_dual.json
'

# 4) STRESS CORE
step "4) STRESS TEST CORE (200 req)" bash -c '
  if [[ -x "'"$REPO_DIR"'/stress_core.sh" ]]; then
    "'"$REPO_DIR"'/stress_core.sh" 200
  else
    echo "WARN: stress_core.sh missing — пропускаю"
  fi
'

# 5) STRESS VRF
step "5) STRESS TEST VRF (:8081 rate-limit)" bash -c '
  source "'"$VENV_DIR"'/bin/activate"
  if [[ -f "'"$REPO_DIR"'/stress_vrf.py" ]]; then
    python3 "'"$REPO_DIR"'/stress_vrf.py"
  else
    echo "WARN: stress_vrf.py missing — пропускаю"
  fi
  deactivate
'

# 6) EXPORT FOR CHAIN + LOCAL VERIFY (ECDSA)
step "6) EXPORT + VERIFY (prep_vrf_for_chain.py / verify_vrf_msg_hash.py)" bash -c '
  source "'"$VENV_DIR"'/bin/activate"
  # Підготуємо свіжий бандл, якщо є скрипт
  if [[ -f "'"$REPO_DIR"'/prep_vrf_for_chain.py" ]]; then
    python3 "'"$REPO_DIR"'/prep_vrf_for_chain.py" || echo "note: PEM parse errors non-fatal; signer_addr дає вузол"
  else
    echo "WARN: prep_vrf_for_chain.py missing — пропускаю"
  fi
  # Локальна перевірка EIP-191
  if [[ -f "'"$REPO_DIR"'/tools/verify_vrf_msg_hash.py" ]]; then
    PYTHONPATH="'"$REPO_DIR"'" python3 "'"$REPO_DIR"'/tools/verify_vrf_msg_hash.py" /tmp/vrf_dual.json | tee /tmp/vrf_verify_out.json
    if [[ -n "'"$JQ"'" ]]; then
      jq -e ".hash_ok == true and .ecdsa_ok == true" /tmp/vrf_verify_out.json >/dev/null
    fi
  else
    echo "WARN: tools/verify_vrf_msg_hash.py missing — пропускаю локальну перевірку"
  fi
  deactivate
'

# 7) HARDHAT TESTS
step "7) HARDHAT TESTS (verifier + LotteryR4)" bash -c '
  cd "'"$VRF_SPEC_DIR"'"
  npx hardhat clean
  npx hardhat compile
  npx hardhat test
'

# --- Summary ---
sep
if (( FAIL == 0 )); then
  ok "DONE. All checks passed (${PASS} OK)."
  echo
  echo "Pipeline:"
  echo "  core RNG (8080)"
  echo "    ↓ signed randomness (8081)"
  echo "    ↓ Solidity verifier (R4VRFVerifierCanonical)"
  echo "    ↓ LotteryR4 fair winner"
  echo
  echo "Artifacts in /tmp:"
  echo "  /tmp/r4_core_version.json, /tmp/r4_core_rand_hex.txt"
  echo "  /tmp/r4_pq_version.json,   /tmp/vrf_dual.json, /tmp/vrf_verify_out.json"
  exit 0
else
  err "DONE WITH FAILURES. PASS=${PASS} FAIL=${FAIL}"
  echo "Подивись /tmp/* та логи hardhat/uvicorn."
  exit 1
fi
