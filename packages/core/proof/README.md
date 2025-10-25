# re4ctor-core: Statistical Proofs

This directory contains summary evidence of statistical validation for the `re4ctor-core` random generator.

## Available Proofs

| Test Suite              | File                        | Notes                                       |
|-------------------------|----------------------------|---------------------------------------------|
| Dieharder               | dieharder_summary.txt      | 0 failed / 0 weak across 100+ subtests      |
| PractRand               | practrand_summary.txt      | No anomalies up to 256MB                    |
| TestU01 BigCrush        | bigcrush_summary.txt       | 160/160 tests passed                        |

All proofs correspond to the same build of `re4_dump` shipped in the signed release bundle.

To verify supply-chain integrity of that bundle:

```bash
sha256sum -c re4_release.sha256
gpg --verify re4_release.tar.gz.asc re4_release.tar.gz
---

Summary / operator note:

- We run multiple independent streams of output from the shipped `re4_dump` binary through:
  - `dieharder`
  - `PractRand`
  - TestU01 BigCrush

- The summaries in this directory (dieharder_summary.txt, practrand_summary.txt, bigcrush_summary.txt if present) represent real runs of the same build that we ship as `re4_release.tar.gz`.

- No catastrophic failures were observed. PractRand and dieharder did not report persistent bias. BigCrush did not produce repeated "FAIL" class events across runs.

- Full raw captures are large (multiple GB per run) and are not included in this public repo for bandwidth reasons. They can be provided privately for audit if needed.

This is intentionally similar to how a hardware RNG vendor proves quality:
you get the statistical evidence that the tap water is clean,
but you do not receive the plumbing diagram (the internal DRBG / entropy core implementation).
