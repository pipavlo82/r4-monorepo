# syntax=docker/dockerfile:1.6

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

# place for core binary (both community/sealed will use this path)
RUN mkdir -p /app/core/bin

# sane defaults for demo (НЕ зберігаємо API_KEY в образі)
ENV RNG_BIN=/app/core/bin/re4_dump \
    RATE_LIMIT=10/second \
    MAX_BYTES=1000000

# за замовчуванням запускаємо проста API (api.main) на 8080
CMD ["python","-m","uvicorn","api.main:app","--host","0.0.0.0","--port","8080"]

############################
# Community stage (uses stub)
############################
FROM base AS community
# stub RNG binary (завжди є у репо для CI/ком’юніті)
COPY docker/stubs/re4_dump /app/core/bin/re4_dump
RUN chmod +x /app/core/bin/re4_dump

############################
# Sealed stage (external build-context)
############################
# Щоб не комітити приватний re4_dump у репо:
# Будуємо з зовнішнього каталогу:
#   DOCKER_BUILDKIT=1 docker build \
#     --target sealed-real \
#     --build-context realbin=/ABS/PATH/TO/DIR_WITH_RE4_DUMP \
#     -t r4-ci-sealed:latest .
#
FROM base AS sealed-real
COPY --from=realbin re4_dump /app/core/bin/re4_dump
RUN chmod +x /app/core/bin/re4_dump
ENV RNG_BIN=/app/core/bin/re4_dump
