# FIPS 140-2 Readiness

Module boundary:
- `core/bin/re4_dump` (sealed entropy core)

Startup self-test:
- On container start, we run `packages/core/selftest/fips_selftest.py`
- It verifies SHA-256 of the sealed binary against `manifest.json`
- If mismatch → FAIL and no `/random` served
- If match → "FIPS-SELFTEST: PASS"

Integrity artifacts:
- `re4_release.sha256`
- `re4_release.tar.gz.asc` (GPG detached signature)
- `SBOM.spdx.json`

Goal:
- Behave like a software HSM: attestable output, verifiable build integrity,
  controlled surface area, fail-closed under fault.
