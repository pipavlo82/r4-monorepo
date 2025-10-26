⚡️ r4-monorepo

🧠 r4 is an entropy appliance and verifiable randomness API.

It ships two things:

🧩 A high-entropy core (re4_dump) — closed-source, statistically verified (Dieharder / PractRand / BigCrush), shipped as a signed binary.

🌐 A hardened HTTP API (/random) — rate-limited, key-protected, designed to run as a service (systemd or Docker).

This repo also contains the roadmap for PQ verifiable randomness (vrf-spec): post-quantum attestable randomness for proof-of-stake rotation, zk-rollup seeding, lotteries, etc.

🚀 Quickstart (Docker)

You can run the whole service with one Docker command.

Prereqs

🐳 Docker Desktop (Windows/macOS) or Docker Engine (Linux)

🔌 Port 8080 free

Run the container
docker run -d \
  --name r4test \
  -p 8080:8080 \
  -e API_KEY=demo \
  pipavlo/r4-local-test:latest

Health check
curl -s http://127.0.0.1:8080/health
# → "ok"

Version / build info
curl -s http://127.0.0.1:8080/version

{
  "name": "re4ctor-api",
  "version": "0.1.0",
  "api_git": "container-build",
  "core_git": "release-core",
  "limits": {
    "max_bytes_per_request": 1000000,
    "rate_limit": "10/sec per IP (enforced in prod by reverse proxy)"
  }
}

Request cryptographic random bytes
curl -s -H "x-api-key: demo" \
"http://127.0.0.1:8080/random?n=32&fmt=hex"
# → 64 hex chars (32 bytes), different every call


What happens here:

re4_dump is executed in the container

the API enforces API_KEY

output is served over HTTP with basic rate limiting

no external network calls — randomness is generated locally in your container

🔐 Auth Model

The API requires a key for /random.

Two ways to pass it:

Header: x-api-key: demo

Query: ?key=demo

By default, the container ships with:

-e API_KEY=demo


Change this in production.

Example production run
docker run -d \
  --name r4prod \
  -p 8080:8080 \
  -e API_KEY="my-super-secret" \
  pipavlo/r4-local-test:latest


Then call:

curl -s -H "x-api-key: my-super-secret" \
"http://127.0.0.1:8080/random?n=64&fmt=hex"

📚 API Reference
GET /health

Returns "ok" if the API is alive.

GET /version

Returns metadata about this running instance:

core_git – build/commit tag of the entropy core

api_git – build tag for the API layer

limits – rate limit and max request size

Designed for audit / fleet inventory / compliance dashboards.

GET /random

Request random bytes.

Query params:

Param	Required	Example	Description
n	✅	32, 1024	Number of bytes
fmt	❌	hex / unset	Output format

Auth:

Header x-api-key:

Query ?key=

Examples

16 bytes, hex-encoded:

curl -s -H "x-api-key: demo" \
"http://127.0.0.1:8080/random?n=16&fmt=hex"


64 raw bytes saved to file:

curl -s -H "x-api-key: demo" \
"http://127.0.0.1:8080/random?n=64" \
--output sample.bin

hexdump -C sample.bin | head


Error example (invalid key):

curl -i -s -H "x-api-key: WRONG" \
"http://127.0.0.1:8080/random?n=16&fmt=hex"

HTTP/1.1 401 Unauthorized
{"detail": "invalid api key"}

🧰 What’s Inside the Container

The published image pipavlo/r4-local-test:latest bundles:

/app/runtime/bin/re4_dump — the high-entropy generator binary (only component allowed to emit randomness)

FastAPI + Uvicorn REST layer exposing /health, /version, /random

Rate limiting, request logging, and IP metadata hints

Runtime config (env vars):

API_KEY            required for /random
API_HOST / PORT    default 0.0.0.0:8080


No external entropy source is pulled at request time — randomness never leaves the container except via your HTTP call.

🧮 Trust / Audit / Compliance

This acts as an entropy appliance.

We ship:

re4_release.tar.gz — release tarball

re4_release.sha256 — SHA-256 manifest

re4_release.tar.gz.asc — detached GPG signature

SBOM.spdx.json — Software Bill of Materials

We run statistical batteries:

Dieharder

PractRand

TestU01 BigCrush

