# VRF Demo (Mock)

This demo shows the plumbing for an on-chain consumer that receives randomness
from an off-chain service. It uses a MockVerifier (NOT a real VRF).

Contracts
- IVRFConsumer.sol: interface for callback-style consumers
- MockVerifier.sol: accepts (roundId, randomness, proof), checks basic sizes, emits Verified

Off-chain script
- examples/vrf/scripts/request_randomness.py:
  - reads 32 bytes from ./bin/r4cat
  - builds a placeholder proof = SHA256(randomness || timestamp)

Quick run
  python3 examples/vrf/scripts/request_randomness.py

To compile contracts use your preferred tool (Foundry/Hardhat).
