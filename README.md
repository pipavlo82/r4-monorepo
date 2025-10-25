# 🧬 r4-monorepo

**r4** is an entropy appliance and verifiable randomness API.

It ships two things:

1. A high-entropy core (`re4_dump`) — closed-source, statistically verified (Dieharder / PractRand / BigCrush), shipped as a signed binary.
2. A hardened HTTP API (`/random`) — rate-limited, key-protected, designed to run as a service (systemd or Docker).

This repo also contains the roadmap for PQ verifiable randomness (`vrf-spec`): post-quantum attestable randomness for proof-of-stake rotation, zk-rollup seeding, lotteries, etc.

---

## 🚀 Quickstart (Docker)

You can run the whole service with **one Docker command**.

Prereqs:
- Docker Desktop (on Windows/macOS) or Docker Engine (Linux)
- Port 8080 free

1. Run the container:

```bash
docker run -d \
  --name r4test \
  -p 8080:8080 \
  -e API_KEY=demo \
  pipavlo/r4-local-test:latest
Health check:

bash
Copy code
curl -s http://127.0.0.1:8080/health
# "ok"
Version / build info:

bash
Copy code
curl -s http://127.0.0.1:8080/version
# {
#   "name": "re4ctor-api",
#   "version": "0.1.0",
#   "api_git": "container-build",
#   "core_git": "release-core",
#   "limits": {
#     "max_bytes_per_request": 1000000,
#     "rate_limit": "10/sec per IP (enforced in prod by reverse proxy)"
#   }
# }
Request cryptographic random bytes:

bash
Copy code
curl -s -H "x-api-key: demo" \
  "http://127.0.0.1:8080/random?n=32&fmt=hex"
# -> 64 hex chars (32 bytes), different every time
What happens here:

re4_dump is executed in the container.

The API enforces API_KEY.

Output is served over HTTP with basic rate limiting.

No external network calls — randomness is generated locally in your container.

🔐 Auth model
The API requires a key for /random.

Two ways to pass it:

Header:
x-api-key: demo

Query:
?key=demo

By default, the container ships with:

bash
Copy code
-e API_KEY=demo
👉 Change this in production.
For example, run:

bash
Copy code
docker run -d \
  --name r4prod \
  -p 8080:8080 \
  -e API_KEY="my-super-secret" \
  pipavlo/r4-local-test:latest
Then call it with:

bash
Copy code
curl -s -H "x-api-key: my-super-secret" \
  "http://127.0.0.1:8080/random?n=64&fmt=hex"
🧪 API reference
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

Params:

n (required): number of bytes, e.g. 32, 1024, 4096

fmt (optional):

hex → hex string

unset → raw bytes

Auth:

header x-api-key: <key>
or

query ?key=<key>

Examples:

bash
Copy code
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

bash
Copy code
curl -i -s -H "x-api-key: WRONG" \
  "http://127.0.0.1:8080/random?n=16&fmt=hex"

# HTTP/1.1 401 Unauthorized
# {"detail": "invalid api key"}
📦 What's inside the container?
The published Docker image (pipavlo/r4-local-test:latest) bundles:

/app/runtime/bin/re4_dump
The high-entropy generator binary.
This is the only component allowed to emit randomness.

FastAPI + uvicorn REST layer
Exposes /health, /version, /random.

Rate limiting, request logging, and IP metadata hints.

Runtime config via env:

API_KEY (required for /random)

API_HOST / API_PORT (default 0.0.0.0:8080)

No external entropy source is pulled at request time.
Randomness never leaves the container except via your HTTP call.

🧾 Trust / Audit / Compliance
This is not rand() from libc.
This is positioned as an entropy appliance.

What we provide:

The binary re4_dump is built from a closed internal DRBG + entropy combiner.

We ship:

a release tarball (re4_release.tar.gz)

SHA-256 manifest (re4_release.sha256)

detached GPG signature (re4_release.tar.gz.asc)

SBOM (SBOM.spdx.json)

We run statistical batteries:

Dieharder

PractRand

TestU01 BigCrush

Human-readable summaries of those test runs live under:
packages/core/proof/

These include PASS, WEAK, FAIL annotations and commentary.

Raw multi-GB logs are not in git and are available only under NDA (to keep this repo lightweight and to protect IP).

⚠ The internal DRBG/entropy core is intentionally not open-sourced.
This is similar to how hardware security modules (HSMs), Secure Enclave, TPMs, etc. are distributed:

you can measure the output

you can verify integrity/signature of the binary

you cannot just clone the core logic

🛰 Production deployment
There are two supported modes:

1. Docker (recommended for most users)
Run behind an internal reverse proxy (nginx, traefik, API gateway).

Expose only /random internally.

Limit who knows the API_KEY.

Monitor /version to confirm you're running the expected core_git.

Example systemd unit (host side, if you want it to auto-start):

ini
Copy code
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
We also support running the API directly under uvicorn + re4_dump as a systemd service under a non-root user with sandboxing:

ProtectSystem=strict

ProtectHome=true

MemoryDenyWriteExecute=true

rate limiting per IP (via reverse proxy)

See packages/core/docs/USAGE.md and packages/core/docs/re4ctor-api.service.example.

🧭 Roadmap: PQ VRF / verifiable randomness
Today:

/random returns high-quality entropy bytes.

You authenticate with an API key.

You trust that we aren't biasing output.

Next step:
provable randomness suitable for consensus / staking.

vrf-spec/ (see packages/vrf-spec) covers the next milestone:

attach a post-quantum identity (Dilithium / Kyber class keys) to the node

sign each randomness response

allow external verifiers (blockchain, zk-rollup sequencers, committees) to verify:

the bytes came from a legit node

the node couldn't "reroll privately" without detection

Intended consumers:

validator rotation in PoS networks

zk-rollup sequencers / prover seeds

on-chain lotteries / airdrops / mint fairness

anti-manipulation beacons

Long-term target:

/vrf endpoint:

json
Copy code
{
  "random": "<bytes>",
  "signature": "<pq_sig>",
  "public_key": "<node_key>",
  "verified": true
}
So /random = fast local entropy,
/vrf = audited, attestable randomness.

📣 Status
This repo is public.

The cryptographic core is not.

The container image is public:
docker pull pipavlo/r4-local-test:latest

This is already enough to:

integrate into backend services,

generate secrets / keys,

feed randomness to systems that can't rely on cloud RNG,

demo to investors / partners.

⚖ License / NOTICE
See LICENSE and NOTICE.

In short:

The wrapper code, docs, and high-level API logic are available for review.

The core entropy generator is shipped as a compiled binary with a reproducible, signed release bundle.

The internals of the DRBG / entropy combiner are not published.

This model is closer to an HSM than a normal RNG library:
you can call it, benchmark it, and audit its statistical output,
but you don't automatically get the full internal design.

🔗 Contact / Sponsors
If you want enterprise access, custom attestations, or dedicated beacons:

integration into validators / rollup sequencers,

dedicated PQ-signed beacon feeds,

compliance / audit packages,

reach out.

Commercial / support / partnership:
TODO: add contact or sponsor link here
