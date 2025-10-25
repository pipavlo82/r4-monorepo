# r4-monorepo

Secure randomness core + verifiable randomness roadmap.

This repo contains two tracks:

1. `packages/core/`  
   A hardened entropy appliance:
   - C generator binary (`re4_dump`) that emits high-entropy bytes
   - API service (`re4ctor-api`) that exposes `/random` over HTTP with rate limiting and API keys
   - signed release bundle + SBOM
   - statistical proof (Dieharder / PractRand / TestU01 BigCrush)
   - systemd unit for running it as a service

   This is what you can run **today**.

2. `packages/vrf-spec/`  
   The next step: post-quantum verifiable randomness (PQ-VRF).
   - design notes, roadmap, investor brief
   - goal: `/vrf` → `random_bytes + post-quantum signature + public key`
   - usable for validator selection, lotteries, rollups, staking fairness

   This is what we're building **next**.

We ship real entropy now. We ship publicly verifiable entropy next.


---

## 1. What problem we solve

Typical RNG story:
- "trust me, it's random"

Our story:
- you get a **sealed binary** that produces randomness
- you get **statistical proof** that output passes industry-grade batteries (Dieharder / PractRand / BigCrush)
- you get a **signed release bundle** + **SBOM** so you know exactly what binary you're running
- you get an **HTTP API** (`/random`) you can drop into infra like any other internal service

For blockchain / validator / zk / staking use cases, you also get a public roadmap to turn that into a **verifiable RNG beacon** with PQ signatures.

This is not "here's some C code lol".
This is "here's an entropy appliance."


---

## 2. Directory layout

```text
packages/
  core/        -> production entropy core + API + proof
  vrf-spec/    -> PQ VRF design, roadmap, investor-facing material
packages/core/
Contents:

src/
The C core around DRBG, entropy collection, health logic, SP800-90B style min-entropy estimation, etc.

Note: some low-level internals are intentionally private. The public repo ships the compiled binary, not the full DRBG / entropy heuristics. Think "Secure Enclave model": you can call it, test it, verify it — but you don't get the guts.

re4_dump
The binary that streams random bytes forever to stdout.

Example quick check:

bash
Copy code
./re4_dump | head -c 32 | hexdump -C
You should never see:

all zeroes

the same 32 bytes twice

docs/USAGE.md
Operator runbook. How to deploy this thing as a local service or as a systemd unit.

docs/re4ctor-api.service.example
Hardened systemd unit with:

non-root user

rate limiting

API key in an .env

memory protections & file system lockdown

The idea is: "entropy box on port 8080".

proof/
Human-readable summaries of statistical test runs:

Dieharder

PractRand

TestU01 BigCrush

We commit summaries, not multi-GB raw logs. Raw data is archived offline.

Position today:

no persistent FAILs

occasional WEAK in Dieharder is normal (even /dev/urandom does that)

PractRand / BigCrush clean for long streams

release/
Software Bill of Materials (SPDX 2.3). We include only the artifacts we ship.

re4_release.tar.gz, .sha256, .asc
Signed release bundle:

tarball of shipped binaries + helpers

SHA-256 checksum

detached GPG signature

So downstream can do supply-chain verification:

bash
Copy code
sha256sum -c re4_release.sha256
gpg --verify re4_release.tar.gz.asc re4_release.tar.gz
If both pass, you are running exactly what we built.

examples_vrf/
Small demo clients / scripts.
CI builds a tiny smoke client (r4cat_light) that just asks the core for bytes and prints them as hex.
This proves the pipeline is alive and the RNG actually emits nontrivial output.

packages/vrf-spec/
This is the "future /vrf API".

The point:

/random gives you bytes, but you have to trust the box.

/vrf gives you bytes plus a proof you can verify anywhere.

The PQ-VRF model (high level):

json
Copy code
{
  "random": "<N bytes>",
  "signature": "<post-quantum signature over (random || context)>",
  "public_key": "<PQ public key of this node>",
  "verified": true
}
Why it matters:

validator / leader election in PoS

on-chain lotteries and airdrops without "the operator secretly rerolled 1000 times"

seeding zk prover challenges

fairness in rollups and committees

We explicitly target post-quantum safe primitives (Dilithium / Kyber class) so this still works in 2030+ threat models.

3. Deploying the core as an entropy appliance
The core package includes a FastAPI service (re4ctor-api) that exposes:

GET /health → "ok"

GET /version → build info, git rev, service limits

GET /random → N random bytes (API key required)

Auth model:

during local dev:

text
Copy code
x-api-key: local-demo
in production: set API_KEY=your-secret in .env, restart the service

Basic usage:

bash
Copy code
curl -s -H "x-api-key: local-demo" \
  "http://127.0.0.1:8080/random?n=32&fmt=hex"
Limits:

10 req/sec per client IP

max 1,000,000 bytes per request

every /random call is logged with IP + first 4 bytes fingerprint for audit

We ship a systemd unit file that:

runs under a dedicated non-root user

applies sandboxing (ProtectSystem, ProtectHome, MemoryDenyWriteExecute)

restarts on failure

loads config from /home/<user>/re4ctor-api/.env

This is meant to be installed like infrastructure.
It's not just "here's a C file", it's "here's a service you can actually run in prod".

4. Compliance / trust / auditability
We do not publish our full entropy core internals in the open repo.

Why?

It's IP.

It's attack surface reduction.

It's closer to how HSMs / Secure Enclave / TPMs work: you don't ship the exact whitening/conditioning guts, but you do prove that the surface behaves.

Instead we give you:

deterministic release bundle re4_release.tar.gz

SBOM (SPDX 2.3) for that exact bundle

SHA-256

GPG detached signature

statistical proof on the actual shipped binary stream

So you can:

Verify you're running the right bits.

Run your own dieharder / PractRand / TestU01 loops against /random or re4_dump.

Monitor in production for drift.

5. Roadmap
Short term:

polish /random as a safe internal entropy source

lock down systemd deployment profile for real ops

keep shipping SBOM + signatures

Medium term:

expose /vrf

attach a post-quantum signing key to each node

return (random_bytes, PQ_signature, public_key)

allow external verification that "this randomness could not be silently biased"

Long term:

become a randomness beacon / oracle for PoS validator rotation, L2 rollup fairness, zk proving challenges, etc.

usable in court / audit / compliance, not just in a hackathon demo

6. TL;DR
Today: packages/core = high-entropy RNG core + HTTP API /random, rate limited, key-gated, signed release bundle, SBOM, statistical proof (Dieharder / PractRand / BigCrush). Drop-in entropy appliance.

Tomorrow: packages/vrf-spec = PQ-verifiable randomness function (/vrf) with signatures you can independently verify on-chain or in consensus.

Entropy for a post-quantum world.
