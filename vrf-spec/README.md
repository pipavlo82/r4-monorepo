# VRF / PQ roadmap

Goal: post-quantum verifiable randomness suitable for validator rotation,
rollup sequencer fairness, lotteries, anti-manipulation beacons.

Planned response shape:
/vrf -> {
  "random": "<bytes>",
  "signature": "<pq_sig>",
  "public_key": "<node_key>",
  "verified": true
}

Requirements:
- Each node has a post-quantum signing identity
- Each response is signed and auditable
- No "grinding" (operator can't silently reroll)

Consumers:
- PoS validator set rotation
- L2 sequencers / prover jobs
- Fair drops / lotteries / raffles
