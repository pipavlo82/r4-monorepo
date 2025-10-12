# R4-CS Cryptographic Specification (Public)

This document describes the public cryptographic construction used by the Re4ctor stream generator, without exposing internal source-code details.

## Key Schedule
- **KDF:** HKDF-SHA256
- **Inputs:** `salt` (optional), `ikm` (seed material), `info = "r4cs/hkdf/v1"`
- **Output:** 32-byte `key` || 12-byte `nonce`

## DRBG
- **Cipher:** ChaCha20 (IETF)
- **IV (nonce16):** `LE32(counter) || nonce(12B)`
- **Counter update:** `counter += ceil(requested_bytes / 64)`

## Reseed Policy (Public)
- On-demand or after a bounded number of blocks (implementation-defined).
- Optional external entropy mixing via HKDF salt.

## Security Goal
- Treat output as a stream-cipher keystream under a secret key.
- IND-CPA security in the ChaCha20 model; forward-security via reseed policy.

## Delivery Integrity
- IPC frames are authenticated with HMAC-SHA256 (see IPC notes).
- Client MUST drop any response failing MAC verification.

This spec provides transparency required for external review without exposing proprietary internals.
