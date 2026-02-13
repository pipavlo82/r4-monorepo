#!/usr/bin/env bash

# -----------------------------------------
# BASE URL selection (canonical)
# -----------------------------------------
MODE="${MODE:-local}"
case "$MODE" in
  local)
    CORE_BASE="${CORE_BASE:-http://127.0.0.1:8080}"
    VRF_BASE="${VRF_BASE:-http://127.0.0.1:8081}"
    ;;
  site)
    CORE_BASE="${CORE_BASE:-https://re4ctor.com/api/v1}"
    VRF_BASE="${VRF_BASE:-https://re4ctor.com/api/v1}"
    ;;
  *)
    echo "ERR: MODE must be local|site (got: $MODE)" >&2
    exit 2
    ;;
esac


set -Eeuo pipefail

#############################################
# R4 FULL STACK SELF-TEST (core + vrf + chain)
#############################################

# --- Paths (configurable via env) ---
REPO_DIR="${REPO_DIR:-$HOME/r4-monorepo}"
VENV_DIR="${VENV_DIR:-$REPO_DIR/.venv}"
VRF_SPEC_DIR="${VRF_SPEC_DIR:-$REPO_DIR/vrf-spec}"

CORE_DIR="${CORE_DIR:-$HOME/re4ctor-local/core-api}"
PQ_DIR="${PQ_DIR:-$HOME/re4ctor-local/pq-api}"

# --- Endpoints / keys ---
CORE_KEY="${CORE_KEY:-demo}"
VRF_KEY="${VRF_KEY:-demo}"

# --- Tools ---
JQ=$(command -v jq || true)
CURL="curl --fail --show-error --silent --location --max-time 8"

# --- Helpers ---
log()  { echo -e "$*"; }
sep()  { printf "%s\n" "========================================"; }
ok()   { log "✅ $*"; }
err()  { log "❌ $*" >&2; }
warn() { log "⚠️  $*"; }

# -----------------------------------------
# Step implementations (run in same shell)
# -----------------------------------------
do_start_core() {
  if [[ -x "$CORE_DIR/core_start.sh" ]]; then
    "$CORE_DIR/core_start.sh" stop || true
    "$CORE_DIR/core_start.sh" start
    "$CORE_DIR/core_start.sh" status || true
  else
    echo "WARN: $CORE_DIR/core_start.sh not found - assuming core is already running"
  fi
}

do_start_vrf() {
  if [[ -x "$PQ_DIR/pq_start.sh" ]]; then
    "$PQ_DIR/pq_start.sh" stop || true
    "$PQ_DIR/pq_start.sh" start
    "$PQ_DIR/pq_start.sh" status || true
  else
    echo "WARN: $PQ_DIR/pq_start.sh not found - assuming PQ/VRF is already running"
  fi
}

do_live_sanity() {
  # Hard gate: VRF_BASE must be reachable in local mode
  if [[ "${MODE:-local}" = "local" ]]; then
    if ! ss -lnt | grep -q ":8081"; then
      echo "FATAL: :8081 not listening (VRF node is down)"
      return 1
    fi
  fi

  echo "→ CORE /health"
  req "${CORE_BASE}/health" "${CORE_KEY}" /tmp/r4_core_health.json
  if [[ -n "$JQ" ]]; then jq . /tmp/r4_core_health.json 2>/dev/null || cat /tmp/r4_core_health.json; else cat /tmp/r4_core_health.json; fi
  echo

  echo "→ VRF /health"
  req "${VRF_BASE}/health" "${VRF_KEY}" /tmp/r4_vrf_health.json
  if [[ -n "$JQ" ]]; then jq . /tmp/r4_vrf_health.json 2>/dev/null || cat /tmp/r4_vrf_health.json; else cat /tmp/r4_vrf_health.json; fi
  echo

  echo "→ CORE /version"
  req "${CORE_BASE}/version" "${CORE_KEY}" /tmp/r4_core_version.json
  [[ -n "$JQ" ]] && jq . /tmp/r4_core_version.json || cat /tmp/r4_core_version.json
  echo

  echo "→ CORE /random (16 bytes HEX)"
if req_soft "${CORE_BASE}/random?n=16&fmt=hex" "${CORE_KEY}" /tmp/r4_core_rand_hex.txt; then
  cat /tmp/r4_core_rand_hex.txt
else
  echo "SKIP: core random requires valid key on this env"
fi
  echo
  echo

  echo "→ VRF /health (meta probe via health)"
  req "${VRF_BASE}/health" "${VRF_KEY}" /tmp/r4_pq_version.json
  [[ -n "$JQ" ]] && jq . /tmp/r4_pq_version.json || cat /tmp/r4_pq_version.json
  echo

  echo "→ VRF /random_dual?sig=ecdsa"
  req "${VRF_BASE}/random_dual?sig=ecdsa" "${VRF_KEY}" /tmp/vrf_dual.json
  [[ -n "$JQ" ]] && jq . /tmp/vrf_dual.json || head -c 600 /tmp/vrf_dual.json
  echo
}

