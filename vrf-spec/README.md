# 🔐 R4 VRF — Verifiable Random Function (ECDSA)

On-chain verification for RE4CTOR randomness. This package provides Solidity contracts, tests, and tooling that allow any EVM-based blockchain to verify randomness produced by a trusted RE4CTOR node.

---

## 📦 Directory Structure

```
vrf-spec/
├── contracts/
│   ├── R4VRFVerifierCanonical.sol   # Canonical ECDSA verifier (main)
│   └── LotteryR4.sol                # Reference provably-fair lottery
│
├── test/
│   ├── verify.js                    # Signing + verification test
│   ├── verify_r4_canonical.js       # Tests against RE4CTOR output
│   └── lottery.js                   # Demonstrates end-to-end flow
│
├── scripts/
│   └── deploy.js                    # Deployment script
│
├── hardhat.config.js
├── package.json
└── SBOM.vrf-spec.cdx.json          # CycloneDX SBOM (security)
```

Everything in this package is tested and known to work with:

```
✅ 6 passing (722ms)
```

---

## 🎯 Overview

### **1. R4VRFVerifierCanonical.sol**

Canonical verifier used by all protocols.

**Function: `verify(bytes32 randomness, bytes sig, address signer)`**

Verifies that `randomness` was produced and signed by the authorized RE4CTOR node.

**Process:**
1. Computes Ethereum Signed Message Hash (EIP-191)
2. Recovers signer via `ECDSA.recover`
3. Compares recovered address with `signer`

**Returns:** `bool` → `true` if signature valid.

**Function: `submitRandom(bytes32 randomness, bytes signature)`**

- Calls `verify()` internally
- Emits event: `RandomnessVerified(address submitter, bytes32 randomness, uint256 timestamp)`

### **2. LotteryR4.sol**

A minimal, production-ready example of provably fair randomness for lotteries, raffles, mints, or gaming.

**Key features:**
- Uses verified randomness only
- Automatically selects winner
- Demonstrates recommended pattern for dApps

---

## 🚀 Quick Start

### Install

```bash
cd vrf-spec
npm install
```

### Compile

```bash
npx hardhat compile
```

### Run Tests

```bash
npx hardhat test
```

**Expected:**

```
✅ 6 passing
```

---

## 🔗 End-to-End Integration Flow

### **Step 1 — RE4CTOR provides randomness**

```bash
curl -H "X-API-Key: demo" \
  "http://localhost:8081/random_dual?sig=ecdsa"
```

**Example response:**

```json
{
  "random": 3727920637,
  "signature_type": "ECDSA(secp256k1)",
  "sig_b64": "zHpyDw2wDv2ioz0LZ...",
  "pubkey_b64": "LS0tLS1CRUdJTiBQVUJMSUMgS0VZ...",
  "signer_addr": "0x5D57D912E1c4FcBA23b208Fe1df3D5306bf644aC"
}
```

### **Step 2 — dApp verifies signature (Solidity)**

```solidity
bool ok = verifier.verify(
    randomBytes32,
    signature,
    r4Signer
);
require(ok, "Invalid randomness");
```

### **Step 3 — Use randomness**

```solidity
uint256 winner = uint256(randomBytes32) % totalPlayers;
```

---

## 📊 Gas Stats

| Function | Gas |
|----------|-----|
| `verify()` | ~25k |
| `submitRandom()` | ~28k |

(Estimates depend on chain; stable across EVM networks.)

---

## 🔒 Security

### **Current**
- ECDSA(secp256k1)
- Ethereum Signed Message Hash (EIP-191)
- Full SBOM (CycloneDX)
- Hardhat tests for all flows

### **Roadmap (Q1 2026)**
- ML-DSA-65 (FIPS-204) PQ verifier
- Dual-mode randomness (ECDSA + PQ)
- Attested entropy proofs

---

## 🌐 Networks

| Network | Status |
|---------|--------|
| Sepolia | ✅ Ready |
| Polygon | ✅ Ready |
| Arbitrum | ✅ Recommended |
| Mainnet | ⏳ Pending audit |

### Deployment

```bash
npx hardhat run scripts/deploy.js --network <network>
```

---

## 📚 Useful Links

- **Core README:** [`../README.md`](../README.md)
- **RE4CTOR API:** `/random`, `/random_dual`, `/random_pq`
- **Hardhat Docs:** https://hardhat.org/docs

---

## 👤 Maintainer

**Pavlo Tvardovskyi**
- Email: shtomko@gmail.com
- GitHub: https://github.com/pipavlo82
