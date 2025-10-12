# Re4ctor RNG — Product Brief

## What it is
A high-integrity random number platform: private optimized core, HMAC-protected IPC, and lightweight SDKs for C/Python.

## Value
- **Trust**: auditability (commit-reveal, deterministic seeds), tamper-proof transport (HMAC).
- **Performance**: ChaCha20-based DRBG, streaming IPC, parallel consumption.
- **Ops**: per-tenant keys, quotas, rate caps, logs for compliance.

## Target Users
- Gaming/lottery backends, web3 oracles, fintech pricing engines, scientific simulations that need reproducibility.

## Key Features (MVP)
- C/Python SDKs, `r4cat` CLI.
- HMAC-framed Unix socket transport.
- Deterministic seeding (for audits & reproducible sims).
- Tamper tests (`tests/tamper.sh`).

## Road to “Provably Fair”
- Public spec + test reports.
- VRF module (client-verifiable proofs).
- Signed transcripts & attestations.

## Pricing (draft)
- Starter (SaaS): monthly cap (GB), basic SLA.
- Pro/Enterprise: dedicated deployment, per-tenant keys, custom SLAs, HSM.
