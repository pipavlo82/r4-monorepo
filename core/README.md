🧬 re4ctor-core

Status: Public Drop v0.1
Build type: Verified core + signed user binary
Includes: FastAPI / random service, usage docs, systemd unit & SBOM proof
License: Restricted public binary — internal entropy / DRBG core not disclosed

This release provides a reproducible entropy tap with verifiable statistical quality and an operational API layer.
You get a callable RNG service with proofs. You do not get the private DRBG/entropy internals.

🔐 Supply Chain Verification

sha256sum -c re4_release.sha256
gpg --verify re4_release.tar.gz.asc re4_release.tar.gz

If both pass — you have exactly what we built.

Extract & test:

mkdir -p ~/re4ctor-local
tar -C ~/re4ctor-local -xzf re4_release.tar.gz
~/re4ctor-local/bin/re4_dump | head -c 32 | hexdump -C

Each run → unique, non-zero, non-repeating hex stream.

⚙️ API Service ( re4ctor-api )

Exposes:

GET /health → "ok"

GET /version → build info + git rev

GET /info → usage help

GET /random → random bytes (requires API key)

Auth

Dev/default: x-api-key: local-demo or ?key=local-demo
Prod: set API_KEY in .env and restart service.

Examples

16 bytes (hex):
curl -s -H "x-api-key: local-demo" "http://127.0.0.1:8080/random?n=16&fmt=hex
"

64 raw bytes:
curl -s -H "x-api-key: local-demo" "http://127.0.0.1:8080/random?n=64
" | hexdump -C

Invalid key:
curl -i -s -H "x-api-key: WRONG" "http://127.0.0.1:8080/random?n=16&fmt=hex
"
→ 401 Unauthorized {"detail":"invalid key"}

Limits

10 req/sec per IP • max 1 000 000 bytes per request
Example log: [re4/random] ip=127.0.0.1 n=16 fmt=hex head4=7eca4753

🧩 Local Run (Developer Mode)

cd ~/re4ctor-local/re4ctor-api

Create .env:

API_HOST=127.0.0.1
API_PORT=8080
API_KEY=local-demo
API_GIT=local-api
CORE_GIT=release-core


Start: ./api_start.sh start
Check:

curl -s http://127.0.0.1:8080/health
curl -s http://127.0.0.1:8080/version
curl -s -H "x-api-key: local-demo" "http://127.0.0.1:8080/random?n=32&fmt=hex"


Manage: status | log | stop Logs → ~/re4ctor-local/re4ctor-api/logs/api.log

🧱 Production Deployment (systemd)

File: docs/re4ctor-api.service.example

Highlights

Dedicated user

.env for keys & metadata

Sandbox: ProtectSystem, ProtectHome, MemoryDenyWriteExecute

Auto-restart on failure

Steps:

Copy bundle → /opt/re4ctor

Set API_KEY in .env

sudo systemctl enable --now re4ctor-api

Operator docs: docs/USAGE.md

🧮 Build & Self-Test (WSL/Ubuntu)

cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build -j"$(nproc)"
./build/re4_dump | head -c 32 | hexdump -C

cd build && ctest --output-on-failure

Executables:

build/re4_dump – entropy stream

build/re4_tests – internal DRBG self-tests

🧾 SBOM & Signed Bundle

syft packages dir:release -o spdx-json > release/SBOM.spdx.json
tar -C release -czf re4_release.tar.gz .
sha256sum re4_release.tar.gz > re4_release.sha256
gpg --armor --detach-sign re4_release.tar.gz

Verify:
sha256sum -c re4_release.sha256
gpg --verify re4_release.tar.gz.asc re4_release.tar.gz

🛡️ Threat Model

Not published:

src/entropy/*.c

src/drbg/*.c

internal heuristics / seed path

Treat binary as hardware RNG:

auditable via PractRand / Dieharder / BigCrush

verifiable SBOM & GPG signature

non-clonable

We prove the water is clean — without showing the plumbing.

📊 Statistical Proof

proof/ contains:

dieharder summary

PractRand summary

BigCrush summary

All passed without critical bias.
Occasional WEAK in Dieharder is normal even for /dev/urandom.
No persistent FAIL detected.
Raw logs (GB-scale) available under NDA.

🚀 CI / Roadmap

Multi-platform build + tests

/health / /version schema checks

Statistical bursts on each run
Next: appliance mode & private-network entropy service

🧠 TL;DR

✅ re4ctor-core → C binary for entropy bytes
✅ re4ctor-api → REST interface with key auth & rate limit
✅ Signed bundle + SBOM + GPG sig
✅ systemd hardened service
❌ DRBG internals remain private by design

💡 Motto: Entropy for a Quantum World.
