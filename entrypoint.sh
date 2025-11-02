#!/bin/sh
set -e

echo "[r4] running FIPS startup self-test..."

# STRICT_FIPS=1 — суворий режим (якщо self-test не пройшов → зупиняє запуск)
if [ "$STRICT_FIPS" = "1" ]; then
    python3 packages/core/proof/fips_selftest.py
else
    python3 packages/core/proof/fips_selftest.py || {
        echo "[r4] WARNING: self-test failed (non-strict mode), continuing anyway"
    }
fi

echo "[r4] self-test passed (or allowed), starting API..."
uvicorn main:app --host 0.0.0.0 --port 8080
