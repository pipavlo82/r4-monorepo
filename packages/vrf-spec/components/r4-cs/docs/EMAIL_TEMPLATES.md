## Security/Infra Engineer (cold intro)
Subject: Minimal HKDF→ChaCha20 DRBG (MVP) + full TestU01 BigCrush pass

Hi <Name>,
We’re sharing an MVP DRBG built from HKDF-SHA256 and ChaCha20, with optional external entropy. It passes PractRand, Dieharder, NIST STS, and TestU01 (Crush & BigCrush) in our runs. Code, logs, and a tiny CLI are here: <repo URL>. It’s not audited; we’re seeking feedback and potential pilot integrations. Interested in a short review?

## Auditor/Researcher
Subject: Review request — HKDF+ChaCha20 DRBG (MVP), full statistical logs provided

Hi <Name>,
We’re requesting a security review of a minimal DRBG (HKDF-SHA256 → ChaCha20). The repo includes reproducibility scripts and full logs (incl. BigCrush). Scope suggestions attached; happy to fund an initial assessment. Would you consider a timebox?

## Investor/BD
Subject: Developer-first DRBG (MVP) with reproducible quality signals

Hi <Name>,
We built a developer-friendly DRBG (HKDF→ChaCha20). It’s simple, fast to integrate, and ships with reproducible test runs (BigCrush passed). We’re collecting design-partner pilots in <X> verticals. Can we show a 10-minute demo?
