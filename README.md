# Re4ctoR-RNG
High-performance cryptographic random number generator with post-quantum security focus.  Tested with NIST STS, Dieharder, and TestU01🔐⚡
# Re4ctoR: A Post-Quantum Verifiable Random Number Generator (VRNG)

## 📌 Project Overview
**Re4ctoR** is an innovative and cryptographically secure random number generator (CSPRNG)
designed to address the most pressing challenges in modern cybersecurity.

Its unique hybrid architecture combines:
- principles of **chaotic systems**,
- state-of-the-art **cryptographic primitives**,
- a novel **entropy model**,

making it an ideal solution for **blockchain, cryptography, and Web3 applications**.

The key advantage of Re4ctoR is its **post-quantum resilience** and the ability to generate
**verifiable random numbers (VRNG)**, ensuring absolute transparency and trust.

---

## 🚀 Key Advantages & Features
- **Unrivaled Reliability** → Passed NIST STS, PractRand, Dieharder, and TestU01.
- **Verifiable Randomness (VRF)** → Each number includes a cryptographic proof,
  verifiable without exposing the seed or core algorithm.
- **Post-Quantum Cryptography (PQC)** → Integration of ML-DSA-65 (Dilithium) ensures resilience
  against quantum attacks.
- **Exceptional Performance** → 90+ MB/s throughput without compromising security.
- **Unique Hybrid Architecture** → “Accumulate chaos, extract once” model eliminates hidden patterns.

---

## 📊 Test Results

| Test Suite             | Result                | Comments |
|------------------------|-----------------------|----------|
| **NIST STS**           | PASSED (100%)         | Passed all 15 core tests and sub-tests. |
| **PractRand**          | PASSED                | No anomalies observed up to 8 GB. |
| **Dieharder**          | PASSED (113/114, 1 WEAK) | 113 passed, 1 weak result (expected statistical fluctuation). |
| **TestU01 SmallCrush** | PASSED (15/15)        | Confirmed uniformity and randomness. |
| **TestU01 Crush**      | PASSED (96/96)        | All advanced statistical tests passed. |
| **TestU01 BigCrush**   | PASSED (160/160)      | Successfully passed the most demanding suite. |
🌍 Applications

Blockchain & Web3 → randomness for smart contracts, DeFi, decentralized games, lotteries.

Cybersecurity → cryptographic keys, nonces, seeds.

Scientific Simulations → Monte Carlo, statistical modeling.

IoT & Edge Computing → lightweight, reliable entropy for connected devices.

📜 Licensing

Re4ctoR is currently in the pre-commercialization phase.
We are open to collaborations and licensing discussions with interested partners.

📞 Contact

For more information, please contact:

✉️ shtomko@gmail.com
