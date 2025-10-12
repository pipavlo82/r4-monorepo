# R4-CS Cryptographic Specification (Public)

## Key Schedule
- **KDF:** HKDF-SHA256
- **Inputs:** `salt` (optional), `ikm` (seed), `info = "r4cs/hkdf/v1"`
- **Output:** 32-byte `key` || 12-byte `nonce`

## DRBG
- **Cipher:** ChaCha20 (IETF)
- **IV (nonce16):** `LE32(counter) || nonce(12B)`
- **Counter update:** `counter += ceil(request_bytes / 64)`

## Reseed (Public)
- On demand or after a bounded number of blocks (implementation-defined).
- Optional external entropy via HKDF salt mix-in.

## IPC Integrity
- Server frames are authenticated with **HMAC-SHA256**.
- Client **must** drop frames with invalid MAC or malformed structure.

This public spec enables external review without exposing proprietary internals.
