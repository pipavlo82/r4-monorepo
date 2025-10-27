# 🎲 Provably Fair Lottery (LotteryR4.sol)

This example shows how to run a **provably fair on-chain lottery** using Re4ctoR randomness.

## 🧠 High-level idea

1. Players join the lottery on-chain (`enterLottery()`).
2. Re4ctoR node generates 32 bytes of randomness and signs it.
3. The lottery contract verifies that signature belongs to the trusted Re4ctoR node.
4. The winner is picked on-chain using that randomness.
5. An event is emitted so anyone can audit the draw.

No "admin picks winner". No backdoor. Fully transparent.

---

## 📦 Components

### 1. `R4VRFVerifier.sol`
- Verifies that a given `bytes32 randomness` was signed by the trusted signer.
- Uses standard ECDSA recovery.
- Emits `RandomnessVerified(...)` for auditability.

Path in repo:
```text
vrf-spec/contracts/R4VRFVerifier.sol
2. LotteryR4.sol
Stores a list of players.

Calls the verifier to make sure randomness is legit.

Computes the winner index from randomness.

Emits WinnerSelected(winner, index, randomness).

Path in repo:

text
Copy code
vrf-spec/contracts/LotteryR4.sol
🔁 Flow
text
Copy code
[ Re4ctoR API ] --randomness+signature--> [ LotteryR4 ]
                                      \
                                       \__ checked by R4VRFVerifier (ECDSA)
Step-by-step:

Off-chain service asks Re4ctoR for entropy.

Re4ctoR signs that entropy with its private key.

We send randomness + signature into the lottery contract.

Contract:

verifies signature on-chain,

calculates winnerIndex = uint256(randomness) % players.length,

emits a public event.

Anyone can reconstruct and verify the draw.

👥 Player join
Players just call:

solidity
Copy code
function enterLottery() external {
    players.push(msg.sender);
    emit PlayerEntered(msg.sender);
}
No admin approval. No lists off-chain. Everything is on-chain and queryable.

🏆 Drawing the winner
The core function:

solidity
Copy code
function drawWinner(bytes32 randomness, bytes calldata signature) external {
    require(players.length > 0, "no players");

    // 1. Check that this randomness was signed by the trusted Re4ctoR node
    bool ok = verifier.verify(randomness, signature, trustedSigner);
    require(ok, "invalid randomness signature");

    // 2. Deterministic, auditable winner index
    uint256 winnerIndex = uint256(randomness) % players.length;
    address winner = players[winnerIndex];

    emit WinnerSelected(winner, winnerIndex, randomness);
}
Why this matters:

The contract does not trust msg.sender for randomness.

Only randomness signed by trustedSigner (the Re4ctoR node key) is accepted.

If someone fakes a signature → tx reverts.

✅ Hardhat test (end-to-end)
We ship vrf-spec/test/lottery.js which:

deploys R4VRFVerifier

deploys LotteryR4 with that verifier and a trusted signer

simulates 3 players joining

generates a signed randomness (like Re4ctoR would)

calls drawWinner()

checks the emitted WinnerSelected(...) event

You can run it locally:

bash
Copy code
cd vrf-spec
npm install
npx hardhat compile
npx hardhat test
Expected result:

text
Copy code
LotteryR4
  ✔ picks a deterministic fair winner using verified randomness
  ✔ reverts if signature is invalid

R4VRFVerifier
  ✔ verifies a valid signature from the signer
  ✔ emits event on submitRandom()

4 passing
This is extremely powerful when pitching to:

casinos / iGaming / lootboxes,

NFT raffle / mint allowlist lotteries,

validator / committee / sequencer rotation for blockchain infra.

🔌 How to integrate in production
1. Off-chain service (backend / oracle / game server)
Call Re4ctoR entropy API to get randomness.

(Planned) Receive (randomness, signature) payload.

Broadcast that pair to chain (as tx into drawWinner()).

2. On-chain contract
Hardcodes trustedSigner = the Re4ctoR node address.

Verifies signature using R4VRFVerifier.

Announces the winner on-chain in an event.

3. Auditors / players
Anyone can recompute the same mod math and verify the same winner.

Anyone can verify the signature was correct (not forged by game operator).

🔐 Why casinos / regulators care
You can prove you didn't "reroll until VIP wins".

Regulator can verify the flow using public chain data.

Jackpot fairness becomes cryptographically provable instead of "trust us".

🧩 Bonus ideas
Auto-payout: extend LotteryR4 so drawWinner() also transfers prize.

Reset rounds: after a winner is picked, clear players[].

Escrow entry fees: require msg.value on enterLottery() and hold ETH/USDC in the contract.

Multi-chain: same pattern works on any EVM (Polygon, Arbitrum, etc.).

📎 Files of interest
vrf-spec/contracts/R4VRFVerifier.sol

vrf-spec/contracts/LotteryR4.sol

vrf-spec/test/lottery.js

vrf-spec/test/verify.js

📣 Contact
For integration, audits, or regulatory-grade fairness proofs:

Maintainer: Pavlo Tvardovskyi

Email: shtomko@gmail.com

GitHub: https://github.com/pipavlo82/r4-monorepo
