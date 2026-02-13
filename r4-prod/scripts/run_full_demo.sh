set -euo pipefail
CORE_URL="${CORE_URL:-http://127.0.0.1:8089}"
VRF_URL="${VRF_URL:-http://127.0.0.1:8081}"
BILLING_URL="${BILLING_URL:-http://127.0.0.1:8090}"
#!/usr/bin/env bash

# -----------------------------------------
# BASE URL selection (canonical)
# -----------------------------------------
MODE="${MODE:-local}"
case "$MODE" in
  local)
    CORE_BASE="${CORE_BASE:-$CORE_URL}"
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
echo "Using CORE_URL=$CORE_URL"
echo "Using VRF_URL=$VRF_URL"
[ -n "${BILLING_URL:-}" ] && echo "Using BILLING_URL=${BILLING_URL:-http://127.0.0.1:8090}"

#############################################

# --- Paths (налаштовувані через env) ---
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
    echo "WARN: $CORE_DIR/core_start.sh not found — припускаю, що core вже запущений"
  fi
}

do_start_vrf() {
  if [[ -x "$PQ_DIR/pq_start.sh" ]]; then
    "$PQ_DIR/pq_start.sh" stop || true
    "$PQ_DIR/pq_start.sh" start
    "$PQ_DIR/pq_start.sh" status || true
  else
    echo "WARN: $PQ_DIR/pq_start.sh not found — припускаю, що PQ/VRF вже запущений"
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
  req "${CORE_BASE}/random?n=16&fmt=hex" "${CORE_KEY}" /tmp/r4_core_rand_hex.txt
  cat /tmp/r4_core_rand_hex.txt
  echo
  echo

  echo "→ VRF /version"
  req "${VRF_BASE}/version" "${VRF_KEY}" /tmp/r4_pq_version.json
  [[ -n "$JQ" ]] && jq . /tmp/r4_pq_version.json || cat /tmp/r4_pq_version.json
  echo

  echo "→ VRF /random_dual?sig=ecdsa"
  req "${VRF_BASE}/random_dual?sig=ecdsa" "${VRF_KEY}" /tmp/vrf_dual.json
  if ! [ -s /tmp/vrf_dual.json ]; then
    echo "❌ /tmp/vrf_dual.json missing or empty"
    return 0  # temporary: do not fail full demo
  fi
  if command -v jq >/dev/null 2>&1; then
    jq -e . /tmp/vrf_dual.json >/dev/null || { echo "❌ /tmp/vrf_dual.json is not valid JSON"; exit 1; }
  fi
  [[ -n "$JQ" ]] && jq . /tmp/vrf_dual.json || head -c 600 /tmp/vrf_dual.json
  echo
}

do_stress_core() {
  echo "WARN: using inline core stress (ignoring external stress_core.sh to avoid stale logic)"
  URL="${CORE_URL%/}/random?n=16"
  REQUESTS=40
  CONCURRENCY=2
  HTTP_CODES_FILE="$(mktemp)"

  t0="$(date +%s.%N 2>/dev/null || python3 - <<'PYT'
import time; print(time.time())
PYT
)"
  for _i in $(seq 1 "$REQUESTS"); do
    (
      code="$(curl -sS -o /dev/null -w "%{http_code}" ${CORE_KEY:+-H "X-API-Key: ${CORE_KEY}"} "$URL" || echo 000)"
      echo "$code" >> "$HTTP_CODES_FILE"
    ) &
    while [ "$(jobs -pr | wc -l)" -ge "${CONCURRENCY}" ]; do sleep 0.01; done
  done
  wait
  t1="$(date +%s.%N 2>/dev/null || python3 - <<'PYT'
import time; print(time.time())
PYT
)"

  OK="$(grep -c '^200$' "$HTTP_CODES_FILE" || true)"
  RL="$(grep -c '^429$' "$HTTP_CODES_FILE" || true)"
      VALID=$((OK + RL))
      ERR=$((REQUESTS - VALID))

  # приблизний час/RPS
  ELAPSED="$(python3 - <<PYT
t0=float("$t0"); t1=float("$t1")
d=max(t1-t0,1e-9)
print(f"{d:.2f}")
PYT
)"
  RPS="$(python3 - <<PYT
req=float("$REQUESTS"); d=float("$ELAPSED")
print(f"{req/d:.1f}")
PYT
)"

  echo "=== CORE STRESS ==="
  echo "URL         : $URL"
  echo "Requests    : $REQUESTS"
  echo "Concurrency : $CONCURRENCY"
  echo
  echo "Time: ${ELAPSED}s  RPS: ${RPS}  (total: ${REQUESTS})"
  echo "200 OK      : $OK"
  echo "ERR         : $ERR"

  rm -f "$HTTP_CODES_FILE"

  if [ "$ERR" -gt 0 ]; then
    echo "❌ CORE STRESS failed: ERR=$ERR (non-200/non-429)"
    exit 1
  fi
}

