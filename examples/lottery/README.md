🎲 Provably Fair Lottery (LotteryR4.sol)

On-chain lottery powered by Re4ctoR randomness verification.  
Fully transparent, cryptographically fair, and regulatory-ready.

Key Features:

✅ Deterministic winner selection via signed randomness  
✅ On-chain verification of randomness authenticity  
✅ Supports BOTH classical ECDSA and post-quantum Dilithium3 signatures  
✅ Complete audit trail via events  
✅ No admin backdoors or rerolls possible  
✅ Production-ready for iGaming, NFT raffles, validator rotation, sequencer/committee rotation  

---

🚀 Quick Start

Installation

```bash
git clone https://github.com/pipavlo82/r4-monorepo
cd vrf-spec
npm install
Build & Test

bash
Copy code
npx hardhat compile
npx hardhat test
Expected output:

text
Copy code
LotteryR4
  ✔ picks a deterministic fair winner using verified randomness
  ✔ reverts if signature is invalid

R4VRFVerifier
  ✔ verifies a valid signature from the signer
  ✔ emits event on submitRandom()

4 passing
📋 How It Works

Architecture Overview

text
Copy code
┌─────────────────────────────────────────────────────────────┐
│ 1. Players call enterLottery()                              │
│    → Added to on-chain players list                         │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Re4ctoR generates 32 bytes of randomness                 │
│    → Signs it with its private key                          │
│      - ECDSA(secp256k1) OR Dilithium3 (post-quantum)        │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Off-chain service calls drawWinner(randomness, sig)      │
│    passing randomness + signature to the contract           │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Contract verifies signature via R4VRFVerifier            │
│    → Rejects if forged or invalid                           │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Winner index = randomness % players.length               │
│    → Deterministic & auditable                              │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. Contract emits WinnerSelected event                      │
│    → Full audit trail on-chain                              │
└─────────────────────────────────────────────────────────────┘
The Fairness Guarantee

No one — not even the lottery operator — can:

Predict which player will win before randomness is generated

Forge a signature to influence the outcome

"Reroll" until a specific player wins

Everything is verified cryptographically and recorded on-chain.

📦 Smart Contracts

R4VRFVerifier.sol
Verifies that randomness was signed by the trusted Re4ctoR node.

solidity
Copy code
function verify(
    bytes32 randomness,
    bytes calldata signature,
    address trustedSigner
) external returns (bool)
Features:

Recovers signer and checks it matches the trusted signer

Emits RandomnessVerified event for auditability

Reusable across multiple dApps

Compatible with the signatures served by the R4PQ node (port 8081)

ECDSA(secp256k1) today

Dilithium3 (post-quantum) for enterprise / regulated builds

Dilithium3 support:
The enterprise build of the R4PQ API can return randomness signed with Dilithium3 (FIPS 204 ML-DSA class).
This allows casinos / validators to prove fairness using post-quantum signatures, not just classical ECDSA.

LotteryR4.sol
Main lottery contract managing players and winner selection.

solidity
Copy code
function enterLottery() external
Players join the lottery on-chain with no approval needed.

solidity
Copy code
function drawWinner(bytes32 randomness, bytes calldata signature) external
Verifies randomness signature and selects winner deterministically.

Events:

event PlayerEntered(address indexed player)
Player joined

event WinnerSelected(address indexed winner, uint256 index, bytes32 randomness)
Winner announced (+ which entropy was used)

🔌 Integration Guide

1. Off-Chain Service
Your backend / game server talks to Re4ctoR and then finalizes result on-chain:

js
Copy code
// Pseudocode
// 1. Ask R4PQ (port 8081) for signed randomness
const { random, sig_b64, pubkey_b64 } = await fetch(
  "http://r4-node:8081/random_pq?sig=ecdsa"
).then(r => r.json());

// 2. Submit result to chain
await lottery.drawWinner(random, sig_b64);
For enterprise / PQ mode:

js
Copy code
// same call but sig=dilithium
const { random, sig_b64, pubkey_b64, signature_type } = await fetch(
  "http://r4-node:8081/random_pq?sig=dilithium"
).then(r => r.json());
This gives you post-quantum signed randomness.
Regulator can later prove: "this exact random was produced by that approved node."

2. On-Chain Setup
solidity
Copy code
// Deploy verifier
R4VRFVerifier verifier = new R4VRFVerifier();

// Deploy lottery with verifier and trusted signer address
LotteryR4 lottery = new LotteryR4(
    address(verifier),
    trustedSignerAddress // this matches R4PQ's public key
);
3. Verification (Auditor / Regulator)
Anyone can verify the draw:

js
Copy code
const idx = BigInt(randomness) % BigInt(players.length);
const winner = players[idx];
// winner MUST match WinnerSelected event
This is "provably fair" in the regulatory sense.

💼 Use Cases

Use Case	Notes
iGaming / Casinos	Regulator can check every draw against Dilithium3 / ECDSA signature
NFT Raffles	On-chain provable mints / allowlist selection
Validator Rotation	Fair committee / sequencer election for PoS validators / rollups
Loot Boxes	Verifiable drop tables, anti-reroll fraud

📁 Project Structure

text
Copy code
vrf-spec/
├── contracts/
│   ├── R4VRFVerifier.sol      # Signature verification (ECDSA + PQ-ready flow)
│   └── LotteryR4.sol          # Main lottery contract
├── test/
│   ├── lottery.js             # End-to-end lottery tests
│   └── verify.js              # Verifier unit tests
├── hardhat.config.js
└── package.json
🧪 Running Tests

bash
Copy code
# Compile contracts
npx hardhat compile

# Run full test suite
npx hardhat test

# Run with gas reporting (if configured)
REPORT_GAS=true npx hardhat test

# Run specific file
npx hardhat test test/lottery.js
🎯 Example Flow

Alice, Bob, Charlie call enterLottery()

text
Copy code
players = [0xAlice, 0xBob, 0xCharlie]
Re4ctoR generates randomness

text
Copy code
randomness = 0x7f3e2a1b...
signature  = <ECDSA or Dilithium3 signature from R4PQ>
Operator calls drawWinner(randomness, signature)

Contract verifies signature

Winner is chosen:

text
Copy code
winnerIndex = uint256(randomness) % players.length
winner = players[winnerIndex]
Contract emits:

text
Copy code
WinnerSelected(winner, winnerIndex, randomness)
Anyone (player, regulator, chain) can confirm the round after the fact.

🔐 Security Considerations

✅ Signature must come from the trusted signer only
✅ Invalid signatures revert the tx
✅ No centralized admin can override the draw
✅ All data recorded on-chain for audit trail
⚠️ The off-chain relay must not modify randomness between R4PQ → chain
(auditor can detect tampering using the signature anyway)

🚀 Advanced Features (Roadmap)

Auto-payout on winner selection

Round-based lotteries with automatic reset

Escrow for entry fees (ETH/USDC)

Multi-chain deployment (Polygon, Arbitrum, Optimism)

Batch player registration

Admin governance via DAO

Native Dilithium3 verification precompiles (L2 / rollup path)

📝 License

MIT

🤝 Contributing

Contributions welcome! Please:

Fork the repo

git checkout -b feature/my-feature

git commit -am 'Add feature'

git push origin feature/my-feature

Open a Pull Request

📧 Support & Contact

Maintainer: Pavlo Tvardovskyi
Email: shtomko@gmail.com
GitHub: @pipavlo82

Made with ❤️ for transparent, on-chain fairness.
