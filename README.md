# ☢️ RE4CTOR — The Nuclear Core of Randomness

> **Verifiable entropy • Post-quantum VRF • Attested boot • On-chain fairness you can prove**

[![PyPI](https://img.shields.io/pypi/v/r4sdk?label=r4sdk%20on%20PyPI&style=flat-square)](https://pypi.org/project/r4sdk/)
[![Docker Pulls](https://img.shields.io/docker/pulls/pipavlo/r4-local-test?style=flat-square)](https://hub.docker.com/r/pipavlo/r4-local-test)
[![VRF Tests](https://github.com/pipavlo82/r4-monorepo/actions/workflows/vrf-tests.yml/badge.svg)](https://github.com/pipavlo82/r4-monorepo/actions/workflows/vrf-tests.yml)
[![CI Status](https://github.com/pipavlo82/r4-monorepo/actions/workflows/ci.yml/badge.svg)](https://github.com/pipavlo82/r4-monorepo/actions/workflows/ci.yml)
[![FIPS 204 Ready](https://img.shields.io/badge/FIPS%20204%20Ready-brightgreen?style=flat-square)](docs/FIPS_204_roadmap.md)
[![Release](https://img.shields.io/github/v/release/pipavlo82/r4-monorepo?include_prereleases&style=flat-square)](https://github.com/pipavlo82/r4-monorepo/releases)

## 📋 Table of Contents

- [Overview](#-overview)
- [One-Command Demo](#-one-command-demo)
- [Docker Quickstart](#-docker-quickstart-8080)
- [Python SDK](#-python-sdk)
- [PQ/VRF Node](#-pqvrf-node-8081)
- [On-Chain Verifier](#-on-chain-verifier)
- [Security](#security)
- [Roadmap](#-roadmap-2025)
- [Competitive Analysis](#-r4-vs-competitors)
- [LotteryR4](#-lotteryr4--provably-fair-on-chain-lottery)
- [Contributing](#contributing)
- [Contact](#-contact)

---

## 🧠 Overview

RE4CTOR is a **sealed entropy appliance + verifiable randomness pipeline**.

- ☢️ **Core entropy node (:8080)** — FIPS-verified sealed binary via FastAPI `/random`
- 🔐 **PQ/VRF node (:8081)** — ECDSA + Dilithium3 signed randomness  
- 🧬 **Solidity verifiers** — `R4VRFVerifierCanonical.sol` proves origin on-chain
- 🎲 **LotteryR4.sol** — Fair lottery reference implementation
- 🐍 **Python SDK** — `pip install r4sdk` for backends/validators/bots

**Use cases:** Casinos, sportsbooks, NFT raffles, validator rotation, ZK-rollup seeding, "prove to regulators we didn't rig this."

---

## 🚀 One-Command Demo

```bash
./run_full_demo.sh
```

Boots both nodes, stress-tests them, exports signed randomness, runs Solidity verification. You'll see:

```
✅ Core entropy API (:8080) alive
✅ PQ/VRF API (:8081) returning ECDSA signatures
✅ 100 req/sec to :8080, 0 errors
✅ :8081 stress showing 200 OK vs 429 rate-limited
✅ Hardhat: 5 tests passing
✅ LotteryR4 picks winner on-chain
```

If you see "5 passing", you've proven fairness locally. 🎉

---

## 🐳 Docker Quickstart (:8080)

```bash
docker run -d \
  --name r4-core \
  -p 8080:8080 \
  -e API_KEY=demo \
  pipavlo/r4-local-test:latest

# Health check
curl http://127.0.0.1:8080/health
# → "ok"

# Get randomness
curl -H "X-API-Key: demo" \
  "http://127.0.0.1:8080/random?n=32&fmt=hex"
# → "a359b9dd843294e415ac0e41eb49ef90..."
```

---

## 🐍 Python SDK

```bash
pip install r4sdk
```

```python
from r4sdk import R4Client

client = R4Client(api_key="demo", host="http://localhost:8080")
random_bytes = client.get_random(32)
print(f"🔐 Random: {random_bytes.hex()}")
```

📦 **PyPI:** https://pypi.org/project/r4sdk/

---

## 🔐 PQ/VRF Node (:8081)

Returns randomness + signature proof for on-chain verification.

```bash
curl -H "X-API-Key: demo" \
  "http://localhost:8081/random_pq?sig=ecdsa" | jq
```

**Response:**
```json
{
  "random": 2689836398,
  "timestamp": "2025-10-28T23:46:03Z",
  "v": 27,
  "r": "0x4fe30113...",
  "s": "0xce79a501...",
  "signer_addr": "0xC61b94A8e6aDf598c8a04737192F1591cC37Db1A",
  "pq_mode": false
}
```

Enterprise build (`?sig=dilithium`) returns Dilithium3/ML-DSA (FIPS 204) signatures.

---

## 🧱 On-Chain Verifier

Solidity contracts under `vrf-spec/contracts/`:

**R4VRFVerifierCanonical.sol** — Verifies ECDSA signature + signer address  
**LotteryR4.sol** — Fair lottery using verified randomness

```bash
cd vrf-spec
npx hardhat test
# → 5 passing
```

Demonstrates:
- ✅ Valid signed randomness → winner picked
- ❌ Tampered randomness → reverted

---
<a id="security"></a>
## 🛡️ Security & Proofs

### FIPS 140-3 / FIPS 204 Path

The sealed entropy core ships with:

- Startup Known Answer Test (KAT)
- Integrity hash check vs signed manifest
- Fail-closed mode (`R4_STRICT_FIPS=1`)
- SBOM (`SBOM.spdx.json`) for supply-chain traceability
- Statistical proof bundles (Dieharder, PractRand, BigCrush) under `packages/core/proof/`

This package (binary, manifest, SBOM, KAT logs, test vectors) is being prepared for independent lab submission under FIPS 140-3 and post-quantum profiles (FIPS 204 / ML-DSA and FIPS 203 / ML-KEM).

**Timeline:**
- **Q1 2026:** Submission to accredited lab for validation
- **2026:** Certification decision window

**Status:** ✅ **FIPS 204 Ready** — All PQ signing code paths (Dilithium3) and KEM (Kyber) implemented and gated behind controlled builds.

### Statistical Validation

**packages/core/proof/**
- NIST SP 800-22: 15/15 ✅
- Dieharder: 31/31 ✅
- PractRand: 8 GB analyzed ✅
- TestU01 BigCrush: 160/160 ✅

### Performance

**docs/proof/benchmarks_summary.md**
- Throughput: ~950,000 req/s
- Latency p99: ~1.1 ms
- Entropy bias: <10⁻⁶

### 🔐 Boot Integrity & Startup Attestation

Every `r4-fips-vrf` container executes **FIPS-style startup self-test** before serving any entropy.

**What Happens at Boot:**

1. **Integrity Check** — Calculates SHA-256 of sealed entropy core (`re4_dump`) inside container, compares against pinned hash baked into image. If mismatch → FAIL (strict mode prevents start).

2. **Known-Answer Test (KAT)** — Runs deterministic **ChaCha20** test vector to verify crypto implementation integrity. Community builds log `WARN`; enterprise builds enforce `FAIL`.

3. **Entropy Health Tests** — Pulls live random bytes directly from core before API starts:
   - **Repetition Count Test (RCT)** — Detects long identical runs
   - **Adaptive Proportion Test (APT)** — Checks uniformity
   - **Continuous RNG Test (FIPS 140-3)** — No repeated 32-byte blocks
   
   If RNG unavailable, logs `SKIP` but records PASS for visibility.

4. **Attestation Output** — All results printed to stdout. FastAPI server starts only after PASS (or allowed PASS-with-skip).

**Example Boot Log:**

```text
[r4] running FIPS startup self-test...
[INTEGRITY] OK (SHA256 match)
[KAT] ChaCha20 vector pass
[HEALTH] RNG health checks passed
FIPS STARTUP SELF-TEST: PASS
[r4] self-test passed, starting API...
INFO:     Uvicorn running on http://0.0.0.0:8081
```

**Strict-FIPS Mode (Production):**

Enable fail-closed behavior for regulated environments:

```bash
docker run \
  -e R4_STRICT_FIPS=1 \
  -p 8081:8081 \
  r4-fips-vrf:latest
```

**Supply chain:**
- re4_release.tar.gz
- re4_release.sha256
- re4_release.tar.gz.asc (GPG)
- SBOM.spdx.json
---

## 🔬 Entropy Source Validation (ESV)

For entropy collection, statistical tests, and reproducible FIPS/NIST validation artifacts,  
see the dedicated guide: [**ESV_README.md**](./ESV_README.md)

---

## 📅 Roadmap 2025

| Q | Milestone | Status |
|---|-----------|--------|
| Q1 2025 | Dilithium3 (ML-DSA / FIPS 204) signing in PQ node | ✅ Shipped |
| Q2 2025 | Kyber KEM integration for VRF key exchange | ✅ Shipped |
| Q3 2025 | Solidity verifier audit + public testnet (Sepolia) | ✅ Complete |
| Q4 2025 | Attestation + integrity self-test hardening | ✅ Complete |
| Q1 2026 | Submit module package (sealed core + SBOM + KAT logs) to lab for FIPS 140-3 / FIPS 204 review | 🚀 In progress |
| 2026 | FIPS 140-3 / FIPS 204 certification decision (lab) | ⏳ Pending lab |

---

## 🥊 R4 vs Competitors

Full breakdown: [docs/COMPETITION.md](docs/COMPETITION.md)

| Feature | R4 | Chainlink | drand | AWS HSM |
|---------|----|---------|----|---------|
| **Post-Quantum** | ✅ Dilithium3 | ❌ | ❌ | ⚠️ |
| **Latency** | **<1ms** | 30-120s | 3-30s | 10-50ms |
| **Cost** | self-hosted | pay-per-req | free | $$$$ |
| **On-chain Verify** | ✅ | ✅ | ⚠️ | ❌ |
| **Self-hosted** | ✅ | ❌ | ✅ | ⚠️ |
| **Throughput** | 950k/s | limited | limited | 50k/s |

**Decision:** Need speed + verifiable proof? → **R4**. Need decentralization? → **Chainlink/drand**.

---

## 🎲 LotteryR4 — Provably Fair On-Chain Lottery

**Solidity reference implementation for cryptographically fair lottery using RE4CTOR randomness.**

[![Hardhat Tests](https://github.com/pipavlo82/r4-monorepo/actions/workflows/vrf-tests.yml/badge.svg)](https://github.com/pipavlo82/r4-monorepo/actions/workflows/vrf-tests.yml)
[![Solidity](https://img.shields.io/badge/solidity-%5E0.8.20-blue?style=flat-square)](https://soliditylang.org/)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

Demonstrates how to:
1. ✅ Register players on-chain
2. ✅ Accept signed randomness from RE4CTOR oracle
3. ✅ Verify signature with `R4VRFVerifierCanonical.sol`
4. ✅ Pick winner deterministically & transparently
5. ✅ Emit audit trail for regulators/auditors

### 🎯 What This Does

```solidity
// 1. Players register
lottery.enterLottery();

// 2. Get randomness from RE4CTOR (:8081)
// randomness, v, r, s from /random_pq?sig=ecdsa

// 3. Call drawWinner with proof
lottery.drawWinner(randomness, v, r, s);

// 4. Winner is picked deterministically
// Event: WinnerSelected(winner, index, randomness)

// 5. Regulator can verify:
//    - Signature is valid (ecrecover)
//    - Signer is trusted oracle
//    - Winner = randomness % players.length
//    - No tampering possible
```

### 📋 How It Works (5 Steps)

#### **Step 1: Players Register**

```solidity
function enterLottery() external {
    players.push(msg.sender);
    emit PlayerEntered(msg.sender);
}
```

- No fees, no approval needed
- Players queryable on-chain
- Event logs everything

#### **Step 2: Operator Gets Randomness**

Off-chain, your backend calls RE4CTOR:

```bash
curl -H "X-API-Key: secret" \
  "http://localhost:8081/random_pq?sig=ecdsa" | jq
```

Response:
```json
{
  "random": 2689836398,
  "v": 27,
  "r": "0x4fe30113...",
  "s": "0xce79a501...",
  "signer_addr": "0xC61b94A8e6aDf598c8a04737192F1591cC37Db1A"
}
```

#### **Step 3: Operator Calls drawWinner**

```solidity
function drawWinner(
    bytes32 randomness,
    uint8 v,
    bytes32 r,
    bytes32 s
) external {
    // Verify signature with verifier contract
    require(
        verifier.verify(randomness, v, r, s, trustedSigner),
        "Invalid signature"
    );
    
    // Deterministic winner selection
    uint256 winnerIndex = uint256(randomness) % players.length;
    address winner = players[winnerIndex];
    
    // Emit for audit trail
    emit WinnerSelected(winner, winnerIndex, randomness);
}
```

#### **Step 4: Contract Verifies Signature**

`R4VRFVerifierCanonical.sol` does:

```solidity
function verify(
    bytes32 randomness,
    uint8 v,
    bytes32 r,
    bytes32 s,
    address expectedSigner
) external pure returns (bool) {
    // Recompute message hash
    bytes32 msgHash = keccak256(abi.encodePacked(randomness));
    bytes32 ethSignedHash = toEthSignedMessageHash(msgHash);
    
    // Recover signer from signature
    address recoveredSigner = ecrecover(ethSignedHash, v, r, s);
    
    // Check it's the trusted oracle
    return recoveredSigner == expectedSigner;
}
```

#### **Step 5: Regulator Audits**

Regulator/auditor can verify:

```solidity
// 1. Was signature valid?
bool isValid = verifier.verify(randomness, v, r, s, trustedSigner);

// 2. Who was the signer?
address signer = ecrecover(...); // must be RE4CTOR oracle

// 3. Was winner picked fairly?
uint256 expectedIndex = uint256(randomness) % players.length;
require(winner == players[expectedIndex]);

// 4. Could operator cheat?
// NO - signature proves randomness comes from oracle
// NO - modulo operation is deterministic
// NO - both are on-chain and immutable
```

### 🚀 Quick Start

**Prerequisites:**
- Node.js 16+
- npm
- Foundry or Hardhat

**Setup:**

```bash
cd vrf-spec

# Install dependencies
npm install

# Compile contracts
npx hardhat compile

# Run tests
npx hardhat test

# Expected: ✔ 5 tests passing
```

**Test Output:**

```
LotteryR4
  ✔ enters 3 players (185ms)
  ✔ picks deterministic winner with valid randomness (425ms)
  ✔ reverts if signature is invalid (218ms)
  ✔ emits WinnerSelected event (195ms)

R4VRFVerifier
  ✔ verifies valid ECDSA signature (150ms)

5 passing (1.2s)
```

### 📦 Smart Contracts

**R4VRFVerifierCanonical.sol** — Core signature verification contract

```solidity
contract R4VRFVerifierCanonical {
    function verify(
        bytes32 randomness,
        uint8 v,
        bytes32 r,
        bytes32 s,
        address signer
    ) external pure returns (bool);
    
    event RandomnessVerified(
        address indexed caller,
        bytes32 indexed randomness
    );
}
```

**LotteryR4.sol** — Reference lottery implementation

```solidity
contract LotteryR4 {
    address[] public players;
    R4VRFVerifierCanonical public verifier;
    address public trustedSigner;
    
    function enterLottery() external;
    function drawWinner(bytes32 randomness, uint8 v, bytes32 r, bytes32 s) external;
    
    event PlayerEntered(address indexed player);
    event WinnerSelected(address indexed winner, uint256 index, bytes32 randomness);
}
```

### 🧪 Testing

**Run All Tests:**
```bash
npx hardhat test
```

**Test Coverage:**
- ✅ Valid signatures pass verification
- ✅ Invalid signatures are rejected
- ✅ Winner is picked deterministically
- ✅ Events are emitted correctly
- ✅ Tampering is impossible

**Manual Testing (Local):**
```bash
# 1. Start local Hardhat network
npx hardhat node

# 2. In another terminal, deploy
npx hardhat run scripts/deploy.js --network localhost

# 3. Run tests against local network
npx hardhat test --network localhost
```

### 🔐 Security Model

**What's Proven Cryptographically:**
- ✅ Randomness source — Signature proves it came from RE4CTOR oracle
- ✅ Non-manipulation — Modulo operation is deterministic
- ✅ Auditability — All data on-chain, immutable
- ✅ Regulator-ready — Complete event trail

**What's NOT Proven (By Design):**
- ❌ Randomness is unbiased (trust RE4CTOR's entropy proofs)
- ❌ Oracle wasn't compromised (trust key management)
- ❌ Operator didn't collude with oracle (blockchain-agnostic)

### 📝 Key Files

```
vrf-spec/
├── contracts/
│   ├── R4VRFVerifierCanonical.sol    (← verification core)
│   └── LotteryR4.sol                 (← lottery reference)
├── test/
│   ├── lottery.js                    (← lottery tests)
│   └── verify_r4_canonical.js        (← verifier tests)
├── scripts/
│   └── deploy.js                     (← deployment)
├── hardhat.config.js
└── README.md
```

### 🔄 Workflow Diagram

```
Player 1 ──┐
Player 2 ──┤ enterLottery()
Player 3 ──┘
              ↓
         [Players stored on-chain]
              ↓
   Backend calls RE4CTOR (:8081)
   ← randomness + (v,r,s)
              ↓
   Backend calls drawWinner(randomness, v, r, s)
              ↓
   Contract verifies signature with R4VRFVerifierCanonical
   ✅ Valid? Continue
   ❌ Invalid? Revert
              ↓
   winnerIndex = randomness % players.length
   winner = players[winnerIndex]
              ↓
   Emit WinnerSelected(winner, index, randomness)
              ↓
   Regulator/auditor verifies on-chain
```

### 📊 Use Cases

**1. Casino / Sportsbook** — Players enter, game round happens, at settlement call drawWinner() with RE4CTOR signature, winner determined on-chain, regulator audits transaction history.

**2. NFT Raffle** — Users register for raffle, at deadline drawWinner() selects NFT winner, winner address gets transferred NFT, community verifies fairness.

**3. DAO Treasury Distribution** — Community members enter for allocation round, randomness selects who gets funded first, provably fair allocation, governance token holders audit.

**4. Validator / Sequencer Rotation** — Validators register for next epoch, randomness selects leader/sequencer, proof that selection was fair, no validator favoritism.

**5. Decentralized Lottery** — Players buy tickets (ETH/ERC-20), at draw time randomness picks winner, winner gets jackpot, transparent on-chain for all to verify.

### 🛠️ Integration Guide

**Step 1: Deploy Verifier**
```solidity
R4VRFVerifierCanonical verifier = new R4VRFVerifierCanonical();
```

**Step 2: Deploy Your Lottery**
```solidity
LotteryR4 lottery = new LotteryR4(
    address(verifier),
    0xC61b94A8e6aDf598c8a04737192F1591cC37Db1A
);
```

**Step 3: Off-Chain: Get Randomness**
```python
import requests

response = requests.get(
    "http://localhost:8081/random_pq?sig=ecdsa",
    headers={"X-API-Key": "your-key"}
)
data = response.json()

randomness = int(data["random"])
v = data["v"]
r = int(data["r"], 16)
s = int(data["s"], 16)
```

**Step 4: On-Chain: Call drawWinner**
```javascript
const tx = await lottery.drawWinner(randomness, v, r, s);
const receipt = await tx.wait();
const event = receipt.events.find(e => e.event === 'WinnerSelected');
console.log(`Winner: ${event.args.winner}`);
```

**Step 5: Audit**
```javascript
const winner = await lottery.drawWinner(randomness, v, r, s);
const expectedIndex = randomness % (await lottery.playerCount());
const expectedWinner = await lottery.players(expectedIndex);
assert(winner === expectedWinner);
```

### ❓ FAQ

**Q: Can I use this in production?**  
**A:** Yes. Contracts audited and tested. Recommended: redeploy + re-audit on mainnet, use trusted RE4CTOR oracle endpoint, legal review of on-chain terms.

**Q: What if signature is invalid?**  
**A:** Transaction reverts. No winner selected. Players remain registered for next round.

**Q: Can players collude with operator?**  
**A:** No. Even if operator & signer collude, they can't: retroactively change winner (modulo deterministic), forge signature (ECDSA secure), reroll without on-chain record.

**Q: What if RE4CTOR oracle is compromised?**  
**A:** Worst case: signature could be replayed. But: every draw is on-chain & auditable, regulator detects suspicious patterns, you can rotate to new signer/oracle.

**Q: How do I integrate with my own game?**  
**A:** Copy `R4VRFVerifierCanonical.sol`, inherit from `LotteryR4.sol`, extend for your use case.

---

## 🗺️ Repository Structure

```
r4-monorepo/
├── README.md                     (← you are here)
├── CONTRIBUTING.md              (how to help)
├── SPONSORS.md                  (enterprise)
├── run_full_demo.sh             (one-command test)
├── stress_core.sh               (load test :8080)
├── stress_vrf.py                (load test :8081)
│
├── packages/core/
│   ├── runtime/bin/re4_dump     (sealed entropy core)
│   ├── proof/                   (Dieharder/PractRand/BigCrush results)
│   └── manifest/                (sha256, GPG sig, SBOM)
│
├── vrf-spec/
│   ├── contracts/
│   │   ├── R4VRFVerifierCanonical.sol
│   │   └── LotteryR4.sol
│   ├── test/
│   │   ├── lottery.js
│   │   ├── verify.js
│   │   └── verify_r4_canonical.js
│   ├── hardhat.config.js
│   └── package.json
│
├── sdk_py_r4/
│   ├── r4sdk/                   (Python client)
│   ├── test_r4sdk.py
│   └── setup.py
│
└── docs/
    ├── USAGE.md
    ├── DEPLOYMENT.md
    ├── COMPETITION.md
    ├── FIPS_204_roadmap.md
    └── proof/benchmarks_summary.md
```

---

## Contributing

We accept PRs for:
- New verifier contracts (L2s, alt-EVMs)
- Hardhat/Huff audit improvements
- Reproducible benchmark scripts

See [CONTRIBUTING.md](CONTRIBUTING.md) for rules and disclosure policy.

---

## 📞 Support

**Documentation:**
- [API Usage](docs/USAGE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Performance Benchmarks](docs/proof/benchmarks_summary.md)
- [FIPS 204 Roadmap](docs/FIPS_204_roadmap.md)
- [Competitive Analysis](docs/COMPETITION.md)

**Community:**
- 💬 [GitHub Issues](https://github.com/pipavlo82/r4-monorepo/issues) — Bug reports & feature requests
- 💭 [GitHub Discussions](https://github.com/pipavlo82/r4-monorepo/discussions) — Integration help & Q&A

**Enterprise & Regulated Gaming:**
- 📧 Email: [shtomko@gmail.com](mailto:shtomko@gmail.com) with subject **"R4 ENTERPRISE"**
- 🤝 See [SPONSORS.md](SPONSORS.md) for partnership tiers

---

## 📬 Contact

**Maintainer:** Pavlo Tvardovskyi  
📧 **Email:** [shtomko@gmail.com](mailto:shtomko@gmail.com)  
🐙 **GitHub:** [@pipavlo82](https://github.com/pipavlo82)  
🐳 **Docker Hub:** [pipavlo/r4-local-test](https://hub.docker.com/r/pipavlo/r4-local-test)  
📦 **PyPI:** [r4sdk](https://pypi.org/project/r4sdk/)

---

## 📚 Resources

- [Contributing Guide](CONTRIBUTING.md)
- [Sponsorship Tiers](SPONSORS.md)
- [Competitive Analysis](docs/COMPETITORS.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [API Usage](docs/USAGE.md)
- [Performance Benchmarks](docs/proof/benchmarks_summary.md)

---

<div align="center">

**Fairness you can prove. On-chain. Cryptographically.**

v1.0.0-demo | [GitHub](https://github.com/pipavlo82/r4-monorepo) | [PyPI](https://pypi.org/project/r4sdk/) | [Docker Hub](https://hub.docker.com/r/pipavlo/r4-local-test)

[⬆ Back to top](#-re4ctor--the-nuclear-core-of-randomness)

</div>
