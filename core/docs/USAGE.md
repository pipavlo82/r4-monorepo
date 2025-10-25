# re4ctor API — Usage Guide

This document describes how to run and consume the local entropy API built from the verified re4_dump binary.

---

## API Endpoints

/health — Returns {"status": "ok"} to indicate service availability.
/version — Shows API and core build versions.
/random?n=32&fmt=hex — Returns random bytes (hex or raw).

---

## Authentication

All /random requests must include an API key, provided in either of these ways:

Header:
  x-api-key: your-key

Query:
  ?key=your-key

---

## Example Usage

# Health check
curl -s http://127.0.0.1:8080/health
# → {"status":"ok"}

# Version info
curl -s http://127.0.0.1:8080/version
# → {"core_git":"release-core","api_git":"main"}

# Request 32 random bytes in hex
curl -s -H "x-api-key: local-demo" "http://127.0.0.1:8080/random?n=32&fmt=hex"

# Request 64 bytes of raw data and pipe to hexdump
curl -s -H "x-api-key: local-demo" "http://127.0.0.1:8080/random?n=64" | hexdump -C

---

## Rate & Size Limits
- Default rate: 10 requests/second per IP
- Max bytes per request: 1,000,000
- Too large requests → {"detail":"too many bytes requested"}

---

## Configuration via .env

API_HOST=127.0.0.1
API_PORT=8080
API_KEY=local-demo
API_GIT=main
CORE_GIT=release-core

---

## Logs

Logs are located at:
~/re4ctor-local/re4ctor-api/logs/api.log

Each /random call is logged like:
[re4/random] ip=127.0.0.1 n=32 head4=a4705f81 status=ok

---

## Service Management (helper script)

./api_start.sh start    # start API
./api_start.sh stop     # stop API
./api_start.sh status   # check status
./api_start.sh log      # follow logs

---

## Systemd Deployment (Production)

For hardened Linux installations, see:
docs/re4ctor-api.service.example
---

## Security posture summary

- The generator core is not published. You receive a compiled binary (`re4_dump`) instead of full DRBG/entropy source.
- Every release is shipped with:
  - SHA256 manifest
  - Detached GPG signature
  - SBOM (SPDX 2.3) describing shipped artifacts
- `/random` is authenticated (API key) and rate-limited.
- Each `/random` call is logged with client IP, size requested, and a short fingerprint of the output, so operators can audit access.
- A hardened systemd unit is provided (`docs/re4ctor-api.service.example`) to run the service under a dedicated system user with restricted privileges.
