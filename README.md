# r4-monorepo

**r4** is an entropy appliance and verifiable randomness API.

It ships two main components:

- **High-entropy core** (`re4_dump`) — closed-source, statistically verified (Dieharder / PractRand / BigCrush), shipped as a signed binary.
- **Hardened HTTP API** (`/random`) — rate-limited, key-protected, designed to run as a service (systemd or Docker).

This repo also contains the roadmap for **Post-Quantum Verifiable Randomness (vrf-spec)** —  
attestable randomness for proof-of-stake rotation, zk-rollup seeding, lotteries, and more.

---

## Quickstart (Docker)

Run the whole service with a single Docker command.

### Prerequisites
- Docker Desktop (Windows/macOS) or Docker Engine (Linux)
- Port `8080` must be free

### Run the container

```bash
docker run -d \
  --name r4test \
  -p 8080:8080 \
  -e API_KEY=demo \
  pipavlo/r4-local-test:latest
Health check
bashcurl -s http://127.0.0.1:8080/health
# -> "ok"
Version / Build info
bashcurl -s http://127.0.0.1:8080/version | jq
Example output:
json{
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
bashcurl -s -H "x-api-key: demo" \
  "http://127.0.0.1:8080/random?n=32&fmt=hex"
Returns 64 hex chars (32 bytes), different every call.
What happens:

The sealed binary /app/runtime/bin/re4_dump executes inside the container.
The API enforces the API key.
Output is served over HTTP with rate limiting.
No external network calls — randomness is generated locally.


Auth Model
The API requires a key for /random.

















MethodExampleHeaderx-api-key: demoQuery?key=demo
Default container env:
bash-e API_KEY=demo
Change in production:
bashdocker run -d \
  -p 8080:8080 \
  -e API_KEY="my-super-secret" \
  pipavlo/r4-local-test:latest
Call with new key:
bashcurl -s -H "x-api-key: my-super-secret" \
  "http://127.0.0.1:8080/random?n=64&fmt=hex"

API Reference
GET /health
Returns "ok" if the API is alive.
GET /version
Returns metadata about the running instance:

























FieldDescriptioncore_gitbuild/commit tag of the entropy coreapi_gitbuild tag for the API layerlimitsrate limit and max request sizeintegrity / selftestruntime FIPS self-test status
Useful for audit dashboards and integrity monitoring.
GET /random
Request random bytes.





























ParamRequiredExampleDescriptionnYes32Number of bytesfmtNohexOutput format (hex, base64, or raw)x-api-keyYesdemoAPI key
Examples
16 bytes, hex-encoded:
bashcurl -s -H "x-api-key: demo" \
  "http://127.0.0.1:8080/random?n=16&fmt=hex"
64 raw bytes saved to file:
bashcurl -s -H "x-api-key: demo" \
  "http://127.0.0.1:8080/random?n=64" \
  --output sample.bin

hexdump -C sample.bin | head
Error (invalid key):
bashcurl -i -s -H "x-api-key: WRONG" \
  "http://127.0.0.1:8080/random?n=16&fmt=hex"
# -> HTTP/1.1 401 Unauthorized
# {"detail": "invalid api key"}

Inside the Container
The published image pipavlo/r4-local-test:latest bundles:





















PathDescription/app/runtime/bin/re4_dumpSealed entropy generator binary/app/selftestIntegrity manifest & FIPS selftest/app/main.pyFastAPI + Uvicorn REST API
Runtime configuration:

API_KEY — required for /random
STRICT_FIPS (optional) — fail-closed mode

No external entropy sources pulled at runtime

Trust / Audit / Compliance
This acts as a software entropy appliance.
We ship:

re4_release.tar.gz — release tarball
re4_release.sha256 — SHA-256 manifest
re4_release.tar.gz.asc — detached GPG signature
SBOM.spdx.json — Software Bill of Materials

Statistical batteries performed:

Dieharder
PractRand
TestU01 BigCrush

Human-readable summaries live under packages/core/proof/.
Full multi-GB raw logs are archived offline and shared under NDA.
The internal DRBG/entropy core is not open-sourced, following an HSM-style model:

You can measure output quality.
You can verify supply-chain integrity (hash + GPG signature + SBOM).
You cannot clone the internal mixing algorithm.


Runtime Integrity & FIPS-Style Self-Test
The r4 container behaves like a sealed entropy appliance.
At startup it performs:

Integrity check — verifies /app/runtime/bin/re4_dump against its shipped manifest.
Known Answer Test (KAT) — ensures the core produces non-zero, non-constant bytes.

Reports results via /version.
If integrity fails → entropy is blocked.
If self-test times out → the API enters degraded or fallback mode.
Example /version output on degradation:
json{
  "integrity": "verified",
  "selftest": "degraded",
  "mode": "fallback",
  "sealed_core": "/app/runtime/bin/re4_dump"
}





















FieldMeaningintegrityCore hash matches manifestselftestpass / degraded / failmodesealed / fallback / blocked

Benchmarks & FIPS Readiness





























MetricValueThroughput~950,000 req/sLatency p99~1.1 msSelf-TestPASSManifestVerifiedEntropy bias<10⁻⁶ deviation
See docs/proof/benchmarks_summary.md and docs/proof/fips_readiness.md for details.

Security / Openness Model
r4 behaves like a software HSM:

Reproducible, signed builds
Verified at startup
Self-tested entropy path
Optional strict FIPS mode (fail-closed)
Supply-chain transparency (SBOM + GPG)


You can test it, verify it, but not modify its core.


Roadmap — Post-Quantum VRF
Goal: verifiable randomness for consensus, staking, and zk-rollups.
Attach a post-quantum signature (Dilithium / Kyber class) to every response:
json{
  "random": "4a6e9d...",
  "signature": "<pq_sig>",
  "public_key": "<node_key>",
  "verified": true
}
Intended consumers:

Validator set rotation (PoS)
zk-rollup sequencers
On-chain lotteries and airdrops
Attested randomness feeds

Positioning:

/random = fast local entropy
/vrf = attestable, cryptographically provable randomness


Production Deployment
Docker (recommended)
Run behind a reverse proxy (nginx / traefik / API gateway).
Expose /random only internally.
Keep API_KEY secret.
Monitor /version for expected core_git values.
Example systemd unit:
ini[Unit]
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
Bare Metal / systemd
Run uvicorn + re4_dump directly as non-root with sandboxing:
iniProtectSystem=strict
ProtectHome=true
MemoryDenyWriteExecute=true
See:

packages/core/docs/USAGE.md
packages/core/docs/re4ctor-api.service.example


Status
This repo is public. The entropy core is sealed.
Public Docker image:
bashdocker pull pipavlo/r4-local-test:latest
Use it to:

Integrate into backend services
Generate keys/secrets
Feed offline RNG systems
Demonstrate for infra / validator teams


License / NOTICE
See LICENSE and NOTICE.
Summary:

Wrapper code & API → open & auditable
Core binary → compiled, signed, reproducible
Internal entropy combiner → private (HSM model)


You can test quality & verify authenticity,
but you can’t tamper with the sealed core.


Benchmarks Summary



































Test SuiteStatusResultDieharderPassAll PassedPractRandPassNo anomalies up to 8GBBigCrushPassPass rate 98%+FIPS MonobitPassp=0.53Runs / Approx EntropyPassWithin expected range
Logs archived under /proof/.

Contact / Sponsors
Maintainer: Pavlo Tvardovskyi
Email: shtomko@gmail.com
Docker Hub: pipavlo/r4-local-test
For enterprise access, on-prem deployments, or PQ-signed VRF services — reach out via email or GitHub Issues.

Tags
text#entropy #fips #pqcrypto #rng #verifiable #docker #secure #hsm

© 2025 Re4ctoR / r4-monorepo
