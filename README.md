
🧠 Overview

Re4ctor (R4) — high-assurance entropy appliance + post-quantum verifiable randomness platform.

It includes:

🔒 Entropy Core (8080) — sealed binary re4_dump, Dieharder / PractRand / BigCrush validated

🔐 PQ-VRF Node (8081) — ECDSA & Dilithium3 (FIPS 204) signatures

💠 On-chain Verifier — Solidity contracts verifying R4 signatures

🧬 Python SDK (r4sdk) — available on PyPI

🚀 One-Command Demo
./run_full_demo.sh


Runs both nodes (8080 + 8081), fetches signed randomness, performs stress-tests, runs Solidity tests, and proves a fair lottery draw.

Expected output:

✅ 8080 entropy OK
✅ 8081 PQ/VRF OK
✅ 200 req/sec no errors
✅ Hardhat tests: 5 passing
✅ LotteryR4: fair winner verified

🐳 Docker Quickstart
docker run -d -p 8080:8080 \
  -e API_KEY=demo \
  pipavlo/r4-local-test:latest


Health:

curl http://127.0.0.1:8080/health


Random bytes:

curl -H "x-api-key: demo" \
  "http://127.0.0.1:8080/random?n=32&fmt=hex"

🐍 Python SDK (r4sdk)
=======
<div align="center">
📋 Table of Contents

What is R4?
 •
Quickstart
 •
Signed/PQ randomness
 •
SDK
 •
API Reference
 •
Use Cases
 •
Security / Proof
 •
Performance
 •
Roadmap
 •
VRF / Lottery / Solidity
 •
Competition
 •
Contact

</div>
🧠 Overview

r4 is a high-entropy appliance and verifiable randomness API.

It delivers:

🔒 Sealed entropy core (re4_dump)
closed-source, statistically verified via Dieharder / PractRand / BigCrush, shipped as a signed binary.

🌐 Hardened FastAPI layer (:8080)
key-protected /random endpoint for secure entropy distribution over HTTP (Docker or systemd).

🔐 PQ / VRF Oracle (:8081)
returns randomness that is cryptographically signed with ECDSA today, and Dilithium3 (FIPS 204 ML-DSA) in the PQ build.
You can prove to a smart contract / regulator / auditor that “this number actually came from R4, not from me cheating”.

💠 Solidity reference contracts
R4VRFVerifierCanonical.sol and LotteryR4.sol let you verify oracle signatures on-chain and run provably fair draws.

🐍 Python SDK (r4sdk on PyPI)
one-line client for backend, validators, casino infra, zk-rollups.

This repo also documents our post-quantum VRF roadmap (vrf-spec/), and ships stress tools, self-tests, audit artifacts, and a one-command demo.

We are not “random() lol”. We are “here’s the signed randomness, here’s the proof, here’s the contract that checks it, here are the statistical reports.”

🚀 One-command full demo (end-to-end fairness)

We ship a single script that boots everything locally and proves the whole flow, no magic.

./run_full_demo.sh


It will:

spin / refresh both nodes:

Core entropy node on :8080

PQ/VRF oracle node on :8081

call /version, /health, /random, /random_pq?sig=ecdsa

run local stress tests (stress_core.sh, stress_vrf.py)

extract a live signed randomness packet and convert it for Solidity (prep_vrf_for_chain.py)

run Hardhat tests in vrf-spec/ (verifier + on-chain lottery)

Expected / desired output:

✅ 8080 responding with raw entropy

✅ 8081 responding with signed randomness (v, r, s, signer_addr)

✅ stress: ~100 req/sec locally, 0 crashes

✅ rate limit on 8081 kicks in (429 seen)

✅ Hardhat: 5 passing

✅ lottery picks a winner using only randomness that verifies on-chain

This is snapshotted and tagged as v1.0.0-demo in git.

That tag is what you send to validators, casinos, auditors, investors.

🐳 Quickstart (Docker)

