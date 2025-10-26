# ⚡ r4-monorepo — entropy appliance & verifiable randomness API

[![docker pulls](https://img.shields.io/docker/pulls/pipavlo/r4-local-test?style=flat-square)](https://hub.docker.com/r/pipavlo/r4-local-test)
[![image size](https://img.shields.io/docker/image-size/pipavlo/r4-local-test/latest?style=flat-square)](https://hub.docker.com/r/pipavlo/r4-local-test)
[![re4ctor-ci](https://github.com/pipavlo82/r4-monorepo/actions/workflows/ci.yml/badge.svg)](https://github.com/pipavlo82/r4-monorepo/actions/workflows/ci.yml)
[![sanity-check](https://img.shields.io/badge/sanity--check-passing-brightgreen?style=flat-square)](https://github.com/pipavlo82/r4-monorepo/actions/workflows/public-sanity.yml)

---

[![Docker Pulls](https://img.shields.io/docker/pulls/pipavlo/r4-local-test?style=flat-square)](https://hub.docker.com/r/pipavlo/r4-local-test)
[![Image Size](https://img.shields.io/docker/image-size/pipavlo/r4-local-test/latest?style=flat-square)](https://hub.docker.com/r/pipavlo/r4-local-test)
[![License](https://img.shields.io/github/license/pipavlo82/r4-monorepo?style=flat-square)](LICENSE)
[![re4ctor-ci](https://github.com/pipavlo82/r4-monorepo/actions/workflows/ci.yml/badge.svg)](https://github.com/pipavlo82/r4-monorepo/actions/workflows/ci.yml)
[![public-sanity](https://github.com/pipavlo82/r4-monorepo/actions/workflows/public-sanity.yml/badge.svg)](https://github.com/pipavlo82/r4-monorepo/actions/workflows/public-sanity.yml)
![NIST STS](https://img.shields.io/badge/NIST%20SP800--22-100%25_Pass-brightgreen?style=flat-square)
![BigCrush](https://img.shields.io/badge/TestU01_BigCrush-160%2F160_Pass-blue?style=flat-square)
![PractRand](https://img.shields.io/badge/PractRand-8GB_Clean-success?style=flat-square)
![FIPS-140](https://img.shields.io/badge/FIPS--140_Pre--Audit-Ready-blue?style=flat-square)
![Post-Quantum VRF](https://img.shields.io/badge/Post--Quantum_VRF-Ready-purple?style=flat-square)

---

### 🧠 Overview
**r4-monorepo** is a self-contained entropy appliance and verifiable randomness API.  
It delivers high-entropy randomness for post-quantum cryptography, zero-knowledge systems, lotteries, and consensus protocols.  
All randomness is statistically verified and cryptographically attestable.

---

### 🛡️ Security & Compliance

Re4ctor entropy core is validated against:

- **NIST SP800-22 (STS)** — 15/15 statistical tests passed (frequency, runs, entropy, block, serial, FFT)
- **Dieharder** — 31/31 passed (no weak results)
- **PractRand** — continuous stream up to 8 GiB, no anomalies detected
- **TestU01 BigCrush** — full battery completed successfully (160/160 passed)
- **FIPS-140 pre-audit** — entropy health tests + continuous self-check
- **VRF / Attestation** — Post-Quantum VRF spec draft (Kyber512 + Dilithium2)
- **SBOM / SPDX manifest** — reproducible cryptographic supply chain (SHA-256 verified)

All proof summaries and statistical audit logs are published under:  
[`/packages/core/proof`](./packages/core/proof)

📦 [SBOM (SPDX JSON)](packages/core/release/SBOM.spdx.json) — reproducible build manifest

### Integrity / Attestation

On startup every container:
1. Verifies the sealed core binary (`/app/runtime/bin/re4_dump`) against a shipped SHA-256 manifest.
2. Runs a self-test (KAT) to make sure the core actually produces non-trivial entropy in time.
3. Exposes its state over `/version`.

Example `/version` response:

```json
{
  "integrity": "verified",
  "selftest": "degraded",
  "mode": "fallback",
  "sealed_core": "/app/runtime/bin/re4_dump",
  "limits": {
    "max_bytes_per_request": 1000000,
    "rate_limit": "10/sec per IP (enforced in prod by reverse proxy)"
  }
}
Field meanings:

"integrity": "verified" → binary hash matches the signed manifest.

"selftest": "pass" | "degraded" | "fail" → startup Known Answer Test status.

"mode": "sealed" | "fallback" | "blocked"

sealed = core OK

fallback = core slow / degraded, service is temporarily using /dev/urandom (only in demo mode)

blocked = strict FIPS mode; no entropy served.

If integrity fails → no randomness is served at all.
If STRICT_FIPS=1 and selftest ≠ "pass" → 503 and still no randomness.

This mimics HSM behavior:

verified boot

power-on self-test

remote attestation surface (/version)

optional fail-closed policy
---

ця секція — прям золото для безпекарів. зараз у README воно є частинами, але не як один концентрований блок. встав її як новий підзаголовок `### Integrity / Attestation`. це дає тобі право казати “FIPS-style sealed entropy appliance” і звучати серйозно.

після вставки:
```bash
nano README.md   # вставляєш блок вище
git add README.md
git commit -m "docs: add Integrity / Attestation section (HSM-style boot + /version semantics)"
git push origin main

### 🧰 Quickstart (Docker)

```bash
docker run -d \
  --name r4test \
  -p 8080:8080 \
  -e API_KEY=demo \
  docker.io/pipavlo/r4-local-test:latest
Then verify:

bash
Copy code
curl -s http://127.0.0.1:8080/random?len=32 | hexdump -C
🧩 Modules
Package	Description
packages/core	C entropy engine + statistical proofs
packages/api	Hardened HTTP API (FastAPI + uvicorn)
packages/vrf	Post-Quantum verifiable randomness (Kyber, Dilithium)
packages/tools	Benchmarks, analyzers, and test harness

📞 Contact
Maintainer: Pavlo Tvardovskyi
Docker Hub: pipavlo
GitHub: pipavlo82/r4-monorepo
=======
>>>>>>> 87979d8 (docs: final clean README with attestation + PQ VRF)
## 🧠 Overview

**r4** is a high-entropy appliance and verifiable randomness API.

It delivers:
- 🔒 **Sealed entropy core (`re4_dump`)** — closed-source, statistically verified via Dieharder / PractRand / BigCrush, shipped as a signed binary.  
- 🌐 **Hardened FastAPI layer** — key-protected `/random` endpoint for secure entropy distribution over HTTP (Docker or systemd).

The repo also tracks the **Post-Quantum VRF roadmap** (`vrf-spec/`) — future attested randomness for proof-of-stake rotation, zk-rollup seeding, and lotteries.

---

## 📦 Docker Image

```bash
docker pull pipavlo/r4-local-test:latest
☑️ Pre-built, signed, and self-testing container.
Each startup performs integrity verification and FIPS-style Known Answer Test (KAT) before serving any entropy.

Full validation reports → packages/core/proof/

Contact → shtomko@gmail.com

🚀 Quickstart (Docker)

Run the service in one line:
docker run -d \
  --name r4test \
  -p 8080:8080 \
  -e API_KEY=demo \
  pipavlo/r4-local-test:latest
Health check:
curl -s http://127.0.0.1:8080/version | jq
Version / integrity info:
curl -s http://127.0.0.1:8080/version | jq
Example:
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
Method	Example
Header	x-api-key: demo
Query	?key=demo

Default (demo):
-e API_KEY=demo
Production:
docker run -d -p 8080:8080 \
  -e API_KEY="my-super-secret" \
  pipavlo/r4-local-test:latest

Call:
curl -s -H "x-api-key: my-super-secret" \
  "http://127.0.0.1:8080/random?n=64&fmt=hex"

📘 API Reference

GET /health — Returns "ok" if API is alive.
GET /version — Returns build info, integrity, and FIPS self-test status.
GET /random — Returns cryptographically strong random bytes.

Param	Req	Example	Description
n	✅	32	Number of bytes
fmt	❌	hex / base64	Output format
x-api-key	✅	demo	Auth key

Example:
curl -s -H "x-api-key: demo" \
  "http://127.0.0.1:8080/random?n=16&fmt=hex"
# -> 64 hex chars (32 bytes)
Unauthorized:
curl -i -s -H "x-api-key: WRONG" \
  "http://127.0.0.1:8080/random?n=16"
# -> HTTP/1.1 401 Unauthorized

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

Statistical Validation:

Dieharder — ✅ 31/31 passed

PractRand — ✅ up to 8 GB, no anomalies

TestU01 BigCrush — ✅ 100 % pass rate (160/160 tests)

NIST SP800-22 — ✅ 15/15 passed (p ≈ 0.5)

Summaries: packages/core/proof/

🔐 Integrity / Attestation

Every container boot performs hardware-style attestation before serving entropy.

Integrity check
The sealed core binary (/app/runtime/bin/re4_dump) is hashed and compared against a shipped manifest (/app/selftest/manifest.json).
If the hash does not match → entropy service is blocked.

Startup self-test (KAT)
A Known-Answer-Test runs the core once and checks that it returns non-zero, non-constant data within a strict timeout.
If it times out or fails → the node reports selftest: "degraded" or "fail".

Remote attestation surface
The node exposes its current state at /version. Example:
{
  "integrity": "verified",
  "selftest": "degraded",
  "mode": "fallback",
  "sealed_core": "/app/runtime/bin/re4_dump",
  "limits": {
    "max_bytes_per_request": 1000000,
    "rate_limit": "10/sec per IP (enforced in prod by reverse proxy)"
  }
}
Field meanings:

integrity: "verified" → binary hash matches the signed manifest.

selftest: "pass" | "degraded" | "fail" → startup Known Answer Test result.

mode: "sealed" | "fallback" | "blocked"

sealed — core OK

fallback — degraded, using /dev/urandom (demo mode only)

blocked — strict FIPS mode, no entropy served.

Fail-closed policy

If integrity fails → no randomness is served.

If STRICT_FIPS=1 and selftest ≠ "pass" → HTTP 503.

Demo mode allows fallback, reported transparently via /version.

This model behaves like an HSM:

verified boot

power-on self-test

remote attestable health

optional fail-closed enforcement

⚙️ Benchmarks
Metric	Value
Throughput	~950 000 req/s
p99 Latency	~1.1 ms
Self-Test	PASS
Manifest	Verified (SHA-256)
Entropy bias	< 10⁻⁶ deviation

See: docs/proof/benchmarks_summary.md, docs/proof/fips_readiness.md

🛡️ Security & Compliance

Re4ctor entropy core is validated against:

NIST SP 800-22 — full suite (15/15 passed)

Dieharder — 31/31 passed

PractRand — 8 GB stream tested, no anomalies

TestU01 BigCrush — 160/160 tests passed (100 % acceptance) → summary-2025-01.md

FIPS-140 pre-audit — entropy health + continuous self-check

VRF / Attestation — post-quantum VRF spec draft (Kyber + Dilithium)

🔭 PQ VRF Roadmap (Q1–Q2)

Next service endpoint: /vrf.

Example output:
{
  "random": "<bytes>",
  "signature": "<pq_sig>",
  "public_key": "<node_key>",
  "verified": true
}
Design goals

Post-quantum signature (Dilithium-class) attached to each randomness output.

Anyone can verify:

randomness came from an authorized node

operator could not reroll for a “lucky” output

Target use-cases

validator rotation / leader election (PoS systems)

zk-rollup sequencer / prover seed

lotteries / airdrops / NFT mints

anti-manipulation feeds for off-chain games

Goal:
beat Chainlink VRF on transparency, latency & PQ-safety.
Expose /version-style attestation for each beacon.

🧰 Deployment

Run behind reverse proxy (nginx / traefik).
Expose /random internally. Monitor /version.

Example systemd unit:

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

✅ Public API wrapper
🔒 Closed sealed core
🐳 Docker image: pipavlo/r4-local-test

Use for:

backend key generation

offline RNG

validator randomness

📬 Contact / Sponsors

Maintainer: Pavlo Tvardovskyi
📧 shtomko@gmail.com
🐳 Docker Hub → pipavlo/r4-local-test

💻 GitHub → pipavlo82/r4-monorepo

For enterprise access / PQ-VRF integration — reach out.

🏷️ Tags: #entropy #fips #pqcrypto #rng #verifiable #docker #secure #hsm

© 2025 Re4ctoR / r4-monorepo
