⚡ r4-monorepo

r4 — an entropy appliance and verifiable randomness API

🧠 Overview

r4 provides deterministic, reproducible, and auditable high-entropy random data for cryptographic, blockchain, and infrastructure applications.
It consists of two tightly coupled layers:

Component	Description
🧩 High-entropy core (re4_dump)	Closed-source, statistically verified with Dieharder / PractRand / BigCrush. Shipped as a signed binary.
🌐 Hardened HTTP API (/random)	Rate-limited, key-protected REST API (FastAPI + Uvicorn). Designed for Docker / systemd deployment.

The repository also contains the roadmap for Post-Quantum Verifiable Randomness (VRF) — attestable randomness for staking, zk-rollups, and lotteries.

🚀 Quickstart
Prerequisites

🐳 Docker Desktop (Windows/macOS) or Docker Engine (Linux)

🔌 Port 8080 available

Run
docker run -d \
  --name r4test \
  -p 8080:8080 \
  -e API_KEY=demo \
  pipavlo/r4-local-test:latest

Health Check
curl -s http://127.0.0.1:8080/health
# -> "ok"

Version Info
curl -s http://127.0.0.1:8080/version | jq

Request Random Bytes
curl -s -H "x-api-key: demo" \
  "http://127.0.0.1:8080/random?n=32&fmt=hex"
# -> 64 hex chars (32 bytes)

🔐 Authentication

The API requires an access key for /random.

Method	Example
Header	x-api-key: demo
Query	?key=demo

Default container key:

-e API_KEY=demo


Change this in production.

📚 API Reference
Endpoint	Description
GET /health	Returns "ok" if the API is alive
GET /version	Returns version, integrity, and self-test state
GET /random	Returns cryptographic-grade random bytes
Parameters
Name	Required	Example	Description
n	✅	32	Number of bytes
fmt	❌	hex	Output format
Header	✅	x-api-key: demo	Authentication key

Example:

curl -s -H "x-api-key: demo" \
  "http://127.0.0.1:8080/random?n=64&fmt=hex"


Error (invalid key):

curl -i -H "x-api-key: WRONG" \
  "http://127.0.0.1:8080/random?n=16&fmt=hex"
# HTTP/1.1 401 Unauthorized

🧰 Inside the Container

/app/runtime/bin/re4_dump — sealed entropy core

FastAPI + Uvicorn — REST layer

Built-in rate limiting & request logging

No external entropy source — all randomness generated locally

Environment variables:

Variable	Default	Description
API_KEY	demo	Required for /random
API_HOST	0.0.0.0	API bind address
API_PORT	8080	Port to expose
🧮 Trust / Audit / Compliance

Every release includes:

re4_release.tar.gz — sealed binary core

re4_release.sha256 — manifest

re4_release.tar.gz.asc — detached GPG signature

SBOM.spdx.json — software bill of materials

Statistical Testing

Performed with:

Dieharder

PractRand

TestU01 BigCrush

Summaries: docs/proof/
Full multi-GB logs are archived offline.

🛡 Runtime Integrity & FIPS-Style Self-Test

At startup the container performs integrity and known-answer tests.

Integrity Check

Verifies /app/runtime/bin/re4_dump against /app/selftest/manifest.json.
If the hash doesn’t match → API refuses to serve entropy.

Startup Self-Test (KAT)

Runs the core once to ensure non-zero, non-constant output within a timeout.
Failure results in:

"selftest": "degraded"

Attestation Endpoint
curl -s http://127.0.0.1:8080/version | jq


Example:

{
  "integrity": "verified",
  "selftest": "degraded",
  "mode": "fallback",
  "sealed_core": "/app/runtime/bin/re4_dump"
}

Field	Description
integrity	"verified" → binary matches manifest
selftest	"pass" / "degraded" → self-test result
mode	"sealed" = core, "fallback" = urandom, "blocked" = strict FIPS
sealed_core	Path to verified binary

Policy:

Integrity fail → block entropy.

STRICT_FIPS=1 + degraded test → block (503).

Demo mode → fallback to /dev/urandom, reported via "mode": "fallback".

⚙️ Benchmarks & FIPS Readiness
Metric	Value
Throughput	~950 000 req/s
p99 Latency	~1.1 ms
Self-Test	PASS
Manifest	Verified (SHA-256)

See docs/proof/benchmarks_summary.md and docs/proof/fips_readiness.md for details.

🔭 Roadmap: Post-Quantum Verifiable Randomness (VRF)

Next phase — attach a Dilithium / Kyber identity to each randomness sample.
Each response will be cryptographically signed and externally verifiable.

Example:

{
  "random": "...",
  "signature": "<pq_sig>",
  "public_key": "<node_key>",
  "verified": true
}


Target use-cases:

PoS validator rotation

zk-rollup sequencing

On-chain lotteries / airdrops

🧩 Security / Openness Model

r4 behaves like a software HSM:

output statistically auditable

release cryptographically verifiable

internals sealed against tampering

You can test and verify every output — but not modify the entropy core.

🤝 Contact