You can run the whole core entropy service with one Docker command.

Prereqs

🐳 Docker Desktop / Docker Engine

🔌 Port 8080 free

Run the container
docker run -d \
  --name r4-core \
  -p 8080:8080 \
  -e API_KEY=demo \
  pipavlo/r4-local-test:latest

Health check
curl -s http://127.0.0.1:8080/health
# → "ok"

Version / build info
curl -s http://127.0.0.1:8080/version | jq


Example:

{
  "name": "re4ctor-api",
  "version": "0.1.0",
  "api_git": "container-build",
  "core_git": "release-core",
  "limits": {
    "max_bytes_per_request": 1000000,
    "rate_limit": "10/sec per IP"
  }
}

Request cryptographic random bytes
curl -s -H "X-API-Key: demo" \
  "http://127.0.0.1:8080/random?n=32&fmt=hex"
# "a359b9dd843294e415ac0e41eb49ef90..."


What happens:

re4_dump (sealed core binary) is executed inside container

API enforces API_KEY

you get real entropy with rate limiting

NO external network calls, no “we fetched data from somewhere else”

🔐 Auth Model

The API requires a key for /random.

Two ways to pass it:

Header: X-API-Key: demo

Query: ?key=demo

The container you run uses:

-e API_KEY=demo


Change this in production.

Production-ish example
docker run -d \
  --name r4prod \
  -p 8080:8080 \
  -e API_KEY="my-super-secret" \
  pipavlo/r4-local-test:latest


Then:

curl -s -H "X-API-Key: my-super-secret" \
  "http://127.0.0.1:8080/random?n=64&fmt=hex"


401 example:

curl -i -s -H "X-API-Key: WRONG" \
  "http://127.0.0.1:8080/random?n=16&fmt=hex"
# → HTTP/1.1 401 Unauthorized
# → {"detail": "invalid api key"}

🔐 Post-quantum / signed randomness (port 8081)

Port 8081 runs the PQ / VRF oracle node.

This node:

talks to the same entropy core

signs the randomness it emits

gives you (v,r,s) (ECDSA) and the signer_addr

can also (enterprise build) return Dilithium3 signatures (FIPS 204 ML-DSA)

Ask it for signed randomness:

curl -s "http://localhost:8081/random_pq?sig=ecdsa" | jq


Typical response:

{
  "random": 2689836398,
  "timestamp": "2025-10-28T23:46:03Z",
  "signature_type": "ECDSA(secp256k1)",
  "msg_hash": "0xaf6036e6...",
  "v": 27,
  "r": "0x4fe30113...",
  "s": "0xce79a501...",
  "signer_addr": "0xC61b94A8e6aDf598c8a04737192F1591cC37Db1A",
  "pq_mode": false
}


Meaning:

random: the number you’ll use on-chain / in the game / for fair selection

(v,r,s): signature over that randomness+timestamp

signer_addr: Ethereum-style address recovered from the sig

contract can check signer_addr == trustedOracle

In the PQ path (sig=dilithium), you get Dilithium3 instead of ECDSA. That’s the post-quantum future / regulated build.

So:

8080 = raw entropy

8081 = auditable/signed/pq-ready randomness

🐍 Python SDK

PyPI package: r4sdk
>>>>>>> eaced2b (docs: full README rewrite (PQ VRF, stress harness, on-chain verifier, v1.0.0-demo, proofs))

Install:

pip install r4sdk


<<<<<<< HEAD
Use:

from r4sdk import R4Client
client = R4Client(api_key="demo", host="http://localhost:8080")
print(client.get_random(16).hex())


Signed randomness:

import requests, json
r = requests.get("http://localhost:8081/random_pq?sig=ecdsa",
                 headers={"X-API-Key":"demo"}).json()
print(json.dumps(r, indent=2))

