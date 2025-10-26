FROM python:3.12-slim

# 1. базові системні тулзи, які нам можуть знадобитись усередині
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl procps tar \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. покласти підписаний реліз ядра (з монорепо: core/release/re4_release.tar.gz)
#    це sealed entropy core, який ми будемо розгортати в контейнер
COPY core/release/re4_release.tar.gz /app/re4_release.tar.gz

# 3. розпакувати ядро в /app/runtime
#    після цього очікується /app/runtime/bin/re4_dump
RUN mkdir -p /app/runtime && \
    tar -C /app/runtime -xzf /app/re4_release.tar.gz && \
    rm /app/re4_release.tar.gz && \
    chmod +x /app/runtime/bin/re4_dump

# 4. додати self-test усередину контейнера
#    цей код ми вже додали в репо: packages/core/selftest/...
#    він включає fips_selftest.py та manifest.json
COPY packages/core/selftest /app/selftest
RUN chmod +x /app/selftest/fips_selftest.py

# 5. додати API-шар (FastAPI) — твій оновлений main.py з SELFTEST_OK
#    важливо: беремо саме версію з packages/core/docker/main.py
COPY packages/core/docker/main.py /app/main.py

# 6. створити venv і встановити рантайм-залежності
RUN python -m venv /app/venv && \
    /app/venv/bin/pip install --no-cache-dir fastapi uvicorn

# 7. ENV дефолти (можна оверрайдити через docker run -e ...)
ENV API_HOST=0.0.0.0
ENV API_PORT=8080
ENV API_KEY=demo
ENV API_GIT=container-build
ENV CORE_GIT=release-core

EXPOSE 8080

# 8. запуск сервера
CMD ["/app/venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
