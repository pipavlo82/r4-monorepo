#!/usr/bin/env bash
set -Eeuo pipefail

CORE_HOST="http://localhost:8080"
CORE_KEY="local-demo"

N=${1:-100}  # скільки запитів (можеш передати числом: ./stress_core.sh 500)

ok=0
err=0
start_ts=$(date +%s)

echo "=== CORE ENTROPY STRESS ==="
echo "Target: $CORE_HOST/random?n=32&fmt=raw"
echo "API-Key: $CORE_KEY"
echo "Requests: $N"
echo

for i in $(seq 1 $N); do
    # беремо тільки статус-код, без тіла
    code=$(curl -s -o /dev/null -w "%{http_code}" \
        "${CORE_HOST}/random?n=32&fmt=raw" \
        -H "X-API-Key: ${CORE_KEY}")

    if [ "$code" = "200" ]; then
        ok=$((ok+1))
    else
        err=$((err+1))
        echo "[$i] ERROR status=$code"
    fi
done

end_ts=$(date +%s)
dur=$((end_ts - start_ts))

echo
echo "Done."
echo "OK:   $ok"
echo "ERR:  $err"
echo "Time: ${dur}s total for $N requests"
echo "RPS:  $(( (ok+err) / (dur > 0 ? dur : 1) )) req/sec"