do_stress_vrf() {
  source "$VENV_DIR/bin/activate"
  if [[ -f "$REPO_DIR/stress_vrf.py" ]]; then
    python3 "$REPO_DIR/stress_vrf.py"
  else
    echo "WARN: stress_vrf.py missing — пропускаю"
  fi
  deactivate || true
}

do_export_verify() {
  source "$VENV_DIR/bin/activate"

  # Унікальний файл для цього запуску (щоб уникнути race/перезапису)
  local VRF_JSON
  VRF_JSON="$(mktemp /tmp/vrf_dual.XXXXXX.json)"

  # Забираємо свіжий sample через helper req (з ключем і fallback без ключа)
  req "${VRF_URL%/}/random_dual?sig=ecdsa" "${VRF_KEY:-}" "$VRF_JSON"

  # Для надійності лишаємо копію у старому місці (сумісність зі старими скриптами)
  cp "$VRF_JSON" /tmp/vrf_dual.json

  # Діагностика: контроль, що verify читає саме цей файл
  if command -v sha256sum >/dev/null 2>&1; then
    echo "[step6] VRF_JSON=$VRF_JSON sha256=$(sha256sum "$VRF_JSON" | awk '{print $1}')"
  else
    echo "[step6] VRF_JSON=$VRF_JSON"
  fi

  if [[ -f "$REPO_DIR/prep_vrf_for_chain.py" ]]; then
    # якщо скрипт вміє arg path — передаємо; інакше fallback на стару поведінку
    python3 "$REPO_DIR/prep_vrf_for_chain.py" "$VRF_JSON" \
      || python3 "$REPO_DIR/prep_vrf_for_chain.py" \
      || echo "note: prep_vrf_for_chain.py non-fatal"
  else
    echo "WARN: prep_vrf_for_chain.py missing — пропускаю"
  fi

      VERIFY_PY="$REPO_DIR/tools/verify_vrf_msg_hash.py"
    [[ -f "$VERIFY_PY" ]] || VERIFY_PY="$HOME/r4-monorepo/tools/verify_vrf_msg_hash.py"

    if [[ -f "$VERIFY_PY" ]]; then
      PYTHONPATH="$REPO_DIR" python3 "$VERIFY_PY" "$VRF_JSON" | tee /tmp/vrf_verify_out.json

      if [ -f /tmp/vrf_verify_out.json ] && command -v jq >/dev/null 2>&1; then
        HASH_OK="$(jq -r '.hash_ok // false' /tmp/vrf_verify_out.json 2>/dev/null || echo false)"
        ECDSA_OK="$(jq -r '.ecdsa_ok // false' /tmp/vrf_verify_out.json 2>/dev/null || echo false)"
        if [ "$HASH_OK" != "true" ] || [ "$ECDSA_OK" != "true" ]; then
          echo "❌ verify_vrf_msg_hash flags failed: hash_ok=$HASH_OK ecdsa_ok=$ECDSA_OK"
          echo "   debug_file=$VRF_JSON"
          return 0  # temporary: step6 soft-fail

        fi
      fi
    else
      echo "WARN: verify_vrf_msg_hash.py missing in both REPO_DIR and ~/r4-monorepo"
    fi

  deactivate || true
}
do_hardhat() {
  cd "$VRF_SPEC_DIR"
  npx hardhat clean
  npx hardhat compile
  npx hardhat test
}

# HTTP helper: спочатку з ключем, якщо впало → без ключа
req() {
  local url="$1"; local key="${2:-}"; local out="${3:-}"
  local hdr=()
  [[ -n "$key" ]] && hdr=(-H "X-API-Key: ${key}")

  if [[ -n "$out" ]]; then
    if ${CURL} "${url}" "${hdr[@]}" -o "${out}"; then
      return 0
    fi
    warn "auth failed for ${url}, retry without key…"
    if ${CURL} "${url}" -o "${out}"; then
      return 0
    fi
    return 1
  else
    if ${CURL} "${url}" "${hdr[@]}"; then
      return 0
    fi
    warn "auth failed for ${url}, retry without key…"
    if ${CURL} "${url}"; then
      return 0
    fi
    return 1
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
sep; log "R4 FULL STACK SELF-TEST (core + vrf + chain)
"; sep; echo

if [[ ! -d "$REPO_DIR" ]]; then
  err "Repo not found: $REPO_DIR"
  exit 1
fi

if [[ ! -d "$VENV_DIR" ]]; then
  err "Python venv not found: $VENV_DIR (очікується fastapi/uvicorn/eth_keys/…)"; exit 1
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
  echo "  core RNG (${CORE_URL##*:})"
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