For enterprise access, validator beacons, or PQ-signed VRF integration:
📧 shtomko@gmail.com

✅ Copy this block as-is — GitHub will render it cleanly, with code blocks, tables, and no text collapse.
Хочеш, я додам зверху три бейджі (Docker Pulls | License | FIPS-Ready) у наступній версії?

You said:
так
ChatGPT said:

Чудово 🔥
Ось фінальна версія README.md з бейджами (Docker Pulls | License | FIPS Ready), чистою розміткою й чітким виглядом у браузері або на GitHub.
Можеш просто скопіювати й вставити у свій README.md.

⚡ r4-monorepo






r4 — an entropy appliance and verifiable randomness API

🧠 Overview

r4 provides deterministic, auditable, and statistically proven randomness for cryptographic / blockchain / infrastructure use.

Component	Description
🧩 High-entropy core (re4_dump)	Closed-source, verified with Dieharder / PractRand / BigCrush. Shipped as a signed binary.
🌐 Hardened HTTP API (/random)	Rate-limited, key-protected FastAPI service for Docker / systemd.

Roadmap includes Post-Quantum Verifiable Randomness (VRF) for staking, zk-rollups and lotteries.

🚀 Quickstart
Prerequisites

🐳 Docker Desktop (Win/macOS) or Docker Engine (Linux)

🔌 Port 8080 available

Run
docker run -d \
  --name r4test \
  -p 8080:8080 \
  -e API_KEY=demo \
  pipavlo/r4-local-test:latest

Health check
curl -s http://127.0.0.1:8080/health
# -> "ok"

Version info
curl -s http://127.0.0.1:8080/version | jq

Request random bytes
curl -s -H "x-api-key: demo" \
  "http://127.0.0.1:8080/random?n=32&fmt=hex"
# -> 64 hex chars (32 bytes)

🔐 Authentication
Method	Example
Header	x-api-key: demo
Query	?key=demo

Default key inside container:

-e API_KEY=demo


Change it in production.

📚 API Reference
Endpoint	Description
GET /health	Returns "ok"
GET /version	Build / integrity info
GET /random	Returns cryptographic random bytes
Parameters
Name	Req	Example	Description
n	✅	32	Number of bytes
fmt	❌	hex	Output format
x-api-key	✅	demo	Auth key

Example

curl -s -H "x-api-key: demo" \
  "http://127.0.0.1:8080/random?n=64&fmt=hex"


Error

curl -i -H "x-api-key: WRONG" \
  "http://127.0.0.1:8080/random?n=16&fmt=hex"
# HTTP/1.1 401 Unauthorized

🧰 Inside the Container

/app/runtime/bin/re4_dump — sealed entropy core

FastAPI + Uvicorn REST layer

Built-in rate limiting & logging

Local entropy generation (offline)

Env Var	Default	Description
API_KEY	demo	Required for /random
API_HOST	0.0.0.0	Bind address
API_PORT	8080	Exposed port
🧮 Trust / Audit / Compliance

Every release includes:

re4_release.tar.gz — sealed core

re4_release.sha256 — manifest

re4_release.tar.gz.asc — GPG signature

SBOM.spdx.json — bill of materials

Statistical Testing

Dieharder

PractRand

TestU01 BigCrush

Summaries: docs/proof/
Full logs archived offline.

🛡 Runtime Integrity & FIPS-Style Self-Test
Integrity Check

Verifies /app/runtime/bin/re4_dump hash vs manifest.json.
If mismatch → no entropy served.

Startup Self-Test (KAT)

Runs once on boot → ensures non-zero entropy.
Failure → "selftest": "degraded".

Attestation Endpoint
curl -s http://127.0.0.1:8080/version | jq


Example:

{
  "integrity": "verified",
  "selftest": "degraded",
  "mode": "fallback",
  "sealed_core": "/app/runtime/bin/re4_dump"
}

Field	Meaning
integrity	verified → manifest matched
selftest	pass / degraded → self-test result
mode	sealed = core, fallback = urandom, blocked = strict FIPS
sealed_core	Path to verified binary

Policy

Integrity fail → block entropy.

STRICT_FIPS=1 + degraded → 503.

Demo mode → fallback /dev/urandom.

⚙️ Benchmarks & FIPS Readiness
Metric	Value
Throughput	~950 000 req/s
p99 Latency	~1.1 ms
Self-Test	PASS
Manifest	SHA-256 Verified

See docs/proof/fips_readiness.md

🔭 Roadmap — Post-Quantum VRF

Attach Dilithium / Kyber identity to randomness outputs:
signed and verifiable entropy for consensus and staking.

Example:

{
  "random": "...",
  "signature": "<pq_sig>",
  "public_key": "<node_key>",
  "verified": true
}


Use cases:

Validator rotation (PoS)

zk-rollup sequencing

On-chain lotteries / airdrops

🧩 Security Model

Behaves like a software HSM:

auditable output

verifiable build integrity

sealed core (anti-tamper)

🤝 Contact

📧 shtomko@gmail.com
For enterprise access, on-prem deployments and PQ-VRF integration.
