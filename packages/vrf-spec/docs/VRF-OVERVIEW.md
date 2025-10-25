# VRF Overview (Mock Demo)

Goal: verifiable randomness consumable by smart contracts.
This MVP is a mock VRF (plumbing only), not a real cryptographic VRF.

Flow (MVP)
1) Off-chain service obtains 32B randomness from r4cat.
2) Service produces a placeholder "proof" (e.g., SHA-256(randomness || timestamp)).
3) On-chain MockVerifier checks sizes and emits an event.

Security
- MockVerifier is not a real VRF verifier; replace with a proper scheme before production.
