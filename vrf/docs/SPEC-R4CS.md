# R4-CS Cryptographic Spec (Public Overview)

Status: public summary (core remains proprietary).
Goal: let external reviewers reason about construction; implementation stays closed.

Construction
- KDF: HKDF-SHA256 (RFC 5869)
- DRBG: ChaCha20 used as DRBG
- IV: 16 bytes = LE32(counter) || 12-byte nonce
- Reseed: HKDF with fresh system entropy + optional external entropy
- Domain tag: "r4cs/hkdf/v1"

Safety Notes
- Never reuse the triple (key, nonce, counter).
- Deterministic seeds allow auditability (commit -> reveal).
- IPC layer must authenticate frames (see Re4ctor IPC summary).