🔐 API Reference
Node	Port	Signature	Endpoint examples
Core	8080	none	/health, /version, /random?n=32
PQ-VRF	8081	ECDSA / Dilithium	/random_pq?sig=ecdsa, /random_pq?sig=dilithium
📊 Security & Compliance
Test	Result
NIST SP 800-22	✅ 15 / 15 passed
Dieharder	✅ 31 / 31
PractRand	✅ 8 GB, no anomalies
TestU01 BigCrush	✅ 160 / 160

Proofs live under packages/core/proof/
.
Each release ships with sha256, gpg, and SBOM.spdx.json.

⚙️ Performance
Metric	Value
Throughput	~950 k req/s
Latency (p99)	~1 ms
Entropy bias	< 10⁻⁶
Max req	1 MB
📅 Roadmap 2025
Quarter	Milestone	Status
Q1	Dilithium 3 PQ signatures	✅ Done
Q2	Kyber KEM integration	✅ Done
Q3	Solidity audit / testnet	✅ Done
Q4	FIPS 140-3 / 204 lab submission	🚀 In progress
🧪 MVP Status
Feature	Status	Notes
Entropy core	✅	FIPS self-test
PQ node (8081)	✅	ECDSA + Dilithium
Hardhat tests	✅	5/5 passing
Stress tools	✅	stress_core.sh, stress_vrf.py
SDK on PyPI	✅	r4sdk v0.1.5
Docker image	✅	pipavlo/r4-local-test
📊 Quick Comparison
Feature	R4	Chainlink VRF	drand	API3 QRNG	AWS HSM
Post-Quantum Ready	✅ Dilithium + Kyber	❌	❌	❌	⚠️ Partial
Latency	< 1 ms	30–120 s	30 s	20 s	10–50 ms
Cost Model	Self-hosted	Pay per req	Free	dAPI	$$$
On-chain Verify	✅ Solidity	✅	⚠️ External	✅	❌
Auditability	✅ Open	✅	✅	⚠️	❌
FIPS 204 Path	🚀 In progress	❌	❌	❌	✅

Full comparison: docs/COMPETITORS.md

🧬 Architecture
┌──────────────┐
│ Core 8080    │
│ /random      │
└─────┬────────┘
      ↓
┌──────────────┐
│ PQ VRF 8081  │
│ /random_pq   │
└─────┬────────┘
      ↓
┌──────────────┐
│ Solidity VRF │
│ Verifier & LotteryR4 │
└──────────────┘

🧭 Repository Map
r4-monorepo/
├── packages/core/          # sealed entropy binary + proofs
├── api/                    # FastAPI 8080
├── pq-api/                 # PQ/VRF node 8081
├── sdk_py_r4/              # Python SDK (PyPI)
├── vrf-spec/               # Solidity + Hardhat tests
├── docs/                   # comparison, deployment, proof
├── stress_core.sh / stress_vrf.py
└── run_full_demo.sh

🏷️ Release Tag

v1.0.0-demo — complete end-to-end reproducible demo (core → PQ/VRF → Solidity).

📬 Contact & Support

Maintainer: Pavlo Tvardovskyi
📧 shtomko@gmail.com

🐙 github.com/pipavlo82

🐳 hub.docker.com/r/pipavlo/r4-local-test

📦 PyPI r4sdk

🧠 Mission Statement

R4 is the fastest, cheapest way to get verifiable randomness for blockchain, gaming, and validator rotation — self-hosted, FIPS-tested, post-quantum-ready.

© 2025 Re4ctoR Project • Built with ⚡ for provable entropy and verifiable fairness.
=======
Usage with core node (:8080):

from r4sdk import R4Client

client = R4Client(
    api_key="demo",
    host="http://localhost:8080",
)

rand_bytes = client.get_random(32)
print("🔐 Random bytes:", rand_bytes.hex())


You can also directly hit the PQ / VRF node from Python for signed randomness:

import requests, json

resp = requests.get(
    "http://localhost:8081/random_pq?sig=ecdsa",
    headers={"X-API-Key": "demo"}
)
data = resp.json()

