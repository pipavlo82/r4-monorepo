# Re4ctor VRF Demo (Mock)

This is a **mock** VRF plumbing demo for Web3 pitch:
- `MockVerifier` (not a real VRF) validates basic sizes & emits event.
- `ConsumerDemo` receives randomness via `fulfillRandomness`.
- Off-chain script reads 32B from `r4cat`, makes a fake proof and calls the consumer.

## Prereqs
- Node 18+ (npm)
- Funded EOA for Sepolia (0.01+ ETH)
- In repo root (`~/r4-monorepo`) have built `bin/r4cat` (`make -B`)

## Setup
cp .env.example .env
# edit SEPOLIA_RPC_URL and PRIVATE_KEY
npm install
npm run build

## Deploy (Sepolia)
npm run deploy
# note ConsumerDemo address; put it to .env as CONSUMER_ADDR

## Push randomness (off-chain -> on-chain)
npm run push
# script logs roundId, randomness, proof and tx hash

## Security
This is NOT a real VRF. Replace `MockVerifier` with a formal VRF and gate `fulfillRandomness`
to a dedicated coordinator in production.
