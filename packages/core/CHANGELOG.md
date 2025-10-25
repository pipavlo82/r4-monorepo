# re4ctor-core Changelog

| Version | Date | Highlights |
|----------|------|-------------|
| v0.2.0 | 2025-10-24 | BigCrush / PractRand / Dieharder full pass; added SBOM + GPG-signed release bundle |
| v0.1.3 | 2025-09-30 | Introduced FastAPI `/random` endpoint + systemd service unit |
| v0.1.0 | 2025-08-20 | Initial open-core drop (opaque DRBG, minimal RNG binary) |

## Upcoming (v0.3.0)
- Add audit logging for `/random` requests.
- Add DRBG reseed diagram to docs.
- Integrate FIPS-like startup self-test module.
- Add sandbox hardening in systemd service.