print(json.dumps({
    "random": data["random"],
    "timestamp": data["timestamp"],
    "signer": data["signer_addr"],
    "signature": {
        "v": data["v"],
        "r": data["r"],
        "s": data["s"],
    }
}, indent=2))


Future SDK rev will have client.get_vrf() that wraps that.

📚 API Reference
GET /health (8080)

Liveness probe.

curl http://127.0.0.1:8080/health
# "ok"

GET /version (8080 and 8081)

Audit metadata:

build hashes

limits

integrity self-test signal

curl http://127.0.0.1:8080/version | jq

GET /random (8080)

Request raw entropy bytes.

Query params:

Param	Required	Example	Description
n	✅	32, 1024	number of bytes
fmt	❌	hex / none	output format (raw if none)

Auth:

Header: X-API-Key: demo

or ?key=demo

Example:

curl -s -H "X-API-Key: demo" \
  "http://127.0.0.1:8080/random?n=16&fmt=hex"

curl -s -H "X-API-Key: demo" \
  "http://127.0.0.1:8080/random?n=256" \
  --output entropy.bin
hexdump -C entropy.bin | head

GET /random_pq?sig=ecdsa (8081)

Signed randomness, ready for Solidity consumption.
Also supports sig=dilithium (PQ / ML-DSA) in enterprise build.

🧪 MVP Status — all core features landed
Feature	Status	Notes
C / Python SDKs	✅	libr4.a, Python r4sdk on PyPI
r4cat CLI	✅	command-line entropy streaming + deterministic seeding
HMAC-framed Unix socket transport	✅	IPC with per-frame HMAC, rejects tampered frames
Deterministic seeding / replay	✅	fixed seeds produce reproducible output for audit
Tamper tests	✅	local scripts simulate corruption / timing attacks
PQ/VRF oracle on :8081	✅	ECDSA live, Dilithium3 path wired
Solidity verifier + lottery	✅	R4VRFVerifierCanonical.sol, LotteryR4.sol, Hardhat tests passing
Stress harness & rate limit checks	✅	stress_core.sh, stress_vrf.py, ~100 req/sec local
Release snapshot v1.0.0-demo	✅	demo state is tagged and reproducible

This is not “idea stage”. It runs.

📊 Use Cases
1. Blockchain validator / PoS leader election
import requests

seed_hex = requests.get(
    "http://r4-node:8080/random?n=32&fmt=hex",
    headers={"X-API-Key": "validator-secret"}
).text

# use seed_hex to shuffle validator set / pick proposer

2. Gaming / sportsbook / casino fairness
resp = requests.get(
    "http://r4-node:8081/random_pq?sig=ecdsa",
    headers={"X-API-Key": "game-secret"}
).json()

rolled = resp["random"] % 100 + 1
print("Rolled:", rolled, "Proof signer:", resp["signer_addr"])
# you can show the proof if anyone screams "rigged"

3. NFT raffle / mint reveal

each mint gets a ticket index

you pull signed randomness

push (random, v, r, s) into contract

contract verifies origin and picks winner with modulo

4. ZK-rollup / L2 sequencer fairness

Use R4 to generate unbiased seed for sequencer rotation / committee assignment.

5. Keygen / secrets bootstrap
curl -H "X-API-Key: prod" \
  "http://r4-internal:8080/random?n=32&fmt=base64" \
  | base64 -d > aes256.key
# drop aes256.key into vault/bootstrap

🔒 Security & Compliance
Statistical validation ✅

Full reports live in packages/core/proof/:

Dieharder (dieharder/summary-2025-01.txt)

PractRand (practrand/summary-2025-01.txt)

TestU01 BigCrush (bigcrush/summary-2025-01.*)

plus README.md and rollup summaries

Snapshot of results:

NIST SP 800-22 — 15/15 pass (p ~0.5 uniformity)

