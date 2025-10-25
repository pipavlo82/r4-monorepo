# re4ctor-core: Design Overview

## Architecture Summary

The `re4ctor-core` generator is designed as a **two-layer deterministic entropy system**:

```
+-------------------------+
|  FastAPI (re4ctor-api)  |  →  /random  (HTTP service)
+-----------+-------------+
            |
            v
+-------------------------+
|  re4ctor-core binary    |  →  /dev/random-like entropy stream
|  (opaque DRBG engine)   |
+-----------+-------------+
            |
            v
+-------------------------+
|  Entropy sources mixer  |  →  system entropy + timing jitter + chaos
+-----------+-------------+
            |
            v
+-------------------------+
|  Health tests (90B-lite)|
|  - startup self-test    |
|  - continuous health    |
+-------------------------+
```

## DRBG / Reseed Flow

```
 [Entropy Mixer] 
      ↓
 [Seed Material] 
      ↓
 [DRBG State Init]
      ↓
 [Output bytes]
      ↓
 (Every N blocks or on demand)
      ↓
 [Reseed ← new entropy + HMAC(key, state)]
```

- Uses **ChaCha-based stream DRBG** with periodic reseed.
- Health tests monitor entropy rate and detect bias.
- Reseed interval is adaptive (based on output correlation metrics).

## Design Goals

| Property | Status | Description |
|-----------|---------|-------------|
| Backtracking resistance | ✅ | Compromise of state doesn’t reveal past outputs. |
| Forward secrecy after reseed | ✅ | Each reseed breaks link to prior outputs. |
| Continuous health tests | ⚙ partial | Lightweight 90B-like bias checks. |
| Deterministic reproducibility | ✅ optional dev mode |
| FIPS 140-3 certified | ❌ planned |
| Statistical transparency | ✅ NIST STS / Dieharder / PractRand / BigCrush passed |

---

## Threat Model

- Internal DRBG and entropy logic are **not public** (opaque core).
- Output is externally verifiable through statistical testing.
- Reproducible signed builds + SBOM guarantee integrity.
- Attack surface limited to HTTP API (`/random`) with rate limit and API key.

In short:  
**we prove the tap water is clean, without revealing the plumbing diagram.**
