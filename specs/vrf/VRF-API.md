# VRF API (Draft, Public)

Goal: Provide verifiable randomness via a Verifiable Random Function (VRF), without disclosing private keys or internal implementation.

## API (Language-agnostic)
- `vrf_prove(sk, alpha) -> pi`
- `vrf_verify(pk, alpha, pi) -> (beta, ok)`

Where:
- `alpha`: input seed/message (bytes)
- `pi`: proof (bytes)
- `beta`: VRF output (bytes32 or similar), used as randomness
- `ok`: boolean validity flag

## Curves & Suites (TBD)
- Ed25519 (RFC8032-style encoding) **or**
- BLS12-381 (pairing-friendly, for on-chain aggregation)

## Determinism
- Proving is deterministic for the same `(sk, alpha)`.

## Security Targets
- VRF-PRF (pseudorandomness, uniqueness, soundness)
- On-chain verification feasibility (gas constraints considered)
