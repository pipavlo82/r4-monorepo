#!/usr/bin/env bash
set -Eeuo pipefail

# ---------------------------------------------------
# R4 CORE ENTROPY STRESS (parallel, percentiles)
# Usage: ./stress_core.sh [-n REQ] [-c CONC] [-b BYTES] [-t TIMEOUT] [--host URL] [--key KEY]
# Defaults: -n 500 -c 32 -b 32 -t 5 --host http://127.0.0.1:8080 --key local-demo
# ---------------------------------------------------

N=500
C=32
BYTES=32
TIMEOUT=5
HOST="http://127.0.0.1:8080"
KEY="local-demo"

while [[ $# -gt 0 ]]; do
  case "$1" in
    -n) N="$2"; shift 2;;
    -c) C="$2"; shift 2;;
    -b) BYTES="$2"; shift 2;;
    -t) TIMEOUT="$2"; shift 2;;
    --host) HOST="$2"; shift 2;;
    --key) KEY="$2"; shift 2;;
    *) echo "Unknown arg: $1"; exit 1;;
  case
done

URL="${HOST}/random?n=${BYTES}&fmt=raw"
OUT_CODES=$(mktemp)
OUT_TIMES=$(mktemp)

echo "=== CORE ENTROPY STRESS ==="
echo "Target : $URL"
echo "API-Key: $KEY"
echo "Req    : $N   Concurrency: $C   Timeout: ${TIMEOUT}s"
echo

do_one() {
  local i="$1"
  local code time
  read -r code time < <(
    curl -sS -o /dev/null \
      -w "%{http_code} %{time_total}\n" \
      -H "X-API-Key: ${KEY}" \
      --max-time "${TIMEOUT}" \
      "${URL}" 2>/dev/null || echo "000 ${TIMEOUT}"
  )
  echo "$code" >> "$OUT_CODES"
  echo "$time" >> "$OUT_TIMES"
}

# Run with bounded parallelism
running=0
start_ts=$(date +%s)
for i in $(seq 1 "$N"); do
  do_one "$i" &
  ((running++))
  if (( running >= C )); then
    wait -n
    ((running--))
  fi
done
wait
end_ts=$(date +%s)

# Stats
total=$N
ok=$(grep -c '^200$' "$OUT_CODES" || true)
c429=$(grep -c '^429$' "$OUT_CODES" || true)
c401=$(grep -c '^401$' "$OUT_CODES" || true)
c5xx=$(grep -E '^(5..)$' "$OUT_CODES" | wc -l | tr -d ' ' || true)
c000=$(grep -c '^000$' "$OUT_CODES" || true)
err=$(( total - ok ))

dur=$(( end_ts - start_ts ))
(( dur == 0 )) && dur=1
rps=$(( total / dur ))

# Latency percentiles
pctile() { # arg: p [0-100]
  local p=$1
  local count=$(wc -l < "$OUT_TIMES")
  (( count == 0 )) && { echo "0"; return; }
  sort -n "$OUT_TIMES" | awk -v p="$p" -v n="$count" '
    BEGIN { idx = int((p/100)*n + 0.5); if (idx<1) idx=1; }
    NR==idx { printf "%.4f", $1; exit }
  '
}

p50=$(pctile 50)
p95=$(pctile 95)
p99=$(pctile 99)

echo "Done."
echo "OK    : $ok"
echo "ERR   : $err  (429=$c429  401=$c401  5xx=$c5xx  000=$c000)"
echo "Time  : ${dur}s total for $total requests"
echo "RPS   : ${rps} req/sec"
echo "p50   : ${p50}s   p95: ${p95}s   p99: ${p99}s"

rm -f "$OUT_CODES" "$OUT_TIMES"
