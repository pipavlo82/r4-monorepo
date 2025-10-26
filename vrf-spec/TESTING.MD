## 🔗 On-chain Verification (VRF Path)

Re4ctoR is not just "here's some random bytes."  
It also includes an **on-chain verification pipeline (VRF)**.

This repo ships a reference Solidity contract:  
**`vrf-spec/contracts/R4VRFVerifier.sol`**

### What it does

**1. `verify(randomness, signature, signer)`**
   - Recomputes the signed message hash  
   - Recovers the signer via ECDSA  
   - Confirms that the randomness was produced by the expected Re4ctoR node  

**2. `submitRandom(randomness)`**
   - Emits an event `RandomnessVerified(sender, randomness)`  
   - Lets consumer contracts (lotteries, games, DeFi apps) react to verified randomness  

### Included Hardhat Test

**`vrf-spec/test/verify.js`**

This test:
- Generates a random value (`bytes32`)
- Signs it with a local Ethereum key (simulating Re4ctoR)
- Verifies it on-chain via the Solidity contract
- Confirms the event emission

### Run Locally

```bash
cd vrf-spec
npm install
npx hardhat compile
npx hardhat test
```

**✅ Result:**

```
R4VRFVerifier
  ✔ verifies a valid signature from the signer (424ms)
  ✔ emits event on submitRandom()

2 passing (448ms)
```

Re4ctoR can now generate randomness off-chain  
and **prove on-chain** that it was produced by a trusted signer.

This forms the **MVP of the Re4ctoR VRF**:

```
Off-chain entropy → ECDSA signature → On-chain verification
```
