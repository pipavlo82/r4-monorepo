# VRF API (Draft, Public)

## Interface
- `vrf_prove(sk, alpha) -> pi`
- `vrf_verify(pk, alpha, pi) -> (beta, ok)`

Where:
- `alpha`: input (bytes)
- `pi`: VRF proof (bytes)
- `beta`: VRF output (bytes32)
- `ok`: boolean

Suites to consider: Ed25519 or BLS12-381 (deterministic proving; targets VRF-PRF, uniqueness, soundness).
