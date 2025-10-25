# FIPS Readiness Statement

**r4** is being developed as a *FIPS-aligned entropy appliance* and verifiable randomness API.  
While the module is **not yet FIPS 140-3 validated**, its architecture and release process are designed
to be compatible with the CMVP validation path.

---

## 1. Module Boundary

The FIPS-style cryptographic module consists of the sealed binary  
`core/bin/re4_dump` and its deterministic runtime environment.

- The FastAPI layer (`api/`) is *not part of the module* — it acts as an HTTP wrapper.
- The Docker runtime (`packages/core/docker/`) is *deployment glue* and *not* security-relevant.
- Randomness leaves the module **only as opaque bytes** after internal health tests.

---

## 2. Health Tests and Self-Checks

At startup, the module performs internal **power-up self-tests**:

- Integrity verification (`sha256` self-check vs. embedded manifest)
- Entropy source availability check

During operation, continuous health monitoring is applied:

- **Continuous RNG test** (FIPS style “no-repeat” check)  
  Detects identical consecutive blocks and halts output if detected.

On any failure, the module enters **FAIL-CLOSED** mode:

```json
{ "detail": "entropy source offline" }
API stops serving /random until manual restart with fresh seed material.

3. Entropy Characterization
The entropy source has been characterized using standard statistical methods:

Dieharder

PractRand

TestU01 BigCrush

SP 800-90B style min-entropy estimation

Large-scale raw test logs (multi-GB) are stored offline and provided under NDA.

Summary results are published in core/proof/README.md.

4. Supply-Chain Attestation
Each release bundle under core/release/ includes:

Artifact	Purpose
SBOM.spdx.json	Software Bill of Materials
re4_release.sha256	Integrity manifest
re4_release.tar.gz.asc	Detached GPG signature of the binary bundle

These artifacts provide verifiable provenance and integrity for each release.

5. Operational Transparency
The API exposes version metadata:

bash
Copy code
GET /version
returns:

json
{
  "core_git": "<commit or tag>",
  "api_git": "<commit>",
  "limits": { "max_bytes": 4096, "rate_per_min": 60 },
  "sbom_present": true,
  "sig_present": true
}
This aligns with FIPS 140-3 operational environment identification requirements.

6. Future Roadmap
✅ Maintain SBOM and signed release bundles

✅ Continuous RNG health test

🧭 Formalize entropy boundary document (NIST 800-90B reference)

🧭 Add startup self-test report export

🧭 Submit for FIPS 140-3 readiness assessment (CMVP partner TBD)

🧭 /vrf endpoint: PQ-signed, auditable randomness output (Dilithium class)

Contact
For audit collaboration, FIPS pre-assessment, or enterprise deployment:

📧 shtomko@gmail.com

Last updated: October 2025


