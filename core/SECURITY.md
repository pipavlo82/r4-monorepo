# Security Policy

## Threat Model

The `re4ctor-core` generator functions as an opaque DRBG engine, similar to Apple Secure Enclave or Intel SGX.

### Transparency without exposure
- Internal entropy and DRBG code are not public.
- External validation via `dieharder`, `PractRand`, `NIST STS`, `BigCrush`.
- Reproducible SBOM (SPDX 2.3) and GPG-signed release bundles.
- API protected by static key, rate limiting, and journald audit logging.

### Design assumptions
- Host system integrity is maintained (no kernel compromise).
- Network connections to `/random` are authenticated and rate-limited.
- Attackers cannot modify binaries without failing signature or hash verification.

### Recommendations for operators
- Rotate `API_KEY` monthly.
- Restrict `.env` to mode `600` and trusted users.
- Enable `journalctl` logging and review `/random` access patterns.
- Deploy under systemd sandbox (`ProtectSystem=strict`, `NoNewPrivileges=yes`).

### Reporting a vulnerability
Report privately to  
📧 **security@re4ctor.dev**  
🔑 GPG: `ED5B0368114DA3AE355E4C6166056461E00D386B`
