# ⚡ r4-monorepo — entropy appliance & verifiable randomness API


[![Docker Pulls](https://img.shields.io/docker/pulls/pipavlo/r4-local-test?style=flat-square)](https://hub.docker.com/r/pipavlo/r4-local-test)
[![Image Size](https://img.shields.io/docker/image-size/pipavlo/r4-local-test/latest?style=flat-square)](https://hub.docker.com/r/pipavlo/r4-local-test)
[![License](https://img.shields.io/github/license/pipavlo82/r4-monorepo?style=flat-square)](LICENSE)
[![re4ctor-ci](https://github.com/pipavlo82/r4-monorepo/actions/workflows/ci.yml/badge.svg)](https://github.com/pipavlo82/r4-monorepo/actions/workflows/ci.yml)
[![public-sanity](https://github.com/pipavlo82/r4-monorepo/actions/workflows/public-sanity.yml/badge.svg?branch=main)](https://github.com/pipavlo82/r4-monorepo/actions/workflows/public-sanity.yml)

---

## 🧠 Overview

**r4** is a high-entropy appliance and verifiable randomness API.

It delivers:

- 🔒 **Sealed entropy core (`re4_dump`)** — closed-source, statistically verified via Dieharder / PractRand / BigCrush, shipped as a signed binary.  
- 🌐 **Hardened FastAPI layer** — key-protected `/random` endpoint for secure entropy distribution over HTTP (Docker or systemd).

The repo also tracks the **Post-Quantum VRF roadmap** (`vrf-spec/`) — future attested randomness for proof-of-stake rotation, zk-rollup seeding, and lotteries.

---

📦 **Docker Image**

```bash
docker pull pipavlo/r4-local-test:latest
☑️ Pre-built, signed, and self-testing container.
Each startup performs integrity verification and FIPS-style Known Answer Test (KAT) before serving any entropy.

Full validation reports → packages/core/proof/

Contact → shtomko@gmail.com

---

## 🚀 Quickstart (Docker)

Run the service in one line:

```bash
docker run -d \
  --name r4test \
  -p 8080:8080 \
  -e API_KEY=demo \
  pipavlo/r4-local-test:latest
Health check

bash
Copy code
curl -s http://127.0.0.1:8080/health
# -> "ok"
Version / integrity info

bash
Copy code
curl -s http://127.0.0.1:8080/version | jq
Example:

json
Copy code
{
  "name": "re4ctor-api",
  "version": "0.1.0",
  "api_git": "container-build",
  "core_git": "release-core",
  "integrity": "verified",
  "selftest": "pass",
  "mode": "sealed"
}
🔐 Auth Model
The API requires an access key for /random.

Method	Example
Header	x-api-key: demo
Query	?key=demo

Default (for demo):

bash
Copy code
-e API_KEY=demo
Production:

bash
Copy code
docker run -d -p 8080:8080 \
  -e API_KEY="my-super-secret" \
  pipavlo/r4-local-test:latest
Call:

bash
Copy code
curl -s -H "x-api-key: my-super-secret" \
  "http://127.0.0.1:8080/random?n=64&fmt=hex"
📘 API Reference
GET /health
→ Returns "ok" if API is alive.

GET /version
→ Returns metadata: build tags, limits, integrity, and FIPS self-test status.

GET /random
→ Returns cryptographically strong random bytes.

Param	Req	Example	Description
n	✅	32	Number of bytes
fmt	❌	hex / base64	Output format
x-api-key	✅	demo	Auth key

Example:

bash
Copy code
curl -s -H "x-api-key: demo" \
  "http://127.0.0.1:8080/random?n=16&fmt=hex"
# -> 64 hex chars (32 bytes)
Error:

bash
Copy code
curl -i -s -H "x-api-key: WRONG" \
  "http://127.0.0.1:8080/random?n=16&fmt=hex"
# HTTP/1.1 401 Unauthorized
# {"detail":"invalid api key"}
🧱 Inside the Container
Path	Description
/app/runtime/bin/re4_dump	Sealed entropy core
/app/selftest	Integrity manifest & FIPS self-tests
/app/main.py	FastAPI + Uvicorn layer

Environment:

API_KEY — required

STRICT_FIPS=1 — optional fail-closed mode

No external entropy sources used.

🧾 Trust / Audit / Compliance
Each release ships with:

re4_release.tar.gz — sealed core

re4_release.sha256 — manifest

re4_release.tar.gz.asc — GPG signature

SBOM.spdx.json — Software Bill of Materials

Statistical Validation
Dieharder — ✅ All Passed

PractRand — ✅ No anomalies up to 8 GB

TestU01 BigCrush — ✅ 98 %+ pass rate

NIST STS (Monobit, Runs, Approx Entropy) — ✅ p ≈ 0.5

Human-readable summaries under packages/core/proof/.

🧠 Runtime Integrity & FIPS-Style Self-Test
Startup performs:

Integrity Check — verifies binary hash vs manifest

Known-Answer Test (KAT) — ensures non-zero, non-constant output

Example degraded /version:

json
Copy code
{
  "integrity": "verified",
  "selftest": "degraded",
  "mode": "fallback",
  "sealed_core": "/app/runtime/bin/re4_dump"
}
Field	Meaning
integrity	Core hash verified
selftest	pass / degraded / fail
mode	sealed / fallback / blocked

If integrity fails → entropy blocked.
If self-test fails under STRICT_FIPS=1 → 503 fail-closed.
Otherwise → fallback to /dev/urandom (demo mode).

⚙️ Benchmarks
Metric	Value
Throughput	~950 000 req/s
p99 Latency	~1.1 ms
Self-Test	PASS
Manifest	Verified (SHA-256)
Entropy bias	< 10⁻⁶ deviation

See docs/proof/benchmarks_summary.md and docs/proof/fips_readiness.md.

🧩 Security & Openness Model
Verified boot & sealed core

Startup self-test before output

Reproducible signed builds

Optional strict FIPS mode

Transparent SBOM + detached signatures

You can verify randomness quality & build integrity —
but not modify or extract internal state.

🔭 Roadmap — Post-Quantum VRF
Goal: attested randomness for consensus, staking, zk-rollups.

Planned /vrf endpoint:

json
Copy code
{
  "random": "4a6e9d...",
  "signature": "<pq_sig>",
  "public_key": "<node_key>",
  "verified": true
}
Use-cases:

Validator rotation (PoS)

zk-rollup sequencing

On-chain lotteries

Attested randomness feeds

🧰 Deployment
Docker
Run behind reverse proxy (nginx / traefik).
Expose /random internally. Monitor /version.

Example systemd unit:

ini
Copy code
[Unit]
Description=R4 entropy API
After=network-online.target
[Service]
Restart=always
ExecStart=/usr/bin/docker run --rm \
  -p 8080:8080 \
  -e API_KEY=prod-secret \
  --name r4-entropy \
  pipavlo/r4-local-test:latest
ExecStop=/usr/bin/docker stop r4-entropy
[Install]
WantedBy=multi-user.target
📈 Status
Public wrapper code ✅

Closed sealed core 🔒

Docker image: pipavlo/r4-local-test

Use for:

backend key generation

offline RNG

validator randomness

📬 Contact / Sponsors
Maintainer: Pavlo Tvardovskyi
📧 shtomko@gmail.com
🐳 Docker Hub → pipavlo/r4-local-test

For enterprise access, validator beacons, or PQ-VRF integration — reach out.

🏷️ Tags
#entropy #fips #pqcrypto #rng #verifiable #docker #secure #hsm

© 2025 Re4ctoR / r4-monorepo