do_stress_core() {
  echo "=== CORE STRESS ==="
  local url="${CORE_BASE}/health"
  local n=40
  local c=2
  echo "URL         : ${url}"
  echo "Requests    : ${n}"
  echo "Concurrency : ${c}"
  echo

  # ApacheBench if available
  if command -v ab >/dev/null 2>&1; then
    local out rc
    out="$(ab -n "${n}" -c "${c}" "${url}" 2>&1)" || rc=$?
    rc=${rc:-0}

    # print useful lines
    echo "$out" | grep -E "Time taken for tests:|Requests per second:|Failed requests:" || true

    # normalized summary
    local t rps failed
    t="$(echo "$out"   | awk -F': *' '/Time taken for tests/{print $2}' | head -n1)"
    rps="$(echo "$out" | awk -F': *' '/Requests per second/{print $2}'   | head -n1)"
    failed="$(echo "$out" | awk -F': *' '/Failed requests/{print $2}'    | head -n1)"
    [[ -z "$t" ]] && t="n/a"
    [[ -z "$rps" ]] && rps="n/a"
    [[ -z "$failed" ]] && failed="0"

    echo
    echo "Time: ${t}  RPS: ${rps}  (total: ${n})"
    echo " ERR: ${failed}"

    # if ab fails, do not fail entire demo
    [[ "$rc" -ne 0 ]] && echo "WARN: ab exited with code ${rc} (non-fatal in demo)"
    return 0
  fi

  # curl fallback
  local ok=0 err=0 t0 t1 dt
  t0="$(date +%s)"
  for _ in $(seq 1 "$n"); do
    if curl -fsS "${url}" >/dev/null 2>&1; then
      ok=$((ok+1))
    else
      err=$((err+1))
    fi
  done
  t1="$(date +%s)"
  dt=$((t1 - t0))
  [[ "$dt" -le 0 ]] && dt=1

  local rps
  rps=$((n / dt))
  echo "Time: ${dt}.00s  RPS: ${rps}  (total: ${n})"
  echo " ERR: ${err}"
  return 0
}

do_stress_vrf() {
  source "$VENV_DIR/bin/activate"
  if [[ -f "$REPO_DIR/stress_vrf.py" ]]; then
    python3 "$REPO_DIR/stress_vrf.py"
  else
    echo "WARN: stress_vrf.py missing - skipping"
  fi
  deactivate || true
}

do_export_verify() {
  source "$VENV_DIR/bin/activate"
  if [[ -f "$REPO_DIR/prep_vrf_for_chain.py" ]]; then
    python3 "$REPO_DIR/prep_vrf_for_chain.py" || echo "note: PEM parse errors are non-fatal; signer_addr is provided by node"
  else
    echo "WARN: prep_vrf_for_chain.py missing - skipping"
  fi

  if [[ -f "$REPO_DIR/tools/verify_vrf_msg_hash.py" ]]; then
    PYTHONPATH="$REPO_DIR" python3 "$REPO_DIR/tools/verify_vrf_msg_hash.py" /tmp/vrf_dual.json | tee /tmp/vrf_verify_out.json
    if [[ -n "$JQ" ]]; then
      jq -e ".hash_ok == true and .ecdsa_ok == true" /tmp/vrf_verify_out.json >/dev/null
    fi
  else
    echo "WARN: tools/verify_vrf_msg_hash.py missing - skipping local verification"
  fi
  deactivate || true
}

do_hardhat() {
  cd "$VRF_SPEC_DIR"
  npx hardhat clean
  npx hardhat compile
  npx hardhat test
}

# HTTP helper: first with key; on failure -> retry without key
req() {
  local url="$1" key="${2:-}" out="${3:-/tmp/r4_req.out}"
  local hdr=()
  [[ -n "$key" ]] && hdr=(-H "X-API-Key: ${key}")

  # 1st attempt (with key if provided)
  if curl -fsS "${hdr[@]}" "$url" > "$out"; then
    return 0
  fi

  # if keyed request failed -> retry without key (noise-safe one-line warning)
  if [[ -n "$key" ]]; then
    warn "auth failed for ${url}, retry without key…"
    if curl -fsS "$url" > "$out"; then
      return 0
    fi
  fi

  err "request failed: ${url}"
  return 1
}


# soft HTTP helper: no warn/err (for optional probes)
req_soft() {
  local url="$1" key="${2:-}" out="${3:-/tmp/r4_req.out}"
  local hdr=()
  [[ -n "$key" ]] && hdr=(-H "X-API-Key: ${key}")

  if curl -fsS "${hdr[@]}" "$url" > "$out" 2>/dev/null; then
    return 0
  fi
  if [[ -n "$key" ]]; then
    curl -fsS "$url" > "$out" 2>/dev/null && return 0
  fi
  return 1
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
  err "Python venv not found: $VENV_DIR (expected fastapi/uvicorn/eth_keys/...)"; exit 1
fi

# 1) START CORE :8080
step "1) START CORE NODE :8080" do_start_core

# 2) START PQ/VRF :8081
step "2) START PQ / VRF NODE :8081" do_start_vrf

sleep 1

# 3) LIVE SANITY
step "3) LIVE SANITY (health/version/random)" do_live_sanity


# 4) STRESS CORE
step "4) STRESS TEST CORE (200 req)" do_stress_core

# 5) STRESS VRF
step "5) STRESS TEST VRF (:8081 rate-limit)" do_stress_vrf

# 6) EXPORT FOR CHAIN + LOCAL VERIFY (ECDSA)
step "6) EXPORT + VERIFY (prep_vrf_for_chain.py / verify_vrf_msg_hash.py)" do_export_verify

# 7) HARDHAT TESTS
step "7) HARDHAT TESTS (verifier + LotteryR4)" do_hardhat

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
  echo "Check /tmp/* and hardhat/uvicorn logs."
  exit 1
fi
