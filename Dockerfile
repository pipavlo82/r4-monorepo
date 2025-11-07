# Re4ctoR public entropy API container (community build)
# Features:
# - FastAPI + SlowAPI rate limiting
# - /random (raw entropy)
# - /random_pq?sig=ecdsa (signed entropy with ECDSA)
# - /verify_pq, /metrics_pq
# - PQ mode (Dilithium3) is declared but disabled in this build

FROM python:3.10-slim

WORKDIR /app

# --- System prep (keep slim, but add tools needed by deps) ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    python3-dev \
    libffi-dev \
    pkg-config \
 && rm -rf /var/lib/apt/lists/*

# --- Python deps ---
# (eth-utils потрібен для ECDSA адрес; якщо вже є в requirements.txt — дубль не зламає)
COPY api/requirements.txt /app/api/requirements.txt
RUN grep -qxF 'eth-utils' /app/api/requirements.txt || echo 'eth-utils' >> /app/api/requirements.txt
RUN pip install --no-cache-dir -r /app/api/requirements.txt

# --- App code ---
COPY api /app/api

# --- Sealed core binary (community build ships it) ---
RUN mkdir -p /app/core/bin
COPY core/bin/re4_dump.stub /app/core/bin/re4_dump
RUN chmod +x /app/core/bin/re4_dump

# --- Keys dir for ECDSA ---
RUN mkdir -p /app/keys

# --- Runtime env (safe defaults; без API_KEY за замовчуванням) ---
ENV RATE_LIMIT="30/minute" \
    PORT="8081" \
    PYTHONUNBUFFERED=1 \
    R4_CORE_BIN="/app/core/bin/re4_dump"

# --- Expose API port ---
EXPOSE 8081

# --- FIPS-style startup self-test + secure startup ---
RUN echo '#!/bin/sh' > /app/entrypoint.sh && \
    echo 'set -e' >> /app/entrypoint.sh && \
    echo 'echo "[r4] running FIPS startup self-test..."' >> /app/entrypoint.sh && \
    echo 'if [ "$STRICT_FIPS" = "1" ]; then' >> /app/entrypoint.sh && \
    echo '    python3 /app/api/fips_selftest.py' >> /app/entrypoint.sh && \
    echo 'else' >> /app/entrypoint.sh && \
    echo '    python3 /app/api/fips_selftest.py || echo "[r4] WARNING: self-test failed (non-strict mode), continuing..."' >> /app/entrypoint.sh && \
    echo 'fi' >> /app/entrypoint.sh && \
    echo 'echo "[r4] self-test passed (or allowed), starting API..."' >> /app/entrypoint.sh && \
    echo 'PORT=${PORT:-8081}' >> /app/entrypoint.sh && \
    echo 'exec uvicorn api.app:app --host 0.0.0.0 --port ${PORT}' >> /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
