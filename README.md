# 🧬 re4-monorepo

> **Entropy appliance + Post-Quantum Verifiable Randomness.**  
> Secure core now. Verifiable randomness next.

---

## 🧩 Repo layout

packages/
core/ → production entropy core + API + proof
vrf-spec/ → PQ-VRF design, roadmap, investor materials

yaml
Copy code

---

## ⚙️ Core (packages/core)

A hardened entropy engine:

- 🧠 **`re4_dump`** — C binary streaming high-entropy bytes
- 🌐 **FastAPI `/random`** — HTTP service with rate limits and API keys
- 🔒 **Signed release** — `.tar.gz` + `.sha256` + `.asc`
- 📦 **SBOM** — SPDX 2.3 software bill of materials
- 📊 **Statistical proof** — Dieharder / PractRand / TestU01 BigCrush
- 🧱 **systemd unit** — sandboxed service (non-root, restart, memory-locked)

### Quick check
```bash
./re4_dump | head -c 32 | hexdump -C
✅ You should see non-repeating hex output each run.

🌐 API Overview
Endpoint	Description
GET /health	returns "ok"
GET /version	build info + git rev
GET /random	random bytes (requires API key)

Auth
text
Copy code
Dev:  x-api-key: local-demo
Prod: API_KEY=<your-secret> in .env
Example
bash
Copy code
curl -s -H "x-api-key: local-demo" \
  "http://127.0.0.1:8080/random?n=32&fmt=hex"
Limits
10 req/sec per client

1 MB max per request

every call logged with IP and first-4-bytes fingerprint

🧰 Systemd Deployment
File → docs/re4ctor-api.service.example

Features:

non-root service user

.env for API_KEY

ProtectSystem, ProtectHome, MemoryDenyWriteExecute

auto-restart on failure

Start:

bash
Copy code
systemctl enable re4ctor-api
systemctl start re4ctor-api
🔐 Supply-chain trust
We publish:

bash
Copy code
re4_release.tar.gz
re4_release.sha256
re4_release.tar.gz.asc
Verify integrity:

bash
Copy code
sha256sum -c re4_release.sha256
gpg --verify re4_release.tar.gz.asc re4_release.tar.gz
If both pass — you’re running the exact build we signed.

📈 Statistical Assurance
Test suite	Status
Dieharder	✅ PASS / occasional WEAK
PractRand	✅ PASS up to multi-GB
TestU01 BigCrush	✅ PASS

All logs summarized in proof/.
Full raw logs archived offline.

🧩 PQ-VRF Roadmap (packages/vrf-spec)
Future endpoint /vrf will return verifiable randomness:

json
Copy code
{
  "random": "<N bytes>",
  "signature": "<post-quantum signature>",
  "public_key": "<PQ public key>",
  "verified": true
}
Use cases
PoS validator / committee rotation

zk-rollup seeding

on-chain lotteries & airdrops

audit-proof entropy beacons

Built on Dilithium / Kyber-class primitives.

🧪 Compliance / audit model
We do not publish private entropy internals.
Instead, we prove behavior through:

reproducible build

SBOM + GPG signature

public statistical evidence

offline reproducibility

Think HSM-style transparency: you can measure the output, not clone the internals.

🚀 Roadmap
Now:
✅ entropy appliance /random
✅ signed bundles + SBOM
✅ statistical certification

Next:
🔜 /vrf endpoint (random + PQ proof)
🔜 validator rotation / fairness oracle

Vision:
Entropy for a post-quantum world.

🧱 TL;DR
Today	Tomorrow
/random entropy appliance	/vrf verifiable PQ randomness
signed SBOM + proof	PQ-signed randomness beacon
production-ready API	blockchain-verifiable source
