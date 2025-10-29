# Contributing to RE4CTOR

Thanks for your interest in contributing 🖤

## Ground rules

- Security > speed.
- Reproducibility > cleverness.
- Anything touching randomness, key material, or signature logic MUST come with:
  - a test
  - and a short plaintext explanation of threat model / assumptions.

## How to contribute

### 1. Fork & branch
- Fork this repo
- Create a feature branch:
  `git checkout -b feature/my-feature`

### 2. Make your change
Good targets for first PRs:
- docs fixes (typos, clarity, diagrams)
- new Hardhat tests under `vrf-spec/test/`
- language SDKs (Go/Rust/etc) that call `/random` and `/random_pq`
- infra scripts / deployment hardening

Please do NOT submit:
- attempts to reimplement the sealed core RNG
- custom crypto constructions
- changes that weaken signature checks

### 3. Run tests locally
- Core stress & health:
  `./run_full_demo.sh`
- Solidity tests:
  `cd vrf-spec && npx hardhat test`

All tests must pass.

### 4. Open PR
Explain:
- what changed
- why it matters
- does it affect security assumptions?

Security-related PRs may be moved to a private thread before merge.

## Security disclosure

If you believe you found a vuln (bias, key extraction, signature forgery, replay abuse, etc), DO NOT open a public issue.

Instead email: `shtomko@gmail.com`  
Subject: `SECURITY DISCLOSURE`

You’ll get a response.
