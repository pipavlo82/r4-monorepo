1. core/ — entropy engine + API

core/ comes from re4ctor-core and contains:

CMake/Ninja build (cmake -S . -B build ...)

re4_dump: infinite byte stream of high-entropy output

re4_tests: DRBG / health self-tests

proof/: summaries from Dieharder, PractRand, TestU01 BigCrush

signed release bundle (re4_release.tar.gz + .sha256 + .asc)

SBOM (SPDX 2.3) via syft

hardened FastAPI/uvicorn service exposing /random

systemd unit for running it as a non-root, sandboxed service

operator docs (usage, rate limiting, audit logs)

API surface (core/api layer)

GET /health → "ok"

GET /version → build info, git rev, limits

GET /info → usage help

GET /random → random bytes (requires API key)

Dev/default auth:
header x-api-key: local-demo
or query ?key=local-demo

Production: set API_KEY in .env, restart service.

Limits:

10 requests/sec per client IP

max 1,000,000 bytes per request

every /random call is logged with IP, n, fmt, first bytes fingerprint

Systemd unit (see core/docs/re4ctor-api.service.example) runs uvicorn under a dedicated user, with sandbox policies (ProtectSystem, ProtectHome, MemoryDenyWriteExecute).
This is positioned as "entropy appliance on port 8080".

Supply-chain trust:

We publish a release tarball with binaries + SBOM.

We publish sha256 and detached GPG signature.

You can reproduce/verify the exact bits you run.

2. vrf/ — PQ verifiable randomness

vrf/ is the evolution path: turning raw entropy into verifiable randomness.

Goal:
Instead of "give me 64 random bytes", a caller can ask for "give me 64 random bytes + a proof that they weren't biased or tampered with".

This is the PQ-VRF direction (Post-Quantum Verifiable Random Function):

Planned /vrf response:

random: N bytes of entropy

signature: post-quantum signature (Dilithium / Kyber class)

public_key: node's PQ public key

verified: true/false (local check)

Why this matters:

blockchain validator selection / committee rotation

zk-rollup / prover seeding

on-chain lotteries / airdrops / mint fairness

anti-manipulation in proof-of-stake randomness (operator can't "reroll" secretly)

This is not "another /dev/urandom".
This is "provable entropy you can verify in a smart contract or consensus layer, even in a post-quantum world".

The vrf/ directory contains:

early PQ-VRF design notes

bindings / components / specs

investor-facing and product-facing briefs

roadmap for making /vrf a first-class API next to /random

Long-term intent:

/random stays as the fast firehose endpoint for local systems.

/vrf becomes a slower, attestable endpoint for staking, audit, and consensus.

3. Statistical assurance

We test the shipped re4_dump binary (not some dev build) against:

Dieharder

PractRand

TestU01 BigCrush

We commit human-readable summaries under core/proof/:

PASS / WEAK / FAIL lines

interpretation

audit notes

We do not commit multi-GB raw logs to git.
They are archived offline and can be shared under NDA.

Position:

No persistent FAILs across the suites.

Occasional WEAK in Dieharder is expected (even /dev/urandom shows that).

Output is treated like hardware RNG tap: measurable, logged, externally auditable.

4. Deployment posture

The "core" API layer is meant to run as:

a local service on 127.0.0.1:8080 during development (x-api-key: local-demo)

or a systemd-managed service bound to LAN, with:

non-root user

rate limiting

request logging

key-based auth

This makes it behave like an internal "entropy appliance box" you can drop into infra and consume via HTTP.

We also ship:

SBOM (SPDX 2.3)

deterministic release bundle

sha256 + detached GPG signature

Anyone downstream can verify they’re running unmodified bits.

5. Roadmap

Harden /random as a production entropy endpoint.

Expose /vrf: random bytes + PQ signature + public key → externally verifiable, on-chain consumable.

Attach PQ identity (Dilithium/Kyber-class keys) to the node and rotate keys sanely.

Treat the service as a randomness oracle / beacon for rollups, staking, leader election, zk proving.

TL;DR:
This repo is the convergence of:

entropy generation (core/)

delivery and ops (systemd, SBOM, signed bundles)

verifiable randomness + post-quantum story (vrf/)

Entropy for a quantum world.
