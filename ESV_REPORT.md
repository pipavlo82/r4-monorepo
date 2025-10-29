# Entropy Source Validation (ESV) Package — RE4CTOR

**Collection date (UTC):** $(date -u +"%Y-%m-%dT%H:%M:%SZ")

## 1. Overview
Short description of the entropy source, hardware and software versions, and collection conditions.

## 2. Artifacts included
- `esv_artifacts/samples/` — raw sample files (.bin)
- `esv_artifacts/rng_reports/` — test outputs (PractRand, dieharder, NIST STS)
- `esv_artifacts/notes.txt` — collection notes
- `ESV_REPORT.md` — this document

## 3. Collection methodology
Describe the generator binary/script used, parameters, environment (temperature, power, date/time), and commands executed.

## 4. Test results
Summarize outcomes from PractRand, dieharder, and NIST STS. Attach raw logs in `esv_artifacts/rng_reports/`.

## 5. Min-entropy estimation
Provide NIST SP800-90B estimator results, method, and numerical estimates.

## 6. Health tests
List runtime health tests implemented (e.g., repetition count, adaptive proportion), thresholds, and recorded triggers.

## 7. Risk assessment
Threat analysis, possible failure modes, and mitigations.

## 8. Reproducibility
Commands to reproduce:
```bash
./collect_samples.sh
./reproduce_and_test.sh