Dieharder — 31/31 pass

PractRand — multi-GB stream, no anomalies

TestU01 BigCrush — 160/160 tests pass, no catastrophic p-values

tl;dr: statistically indistinguishable from ideal entropy.

Boot integrity & self-test

Every container startup:

Integrity check — sealed binary hash is compared to signed manifest

Known Answer Test (KAT) — deterministic seed run sanity check

Attestation — /version exposes runtime git hashes, limits

Strict mode (fail closed, not “best effort”):

docker run -d \
  -p 8080:8080 \
  -e API_KEY=demo \
  -e STRICT_FIPS=1 \
  pipavlo/r4-local-test:latest
# if self-test fails → HTTP 503 instead of garbage RNG

Supply chain / audit trail

Each release bundle ships:

re4_release.tar.gz — sealed entropy core

re4_release.sha256 — hash manifest

re4_release.tar.gz.asc — GPG signature

SBOM.spdx.json — software bill of materials

This is what you hand an auditor / regulator / security lead to prove:

what binary is running

that it wasn’t silently modified

how the binary behaves statistically

NOTE: The entropy core itself (the heart, re4_dump) is intentionally not fully open-source. This is the HSM model:

you can measure its entropy quality

you can verify its supply chain hash/signature

but you can’t just clone / mutate it and still claim “we are R4”

⚙️ Performance
Metric	Value
Throughput	~950,000 req/s (local IPC)
Latency (p99)	~1.1 ms
Max request size	1 MB
Entropy bias	< 10⁻⁶ deviation
Stress test observed	~100 req/sec over HTTP on dev laptop
Rate limiting (8081)	returns 429 under load

Benchmarks summary lives in docs/proof/benchmarks_summary.md.

🔭 Roadmap Progress — 2025

We’re late 2025, so here’s the honest state:

Milestone / Deliverable	Status
Dilithium3 / ML-DSA (FIPS 204 PQ signatures) in the oracle path	✅ integrated (enterprise build)
Kyber KEM handshake channel for VRF key exchange	✅ integrated
Solidity verifier (R4VRFVerifierCanonical.sol)	✅ shipped
Provably fair on-chain lottery (LotteryR4.sol)	✅ shipped
Hardhat tests proving fairness end-to-end (5 passing)	✅ stable
Stress tools (stress_core.sh, stress_vrf.py)	✅ in repo
Export-to-chain helper (prep_vrf_for_chain.py)	✅ in repo
Attestation + SBOM + selftest in /version	✅ wired
FIPS 140-3 / 204 certification track (lab handoff / audit package)	✅ entering certification flow

TL;DR:

PQ path (Dilithium3 / Kyber) already wired

Verifier and Lottery contracts already exist and pass tests

full audit bundle (SBOM + statistical proof) exists

v1.0.0-demo is a reproducible snapshot

🧬 Provably fair lottery & on-chain VRF

We include a working reference design in vrf-spec/:

Contracts:

R4VRFVerifierCanonical.sol

LotteryR4.sol

Tests:

vrf-spec/test/lottery.js

vrf-spec/test/verify.js

vrf-spec/test/verify_r4_canonical.js

Flow:

Players enter lottery via enterLottery()

R4 oracle (:8081) produces randomness + signature (v, r, s)

The contract calls the verifier to confirm signature came from the trusted signer address

Winner is computed as uint256(random) % players.length

Emits WinnerSelected(winner, index, randomness)

Attack attempt (“I’ll just give fake random”):

contract will revert because signature won't match signer_addr

tests assert that

This design is ready for:

casinos / sportsbooks

NFT mint reveals / whitelist raffles

esports brackets + prize splits

validator / committee selection

zk-rollup sequencer rotation

