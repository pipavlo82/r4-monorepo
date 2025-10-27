# 🎲 Provably Fair Lottery (LotteryR4.sol)

On-chain lottery powered by Re4ctoR randomness verification. Fully transparent, cryptographically fair, and regulatory-ready.

**Key Features:**
- ✅ Deterministic winner selection via signed randomness
- ✅ ECDSA signature verification on-chain
- ✅ Complete audit trail via events
- ✅ No admin backdoors or rerolls possible
- ✅ Production-ready for iGaming, NFT raffles, validator rotation

---

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/pipavlo82/r4-monorepo
cd vrf-spec
npm install
```

### Build & Test

```bash
npx hardhat compile
npx hardhat test
```

**Expected output:**
```
LotteryR4
  ✔ picks a deterministic fair winner using verified randomness
  ✔ reverts if signature is invalid

R4VRFVerifier
  ✔ verifies a valid signature from the signer
  ✔ emits event on submitRandom()

4 passing
```

---

## 📋 How It Works

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Players call enterLottery()                              │
│    → Added to on-chain players list                          │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Re4ctoR generates 32 bytes of randomness                 │
│    → Signs it with private key                              │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Off-chain service calls drawWinner(randomness, sig)      │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Contract verifies signature via R4VRFVerifier            │
│    → Rejects if forged or invalid                           │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Winner index = randomness % players.length              │
│    → Deterministic & auditable                              │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. Emit WinnerSelected event for public verification        │
└─────────────────────────────────────────────────────────────┘
```

### The Fairness Guarantee

No one—not even the lottery operator—can:
- Predict which player will win before randomness is generated
- Forge a signature to influence the outcome
- "Reroll" until a specific player wins

Everything is verified cryptographically and recorded on-chain.

---

## 📦 Smart Contracts

### `R4VRFVerifier.sol`

Verifies that randomness was signed by the trusted Re4ctoR node using ECDSA recovery.

```solidity
function verify(
    bytes32 randomness,
    bytes calldata signature,
    address trustedSigner
) external returns (bool)
```

**Features:**
- Standard ECDSA signature verification
- Emits `RandomnessVerified` event for auditability
- Reusable across multiple dApps

### `LotteryR4.sol`

Main lottery contract managing players and winner selection.

```solidity
function enterLottery() external
```
Players join the lottery on-chain with no approval needed.

```solidity
function drawWinner(bytes32 randomness, bytes calldata signature) external
```
Verifies randomness signature and selects winner deterministically.

**Events:**
- `PlayerEntered(address indexed player)` — Player joined
- `WinnerSelected(address indexed winner, uint256 index, bytes32 randomness)` — Winner announced

---

## 🔌 Integration Guide

### For Production Deployments

#### 1. Off-Chain Service

```javascript
// Pseudocode: your backend/game server
const randomness = await re4ctor.generateEntropy();
const signature = await re4ctor.sign(randomness);

// Broadcast to chain
await lottery.drawWinner(randomness, signature);
```

#### 2. On-Chain Setup

```solidity
// Deploy verifier
R4VRFVerifier verifier = new R4VRFVerifier();

// Deploy lottery with verifier and trusted signer
LotteryR4 lottery = new LotteryR4(address(verifier), trustedSignerAddress);
```

#### 3. Verification (Auditor/Regulator)

```javascript
// Anyone can verify the draw
const winner = players[uint256(randomness) % players.length];
// Compare with emitted event
```

---

## 💼 Use Cases

| Use Case | Notes |
|----------|-------|
| **iGaming/Casinos** | Regulatory-compliant, cryptographic fairness proof |
| **NFT Raffles** | On-chain randomness for allowlist lotteries |
| **Validator Rotation** | Fair committee/sequencer selection for blockchain infra |
| **Loot Boxes** | Verifiable randomness for game item distribution |

---

## 📁 Project Structure

```
vrf-spec/
├── contracts/
│   ├── R4VRFVerifier.sol      # ECDSA signature verification
│   └── LotteryR4.sol          # Main lottery contract
├── test/
│   ├── lottery.js             # End-to-end lottery tests
│   └── verify.js              # Verifier unit tests
├── hardhat.config.js
└── package.json
```

---

## 🧪 Running Tests

```bash
# Compile contracts
npx hardhat compile

# Run full test suite
npx hardhat test

# Run with gas reporting (if configured)
REPORT_GAS=true npx hardhat test

# Run specific test file
npx hardhat test test/lottery.js
```

---

## 🎯 Example Flow

1. **Alice, Bob, Charlie** call `enterLottery()`
   ```
   players = [0xAlice, 0xBob, 0xCharlie]
   ```

2. **Re4ctoR generates randomness**
   ```
   randomness = 0x7f3e2a1b...
   signature = <ECDSA signature from Re4ctoR>
   ```

3. **Operator calls drawWinner()**
   ```
   drawWinner(0x7f3e2a1b..., signature)
   ```

4. **Contract verifies & selects winner**
   ```
   winnerIndex = uint256(0x7f3e2a1b...) % 3 = 1
   winner = players[1] = 0xBob ✓
   ```

5. **Event emitted**
   ```
   WinnerSelected(0xBob, 1, 0x7f3e2a1b...)
   ```

6. **Anyone can verify the draw** using the on-chain data

---

## 🔐 Security Considerations

- ✅ Signature must be from trusted signer only
- ✅ Invalid signatures revert the transaction
- ✅ No centralized admin can override the draw
- ✅ All data recorded on-chain for audit trail
- ⚠️ Operator must securely relay Re4ctoR randomness (no tampering in transit)

---

## 🚀 Advanced Features (Roadmap)

- [ ] Auto-payout on winner selection
- [ ] Round-based lotteries with automatic reset
- [ ] Escrow for entry fees (ETH/USDC)
- [ ] Multi-chain deployment (Polygon, Arbitrum, Optimism)
- [ ] Batch player registration
- [ ] Admin governance via DAO

---

## 📝 License

MIT

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit changes (`git commit -am 'Add feature'`)
4. Push to branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## 📧 Support & Contact

**For integration, audits, or regulatory-grade fairness proofs:**

- **Maintainer:** Pavlo Tvardovskyi
- **Email:** shtomko@gmail.com
- **GitHub:** [@pipavlo82](https://github.com/pipavlo82)

---

## 🔗 Resources

- [Re4ctoR Randomness API Documentation](#)
- [ECDSA Signature Verification](https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm)
- [EIP-191: Signed Data Standard](https://eips.ethereum.org/EIPS/eip-191)

---

**Made with ❤️ for transparent, on-chain fairness**