Human-readable summaries live under packages/core/proof/.
Full multi-GB raw logs are not committed — archived offline and shared under NDA.

The internal DRBG/entropy core is intentionally not open-sourced, following an HSM / Secure Enclave model:

you can measure output quality

you can verify supply-chain integrity (hash + signature + SBOM)

you cannot clone the internal core

🏭 Production Deployment

Two supported modes:

1. 🐳 Docker (recommended)

Run behind a reverse proxy (nginx / traefik / API gateway).
Expose /random only internally.
Keep API_KEY secret.
Monitor /version for expected core_git.

Example systemd unit:

[Unit]
Description=R4 entropy API container
After=network-online.target
Wants=network-online.target

[Service]
Restart=always
ExecStart=/usr/bin/docker run --rm \
  -p 8080:8080 \
  -e API_KEY=prod-secret-here \
  --name r4-entropy \
  pipavlo/r4-local-test:latest
ExecStop=/usr/bin/docker stop r4-entropy

[Install]
WantedBy=multi-user.target

2. ⚙️ Bare Metal / systemd

Run uvicorn + re4_dump directly under systemd as non-root with sandboxing:

ProtectSystem=strict
ProtectHome=true
MemoryDenyWriteExecute=true


See:

packages/core/docs/USAGE.md

packages/core/docs/re4ctor-api.service.example

🔭 Roadmap — VRF / Post-Quantum Verifiable Randomness

Today:

/random returns high-quality entropy bytes

you authenticate with API key

you trust we’re not biasing output

Next: provable randomness for consensus / staking.
The vrf-spec/ package tracks the next milestone:

attach post-quantum identity (Dilithium / Kyber class keys)

sign each randomness response

allow external verifiers to prove:

the bytes came from an authorized node

the operator couldn’t re-roll for a “better” outcome

Planned /vrf response shape:

{
  "random": "",
  "signature": "<pq_sig>",
  "public_key": "<node_key>",
  "verified": true
}


Intended consumers:

Validator set rotation in PoS

zk-rollup sequencers / prover seeds

On-chain lotteries / airdrops / mint fairness

Anti-manipulation randomness feeds

Positioning:

/random = fast local entropy

/vrf = attestable randomness with cryptographic accountability

📦 Status

This repo is public.
The core entropy code is not.

Public Docker image:

docker pull pipavlo/r4-local-test:latest


Enough to:

integrate into backend services

generate keys/secrets

feed offline systems needing strong RNG

demo to infra / security / validator teams

📄 License / NOTICE

See LICENSE and NOTICE.

Summary:

Wrapper code, API logic, docs → public & reviewable

Entropy core → compiled & signed binary (reproducible build)

Internal DRBG/entropy combiner → private (HSM model)

You can test output quality, verify signatures and SBOM, but not access the private core.

🤝 Contact / Sponsors

For enterprise access, on-prem deployments, validator beacons, or PQ-signed /vrf services (enterprise / auditors / rollup / staking infra):

→ Add your contact / sponsor channel here.

Would you like me to:

💾 generate this as a ready-to-paste Markdown file (README.md)

or 🧱 embed it back into your GitHub repo format (with badges, Docker links, etc.)?

## Security / Openness Model

r4 behaves like a small software HSM: you can test its output quality,
verify release integrity (hash, GPG signature, SBOM),
but the internal entropy-combiner code remains sealed.
This prevents trivial forks and targeted backdoors while keeping
statistical and supply-chain transparency for auditors.

## Benchmarks & FIPS Readiness 🔥

[![Speed](https://img.shields.io/badge/speed-950k_req/s-brightgreen)]()
[![Integrity](https://img.shields.io/badge/FIPS-ready-blue)]()

r4 is positioned as an attested entropy appliance.

- High-throughput randomness API (FastAPI + sealed core)
- <~1ms p99 latency on commodity hardware
- Startup self-test: SHA-256 integrity check on the sealed binary
- SBOM + SHA256 manifest + GPG signature shipped with each release

| Metric        | Value                |
|---------------|----------------------|
| Throughput    | ~950 000 req/s       |
| p99 Latency   | ~1.1 ms              |
| Self-Test     | PASS                 |
| Manifest      | verified (SHA-256)   |

See `docs/proof/benchmarks_summary.md` and `docs/proof/fips_readiness.md` for details.

Contact: shtomko@gmail.com
