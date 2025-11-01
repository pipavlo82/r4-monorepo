# syntax=docker/dockerfile:1

############################
# Base stage
############################
FROM python:3.10-slim AS base
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# deps for API
COPY api/requirements.txt /app/api/requirements.txt
RUN pip install --no-cache-dir -r /app/api/requirements.txt

# API source
COPY api/ /app/api/

# place for core binary
RUN mkdir -p /app/core/bin

############################
# Community stage (uses stub)
############################
FROM base AS community
# stub RNG binary (always available for CI/community)
COPY docker/stubs/re4_dump /app/core/bin/re4_dump
RUN chmod +x /app/core/bin/re4_dump

# sane defaults for demo
ENV API_KEY=demo \
    RNG_BIN=/app/core/bin/re4_dump \
    RATE_LIMIT=10/second \
    MAX_BYTES=1000000

CMD ["python","-m","uvicorn","api.main:app","--host","0.0.0.0","--port","8080"]

############################
# Sealed stage (uses real core/bin)
############################
FROM base AS sealed
# copy your real sealed binary if present in repo (optional for CI)
COPY core/bin/re4_dump /app/core/bin/re4_dump
RUN chmod +x /app/core/bin/re4_dump

ENV RNG_BIN=/app/core/bin/re4_dump

CMD ["python","-m","uvicorn","api.main:app","--host","0.0.0.0","--port","8080"]