🥊 R4 vs the rest
High-level “why we exist” table
Feature	R4	Chainlink VRF	drand	API3 QRNG	AWS HSM / CloudHSM
Post-Quantum Ready	✅ Dilithium3 + Kyber roadmap	❌ ECDSA	❌ BLS only	❌ centralized	❌ classical curves
Latency	<1 ms (local)	~30s–120s	~30s beacon interval	~15–20s	~50–200 ms
Cost Model	self-hosted / flat infra	per-request fees	free public beacon	per-request	$$$ subscription
On-chain Verification	✅ Solidity verifier shipped	✅ VRF proof	⚠ ext trust anchor	✅ merkle proof	❌ off-chain only
Self-Hosted	✅ yes	❌ no	✅ you can run node	⚠ depends	✅ (vendor lock)
Throughput	~950k req/s core, ~100 req/s HTTP	limited by gas	limited by period	oracle limited	~50k req/s typical
Regulator / audit story	✅ SBOM + stats + signed output	✅ big brand	⚠ research infra	⚠ newer brand	✅ enterprise certs
FIPS 204 (PQ signatures)	in flight / integrated path	❌	❌	❌	❌ (PQ not default)

Plain English:

Chainlink is decentralized, slow, and costs per request.

drand is free and public, but ~30s latency and not private.

AWS HSM is “call a cloud HSM, get bytes”, no on-chain proof.

R4 is: run it yourself, get sub-ms entropy, get a signed proof your contract can verify, and we’re already wiring in post-quantum.

You can show this table to infra people and casino compliance and they’ll get it.

🗺️ Repo layout
r4-monorepo/
├── api/                         # FastAPI / PQ oracle (:8081)
├── packages/
│   └── core/
│        ├── runtime/bin/re4_dump        # sealed entropy core executable
│        └── proof/                      # Dieharder / PractRand / BigCrush summaries
├── sdk_py_r4/                  # Python SDK (published as r4sdk on PyPI)
├── vrf-spec/
│   ├── contracts/
│   │   ├── R4VRFVerifierCanonical.sol   # solidity signature verifier
│   │   └── LotteryR4.sol                # provably-fair lottery example
│   └── test/                            # hardhat tests (5 passing)
├── stress_core.sh              # hammer :8080, measure throughput
├── stress_vrf.py               # hammer :8081, measure rate limit & stability
├── prep_vrf_for_chain.py       # pull live signature + format it for solidity replay
├── run_full_demo.sh            # full end-to-end demo script
├── README_RUNTIME.md           # ops runbook / healthcheck / prod notes
└── packages/core/proof/        # statistical validation artifacts (dieharder, practrand, bigcrush)


License model:
runtime wrapper code is open
entropy core (re4_dump) is sealed (HSM-style)
proof & SBOM let auditors trust-but-verify

📦 Status

This repo is public. The core entropy binary is not.

Public Docker image:

docker pull pipavlo/r4-local-test:latest


This is enough to:

integrate into backend / backend games

generate keys/secrets at high rate

prove fairness in raffles / lotteries / leader elections

show an auditor “here’s the signed random, here’s how the smart contract checks it, here’s the SBOM and statistical proof”

v1.0.0-demo is the “freeze point”.

📬 Contact & Support

Maintainer: Pavlo Tvardovskyi
📧 Email: shtomko@gmail.com

🐙 GitHub: @pipavlo82

🐳 Docker Hub: pipavlo/r4-local-test
📦 PyPI: r4sdk (https://pypi.org/project/r4sdk/
)

Enterprise / regulated gaming / validator networks

For:

on-prem deployments

validator beacon / PoS rotation

casino provably-fair RNG

PQ-signed VRF streams

audit packs (SBOM, test logs, PractRand/Dieharder summaries)

→ ping shtomko@gmail.com

<div align="center">

© 2025 Re4ctoR Project • “don’t trust the house, verify the entropy” ☢

⬆ Back to top

</div> ::contentReference[oaicite:0]{index=0}
>>>>>>> eaced2b (docs: full README rewrite (PQ VRF, stress harness, on-chain verifier, v1.0.0-demo, proofs))
