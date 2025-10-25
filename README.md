r4-monorepo

r4 is an entropy appliance and verifiable randomness API.

It ships two things:

A high-entropy core (re4_dump) — closed-source, statistically verified (Dieharder / PractRand / BigCrush), shipped as a signed binary.

A hardened HTTP API (/random) — rate-limited, key-protected, designed to run as a service (systemd or Docker).

This repo also contains the roadmap for PQ verifiable randomness (vrf-spec): post-quantum attestable randomness for proof-of-stake rotation, zk-rollup seeding, lotteries, etc.

Quickstart (Docker)

You can run the whole service with one Docker command.

Prereqs:

Docker Desktop (Windows/macOS) or Docker Engine (Linux)

Port 8080 free

Run the container:

docker run -d
--name r4test
-p 8080:8080
-e API_KEY=demo
pipavlo/r4-local-test:latest

Health check:

curl -s http://127.0.0.1:8080/health

"ok"

Version / build info:

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

Request cryptographic random bytes:

curl -s -H "x-api-key: demo"
"http://127.0.0.1:8080/random?n=32&fmt=hex
"

-> 64 hex chars (32 bytes), different every call

What happens here:

re4_dump is executed in the container

the API enforces API_KEY

output is served over HTTP with basic rate limiting

no external network calls — randomness is generated locally in your container

Auth model

The API requires a key for /random.

Two ways to pass it:

Header:
x-api-key: demo

Query:
?key=demo

By default, the container ships with:

-e API_KEY=demo


Change this in production.

Example production run:

docker run -d \
  --name r4prod \
  -p 8080:8080 \
  -e API_KEY="my-super-secret" \
  pipavlo/r4-local-test:latest


Then call:

curl -s -H "x-api-key: my-super-secret" \
  "http://127.0.0.1:8080/random?n=64&fmt=hex"

API reference
GET /health

Returns "ok" if the API is alive.

GET /version

Returns metadata about this running instance:

core_git – build/commit tag of the entropy core

api_git – build tag for the API layer

limits – rate limit and max request size

This is designed for audit / fleet inventory / compliance dashboards.

GET /random

Request random bytes.

Query params:

n (required): number of bytes, e.g. 32, 1024, 4096

fmt (optional):

hex → hex string

unset → raw bytes

Auth:

header x-api-key: <key>
or

query ?key=<key>

Examples:

# 16 bytes, hex-encoded
curl -s -H "x-api-key: demo" \
  "http://127.0.0.1:8080/random?n=16&fmt=hex"
# -> "63968169edffa881f6a4f6d0adc406eb"

# 64 raw bytes saved to file
curl -s -H "x-api-key: demo" \
  "http://127.0.0.1:8080/random?n=64" \
  --output sample.bin

hexdump -C sample.bin | head


Error example (invalid key):

curl -i -s -H "x-api-key: WRONG" \
  "http://127.0.0.1:8080/random?n=16&fmt=hex"

# HTTP/1.1 401 Unauthorized
# {"detail": "invalid api key"}

What's inside the container

The published Docker image pipavlo/r4-local-test:latest bundles:

/app/runtime/bin/re4_dump
The high-entropy generator binary. This is the only component allowed to emit randomness.

FastAPI + uvicorn REST layer
Exposes /health, /version, /random.

Rate limiting, request logging, and IP metadata hints.

Runtime config via env:

API_KEY (required for /random)

API_HOST / API_PORT (default 0.0.0.0:8080)

No external entropy source is pulled at request time.
Randomness never leaves the container except via your HTTP call.

Trust / audit / compliance

This is positioned as an entropy appliance.

What we ship:

The binary re4_dump is built from an internal DRBG + entropy combiner.

We publish:

release tarball (re4_release.tar.gz)

SHA-256 manifest (re4_release.sha256)

detached GPG signature (re4_release.tar.gz.asc)

SBOM (SBOM.spdx.json)

We run statistical batteries:

Dieharder

PractRand

TestU01 BigCrush

Human-readable summaries of those runs live under:
packages/core/proof/

These include PASS / WEAK / FAIL annotations and commentary.

Full raw multi-GB logs are NOT committed to git. They are archived offline and shared under NDA if required.

The internal DRBG/entropy core is intentionally not open-sourced.
This is similar to an HSM / Secure Enclave model:

you can measure output quality,

you can verify supply-chain integrity (hash + signature + SBOM),

you cannot just clone the internal core.

Production deployment

Two supported modes:

1. Docker (recommended)

Run behind an internal reverse proxy (nginx / traefik / API gateway).

Expose /random only internally.

Keep API_KEY secret.

Monitor /version to confirm expected core_git.

Example systemd unit (host side, auto-start via Docker):

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

2. Bare metal / systemd (no Docker)

We also support running uvicorn + re4_dump directly under systemd as a non-root service with sandboxing:

ProtectSystem=strict

ProtectHome=true

MemoryDenyWriteExecute=true

See:
packages/core/docs/USAGE.md
packages/core/docs/re4ctor-api.service.example

Roadmap: VRF / post-quantum verifiable randomness

Today:

/random returns high-quality entropy bytes

you authenticate with an API key

you trust that we are not biasing output

Next:
provable randomness suitable for consensus / staking.

The vrf-spec/ package (see packages/vrf-spec) tracks the next milestone:

attach a post-quantum identity (Dilithium / Kyber class keys) to each node

sign each randomness response

allow external verifiers (validators, rollup sequencers, smart contracts) to prove:

the bytes came from an authorized node

the operator could not secretly re-roll until they got a "good" outcome

Planned /vrf response shape:

{
  "random": "<bytes>",
  "signature": "<pq_sig>",
  "public_key": "<node_key>",
  "verified": true
}


Intended consumers:

validator set rotation in PoS networks

zk-rollup sequencers / prover seeds

on-chain lotteries / airdrops / mint fairness

anti-manipulation randomness feeds

Positioning:

/random = fast local entropy

/vrf = attestable randomness with cryptographic accountability

Status

This repo is public.

The core entropy code is not.

The container image is public:

docker pull pipavlo/r4-local-test:latest

This is already enough to:

integrate into backend services,

generate keys/secrets,

feed randomness into systems that can’t rely on cloud RNG,

demo to infra / security / validators / investors.

License / NOTICE

See LICENSE and NOTICE.

Summary:

Wrapper code, API logic, docs are available for review.

The entropy core ships as a compiled binary with a signed, reproducible release bundle.

The internals of the DRBG / entropy combiner are intentionally not published.

This is closer to an HSM than a normal RNG library:
you can call it,
you can test statistical quality,
you get verifiable supply-chain artifacts (hash, GPG sig, SBOM),
but you do not automatically get the private core.

Contact / Sponsors

If you want enterprise access, on-prem deployments, validator-facing beacons, or PQ-signed /vrf service:
(enterprise / auditors / rollup teams / staking infra)

→ add your contact / sponsor channel here
