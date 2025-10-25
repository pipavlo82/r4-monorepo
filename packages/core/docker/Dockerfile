FROM python:3.12-slim

# system deps just in case (head, base64 etc optional)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl procps \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. copy signed release bundle from repo into image
COPY packages/core/re4_release.tar.gz /app/re4_release.tar.gz

# 2. unpack core into /app/runtime
RUN mkdir -p /app/runtime && \
    tar -C /app/runtime -xzf /app/re4_release.tar.gz && \
    rm /app/re4_release.tar.gz

# sanity: ensure core binary is executable
RUN chmod +x /app/runtime/bin/re4_dump

# 3. copy our FastAPI app code into the image
COPY main.py /app/main.py

# 4. create venv and install runtime deps
RUN python -m venv /app/venv && \
    /app/venv/bin/pip install --no-cache-dir fastapi uvicorn

# 5. runtime env (non-secret defaults; user can override with -e)
ENV API_HOST=0.0.0.0
ENV API_PORT=8080
ENV API_KEY=demo
ENV API_GIT=container-build
ENV CORE_GIT=release-core

EXPOSE 8080

# 6. run uvicorn with our FastAPI app
CMD ["/app/venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
