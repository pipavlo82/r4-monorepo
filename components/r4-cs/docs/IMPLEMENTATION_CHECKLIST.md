# R4-CS Integration Checklist

- [ ] Build lib & CLI from source; pin compiler/openssl versions.
- [ ] Initialize `r4cs` with high-quality seed; define reseed interval/policy.
- [ ] (Optional) Wire external entropy (`re4_stream`) and handle timeouts/fallbacks.
- [ ] Zeroize sensitive buffers; ensure crash-safe state handling.
- [ ] Add healthcheck/self-test at startup (sanity bytes, not a security test).
- [ ] Log version, build flags, entropy sources (without secrets).
- [ ] Run reproducible test suite on target hardware; store logs.
- [ ] Threat model review; confirm usage boundaries (not a CSPRNG unless audited).
- [ ] Prepare rollback plan and kill-switch.
