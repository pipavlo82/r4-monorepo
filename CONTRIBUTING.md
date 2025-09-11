# Contributing to Re4ctoR-RNG

Thanks for your interest in contributing! This project focuses on a high-quality, verifiable RNG with post-quantum considerations.

## Ways to contribute
- Report bugs and suspected randomness issues
- Improve docs and examples
- Add tests (PractRand, Dieharder, NIST STS, TestU01) and reproducible harnesses
- Fix bugs or propose well-scoped features

## Before you start
1. Search existing Issues/PRs.
2. For larger changes, open a discussion Issue first.

## Workflow
1. Fork → create a feature branch from `main`.
2. Make commits with clear messages (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).
3. Add/adjust tests and update docs if behavior changes.
4. Open a Pull Request (PR) against `main`.

## Bug reports
Please include:
- Environment (OS/arch), build info, commit SHA/release tag
- Exact steps to reproduce
- If RNG quality is involved:
  - test tool + version (PractRand/Dieharder/NIST STS/TestU01),
  - parameters, data volume, seeds/nonces, command lines,
  - failing logs/output.

## Coding & testing guidelines
- Keep changes minimal and focused.
- Provide deterministic test inputs or attach command lines for long-running statistical tests.
- Avoid breaking public APIs without prior discussion.

## Security issues
**Do not** open public Issues. See `SECURITY.md` and use GitHub Security Advisories.

## License
By contributing, you agree your contributions are licensed under the repository’s Apache-2.0 license.
