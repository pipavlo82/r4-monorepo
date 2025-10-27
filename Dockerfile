# Re4ctoR public entropy API container (community build)
# Features:
# - FastAPI + SlowAPI rate limiting
# - /random (raw entropy)
# - /random_pq?sig=ecdsa (signed entropy with ECDSA)
# - /verify_pq, /metrics_pq
# - PQ mode (Dilithium3) is declared but disabled in this build

FROM python:3.10-slim

# set workdir inside container
WORKDIR /app

# --- System prep (not heavy, we keep slim) ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# --- Copy requirements and install ---
# Ми очікуємо, що requirements.txt лежить у /app/api/requirements.txt
# Якщо у тебе зараз requirements.txt в корені репо, то просто залиш так як є нижче.
COPY api/requirements.txt /app/api/requirements.txt

RUN pip install --no-cache-dir -r /app/api/requirements.txt

# --- Copy source code into container ---
COPY api /app/api

# створимо директорію keys всередині контейнера (для ECDSA ключів)
RUN mkdir -p /app/keys

# --- Default env (можна оверрайдити при `docker run -e ...`) ---
ENV API_KEY="demo" \
    RATE_LIMIT="30/minute" \
    PORT="8081" \
    PYTHONUNBUFFERED=1

# --- Expose API port ---
EXPOSE 8081

# --- Run server ---
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8081"]
